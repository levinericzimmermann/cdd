import itertools

# import math
import typing

import abjad
import expenvelope

import more_itertools
import quicktions as fractions

from mutwo import cdd_parameters
from mutwo import common_generators
from mutwo import core_events
from mutwo import core_parameters
from mutwo import core_utilities
from mutwo import music_events

import cdd


"""
Pedi tão pouco à vida
e esse mesmo pouco a vida me negou.

---

s0: 0 - 8
s1: 8 - 14

---

simple cycle permutations:

    1. Pedi tão pouco à
    2. tão pouco à vida
    3. Pedi pouco à vida
    4. Pedi tão à vida
    5. Pedi tão pouco vida

for the second sentence we always ignore two words:

    1. e esse mesmo pouco a vida
    2. esse mesmo pouco a vida me
    3. mesmo pouco a vida me negou
    ...

Because the second sentence is longer, we will
need more repetitions of the second one until
we are finished with all repetitions.

When done with the first one there will simply be a
rest (which gives a nice ending for the song).
But we will repeat the first variation of the first
sentence, so there are only two lonely second sentences.

The amount of speakers can be defined by a gray code

    common_generators.reflected_binary_code(3,2)

There are 7 usable items (one is empty). So 7 x 2 = 14,
which is also 6 + 8 = 14 (6 times first sentence, 8 times
second sentence). So we can repeat the gray code once.

At the empty position of the gray code there should be
a FERMATA (so we aren't cheating + fermatas are nice).

TODO

- add varying percussion interpolation part (sometimes rest)
- add varying bar duration

---

Ich habe so wenig vom Leben erbeten,
und selbst dieses wenige hat das Leben mir versagt.
"""


METRONME_LOOP = core_events.SequentialEvent(
    [
        # bar 6/4
        music_events.NoteLike(duration=fractions.Fraction(1, 4)),
        music_events.NoteLike(duration=fractions.Fraction(1, 4)),
        music_events.NoteLike(pitch_list=[], duration=fractions.Fraction(6, 4)),
        # bar 3/4
        music_events.NoteLike(duration=fractions.Fraction(1, 4)),
        music_events.NoteLike(pitch_list=[], duration=fractions.Fraction(4, 4)),
        # bar 6/4
        music_events.NoteLike(duration=fractions.Fraction(3, 16)),
        music_events.NoteLike(duration=fractions.Fraction(1, 16)),
        music_events.NoteLike(duration=fractions.Fraction(1, 4)),
        music_events.NoteLike(pitch_list=[], duration=fractions.Fraction(7, 4)),
        # bar 4/4
        music_events.NoteLike(pitch_list=[], duration=fractions.Fraction(1, 4)),
        music_events.NoteLike(duration=fractions.Fraction(1, 4)),
        music_events.NoteLike(pitch_list=[], duration=fractions.Fraction(2, 4)),
    ]
)

LOOP_COUNT = 2


def make_permutated_tuple(
    content: tuple[typing.Any, ...], remove_count: int = 1
) -> tuple[tuple[typing.Any, ...], ...]:
    assert remove_count >= 1
    content_count = len(content)

    permutated_content_list = []
    for remove_index in range(content_count):
        to_remove_index_list = []
        for to_remove_index_offset in range(remove_count):
            to_remove_index_list.append(
                (remove_index + to_remove_index_offset) % content_count
            )
        permutated_content = tuple(
            item
            for index, item in enumerate(content)
            if index not in to_remove_index_list
        )
        permutated_content_list.append(permutated_content)

    return tuple(permutated_content_list)


