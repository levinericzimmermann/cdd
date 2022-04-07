import copy
import random

import voxpopuli

from mutwo import core_converters
from mutwo import core_events
from mutwo import mbrola_converters
from mutwo import midi_converters
from mutwo import music_events
from mutwo import music_parameters

import cdd


class SimpleEventToPhonemeString(core_converters.SimpleEventToAttribute):
    """Convert a simple event to a phoneme string."""

    def __init__(
        self,
        attribute_name: str = "phonetic_representation",
        exception_value: str = "_",
    ):
        super().__init__(attribute_name, exception_value)


class SequentialEventToMbrolaFriendlyEvent(core_converters.abc.EventConverter):
    def _convert_simple_event(self, event_to_convert, _):
        sequential_event = core_events.SequentialEvent([])
        try:
            phonetic_representation = event_to_convert.lyric.phonetic_representation
        except AttributeError:
            phonetic_representation = None
        if phonetic_representation:
            duration_per_event = event_to_convert.duration / len(
                phonetic_representation
            )
            for phoneme in phonetic_representation:
                new_event = music_events.NoteLike(
                    copy.deepcopy(event_to_convert.pitch_list),
                    duration=duration_per_event,
                )
                new_event.phoneme = phoneme
                sequential_event.append(new_event)
        else:
            sequential_event.append(event_to_convert)
        return sequential_event

    def _convert_sequential_event(self, event_to_convert, absolute_entry_delay):
        return core_events.SequentialEvent(
            super()._convert_sequential_event(event_to_convert, absolute_entry_delay)
        )

    def convert(self, event_to_convert):
        return self._convert_event(event_to_convert, 0)


def main(chapter: cdd.chapters.Chapter):
    tempo_converter = core_converters.TempoConverter(chapter.tempo_envelope)
    simultaneous_event = tempo_converter.convert(
        chapter.simultaneous_event.set_parameter(
            "duration", lambda duration: duration * 4, mutate=False
        )
    )

    to_mbrola_friendly = SequentialEventToMbrolaFriendlyEvent()
    pitch_converter_tuple = (
        lambda _: music_parameters.WesternPitch(
            random.choice(["a", "gqs", "aqs", "af", "aqf"]), 4
        ),
        lambda _: music_parameters.WesternPitch(
            random.choice(["f", "fqs", "fs", "e", "eqs"]), 3
        ),
        lambda _: music_parameters.WesternPitch(random.choice(["b", "bqs"]), 2),
    )
    for voice_index, voice in enumerate(simultaneous_event[1:]):
        voice = copy.deepcopy(voice)
        sequential_event_to_speaking_synthesis = (
            mbrola_converters.EventToSpeakSynthesis(
                voice=voxpopuli.Voice(lang="pt"),
                event_to_phoneme_list=mbrola_converters.EventToPhonemeList(
                    simple_event_to_pitch=pitch_converter_tuple[voice_index],
                ),
            )
        )
        path = chapter.get_sound_file_path(f"voice{voice_index}")
        mbrola_voice = to_mbrola_friendly(voice)
        sequential_event_to_speaking_synthesis.convert(mbrola_voice, path)

    event_to_midi_file = midi_converters.EventToMidiFile()
    event_to_midi_file.convert(
        simultaneous_event[0],
        chapter.get_midi_path("percussion"),
    )
