import functools
import operator

from mutwo import cdd_converters
from mutwo import core_events
from mutwo import csound_converters
from mutwo import isis_converters
from mutwo import midi_converters
from mutwo import music_converters

from cdd import configurations
from cdd import constants


class EventToVolumeControl(csound_converters.EventToSoundFile):
    def __init__(self):
        def p4(note_like):
            playing_indicator_collection = note_like.playing_indicator_collection
            if hairpin := playing_indicator_collection.hairpin.symbol:
                if hairpin in ("<", "<>"):
                    return 0.0001
                elif hairpin == ">":
                    return 1
            return 1

        def p5(note_like):
            playing_indicator_collection = note_like.playing_indicator_collection
            if hairpin := playing_indicator_collection.hairpin.symbol:
                if hairpin in (">", "<"):
                    return 0.3
                else:
                    return 1
            return 1

        def p6(note_like):
            playing_indicator_collection = note_like.playing_indicator_collection
            if hairpin := playing_indicator_collection.hairpin.symbol:
                if hairpin in (">", "<>"):
                    return 0.0001
                elif hairpin == "<":
                    return 1
            return 1

        super().__init__(
            f"{configurations.PATH.ETC.CSOUND}/12_volume_control.orc",
            csound_converters.EventToCsoundScore(
                p4=p4,
                p5=p5,
                p6=p6,
            ),
        )


def _render_sustaining_instrument_time_bracket_tuple(chapter, instrument_name: str):
    time_bracket_tuple = chapter.sustaining_instrument_dict[instrument_name]
    event_to_midi_file = midi_converters.EventToMidiFile()
    sequential_event = core_events.SequentialEvent([])
    for start_time, end_time, local_sequential_event, *_ in time_bracket_tuple:
        local_sequential_event = local_sequential_event.copy()
        difference = start_time - sequential_event.duration
        if difference > 0:
            sequential_event.append(core_events.SimpleEvent(difference))
        local_sequential_event.duration = end_time - start_time
        sequential_event.extend(local_sequential_event)

    event_to_volume_control = EventToVolumeControl()
    midi_file_path = chapter.get_midi_path(instrument_name)
    event_to_midi_file.convert(
        sequential_event.set_parameter(
            "duration", lambda duration: duration * 2, mutate=False
        ),
        midi_file_path,
    )
    event_to_volume_control.convert(
        sequential_event, midi_file_path + "_volume_control.wav"
    )

    if instrument_name == constants.SOPRANO:

        def simple_event_to_pitch(simple_event):
            pitch_list = simple_event.pitch_list
            if pitch_list:
                return pitch_list[0]
            else:
                raise AttributeError()

        event_to_singing_synthesis = cdd_converters.EventToSafeSingingSynthesis(
            isis_converters.EventToSingingSynthesis(
                isis_converters.EventToIsisScore(
                    simple_event_to_vowel=lambda simple_event: simple_event.lyric.vowel,
                    simple_event_to_consonant_tuple=lambda simple_event: simple_event.lyric.consonant_tuple,
                    simple_event_to_pitch=simple_event_to_pitch,
                ),
                f"--cfg_synth {configurations.PATH.ETC.ISIS}/isis-cfg-synth.cfg",
                f"--cfg_style {configurations.PATH.ETC.ISIS}/isis-cfg-style.cfg",
                # "-sv EL",
                "-sv MS",
                "--seed 100",
            ),
        )
        sound_file_path = chapter.get_sound_file_path(instrument_name)
        # event_to_singing_synthesis.convert(sequential_event, sound_file_path)


def render_soprano(chapter):
    _render_sustaining_instrument_time_bracket_tuple(chapter, constants.SOPRANO)


def render_clarinet(chapter):
    _render_sustaining_instrument_time_bracket_tuple(chapter, constants.CLARINET)


def render_clavichord(chapter):
    instrument_name = constants.CLAVICHORD
    midi_file_path = chapter.get_midi_path(instrument_name)
    playing_indicators_converter = music_converters.PlayingIndicatorsConverter(
        [music_converters.ArpeggioConverter(duration_for_each_attack=0.18)]
    )
    grace_note_converter = music_converters.GraceNotesConverter()

    sequential_event = chapter.clavichord_time_bracket_container.sequential_event
    sequential_event = grace_note_converter.convert(sequential_event)
    sequential_event = functools.reduce(
        operator.add, playing_indicators_converter.convert(sequential_event)
    )

    midi_converters.EventToMidiFile().convert(
        sequential_event.set_parameter(
            "duration", lambda duration: duration * 2, mutate=False
        ),
        midi_file_path,
    )


def main(chapter):
    render_soprano(chapter)
    render_clarinet(chapter)
    render_clavichord(chapter)