class Chapter(cdd.chapters.Chapter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.percussion_count = itertools.cycle((0, 1, 2, 3, 4, 5))
        self.sentence0, self.sentence1 = self.make_suject_divided_sentence()
        self.permutated_sentence_tuple = self.make_permutated_sentence_tuple()
        self.suject_duration_tuple = (
            fractions.Fraction(8, 4),
            fractions.Fraction(5, 4),
            fractions.Fraction(13, 4),
        )
        self.simultaneous_event = self.make_simultaneous_event()
        self.time_signature_sequence = self.make_time_signature_sequence()

    def make_suject_divided_sentence(
        self,
    ) -> tuple[cdd_parameters.Sentence, cdd_parameters.Sentence]:
        sentence = self.pessoa_lyric[0]
        part0, part1 = cdd_parameters.Sentence(sentence[:5]), cdd_parameters.Sentence(
            sentence[5:]
        )
        return part0, part1

    def make_permutated_sentence_tuple(self) -> tuple[cdd_parameters.Sentence, ...]:
        permutation0 = tuple(reversed(make_permutated_tuple(self.sentence0, 1)))
        # We want to repeat the first sentence once again
        permutation0 += (permutation0[0],)
        permutation1 = make_permutated_tuple(self.sentence1, 2)
        while len(permutation0) < len(permutation1):
            permutation0 += (None,)
        return tuple(more_itertools.interleave_longest(permutation0, permutation1))
        # return tuple(zip(permutation0, permutation1))

    def _get_empty_simultaneous_event(self) -> core_events.SimultaneousEvent:
        return core_events.SimultaneousEvent(
            [
                core_events.TaggedSequentialEvent(
                    [],
                    tag=cdd.constants.ADDED_INSTRUMENT_NAME_TO_SHORT_INSTRUMENT_NAME[
                        "percussion"
                    ],
                ),
                core_events.TaggedSequentialEvent(
                    [],
                    tag=cdd.constants.INSTRUMENT_NAME_TO_SHORT_INSTRUMENT_NAME[
                        "soprano"
                    ],
                ),
                core_events.TaggedSequentialEvent(
                    [],
                    tag=cdd.constants.INSTRUMENT_NAME_TO_SHORT_INSTRUMENT_NAME[
                        "clarinet"
                    ],
                ),
                core_events.TaggedSequentialEvent(
                    [],
                    tag=cdd.constants.INSTRUMENT_NAME_TO_SHORT_INSTRUMENT_NAME[
                        "clavichord"
                    ],
                ),
            ]
        )

    def make_time_signature_sequence(self) -> tuple[abjad.TimeSignature, ...]:
        # print("TIME SIG", (int(math.ceil(self.simultaneous_event.duration * 4)), 4))
        # return (
        #     abjad.TimeSignature(
        #         (int(math.ceil(self.simultaneous_event.duration * 4)), 4)
        #     ),
        # )
        return (abjad.TimeSignature((19, 4)),)
        # time_signature_list = []
        # for _ in range(LOOP_COUNT):
        #     time_signature_list.extend(TIME_SIGNATURE_LOOP)
        # return tuple(time_signature_list)

    def add_missing_note(self, simultaneous_event):
        simultaneous_event_duration = simultaneous_event.duration
        for event in simultaneous_event:
            difference = simultaneous_event_duration - event.duration
            if difference:
                event.append(music_events.NoteLike(pitch_list=[], duration=difference))

    def _add_rest_to_simultaneous_event(
        self, simultaneous_event, duration, add_fermata, pitch_list=[]
    ):
        fermata = core_events.SequentialEvent(
            [music_events.NoteLike(duration=duration, pitch_list=pitch_list)]
        )
        if add_fermata:
            fermata[0].playing_indicator_collection.fermata.fermata_type = "fermata"
        for sequential_event in simultaneous_event:
            sequential_event.extend(fermata.copy())

    def _get_responsible_voice_tuple(
        self, simultaneous_event: core_events.SimultaneousEvent, gray_code_cycle
    ) -> tuple[int, ...]:
        responsible_voice_tuple = next(gray_code_cycle)
        while sum(responsible_voice_tuple) == 0:
            self._add_rest_to_simultaneous_event(
                # simultaneous_event, fractions.Fraction(1, 1), True, "c"
                simultaneous_event,
                fractions.Fraction(2, 1),
                False,
            )
            responsible_voice_tuple = next(gray_code_cycle)

        responsible_voice_tuple = tuple(
            index
            for index, is_active in enumerate(responsible_voice_tuple)
            if is_active
        )
        return responsible_voice_tuple

    def _make_percussion_rhythm(self) -> core_events.SequentialEvent:
        percussion_count = next(self.percussion_count)
        if percussion_count % 3 == 0:
            if percussion_count % 6 == 0:
                return core_events.SequentialEvent(
                    [
                        music_events.NoteLike(duration=fractions.Fraction(1, 8)),
                        music_events.NoteLike(duration=fractions.Fraction(1, 4)),
                        music_events.NoteLike(duration=fractions.Fraction(1, 1)),
                    ]
                )
            else:
                return core_events.SequentialEvent(
                    [
                        music_events.NoteLike(duration=fractions.Fraction(1, 2)),
                        music_events.NoteLike(duration=fractions.Fraction(1, 8)),
                        music_events.NoteLike(duration=fractions.Fraction(1, 1)),
                    ]
                )
        elif percussion_count % 3 == 1:
            return core_events.SequentialEvent(
                [
                    music_events.NoteLike(
                        pitch_list=[], duration=fractions.Fraction(1, 2)
                    ),
                    music_events.NoteLike(duration=fractions.Fraction(1, 4)),
                    music_events.NoteLike(
                        pitch_list=[], duration=fractions.Fraction(5, 4)
                    ),
                ]
            )
        elif percussion_count % 3 == 2:
            return core_events.SequentialEvent(
                [
                    music_events.NoteLike(
                        pitch_list=[], duration=fractions.Fraction(1, 1)
                    ),
                ]
            )

    def _add_sentence_to_simultaneous_event(
        self,
        simultaneous_event: core_events.SimultaneousEvent,
        sentence: typing.Optional[tuple[cdd_parameters.Word, ...]],
        gray_code_cycle,
    ):
        if sentence is None:
            self._add_rest_to_simultaneous_event(
                simultaneous_event, fractions.Fraction(2, 1), False
            )
            return

        responsible_voice_tuple = self._get_responsible_voice_tuple(
            simultaneous_event, gray_code_cycle
        )
        syllable_list = []
        for word in sentence:
            # syllable_list.extend(word)
            syllable_list.append(word)
        percussion_rhythm = self._make_percussion_rhythm()
        spoken_text = core_events.SequentialEvent(
            [
                music_events.NoteLike(lyric=syllable, duration=fractions.Fraction(1, 8))
                for syllable in syllable_list
            ]
        )
        spoken_text.append(
            music_events.NoteLike(pitch_list=[], duration=fractions.Fraction(1, 2))
        )
        rest_spoken_text = core_events.SimpleEvent(percussion_rhythm.duration)
        rest_percussion = core_events.SimpleEvent(spoken_text.duration)
        spoken_text.insert(0, rest_spoken_text)
        percussion_rhythm.append(rest_percussion)

        rest_event = core_events.SequentialEvent(
            [music_events.NoteLike(pitch_list=[], duration=spoken_text.duration)]
        )

        assert spoken_text.duration == percussion_rhythm.duration

        simultaneous_event[0].extend(percussion_rhythm)
        for voice_index, sequential_event in enumerate(simultaneous_event[1:]):
            if voice_index in responsible_voice_tuple:
                sequential_event.extend(spoken_text)
            else:
                sequential_event.extend(rest_event)

    def make_simultaneous_event(self) -> core_events.SimultaneousEvent:
        simultaneous_event = self._get_empty_simultaneous_event()
        gray_code = common_generators.reflected_binary_code(3, 2)
        gray_code = tuple(core_utilities.cyclic_permutations(gray_code))[2]
        gray_code_cycle = itertools.cycle(gray_code)
        for sentence in self.permutated_sentence_tuple:
            self._add_sentence_to_simultaneous_event(
                simultaneous_event, sentence, gray_code_cycle
            )

        self.add_missing_note(simultaneous_event)
        cdd.utilities.add_instrument_name(simultaneous_event)
        # We don't need short instrument name notation for this score
        [setattr(event, "short_instrument_name", "") for event in simultaneous_event]
        return simultaneous_event

    tempo_envelope = expenvelope.Envelope.from_points(
        [2, core_parameters.TempoPoint(55 / 4)]
    )

    instruction_text = r"""
\begin{footnotesize}
speak text clearly \& naturally (in a calm voice); avoid theatric, monotonous or mechanical intonation.
singer leads group by playing the additional percussion line.
instrument can be any (but only one) pitched metallic percussion, e.g. a tiny bell, crotales, kalimba, \dots
\end{footnotesize}
"""

    instruction_text_noise = r"""
\begin{center}
    \bigskip
    \bigskip

    play field of noise from circa

    \bigskip

    { \tt \large 0'40 to 2'45 }

    \bigskip

    soft but rich, steady but granular.\\
    from silence to silence.
\end{center}
"""
