import quicktions as fractions

from mutwo import music_parameters


def post_process_time_bracket_10(clarinet_time_bracket):
    clarinet_time_bracket[1] += 2
    sequential_event = clarinet_time_bracket[2]
    sequential_event.split_child_at(fractions.Fraction(5, 2))
    sequential_event.split_child_at(fractions.Fraction(6, 2))
    sequential_event[1].pitch_list = "6/7"
    sequential_event[2].pitch_list = "3/4"


def post_process(clarinet_time_bracket_tuple: tuple):
    post_process_time_bracket_10(clarinet_time_bracket_tuple[10])
    # post_process_time_bracket_11(clarinet_time_bracket_tuple)
