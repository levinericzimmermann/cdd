import functools
import itertools
import operator
import typing

import quicktions as fractions
import schillinger
import yamm

from mutwo import common_generators
from mutwo import core_constants
from mutwo import core_converters
from mutwo import core_events
from mutwo import core_utilities
from mutwo import csound_converters
from mutwo import midi_converters
from mutwo import music_events
from mutwo import music_parameters

import cdd


def make_rhythm_generator():
    def generator():
        generator_history_list = [2]
        generator_tuple = (2, 3)
        generator_iterator = itertools.cycle((1, 4, 2, 3))
        factor_cycle = itertools.cycle(
            (
                1,
                fractions.Fraction(2, 1),
                1,
                1,
                fractions.Fraction(3, 2),
                fractions.Fraction(5, 4),
            )
        )
        complementary_factor_cycle = itertools.cycle(
            (
                1,
                fractions.Fraction(1, 2),
                fractions.Fraction(1, 3),
                1,
                fractions.Fraction(1, 2),
            )
        )
        while True:
            if (generator_count := len(generator_tuple)) == 2:
                get_duration_tuple = schillinger.synchronize
                new_generator = next(generator_iterator)
                while new_generator in generator_tuple:
                    new_generator = next(generator_iterator)
                generator_history_list.append(new_generator)
                factor = next(factor_cycle)
                new_generator_tuple = generator_tuple + (new_generator,)
            elif generator_count == 3:
                factor = next(complementary_factor_cycle)
                get_duration_tuple = schillinger.synchronize_complementary
                generator_to_remove = generator_history_list[0]
                new_generator_tuple = tuple(
                    generator
                    for generator in generator_tuple
                    if generator != generator_to_remove
                )
                del generator_history_list[0]
            else:
                raise Exception("")
            rhythm = core_events.SequentialEvent(
                [
                    core_events.SimpleEvent(duration)
                    for duration in get_duration_tuple(*generator_tuple)
                ]
            )
            rhythm.duration *= factor
            yield rhythm
            generator_tuple = new_generator_tuple

    return generator()


VOICE_COUNT = 3


class DurationToRhythmSimultaneousEvent(core_converters.abc.Converter):
    start_voice_index_cycle = itertools.cycle(
        core_utilities.cyclic_permutations(tuple(range(VOICE_COUNT)))
    )

    activity_level = common_generators.ActivityLevel()

    def __init__(
        self,
        duration_of_one_beat: float,
        bell_activity_level: int,
        rhythm_generator: typing.Optional[
            typing.Generator[
                core_events.SequentialEvent[core_events.SimpleEvent],
                core_events.SequentialEvent[core_events.SimpleEvent],
                core_events.SequentialEvent[core_events.SimpleEvent],
            ]
        ] = None,
    ):
        if rhythm_generator is None:
            rhythm_generator = make_rhythm_generator()
        self._duration_of_one_beat = duration_of_one_beat
        self._bell_activity_level = bell_activity_level
        self._rhythm_generator = rhythm_generator

    def _get_rhythm(
        self, duration_in_seconds: float
    ) -> core_events.SequentialEvent[core_events.SimpleEvent]:
        rhythm = core_events.SequentialEvent([])
        while rhythm.duration < duration_in_seconds:
            rhythm_part = next(self._rhythm_generator)
            rhythm_part.duration *= self._duration_of_one_beat
            rhythm.extend(rhythm_part)
        while rhythm.duration > duration_in_seconds:
            rhythm = rhythm[:-1]

        rhythm.duration = duration_in_seconds
        return rhythm

    def _get_voice_index_cycle(self) -> typing.Iterator[int]:
        start_voice_index_tuple = next(self.start_voice_index_cycle)
        return itertools.cycle(
            functools.reduce(
                operator.add,
                tuple(core_utilities.cyclic_permutations(start_voice_index_tuple)),
            )
        )

    @staticmethod
    def _rhythm_data_to_simultaneous_event(
        rhythm_index_list_list: list[list[int]],
        rhythm: core_events.SequentialEvent[core_events.SimpleEvent],
        duration_in_seconds: float,
    ) -> core_events.SimultaneousEvent[core_events.SequentialEvent]:
        simultaneous_event = core_events.SimultaneousEvent([])
        rhythm_absolute_time = rhythm.absolute_time_tuple
        for rhythm_index_list in rhythm_index_list_list:
            sequential_event = core_events.SequentialEvent([])
            if 0 not in rhythm_index_list:
                rest = music_events.NoteLike(
                    [], duration=rhythm_absolute_time[rhythm_index_list[0]]
                )
                sequential_event.append(rest)
            for index0, index1 in zip(rhythm_index_list, rhythm_index_list[1:]):
                duration = rhythm_absolute_time[index1] - rhythm_absolute_time[index0]
                note_like = music_events.NoteLike("1/1", duration)
                sequential_event.append(note_like)
            difference = duration_in_seconds - sequential_event.duration
            if difference > 0:
                rest = music_events.NoteLike([], difference)
                sequential_event.append(rest)
            simultaneous_event.append(sequential_event)
        return simultaneous_event

    def _distribute_rhythm_on_sine_voices(
        self,
        rhythm: core_events.SequentialEvent[core_events.SimpleEvent],
        duration_in_seconds: float,
    ) -> core_events.SimultaneousEvent[core_events.SequentialEvent]:
        sine_rhythm_index_list_list = [[] for _ in range(VOICE_COUNT)]
        voice_index_cycle = self._get_voice_index_cycle()
        for index, _ in enumerate(rhythm):
            voice_index = next(voice_index_cycle)
            sine_rhythm_index_list_list[voice_index].append(index)

        return self._rhythm_data_to_simultaneous_event(
            sine_rhythm_index_list_list, rhythm, duration_in_seconds
        )

    def _distribute_rhythm_on_bell_voices(
        self,
        rhythm: core_events.SequentialEvent[core_events.SimpleEvent],
        duration_in_seconds: float,
    ) -> core_events.SimultaneousEvent[core_events.SequentialEvent]:
        bell_rhythm_index_list_list = [[] for _ in range(VOICE_COUNT)]
        voice_index_tuple_cycle = itertools.cycle(
            (
                (0,),
                (1, 2),
                (0, 2),
            )
        )
        for index, _ in enumerate(rhythm):
            if self.activity_level(self._bell_activity_level):
                voice_index_tuple = next(voice_index_tuple_cycle)
                for voice_index in voice_index_tuple:
                    bell_rhythm_index_list_list[voice_index].append(index)

        return self._rhythm_data_to_simultaneous_event(
            bell_rhythm_index_list_list, rhythm, duration_in_seconds
        )

    def convert(
        self, duration_in_seconds: float
    ) -> core_events.SimultaneousEvent[
        core_events.SimultaneousEvent[core_events.SequentialEvent]
    ]:
        rhythm = self._get_rhythm(duration_in_seconds)
        sine_voice_rhythm_simultaneous_event = self._distribute_rhythm_on_sine_voices(
            rhythm, duration_in_seconds
        )
        bell_voice_rhythm_simultaneous_event = self._distribute_rhythm_on_bell_voices(
            rhythm, duration_in_seconds
        )

        return core_events.SimultaneousEvent(
            [
                sine_voice_rhythm_simultaneous_event,
                bell_voice_rhythm_simultaneous_event,
            ]
        )


