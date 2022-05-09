import quicktions as fractions

from mutwo import music_parameters


def post_process_time_bracket_4(soprano_time_bracket):
    sequential_event = soprano_time_bracket[2]
    sequential_event.split_child_at(fractions.Fraction(5, 2))
    sequential_event.split_child_at(fractions.Fraction(6, 2))
    sequential_event[0].lyric.is_last_syllable = False
    sequential_event[1].pitch_list = "256/189"
    sequential_event[2].pitch_list = "32/21"
    for index in (1, 2):
        sequential_event[index].lyric = music_parameters.DirectLyric("")
        sequential_event[index].playing_indicator_collection.hairpin.symbol = None


def post_process_time_bracket_12(soprano_time_bracket):
    sequential_event = soprano_time_bracket[2]
    # sequential_event[0].pitch_list[0].register(1)


def post_process(soprano_time_bracket_tuple: tuple):
    # post_process_time_bracket_4(soprano_time_bracket_tuple[4])
    post_process_time_bracket_12(soprano_time_bracket_tuple[12])
