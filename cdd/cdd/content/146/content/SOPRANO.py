import expenvelope
import ranges

from mutwo import core_converters
from mutwo import core_events
from mutwo import core_utilities
from mutwo import mmml_converters
from mutwo import music_parameters


def remove_phrases(phrase_index_tuple: tuple[int, ...]):
    globals()["fado_part_sequential_event_tuple"] = tuple(
        sequential_event
        for index, sequential_event in enumerate(fado_part_sequential_event_tuple)
        if index not in phrase_index_tuple
    )
    globals()["sequential_event_absolute_time_tuple"] = tuple(
        absolute_time
        for index, absolute_time in enumerate(sequential_event_absolute_time_tuple)
        if index not in phrase_index_tuple
    )
    globals()["repetition_count_tuple"] = tuple(
        repetition_count
        for index, repetition_count in enumerate(repetition_count_tuple)
        if index not in phrase_index_tuple
    )


# This if from fado number 82
fado_part_mmml_tuple = (
    # algons
    # r"3+:-1`16 1:0`8 7+3-`8 1:`8",  # this is the original, but I prefered a calmer start
    # r"3+++7-:-1`16 1:0`8 7+3-`8 1:`8",
    # r"1:0`8 1:0`16 :before [ 3+++7-:-1`8 ] 7+3-:0`8 1:`8",
    r"1:0`8 1:0`8 :before [ 7+3---:0`8 ] 7+3-:0`8 1:`8",
    # tem na vida
    # r"7+3--:0`8 3+`16 3-`4 7-`8",  # this is original, but I liked to change it
    r"7+3--:0`8 3+`16 3-`4 3+`8",
    # um grande
    r"3+:-1`16 3+++7-`8 3++:0`8 3+7+`16 7+3-`8 3++`16",
    # sonho
    r"7+3--:0`8 3+`4",
    # e faltam a esse
    r"1:0`16 7+3-`8 3+:0`8 7+`16 7+3--`8 3+`16",
    # sonho
    r"7+3--:0`8 3+`4",
    # outros nao
    r"3+:-1`16 1:0`8 7+3-`8 1:`8",
    # tem na vida
    r"7+3--:0`8 3+`16 3-`4 7-`8",
    # nenhum
    r"1:0`16 7+3-`8 3+:0`8 7+`16 7+3--`8 3+`16",
    # sonho
    # r"7+3--:0`8 3+`4",  # original, but I prefer to change it
    r"7+3--:0`16*p<articulation.name='.'> r`16 3+`16*p r`3/16",
    # e faltam a esse
    # r"3-:0`16 3-`8 3+`8 7+3--`16 7+`8",  # original, but I prefer to change it
    # r"3-:-1`16*p<articulation.name='.'> r`16 3-*p r 3- r 3- r`3/16 3-`16 r 3- r",
    r"3-:-1`16*p<articulation.name='.'> r`16 3-*p r 3- r 3- r`3/16 3-`16 r 3- r 3- r 3-",
    # tambem
    r"3-`16 7+3--`8 3+`4",
)

# Make it much slower than in original version
duration_factor = 4

fado_part_sequential_event_tuple = tuple(
    mmml_converters.MMMLEventsConverter(
        mmml_converters.MMMLPitchesConverter(
            mmml_converters.MMMLSingleJIPitchConverter()
        )
    )
    .convert(mmml_string)
    .set_parameter("duration", lambda duration: duration * duration_factor)
    for mmml_string in fado_part_mmml_tuple
)

fado_part_sequential_event_tuple[4].set_parameter("pitch_list", "3/2")
fado_part_sequential_event_tuple[6].set_parameter("pitch_list", "4/3")
fado_part_sequential_event_tuple[7].set_parameter("pitch_list", "3/2")
fado_part_sequential_event_tuple[9].set_parameter(
    "pitch_list",
    lambda pitch_list: [
        pitch - music_parameters.JustIntonationPitch("2/1") for pitch in pitch_list
    ],
)
# changed manually in mmml string (therefore commented)
# fado_part_sequential_event_tuple[10].set_parameter("pitch_list", "2/3")

# Remove articulation from rests
for sequential_event in fado_part_sequential_event_tuple:
    for note_like in sequential_event:
        if not note_like.pitch_list:
            note_like.playing_indicator_collection.articulation.name = None


repetition_count_tuple = (1, 1, 1, 2, 1, 2, 1, 2, 1, 3, 1, 1)

tempo_range = ranges.Range(55, 70)


# Rest durations
repetition_rest_duration_range = ranges.Range(5, 10)
initial_rest_duration = 35
rest_duration_type_to_envelope = {
    "phrase": core_events.Envelope([[0, 10], [0.3, 7], [0.5, 15], [1, 20]]),
    "sentence_part": core_events.Envelope(
        [
            [0, 27],
            [0.2, 27],
            [0.25, 95],
            [0.3, 95],
            [0.35, 20],
            [0.4, 18],
            [0.6, 16],
            [0.7, 22],
            [0.75, 25],
            [0.8, 25],
            [0.85, 25],
        ]
    ),
    "sentence": core_events.Envelope([[0, 30]]),
}

# 0: rest_duration_phrase
# 1: rest_duration_sentence_part
# 1: rest_duration_sentence

between_sequential_event_rest_type_tuple = (0, 1, 0, 1, 0, 2, 0, 1, 0, 1, 0, 2)

sequential_event_max_duration_in_seconds_tuple = tuple(
    (
        core_converters.TempoConverter(
            expenvelope.Envelope.from_points((0, tempo_range.end / 4))
        )(sequential_event.copy()).duration
        * repetition_count
    )
    + ((repetition_count - 1) * repetition_rest_duration_range.end)
    for repetition_count, sequential_event in zip(
        repetition_count_tuple, fado_part_sequential_event_tuple
    )
)

sequential_event_count = len(sequential_event_max_duration_in_seconds_tuple)

sequential_event_absolute_time_tuple = tuple(
    core_utilities.accumulate_from_n(
        [
            sequential_event_max_duration
            + rest_duration_type_to_envelope[
                (
                    "phrase",
                    "sentence_part",
                    "sentence",
                )[duration_type]
            ].value_at(index / sequential_event_count)
            for index, sequential_event_max_duration, duration_type in zip(
                range(sequential_event_count),
                sequential_event_max_duration_in_seconds_tuple,
                between_sequential_event_rest_type_tuple,
            )
        ],
        initial_rest_duration,
    ),
)

duration = sequential_event_absolute_time_tuple[-1]
sequential_event_absolute_time_tuple = sequential_event_absolute_time_tuple[:-1]

instruction_text = f"""
start phrases at given time (use stop watch); vary tempo from {tempo_range.start} to {tempo_range.end} bpm (= 1/4).
take rests ({repetition_rest_duration_range.start} to {repetition_rest_duration_range.end} seconds) between repetitions of phrases.
timbre is reserved, almost limp; embed yourself into the surrounding field.
"""

phrase_to_remove_index_tuple = (
    8,
    11,
)

remove_phrases(phrase_to_remove_index_tuple)
