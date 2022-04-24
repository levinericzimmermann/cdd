import copy
import itertools
import re
import typing
import warnings

import numpy as np
import pyphen

from mutwo import cdd_parameters
from mutwo import common_generators
from mutwo import core_converters
from mutwo import music_parameters


__all__ = ("LyricsStringToLyrics", "SentenceAndBeatCountToDistributedSentenceTuple")


class LyricsStringToLyrics(core_converters.abc.Converter):
    def _add_sentence_string(
        self,
        lyric: cdd_parameters.NestedLanguageBasedLyric,
        sentence_string: str,
        punctuation: str,
        pyphen_dic,
    ):
        sentence_string = sentence_string.replace("-", " ")
        regex_latin_letter = re.compile(r"[^-/().&' \w]|_")
        hyphen_string = "-"
        if letter_only_sentence_string := regex_latin_letter.sub("", sentence_string):
            word_list = letter_only_sentence_string.split(" ")
            sentence = cdd_parameters.Sentence([], punctuation)
            for word in filter(bool, word_list):
                syllable_list = []
                syllable_string_list = pyphen_dic.inserted(word, hyphen_string).split(
                    hyphen_string
                )
                is_last_syllable = True
                for syllable in reversed(syllable_string_list):
                    syllable_list.append(
                        music_parameters.LanguageBasedSyllable(
                            is_last_syllable, syllable
                        )
                    )
                    is_last_syllable = False
                if syllable_list:
                    sentence.append(cdd_parameters.Word(list(reversed(syllable_list))))
            lyric.append(sentence)

    def convert(
        self, lyrics_string: str, language_code: str = "pt"
    ) -> cdd_parameters.NestedLanguageBasedLyric:
        regex_punctuation = re.compile(r"[\?\.\!\…\:\;]")

        pyphen_dic = pyphen.Pyphen(lang=language_code)

        lyric = cdd_parameters.NestedLanguageBasedLyric([])
        index = 0
        for match in re.finditer(regex_punctuation, lyrics_string):
            sentence_string = lyrics_string[index : match.start()]
            index = match.end()
            punctuation = match.group()
            self._add_sentence_string(lyric, sentence_string, punctuation, pyphen_dic)
        lyric_count = len(lyric)
        if lyric_count > index:
            self._add_sentence_string(lyric, lyrics_string[index:], ".", pyphen_dic)
        return lyric


def find_numbers_which_sums_up_to(
    given_sum: int, number_tuple_tuple: tuple[tuple[int, ...], ...]
):
    numbers = [
        solution
        for solution in itertools.product(*number_tuple_tuple)
        if sum(solution) == given_sum
    ]
    return tuple(numbers)


