import copy
import itertools
import warnings

import expenvelope
import numpy as np

from mutwo import cdd_converters
from mutwo import cdd_parameters
from mutwo import core_converters
from mutwo import core_events
from mutwo import core_parameters
from mutwo import core_utilities
from mutwo import music_parameters

import cdd

__all__ = ("Chapter",)


class Chapter(cdd.chapters.Chapter):
    from . import SOPRANO
    from . import CLARINET
    from . import CLAVICHORD
    from . import NOISE

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.all_sentence_tuple = self._get_sentence_tuple()
        self.sentence_tuple = tuple(
            sentence
            for index, sentence in enumerate(self.all_sentence_tuple)
            if index not in self.SOPRANO.phrase_to_remove_index_tuple
        )
        self.SOPRANO.sequential_event_tuple = self._get_soprano_sequential_event_tuple()
        self.duration_in_seconds = self.SOPRANO.duration
        self.duration_in_minutes = self.duration_in_seconds / 60

        self._apply_sentence_on_clavichord()

        self._post_process_soprano()

    def _get_sentence_tuple(self) -> tuple[cdd_parameters.Sentence, ...]:
        base_sentence = cdd_parameters.Sentence(
            self.pessoa_lyric[0][:] + self.pessoa_lyric[1][:]
        )
        # word_count_tuple = (1, 3, 2, 1, 4, 1, 2, 3, 1, 1, 4, 1)
        word_count_tuple = (1, 3, 2, 1, 4, 1, 2, 3, 1, 1, 5)
        word_index_tuple = tuple(core_utilities.accumulate_from_zero(word_count_tuple))
        sentence_list = []
        for word_index0, word_index1 in zip(word_index_tuple, word_index_tuple[1:]):
            sentence_list.append(
                cdd_parameters.Sentence(base_sentence[word_index0:word_index1])
            )
        return tuple(sentence_list)

    def _add_sentence_to_soprano_sequential_event(self, sentence, sequential_event):
        beat_count = len([event for event in sequential_event if event.pitch_list])
        (
            solution,
            *_,
        ) = cdd_converters.SentenceAndBeatCountToDistributedSentenceTuple().convert(
            sentence, beat_count
        )
        lyric_iterator = iter(solution)
        for note_like in sequential_event:
            if note_like.pitch_list:
                try:
                    note_like.lyric = next(lyric_iterator)
                except StopIteration:
                    warnings.warn(f"Not enough text for pitched events: {sentence}")

    def _get_soprano_sequential_event_tuple(
        self,
    ) -> tuple[core_events.SequentialEvent, ...]:
        soprano_sequential_event_tuple = copy.deepcopy(
            self.SOPRANO.fado_part_sequential_event_tuple
        )
        for sequential_event, sentence in zip(
            soprano_sequential_event_tuple, self.sentence_tuple
        ):
            self._add_sentence_to_soprano_sequential_event(sentence, sequential_event)
        return soprano_sequential_event_tuple

    def _apply_sentence_on_clavichord(self):
        clavichord_word_list = []
        for index in self.SOPRANO.phrase_to_remove_index_tuple:
            try:
                for word in self.all_sentence_tuple[index]:
                    clavichord_word_list.append(word)
            except IndexError:
                pass

        clavichord_word_cycle = itertools.cycle(clavichord_word_list)

        valid_event_count = sum(
            len(list(filter(bool, sequential_event.get_parameter("pitch_list"))))
            for sequential_event in self.CLAVICHORD.sequential_event_tuple
        )

        random = np.random.default_rng(10000)
        index = 0
        new_sequential_event_list = []
        for sequential_event in self.CLAVICHORD.sequential_event_tuple:
            new_sequential_event = core_events.SequentialEvent([])
            for note_like_or_simple_event in sequential_event.copy():
                if (
                    hasattr(note_like_or_simple_event, "pitch_list")
                    and note_like_or_simple_event.pitch_list
                ):
                    position = index / valid_event_count
                    if (
                        random.random()
                        < self.CLAVICHORD.add_word_likelihood_envelope.value_at(
                            position
                        )
                    ):
                        # note_like_or_simple_event.lyric = next(clavichord_word_cycle)
                        pass
                    index += 1
                new_sequential_event.append(note_like_or_simple_event)
            new_sequential_event_list.append(new_sequential_event)

        self.clavichord_sequential_event_tuple = tuple(new_sequential_event_list)

    def _post_process_soprano(self):
        # ######## post process soprano ########## #

        # when repeating this line, the repetition will be varied (the pitch
        # will be lower)
        new_sequential_event = self.SOPRANO.sequential_event_tuple[7].copy()
        new_sequential_event.set_parameter("pitch_list", "4/3")
        self.soprano_sequential_event_tuple = (
            self.SOPRANO.sequential_event_tuple[:8]
            + (new_sequential_event,)
            + self.SOPRANO.sequential_event_tuple[8:]
        )
        self.soprano_repetition_count_tuple = (
            self.SOPRANO.repetition_count_tuple[:7]
            + (1, 1)
            + self.SOPRANO.repetition_count_tuple[8:]
        )
        self.soprano_sequential_event_absolute_time_tuple = (
            self.SOPRANO.sequential_event_absolute_time_tuple[:8]
            + (
                self.SOPRANO.sequential_event_absolute_time_tuple[7]
                + core_converters.TempoConverter(
                    expenvelope.Envelope.from_points([0, self.SOPRANO.tempo_range.end])
                )(new_sequential_event).duration
                + 7
                + self.SOPRANO.repetition_rest_duration_range.end,
            )
            + self.SOPRANO.sequential_event_absolute_time_tuple[8:]
        )

        self.soprano_sequential_event_tuple[2][3].pitch_list = []
        self.soprano_sequential_event_tuple[2][4].pitch_list = []

        for sequential_event in self.soprano_sequential_event_tuple:
            cdd.utilities.add_cent_deviation_to_sequential_event(sequential_event)

        # There are four lines, where singer plays unisonos
        # with clarinet.
        # They are added here.

        soprano_and_clarinet_unisono_simultaneous_event_list = []
        for index, pitch_interval in zip(
            self.CLARINET.unisono_part_index_tuple,
            self.CLARINET.clarinet_unisono_interval_tuple,
        ):
            soprano_sequential_event = self.soprano_sequential_event_tuple[index]
            clarinet_sequential_event = soprano_sequential_event.set_parameter(
                "pitch_list",
                lambda pitch_list: [
                    pitch + pitch_interval for pitch in pitch_list if pitch
                ],
                mutate=False,
            ).set_parameter("lyric", music_parameters.DirectLyric(""))
            simultaneous_event = core_events.SimultaneousEvent(
                [soprano_sequential_event, clarinet_sequential_event]
            )
            soprano_and_clarinet_unisono_simultaneous_event_list.append(
                simultaneous_event
            )

        soprano_and_clarinet_unisono_simultaneous_event_list[2][1][0].pitch_list = "8/5"
        soprano_and_clarinet_unisono_simultaneous_event_list[2][1][2].pitch_list = "1/1"
        soprano_and_clarinet_unisono_simultaneous_event_list[2][1][3].pitch_list = "2/3"
        soprano_and_clarinet_unisono_simultaneous_event_list[2][0][3].pitch_list = "8/5"

        soprano_and_clarinet_unisono_simultaneous_event_list[3][1][
            6
        ].pitch_list = music_parameters.WesternPitch("as", 3)
        soprano_and_clarinet_unisono_simultaneous_event_list[3][1][
            12
        ].pitch_list = music_parameters.WesternPitch("e", 4)

        soprano_and_clarinet_unisono_simultaneous_event_list[3][0][
            12
        ].pitch_list = "7/12"

        for sequential_event in soprano_and_clarinet_unisono_simultaneous_event_list[
            -2
        ]:
            sequential_event[
                -1
            ].playing_indicator_collection.fermata.fermata_type = "fermata"

        for simultaneous_event in soprano_and_clarinet_unisono_simultaneous_event_list:
            for sequential_event in simultaneous_event:
                cdd.utilities.add_cent_deviation_to_sequential_event(sequential_event)

        self.soprano_and_clarinet_unisono_simultaneous_event_tuple = tuple(
            soprano_and_clarinet_unisono_simultaneous_event_list
        )

        soprano_sequential_event_absolute_time_list = list(
            self.soprano_sequential_event_absolute_time_tuple
        )
        soprano_sequential_event_absolute_time_list[6] -= 2
        soprano_sequential_event_absolute_time_list[8] += 6

        self.soprano_sequential_event_absolute_time_tuple = tuple(
            soprano_sequential_event_absolute_time_list
        )

    tempo_envelope = expenvelope.Envelope.from_points(
        [2, core_parameters.TempoPoint(55 / 4)]
    )
