import functools
import operator
import random

import expenvelope
import voxpopuli

from mutwo import cdd_converters
from mutwo import core_converters
from mutwo import core_events
from mutwo import isis_converters
from mutwo import mbrola_converters
from mutwo import midi_converters
from mutwo import music_converters
from mutwo import music_events
from mutwo import music_parameters

import cdd


def render_soprano(chapter: cdd.chapters.Chapter):
    def simple_event_to_pitch(simple_event):
        pitch_list = simple_event.pitch_list
        if pitch_list:
            return pitch_list[0]
        else:
            raise AttributeError()

    sequential_event_to_singing_synthesis = cdd_converters.EventToSafeSingingSynthesis(
        isis_converters.EventToSingingSynthesis(
            isis_converters.EventToIsisScore(
                simple_event_to_vowel=lambda simple_event: simple_event.lyric.vowel,
                simple_event_to_consonant_tuple=lambda simple_event: simple_event.lyric.consonant_tuple,
                simple_event_to_pitch=simple_event_to_pitch,
            ),
            "--cfg_synth etc/isis/isis-cfg-synth.cfg",
            "--cfg_style etc/isis/isis-cfg-style.cfg",
            # "-sv EL",
            "-sv MS",
            "--seed 100",
        ),
    )

    grace_note_converter = music_converters.GraceNotesConverter()
    soprano = core_events.SequentialEvent([])
    for absolute_time_in_seconds, repetition_count, sequential_event in zip(
        chapter.soprano_sequential_event_absolute_time_tuple,
        chapter.soprano_repetition_count_tuple,
        chapter.soprano_sequential_event_tuple,
    ):
        difference = absolute_time_in_seconds - soprano.duration
        if difference > 0:
            soprano.append(core_events.SimpleEvent(difference))
        elif difference < 0:
            raise Exception(f"DIFFERENCE: {difference}")
        for counter in range(repetition_count):
            local_sequential_event = sequential_event.copy()
            tempo_converter = core_converters.TempoConverter(
                expenvelope.Envelope.from_points(
                    (
                        0,
                        random.uniform(
                            chapter.SOPRANO.tempo_range.start,
                            chapter.SOPRANO.tempo_range.end,
                        )
                        / 4,
                    )
                )
            )
            local_sequential_event = grace_note_converter(
                tempo_converter.convert(local_sequential_event)
            )
            # local_sequential_event.set_parameter("volume", "p")
            for index, simple_event in enumerate(local_sequential_event):
                if not simple_event.lyric.written_representation:
                    simple_event.lyric = music_parameters.DirectLyric(
                        local_sequential_event[index - 1].lyric.vowel
                    )
                simple_event.duration = float(simple_event.duration)
            soprano.extend(local_sequential_event)
            # Add rest with random duration
            if counter + 1 != repetition_count:
                soprano.append(
                    core_events.SimpleEvent(
                        random.uniform(
                            chapter.SOPRANO.repetition_rest_duration_range.start,
                            chapter.SOPRANO.repetition_rest_duration_range.end,
                        )
                    )
                )

    path = chapter.get_sound_file_path("soprano")
    sequential_event_to_singing_synthesis.convert(soprano, path)


def render_clarinet(chapter: cdd.chapters.Chapter):
    instrument = "clarinet"
    base_midi_file_path = chapter.get_midi_path(instrument)

    event_to_midi_file = midi_converters.EventToMidiFile()

    for event_index, simultaneous_event in enumerate(
        chapter.soprano_and_clarinet_unisono_simultaneous_event_tuple
    ):
        tempo_converter = core_converters.TempoConverter(
            expenvelope.Envelope.from_points(
                (
                    0,
                    random.uniform(
                        chapter.SOPRANO.tempo_range.start,
                        chapter.SOPRANO.tempo_range.end,
                    )
                    / 4,
                )
            )
        )
        soprano_sequential_event = tempo_converter.convert(simultaneous_event[1])
        soprano_sequential_event.set_parameter("volume", "p")
        soprano_sequential_event.duration *= 2
        event_to_midi_file.convert(
            soprano_sequential_event,
            f"{base_midi_file_path}_soprano_{event_index}.mid",
        )