class SentenceAndBeatCountToDistributedSentenceTuple(core_converters.abc.Converter):
    """Distribute sentence on n beats

    The converter returns the solutions in order, so that the first solution
    will be the most balanced one and the last solution the least balanced one
    (balanced in terms of equal distribution of syllables).
    """

    DistributedSentence = tuple[
        typing.Union[
            cdd_parameters.Word,
            music_parameters.abc.Syllable,
            music_parameters.DirectLyric,
        ],
        ...,
    ]

    SyllableCountTupleTuple = tuple[tuple[int, ...], ...]

    def _get_syllable_distribution_tuple(
        self, beat_count: int, word: cdd_parameters.Word
    ) -> tuple[tuple[DistributedSentence, ...], SyllableCountTupleTuple]:
        solution = [music_parameters.DirectLyric("") for _ in range(beat_count)]
        if beat_count == 1:
            solution[0] = word
            return (tuple(copy.deepcopy(solution)),), ((len(word),),)
        if beat_count == 2:
            first_part = word[:-1]
            first_part_count = len(first_part)
            if first_part_count == 1:
                first_part = word[0]
            solution[0] = first_part
            solution[-1] = word[-1]
            return (tuple(copy.deepcopy(solution)),), ((first_part_count, 1),)
        solution[0] = word[0]
        solution[-1] = word[-1]
        remaining_syllable_list = word[1:-1]
        euclidean_distribution = common_generators.euclidean(
            len(remaining_syllable_list), beat_count - 2
        )
        syllable_distribution_list = []
        # We won't return all solutions, but only solutions with a balanced
        # distribution
        distribution_list = [euclidean_distribution]
        reversed_euclidean_distribution = tuple(reversed(euclidean_distribution))
        if euclidean_distribution != reversed_euclidean_distribution:
            distribution_list.append(reversed_euclidean_distribution)
        base_syllable_count_list = [1] + [0 for _ in range(beat_count - 2)] + [1]
        syllable_count_tuple_list = []
        for distribution in distribution_list:
            local_syllable_count_list = list(base_syllable_count_list)
            local_solution = copy.deepcopy(solution)
            syllable_iterator = iter(remaining_syllable_list)
            for index, use_syllable in enumerate(distribution):
                if use_syllable:
                    local_index = index + 1
                    local_solution[local_index] = copy.deepcopy(next(syllable_iterator))
                    local_syllable_count_list[local_index] = 1
            syllable_distribution_list.append(tuple(local_solution))
            syllable_count_tuple_list.append(tuple(local_syllable_count_list))
        return tuple(syllable_distribution_list), tuple(syllable_count_tuple_list)

    def convert(
        self, sentence_to_convert: cdd_parameters.Sentence, beat_count: int
    ) -> tuple[DistributedSentence, ...]:
        assert beat_count >= 0
        if word_count := len(sentence_to_convert) > beat_count:
            warnings.warn(
                f"Found too long sentence '{sentence_to_convert.written_representation}'"
                f"with {word_count} words to distribute on {beat_count} beats. "
                f"Auto short sentence to {beat_count} words!",
                RuntimeWarning,
            )
            sentence_to_convert = sentence_to_convert[:beat_count]

        beat_range_tuple = tuple(
            tuple(range(1, (2, beat_count + 1)[len(word) > 1]))
            for word in sentence_to_convert
        )
        beat_count_tuple_tuple = find_numbers_which_sums_up_to(
            beat_count, beat_range_tuple
        )
        distributed_sentence_list = []
        fitness_list = []  # how balanced a solution is
        for beat_count_tuple in beat_count_tuple_tuple:
            solutions_per_word_list = []
            syllable_count_tuple_tuple_list = []
            for beat_count_for_word, word in zip(beat_count_tuple, sentence_to_convert):
                (
                    syllable_distribution_tuple,
                    syllable_count_tuple_tuple,
                ) = self._get_syllable_distribution_tuple(beat_count_for_word, word)
                assert len(syllable_count_tuple_tuple) == len(
                    syllable_distribution_tuple
                )
                solutions_per_word_list.append(syllable_distribution_tuple)
                syllable_count_tuple_tuple_list.append(syllable_count_tuple_tuple)
            for nested_distributed_sentence, nested_syllable_count_tuple in zip(
                itertools.product(*solutions_per_word_list),
                itertools.product(*syllable_count_tuple_tuple_list),
            ):
                distributed_sentence = []
                for part in nested_distributed_sentence:
                    distributed_sentence.extend(part)
                syllable_count_list = []
                for syllable_count_tuple in nested_syllable_count_tuple:
                    syllable_count_list.extend(syllable_count_tuple)
                fitness = np.average(
                    sum(
                        [
                            abs(syllable_count0 - syllable_count1)
                            for syllable_count0, syllable_count1 in itertools.combinations(
                                syllable_count_list, 2
                            )
                        ]
                    )
                )
                distributed_sentence_list.append(tuple(distributed_sentence))
                fitness_list.append(fitness)
        return tuple(
            sorted(
                distributed_sentence_list,
                key=lambda distributed_sentence: fitness_list[
                    distributed_sentence_list.index(distributed_sentence)
                ],
            )
        )
