import voxpopuli

from mutwo import core_converters
from mutwo import mbrola_converters
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


def main(chapter: cdd.chapters.Chapter):
    def simple_event_to_phoneme_string(simple_event_to_convert) -> str:
        if hasattr(simple_event_to_convert, "lyric"):
            phonetic_representation = (
                simple_event_to_convert.lyric.phonetic_representation
            )
        else:
            phonetic_representation = "_"
        return phonetic_representation

    sequential_event_to_speaking_synthesis = mbrola_converters.EventToSpeakSynthesis(
        voice=voxpopuli.Voice(lang="pt"),
        event_to_phoneme_list=mbrola_converters.EventToPhonemeList(
            simple_event_to_pitch=lambda _: music_parameters.WesternPitch("e", 4),
            simple_event_to_phoneme_string=simple_event_to_phoneme_string,
        ),
    )
    for voice_index, voice in enumerate(chapter.simultaneous_event[1:]):
        path = chapter.get_sound_file_path(f"voice{voice_index}")
        # voice.duration = 1
        voice = voice[1:5]
        sequential_event_to_speaking_synthesis.convert(voice, path)