def render_clavichord(chapter: cdd.chapters.Chapter):
    instrument = "clavichord"

    midi_file_path = chapter.get_midi_path(instrument)
    sound_file_path = chapter.get_sound_file_path(instrument)

    to_mbrola_friendly = cdd_converters.SequentialEventToMbrolaFriendlyEvent()

    playing_indicators_converter = music_converters.PlayingIndicatorsConverter(
        [music_converters.ArpeggioConverter(duration_for_each_attack=0.18)]
    )
    grace_note_converter = music_converters.GraceNotesConverter()

    event_to_midi_file = midi_converters.EventToMidiFile()

    sequential_event_to_speaking_synthesis = cdd_converters.EventToSafeSpeakingSynthesis(
        mbrola_converters.EventToSpeakSynthesis(
            voice=voxpopuli.Voice(lang="pt"),
            event_to_phoneme_list=mbrola_converters.EventToPhonemeList(
                simple_event_to_pitch=lambda *_, **__: music_parameters.WesternPitch(
                    random.choice(["b", "bqs", "bqf"]), 3
                ),
            ),
        )
    )

    max_spoken_work_duration = 2
    clavichord = core_events.SequentialEvent([])
    voice = core_events.SequentialEvent([])
    for sequential_event in chapter.clavichord_sequential_event_tuple:
        voice_sequential_event = sequential_event.copy()
        voice_sequential_event.duration = chapter.CLAVICHORD.line_duration
        new_voice_sequential_event = core_events.SequentialEvent([])
        for simple_event in voice_sequential_event:
            rest_duration = 0
            if hasattr(simple_event, "pitch_list"):
                if not simple_event.lyric.phonetic_representation:
                    simple_event.pitch_list = []
                else:
                    difference = simple_event.duration - max_spoken_work_duration
                    if difference > 0:
                        simple_event.duration = max_spoken_work_duration
                        rest_duration = difference
            new_voice_sequential_event.append(simple_event)
            if rest_duration > 0:
                new_voice_sequential_event.append(
                    core_events.SimpleEvent(rest_duration)
                )
        new_voice_sequential_event.tie_by(
            lambda event0, event1: cdd.utilities.is_rest(event0)
            and cdd.utilities.is_rest(event1)
        )
        voice.extend(to_mbrola_friendly(new_voice_sequential_event.copy()))

        new_sequential_event = sequential_event.copy()
        # * 2 because default tempo is 120 bpm
        new_sequential_event.duration = chapter.CLAVICHORD.line_duration * 2
        new_sequential_event = grace_note_converter.convert(new_sequential_event)
        new_sequential_event = functools.reduce(
            operator.add, playing_indicators_converter.convert(new_sequential_event)
        )
        clavichord.extend(new_sequential_event)

    voice.tie_by(
        lambda event0, event1: cdd.utilities.is_rest(event0)
        and cdd.utilities.is_rest(event1)
    )

    event_to_midi_file.convert(clavichord, midi_file_path)
    # sequential_event_to_speaking_synthesis(voice, sound_file_path)


def render_noise(chapter: cdd.chapters.Chapter):
    instrument = "noise"
    midi_file_path = chapter.get_midi_path(instrument)
    event_to_midi_file = midi_converters.EventToMidiFile()

    sequential_event = core_converters.TempoConverter(
        expenvelope.Envelope.from_points([0, 60 / 2])
    ).convert(
        core_events.SequentialEvent(
            [
                music_events.NoteLike("c", start1 - start0)
                for start0, start1 in zip(
                    (0,) + chapter.NOISE.absolute_time_tuple,
                    chapter.NOISE.absolute_time_tuple
                    + (chapter.NOISE.absolute_time_tuple[-1] + 1,),
                )
            ]
        )
    )

    sequential_event[0].pitch_list = []

    event_to_midi_file.convert(
        sequential_event,
        midi_file_path,
    )


def main(chapter: cdd.chapters.Chapter):
    render_noise(chapter)
    render_clavichord(chapter)
    render_clarinet(chapter)
    # render_soprano(chapter)  # a bit slowly, therefore only render if necessary