class RhythmSequentialEventToPitchedSequentialEvent(
    core_converters.abc.SymmetricalEventConverter
):
    comma_tuple: tuple[music_parameters.JustIntonationPitch, ...] = tuple(
        music_parameters.JustIntonationPitch(ratio)
        for ratio in "27/28 63/64 1/1 81/80 33/32".split(" ")
    )
    comma_index_tuple = tuple(range(len(comma_tuple)))
    comma_weight_tuple: tuple[int, ...] = (1, 3, 5, 3, 1)

    decibel_difference_tuple = (-20, -10, 0, -10, -20)

    assert len(comma_tuple) == len(comma_weight_tuple) == len(decibel_difference_tuple)

    def __init__(
        self,
        pitch_offset: music_parameters.JustIntonationPitch,
    ):
        self._pitch_tuple = tuple(
            pitch_offset + pitch_comma for pitch_comma in self.comma_tuple
        )
        self._pitch_and_decibel_iterator = self._get_pitch_and_decibel_iterator()
        self._previous_pitch = None

    def _get_pitch_and_decibel_iterator(
        self,
    ) -> typing.Iterator[music_parameters.JustIntonationPitch]:
        markov_chain = yamm.Chain(
            {
                (comma_index,): {
                    other_comma_index: self.comma_weight_tuple[other_comma_index]
                    if other_comma_index != comma_index
                    else 1
                    for other_comma_index in self.comma_index_tuple
                }
                for comma_index in self.comma_index_tuple
            }
        )
        markov_chain.make_deterministic_map()
        pitch_index_iterator = markov_chain.walk_deterministic((0,))

        def pitch_and_decibel_iterator():
            while True:
                pitch_index = next(pitch_index_iterator)
                yield self._pitch_tuple[pitch_index], self.decibel_difference_tuple[
                    pitch_index
                ]

        return pitch_and_decibel_iterator()

    def _convert_simple_event(
        self,
        event_to_convert: core_events.SimpleEvent,
        _: core_constants.DurationType,
    ) -> core_events.SimpleEvent:
        if event_to_convert.pitch_list:
            new_pitch, decibel_difference = next(self._pitch_and_decibel_iterator)
            converted_event = event_to_convert.set_parameter(
                "pitch_list", new_pitch, mutate=False
            )
            converted_event.volume = music_parameters.DecibelVolume(
                converted_event.volume.decibel + decibel_difference
            )
            if (previous_pitch := self._previous_pitch) is None:
                previous_pitch = converted_event.pitch_list[0]
            converted_event.previous_pitch = previous_pitch
            self._previous_pitch = converted_event.pitch_list[0]
        else:
            converted_event = event_to_convert.set_parameter("volume", 0, mutate=False)
        return converted_event

    def convert(
        self, event_to_convert: core_events.SequentialEvent
    ) -> core_events.SequentialEvent:
        return self._convert_event(event_to_convert, 0)


