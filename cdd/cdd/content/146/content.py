import copy

import expenvelope

from mutwo import cdd_converters
from mutwo import cdd_parameters
from mutwo import core_events
from mutwo import core_parameters
from mutwo import core_utilities
from mutwo import mmml_converters
from mutwo import music_parameters

import cdd

# This if from fado number 82
FADO_PART_MMML_TUPLE = (
    # algons
    r"3+:-1`16 1:0`8 7+3-`8 1:`8",
    # tem na vida
    r"7+3--:0`8 3+`16 3-`4 7-`8",
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
    r"7+3--:0`8 3+`4",
    # e faltam a esse
    r"3-:0`16 3-`8 3+`8 7+3--`16 7+`8",
    # tambem
    r"3-`16 7+3--`8 3+`4",
)

FADO_PART_SEQUENTIAL_EVENT_TUPLE = tuple(
    mmml_converters.MMMLEventsConverter(
        mmml_converters.MMMLPitchesConverter(
            mmml_converters.MMMLSingleJIPitchConverter()
        )
    )
    .convert(mmml_string)
    .set_parameter("duration", lambda duration: duration * 4)
    for mmml_string in FADO_PART_MMML_TUPLE
)

SOPRANO_REPETITION_COUNT_TUPLE = (1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 1)


class Chapter(cdd.chapters.Chapter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sentence_tuple = self._get_sentence_tuple()
        self.soprano_sequential_event_tuple = self._get_soprano_sequential_event_tuple()
        self.soprano_repetition_count_tuple = SOPRANO_REPETITION_COUNT_TUPLE
        self.soprano_tempo_envelope_tuple = tuple(
            expenvelope.Envelope.from_points([2, core_parameters.TempoPoint(tempo)])
            for tempo in (60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60)
        )
        # TODO(define rest between parts (between rising melody A and falling melody B))
        # TODO(define rest between phrases (one phrase consist of two parts: A-B))
        # TODO(is tempo everywhere really necessary? what if we just define it in
        #      the introduction text: always between 55 - 70; vary ad. lib.)
        self.soprano_start_time_tuple = (10, 25, 70, 85, 120, 135)

    def _get_sentence_tuple(self) -> tuple[cdd_parameters.Sentence, ...]:
        base_sentence = cdd_parameters.Sentence(
            self.pessoa_lyric[0][:] + self.pessoa_lyric[1][:]
        )
        word_count_tuple = (1, 3, 2, 1, 4, 1, 2, 3, 1, 1, 4, 1)
        word_index_tuple = tuple(core_utilities.accumulate_from_zero(word_count_tuple))
        sentence_list = []
        for word_index0, word_index1 in zip(word_index_tuple, word_index_tuple[1:]):
            sentence_list.append(
                cdd_parameters.Sentence(base_sentence[word_index0:word_index1])
            )
        return tuple(sentence_list)

    def _add_sentence_to_sequential_event(self, sentence, sequential_event):
        beat_count = len(sequential_event)
        solution_tuple = (
            cdd_converters.SentenceAndBeatCountToDistributedSentenceTuple().convert(
                sentence, beat_count
            )
        )
        choosen_solution = solution_tuple[0]
        for lyric, note_like in zip(choosen_solution, sequential_event):
            note_like.lyric = lyric

    def _get_soprano_sequential_event_tuple(
        self,
    ) -> tuple[core_events.SequentialEvent, ...]:
        soprano_sequential_event_tuple = copy.deepcopy(FADO_PART_SEQUENTIAL_EVENT_TUPLE)
        for sequential_event, sentence in zip(
            soprano_sequential_event_tuple, self.sentence_tuple
        ):
            cdd.utilities.add_cent_deviation_to_sequential_event(sequential_event)
            self._add_sentence_to_sequential_event(sentence, sequential_event)
        return soprano_sequential_event_tuple

    tempo_envelope = expenvelope.Envelope.from_points(
        [2, core_parameters.TempoPoint(55 / 4)]
    )

    instruction_text_soprano = r"""
start phrases at given time (use stop watch).
take rests (ad lib. duration) between repetitions of phrases.
timbre is reserved, almost limp; embed yourself into the surrounding field.
"""

    instruction_text_clarinet = r"""
freely choose from the given material of pedal notes and hyperchromatic melodies; vary them ad. lib.
play until soprano finishes.
"""

    instruction_text_clavichord = r"""
take for each line circa 30 seconds (use a stop watch).
rhythmic notation is proportional; space in notation equals time in music.
"""
