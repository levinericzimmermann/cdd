import copy
import random

import voxpopuli

from mutwo import cdd_converters
from mutwo import core_converters
from mutwo import mbrola_converters
from mutwo import midi_converters
from mutwo import music_parameters

import cdd


def render(chapter: cdd.chapters.Chapter):
    tempo_converter = core_converters.TempoConverter(chapter.tempo_envelope)
    simultaneous_event = tempo_converter.convert(chapter.simultaneous_event)
    # simultaneous_event = chapter.simultaneous_event.set_parameter(
    #     "duration", lambda duration: duration * 2, mutate=False
    # )
    to_mbrola_friendly = cdd_converters.SequentialEventToMbrolaFriendlyEvent()
    pitch_converter_tuple = (
        lambda _: music_parameters.WesternPitch(
            random.choice(["c", "cqs", "dqs", "cf", "cqf"]), 4
        ),
        lambda _: music_parameters.WesternPitch(
            random.choice(["f", "fqs", "fs", "e", "eqs"]), 3
        ),
        lambda _: music_parameters.WesternPitch(random.choice(["b", "bqs"]), 2),
    )
    for voice_index, voice in enumerate(simultaneous_event[1:]):
        voice = copy.deepcopy(voice)
        sequential_event_to_speaking_synthesis = (
            cdd_converters.EventToSafeSpeakingSynthesis(
                mbrola_converters.EventToSpeakSynthesis(
                    voice=voxpopuli.Voice(lang="pt"),
                    event_to_phoneme_list=mbrola_converters.EventToPhonemeList(
                        simple_event_to_pitch=pitch_converter_tuple[voice_index],
                    ),
                )
            )
        )
        path = chapter.get_sound_file_path(f"voice{voice_index}")
        mbrola_voice = to_mbrola_friendly(voice)
        sequential_event_to_speaking_synthesis.convert(mbrola_voice, path)

    event_to_midi_file = midi_converters.EventToMidiFile()
    event_to_midi_file.convert(
        simultaneous_event[0].set_parameter(
            "duration", lambda duration: duration * 2, mutate=False
        ),
        chapter.get_midi_path("percussion"),
    )
