import quicktions as fractions

from mutwo import core_events
from mutwo import music_events
from mutwo import music_parameters


def post_process_time_bracket_1(soprano_time_bracket):
    sequential_event = soprano_time_bracket[2]
    grace_note_sequential_event = core_events.SequentialEvent(
        [
            music_events.NoteLike(
                music_parameters.WesternPitch("d", 5), fractions.Fraction(1, 4)
            )
        ]
    )
    grace_note_sequential_event[0].playing_indicator_collection.glissando = True
    # grace_note_sequential_event[0].playing_indicator_collection.tie = True
    sequential_event[0].grace_note_sequential_event = grace_note_sequential_event


def post_process_time_bracket_3(soprano_time_bracket):
    sequential_event = soprano_time_bracket[2]
    sequential_event[0].notation_indicator_collection.duration_line.style = "none"
    sequential_event[0].playing_indicator_collection.fancy_glissando.command = (
        (1, 0, 0, 0, 0, 0),
        (2, 0.15),
        (3, 0.74),
        (4, 0.9),
        (5, 0.75),
        (6, 0.5),
        (7, 0.3),
        (8, 0.2),
        (9, 0.15),
        (10, 0.04),
        (11, 0.01),
        (12, 0, 0, 0, 30, 0),
    )


def post_process_time_bracket_4_old(soprano_time_bracket):
    sequential_event = soprano_time_bracket[2]
    sequential_event.split_child_at(fractions.Fraction(5, 2))
    sequential_event.split_child_at(fractions.Fraction(6, 2))
    sequential_event[0].lyric.is_last_syllable = False
    sequential_event[1].pitch_list = "256/189"
    sequential_event[2].pitch_list = "32/21"
    for index in (1, 2):
        sequential_event[index].lyric = music_parameters.DirectLyric("")
        sequential_event[index].playing_indicator_collection.hairpin.symbol = None


def post_process_time_bracket_4(soprano_time_bracket):
    sequential_event = soprano_time_bracket[2]
    sequential_event.split_child_at(fractions.Fraction(5, 2))
    sequential_event[0].lyric.is_last_syllable = False
    sequential_event[1].pitch_list = "256/189"
    for index in (1,):
        sequential_event[index].lyric = music_parameters.DirectLyric("")
        sequential_event[index].playing_indicator_collection.hairpin.symbol = None


def post_process_time_bracket_12(soprano_time_bracket):
    pass
    # sequential_event = soprano_time_bracket[2]
    # sequential_event[0].pitch_list[0].register(1)


def post_process(soprano_time_bracket_tuple: tuple):
    post_process_time_bracket_4(soprano_time_bracket_tuple[4])
    post_process_time_bracket_1(soprano_time_bracket_tuple[1])
    post_process_time_bracket_3(soprano_time_bracket_tuple[3])
    post_process_time_bracket_12(soprano_time_bracket_tuple[12])
