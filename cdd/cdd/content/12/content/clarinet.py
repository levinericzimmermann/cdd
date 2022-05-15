import quicktions as fractions

from mutwo import core_events
from mutwo import music_events
from mutwo import music_parameters


def post_process_time_bracket_2(clarinet_time_bracket):
    sequential_event = clarinet_time_bracket[2]
    sequential_event[0].notation_indicator_collection.duration_line.style = "none"
    sequential_event[0].playing_indicator_collection.fancy_glissando.command = (
        (1, 0, 0, 0, 0, 0),
        (2, -0.15),
        (3, -0.74),
        (4, -0.9),
        (5, -0.75),
        (6, -0.5),
        (7, -0.3),
        (8, -0.2),
        (9, -0.15),
        (10, -0.04),
        (11, -0.01),
        (12, 0, 0, 0, 30, 0),
    )


def post_process_time_bracket_4(clarinet_time_bracket):
    sequential_event = clarinet_time_bracket[2]
    grace_note_sequential_event = core_events.SequentialEvent(
        [
            music_events.NoteLike(
                music_parameters.WesternPitch("a", 3), fractions.Fraction(1, 4)
            )
        ]
    )
    grace_note_sequential_event[0].playing_indicator_collection.glissando = True
    # grace_note_sequential_event[0].playing_indicator_collection.tie = True
    sequential_event[0].grace_note_sequential_event = grace_note_sequential_event


def post_process_time_bracket_10(clarinet_time_bracket):
    clarinet_time_bracket[1] += 2
    sequential_event = clarinet_time_bracket[2]
    sequential_event.split_child_at(fractions.Fraction(5, 2))
    sequential_event.split_child_at(fractions.Fraction(6, 2))
    sequential_event[1].pitch_list = "6/7"
    sequential_event[2].pitch_list = "3/4"


def post_process(clarinet_time_bracket_tuple: tuple):
    post_process_time_bracket_2(clarinet_time_bracket_tuple[2])
    post_process_time_bracket_4(clarinet_time_bracket_tuple[4])
    post_process_time_bracket_10(clarinet_time_bracket_tuple[10])