class GlimmeringEvent(core_events.SimpleEvent):
    def __init__(
        self,
        base_pitch: music_parameters.JustIntonationPitch,
        duration: core_constants.DurationType,
        duration_of_one_beat: float = 0.15,
        bell_activity_level: int = 1,
    ):
        super().__init__(duration)
        self.base_pitch = base_pitch
        self.duration_of_one_beat = duration_of_one_beat
        self.bell_activity_level = bell_activity_level


class GlimmeringSequentialEventToSimultaneousEvent(core_converters.abc.EventConverter):
    SineSimultaneousEvent = core_events.SimultaneousEvent[
        core_events.SequentialEvent[music_events.NoteLike]
    ]
    BellSimultaneousEvent = core_events.SimultaneousEvent[
        core_events.SequentialEvent[music_events.NoteLike]
    ]

    MixedSimultaneousEvent = core_events.SimultaneousEvent[
        typing.Union[SineSimultaneousEvent, BellSimultaneousEvent]
    ]

    def _convert_simple_event(
        self,
        event_to_convert: core_events.SimpleEvent,
        _: core_constants.DurationType,
    ) -> typing.Union[music_events.NoteLike, MixedSimultaneousEvent]:
        if isinstance(event_to_convert, GlimmeringEvent):
            duration_to_rhythm_simultaneous_event = DurationToRhythmSimultaneousEvent(
                event_to_convert.duration_of_one_beat,
                event_to_convert.bell_activity_level,
            )
            rhythm_simultaneous_event = duration_to_rhythm_simultaneous_event.convert(
                event_to_convert.duration
            )
            rhythm_sequentialevent_to_pitched_sequential_event = (
                RhythmSequentialEventToPitchedSequentialEvent(
                    event_to_convert.base_pitch
                )
            )
            converted_event = (
                rhythm_sequentialevent_to_pitched_sequential_event.convert(
                    rhythm_simultaneous_event
                )
            )

        # rest
        else:
            converted_event = music_events.NoteLike(
                [], duration=event_to_convert.duration
            )

        return (converted_event,)

    def _add_fade_in_and_fade_out_to_sequential_event(
        self, sequential_event: core_events.SequentialEvent[music_events.NoteLike]
    ):
        duration = sequential_event.duration
        envelope = core_events.Envelope(
            [[0, -40], [duration * 0.4, 0], [duration * 0.66, 0], [duration, -45]]
        )
        for absolute_time, event in zip(
            sequential_event.absolute_time_tuple, sequential_event
        ):
            event.volume = music_parameters.DecibelVolume(
                event.volume.decibel + envelope.value_at(absolute_time)
            )
        return sequential_event

    def convert(
        self,
        event_to_convert: core_events.SequentialEvent[
            typing.Union[GlimmeringEvent, core_events.SimpleEvent]
        ],
    ) -> MixedSimultaneousEvent:
        simultaneous_event = core_events.SimultaneousEvent(
            [
                core_events.SimultaneousEvent(
                    [core_events.SequentialEvent([]) for _ in range(VOICE_COUNT)]
                )
                for _ in range(2)
            ]
        )
        for converted_event in self._convert_event(event_to_convert, 0):
            if isinstance(converted_event, music_events.NoteLike):
                for sub_simultaneous_event in simultaneous_event:
                    for sequential_event in sub_simultaneous_event:
                        sequential_event.append(
                            converted_event.set_parameter(
                                "duration", converted_event.duration, mutate=False
                            )
                        )
            else:
                for main_simultaneous_event, new_simultaneous_event in zip(
                    simultaneous_event, converted_event
                ):
                    for main_sequential_event, new_sequential_event in zip(
                        main_simultaneous_event, new_simultaneous_event
                    ):
                        main_sequential_event.extend(
                            self._add_fade_in_and_fade_out_to_sequential_event(
                                new_sequential_event
                            )
                        )
        return simultaneous_event


