import copy
import itertools

import quicktions as fractions

from mutwo import common_generators
from mutwo import core_converters
from mutwo import core_events
from mutwo import csound_converters
from mutwo import midi_converters
from mutwo import music_events
from mutwo import music_parameters

from cdd import configurations


class TimeSignatureSequenceToRhythmSequentialEvent(core_converters.abc.Converter):
    def __init__(
        self,
        base_rhythm: core_events.SequentialEvent = core_events.SequentialEvent(
            [
                music_events.NoteLike([], fractions.Fraction(1, 2), volume="pp"),
                music_events.NoteLike([], fractions.Fraction(1, 1), volume="pp"),
            ]
        ),
    ):
        self._base_rhythm = base_rhythm
        self._base_rhythm_duration = base_rhythm.duration

    def convert(self, time_signature_sequence) -> core_events.SequentialEvent:
        rhythm = core_events.SequentialEvent([])
        for time_signature in time_signature_sequence:
            bar_duration = fractions.Fraction(time_signature.duration)
            base_rhythm_count = int(bar_duration // self._base_rhythm_duration)
            local_rhythm = core_events.SequentialEvent([])
            for _ in range(base_rhythm_count):
                local_rhythm.extend(self._base_rhythm.copy())
            difference = bar_duration - local_rhythm.duration
            if difference > 0:
                local_rhythm.append(core_events.SimpleEvent(difference))
            rhythm.extend(local_rhythm)
        return rhythm


class ChordSequentialEventToPitchListTuple(core_converters.abc.Converter):
    def __init__(
        self,
        start_register: int = 2,
        minima_register: int = 1,
        maxima_register: int = 3,
    ):
        self._start_register = start_register
        self._minima_register, self._maxima_register = minima_register, maxima_register

    def _get_best_voice_leading_pitch_list(
        self,
        pitch_list: list[music_parameters.JustIntonationPitch],
        previous_pitch_list: list[music_parameters.JustIntonationPitch],
    ) -> list[music_parameters.JustIntonationPitch]:
        pitch_and_cent_deviation_list_list = []
        for current_pitch in pitch_list:
            pitch_and_cent_deviation_list = []
            for previous_pitch in previous_pitch_list:
                closest_pitch = current_pitch.move_to_closest_register(
                    previous_pitch, mutate=False
                )
                if (octave := closest_pitch.octave) < self._minima_register:
                    closest_pitch.register(self._minima_register)
                elif octave > self._maxima_register:
                    closest_pitch.register(self._maxima_register)
                cent_deviation = abs((closest_pitch - previous_pitch).interval)
                pitch_and_cent_deviation_list.append((closest_pitch, cent_deviation))
            pitch_and_cent_deviation_list_list.append(pitch_and_cent_deviation_list)

        champion = None
        fitness = float("inf")
        for permutation in itertools.permutations(range(len(previous_pitch_list))):
            candidate = [
                pitch_and_cent_deviation_list[index]
                for pitch_and_cent_deviation_list, index in zip(
                    pitch_and_cent_deviation_list_list, permutation
                )
            ]
            pitch_list_candidate, interval_list_candidate = zip(*candidate)
            fitness_candidate = sum(interval_list_candidate)
            if fitness_candidate < fitness:
                champion, fitness = pitch_list_candidate, fitness_candidate

        return champion

    def convert(
        self, chord_sequential_event: core_events.SequentialEvent
    ) -> tuple[list[music_parameters.abc.Pitch], ...]:
        pitch_list_list = []
        for pitch_list in chord_sequential_event.get_parameter("pitch_list"):
            if not pitch_list_list:
                new_pitch_list = [
                    pitch.register(self._start_register, mutate=False)
                    for pitch in pitch_list
                ]

            else:
                new_pitch_list = self._get_best_voice_leading_pitch_list(
                    pitch_list, pitch_list_list[-1]
                )

            pitch_list_list.append(new_pitch_list)
        return tuple(pitch_list_list)


class ChapterToSequentialEvent(core_converters.abc.Converter):
    def __init__(
        self,
        chord_sequential_event_to_pitch_list_tuple: ChordSequentialEventToPitchListTuple = ChordSequentialEventToPitchListTuple(),
        time_signature_sequence_to_rhythm_sequential_event: TimeSignatureSequenceToRhythmSequentialEvent = TimeSignatureSequenceToRhythmSequentialEvent(),
    ):
        self._time_signature_sequence_to_rhythm_sequential_event = (
            time_signature_sequence_to_rhythm_sequential_event
        )
        self._chord_sequential_event_to_pitch_list_tuple = (
            chord_sequential_event_to_pitch_list_tuple
        )

    def convert(self, chapter):
        sequential_event = self._time_signature_sequence_to_rhythm_sequential_event(
            chapter.time_signature_sequence
        )
        pitch_list_tuple = self._chord_sequential_event_to_pitch_list_tuple(
            chapter.chord_sequential_event
        )

        for absolute_time, note_like_or_simple_event in zip(
            sequential_event.absolute_time_tuple, sequential_event
        ):
            if hasattr(note_like_or_simple_event, "pitch_list"):
                pitch_list = pitch_list_tuple[
                    chapter.time_range_to_pitch_list_index_dict[absolute_time]
                ]
                note_like_or_simple_event.pitch_list = [
                    copy.deepcopy(pitch) for pitch in pitch_list
                ]

        tempo_converter = core_converters.TempoConverter(chapter.tempo_envelope)
        sequential_event = tempo_converter(sequential_event)

        return sequential_event


class SequentialEventToSimultaneousEvent(core_converters.abc.Converter):
    def convert(
        self, sequential_event: core_events.SequentialEvent
    ) -> core_events.SimultaneousEvent:
        simultaneous_event = core_events.SimultaneousEvent(
            [core_events.SequentialEvent([]) for _ in range(3)]
        )
        gray_code_cycle = itertools.cycle(common_generators.reflected_binary_code(3, 4))
        for note_like_or_simple_event in sequential_event:
            if (
                hasattr(note_like_or_simple_event, "pitch_list")
                and note_like_or_simple_event.pitch_list
            ):
                channel_tuple = next(gray_code_cycle)
                for sequential_event, pitch, channel in zip(
                    simultaneous_event,
                    note_like_or_simple_event.pitch_list,
                    channel_tuple,
                ):
                    new_note_like = note_like_or_simple_event.set_parameter(
                        "pitch_list", [pitch], mutate=False
                    )
                    new_note_like.channel = channel
                    sequential_event.append(new_note_like)
            else:
                for sequential_event in simultaneous_event:
                    sequential_event.append(copy.deepcopy(note_like_or_simple_event))

        return simultaneous_event


def to_sound_file(sequential_event, chapter, instrument_name):
    event_to_csound_score = csound_converters.EventToCsoundScore(
        p4=lambda note_like: note_like.pitch_list[0].frequency
        if note_like.pitch_list
        else note_like.UNAVAILABLE_ATTRIBUTE,
        p5=lambda note_like: note_like.volume.amplitude,
        p6=lambda note_like: note_like.channel,
    )
    event_to_sound_file = csound_converters.EventToSoundFile(
        f"{configurations.PATH.ETC.CSOUND}/12_chords.orc", event_to_csound_score
    )
    sequential_event.duration *= 4
    simultaneous_event = SequentialEventToSimultaneousEvent()(sequential_event)
    event_to_sound_file.convert(
        simultaneous_event, chapter.get_sound_file_path(instrument_name)
    )


def to_midi_file(sequential_event, chapter, instrument_name):
    event_to_midi_file = midi_converters.EventToMidiFile()
    sequential_event.duration *= 8
    event_to_midi_file.convert(sequential_event, chapter.get_midi_path(instrument_name))


def main(chapter):
    sequential_event = ChapterToSequentialEvent()(chapter)
    instrument_name = "tape_chords"

    to_sound_file(sequential_event.copy(), chapter, instrument_name)
    to_midi_file(sequential_event.copy(), chapter, instrument_name)
