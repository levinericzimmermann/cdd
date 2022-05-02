import functools
import os
import operator

from mutwo import cdd_converters
from mutwo import core_converters
from mutwo import csound_converters
from mutwo import isis_converters
from mutwo import midi_converters
from mutwo import music_converters

import cdd


class EventToVolumeControl(csound_converters.EventToSoundFile):
    csound_orchestra = r"""
0dbfs=1
instr 1
    asig poscil 1, 200
    istartAndEnd = p3 * 0.4
    icenter = p3 * 0.2
    kenv expseg p4, istartAndEnd, p5, icenter, p5, istartAndEnd, p6
    out asig * kenv
endin
"""

    def __init__(self):
        def p4(note_like):
            playing_indicator_collection = note_like.playing_indicator_collection
            if hairpin := playing_indicator_collection.hairpin.symbol:
                if hairpin in ('<', '<>'):
                    return 0.0001
                elif hairpin == ">":
                    return 1
            return 0.0001

        def p5(note_like):
            playing_indicator_collection = note_like.playing_indicator_collection
            if hairpin := playing_indicator_collection.hairpin.symbol:
                if hairpin in ('>', '<'):
                    return 0.3
                else:
                    return 1
            return 0.0001

        def p6(note_like):
            playing_indicator_collection = note_like.playing_indicator_collection
            if hairpin := playing_indicator_collection.hairpin.symbol:
                if hairpin in ('>', '<>'):
                    return 0.0001
                elif hairpin == "<":
                    return 1
            return 0.0001

        super().__init__(
            ".event_to_volume_control.orc",
            csound_converters.EventToCsoundScore(
                p4=p4,
                p5=p5,
                p6=p6,
            ),
        )

    def _write_orchestra(self):
        with open(self.csound_orchestra_path, "w") as csound_orchestra:
            csound_orchestra.write(self.csound_orchestra)

    def _remove_orchestra(self):
        try:
            os.remove(self.csound_orchestra_path)
        except Exception:
            pass

    def convert(self, *args, **kwargs):
        self._write_orchestra()
        super().convert(*args, **kwargs)
        self._remove_orchestra()


def main(chapter: cdd.chapters.Chapter):
    def simple_event_to_pitch(simple_event):
        pitch_list = simple_event.pitch_list
        if pitch_list:
            return pitch_list[0]
        else:
            raise AttributeError()

    event_to_midi_file = midi_converters.EventToMidiFile()
    event_to_singing_synthesis = cdd_converters.EventToSafeSingingSynthesis(
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

    event_to_volume_control = EventToVolumeControl()

    playing_indicators_converter = music_converters.PlayingIndicatorsConverter(
        [music_converters.ArpeggioConverter(duration_for_each_attack=0.18)]
    )
    tempo_converter = core_converters.TempoConverter(chapter.tempo_envelope)
    for tagged_sequential_event in chapter.simultaneous_event:
        instrument_name = tagged_sequential_event.tag
        tagged_sequential_event = tempo_converter(tagged_sequential_event.copy())
        tagged_sequential_event.duration *= 4
        midi_file_path = chapter.get_midi_path(instrument_name)
        event_to_volume_control.convert(
            tagged_sequential_event, midi_file_path + "_volume_control.wav"
        )
        if instrument_name == "soprano":
            sound_file_path = chapter.get_sound_file_path(instrument_name)
            # event_to_singing_synthesis.convert(tagged_sequential_event, sound_file_path)
        tagged_sequential_event.duration *= 2
        tagged_sequential_event = functools.reduce(
            operator.add,
            playing_indicators_converter.convert(tagged_sequential_event),
        )
        event_to_midi_file.convert(tagged_sequential_event, midi_file_path)
