import copy

from mutwo import cdd_converters
from mutwo import core_converters
from mutwo import core_events
from mutwo import isis_converters
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
    sequential_event_to_singing_synthesis = cdd_converters.EventToSafeSingingSynthesis(
        isis_converters.EventToSingingSynthesis(
            isis_converters.EventToIsisScore(
                simple_event_to_vowel=lambda simple_event: simple_event.lyric.vowel,
                simple_event_to_consonant_tuple=lambda simple_event: simple_event.lyric.consonant_tuple,
            ),
            "--cfg_synth etc/isis-cfg-synth.cfg",
            "--cfg_style etc/isis-cfg-style.cfg",
            "--seed 100",
        )
    )
    for index, sequential_event in enumerate(chapter.soprano_sequential_event_tuple):
        path = f"{chapter.get_sound_file_path('soprano')}_{index}.wav"
        sequential_event = sequential_event.copy()
        sequential_event.duration *= 4
        for index, simple_event in enumerate(sequential_event):
            if not simple_event.lyric.written_representation:
                simple_event.lyric = music_parameters.DirectLyric(
                    sequential_event[index - 1].lyric.vowel
                )
            simple_event.duration = float(simple_event.duration)
        sequential_event_to_singing_synthesis.convert(sequential_event, path)