def _get_glimmering_sequential_event():
    octave = 0
    pitch_index_to_pitch_dict = {
        0: music_parameters.JustIntonationPitch("1/1").register(octave),
        # 1: music_parameters.JustIntonationPitch("256/243").register(octave),
        1: music_parameters.JustIntonationPitch("32/27").register(octave),
        # 2: music_parameters.JustIntonationPitch("32/27").register(octave),
        2: music_parameters.JustIntonationPitch("4/3").register(octave),
    }

    glimmering_sequential_event = core_events.SequentialEvent(
        [
            # 0:00
            core_events.SimpleEvent(40),
            # 0:40
            GlimmeringEvent(
                pitch_index_to_pitch_dict[1],
                21,
                duration_of_one_beat=0.15,
            ),
            # 1:01
            GlimmeringEvent(
                pitch_index_to_pitch_dict[0],
                35,
                duration_of_one_beat=0.2,
            ),
            # 1:36
            core_events.SimpleEvent(14),
            # 1:50
            GlimmeringEvent(
                pitch_index_to_pitch_dict[2],
                26,
                duration_of_one_beat=0.125,
            ),
            # 2:16
            GlimmeringEvent(
                pitch_index_to_pitch_dict[0],
                39,
                duration_of_one_beat=0.225,
            ),
            # 2:55
            core_events.SimpleEvent(15),
        ]
    )
    return glimmering_sequential_event


def _get_mixed_simultaneous_event():
    glimmering_sequential_event = _get_glimmering_sequential_event()

    return GlimmeringSequentialEventToSimultaneousEvent().convert(
        glimmering_sequential_event
    )


def _render_sine(
    chapter: cdd.chapters.Chapter,
    sine_simultaneous_event: core_events.SimultaneousEvent,
):
    event_to_csound_score = csound_converters.EventToCsoundScore(
        p3=lambda note_like: note_like.duration * 1.2,
        p4=lambda note_like: note_like.pitch_list[0].frequency
        if note_like.pitch_list
        else 0,
        p5=lambda note_like: note_like.volume.amplitude if note_like.pitch_list else 0,
        p6=lambda note_like: note_like.previous_pitch.frequency,
    )
    event_to_sound_file = csound_converters.EventToSoundFile(
        f"{cdd.configurations.PATH.ETC.CSOUND}/6_sine.orc", event_to_csound_score
    )

    for voice_index, sequential_event in enumerate(sine_simultaneous_event):
        sound_file_path = chapter.get_sound_file_path(f"sine-{voice_index}")
        event_to_sound_file.convert(sequential_event, sound_file_path)


def _render_simple_sine(
    chapter: cdd.chapters.Chapter,
):
    event_to_csound_score = csound_converters.EventToCsoundScore(
        p4=lambda note_like: note_like.pitch_list[0].frequency * 2
        if note_like.pitch_list
        else 0,
    )
    event_to_sound_file = csound_converters.EventToSoundFile(
        f"{cdd.configurations.PATH.ETC.CSOUND}/6_simple_sine.orc", event_to_csound_score
    )

    pitch_tuple = core_utilities.uniqify_sequence(
        tuple(
            filter(bool, _get_glimmering_sequential_event().get_parameter("base_pitch"))
        )
    )

    for pitch_index, pitch in enumerate(pitch_tuple):
        sound_file_path = chapter.get_sound_file_path(f"simple-sine-{pitch_index}")
        note_like = music_events.NoteLike(pitch, 45)
        event_to_sound_file.convert(note_like, sound_file_path)


def _render_bell(
    chapter: cdd.chapters.Chapter,
    bell_simultaneous_event: core_events.SimultaneousEvent,
):
    # event_to_midi_file = midi_converters.EventToMidiFile()

    event_to_csound_score = csound_converters.EventToCsoundScore(
        p4=lambda note_like: note_like.pitch_list[0].frequency
        if note_like.pitch_list
        else 0,
        p5=lambda note_like: note_like.volume.amplitude if note_like.pitch_list else 0,
    )
    event_to_sound_file = csound_converters.EventToSoundFile(
        f"{cdd.configurations.PATH.ETC.CSOUND}/6_bell.orc", event_to_csound_score
    )

    for voice_index, sequential_event in enumerate(bell_simultaneous_event):
        sound_file_path = chapter.get_sound_file_path(f"bell-{voice_index}")
        event_to_sound_file.convert(sequential_event, sound_file_path)
        # sequential_event = sequential_event.copy()
        # sequential_event.duration *= 2
        # midi_file_path = chapter.get_midi_path(f"bell-{voice_index}")
        # event_to_midi_file.convert(sequential_event, midi_file_path)


def render(chapter: cdd.chapters.Chapter):
    _render_simple_sine(chapter)

    sine_simultaneous_event, bell_simultaneous_event = _get_mixed_simultaneous_event()
    _render_sine(chapter, sine_simultaneous_event)
    _render_bell(chapter, bell_simultaneous_event)
