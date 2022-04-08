import math

import abjad
import expenvelope
import quicktions as fractions

from mutwo import cdd_parameters
from mutwo import core_events
from mutwo import core_parameters
from mutwo import music_events

import cdd


# TODO(
#   make one loop much longer with more smaller bars,
#   to make it more delicate and to give the language more
#   space for rests and rhythmic variations
# )

# TODO(split the uniform speaking)

TIME_SIGNATURE_LOOP = (abjad.TimeSignature((20, 4)),)

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


class Chapter(cdd.chapters.Chapter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.suject_divided_sentence_tuple = self.make_suject_divided_sentence_tuple()
        self.suject_duration_tuple = (
            fractions.Fraction(8, 4),
            fractions.Fraction(5, 4),
            fractions.Fraction(13, 4),
        )
        self.rhythm_per_sentence_per_suject = self.make_rhythm_per_suject()
        self.simultaneous_event = self.make_simultaneous_event()
        self.time_signature_sequence = self.make_time_signature_sequence()

    def make_suject_divided_sentence_tuple(
        self,
    ) -> tuple[
        tuple[tuple[cdd_parameters.Word, ...], ...],
        tuple[tuple[cdd_parameters.Word, ...], ...],
    ]:
        sentence0, sentence1 = self.pessoa_lyric
        suject_index_list0 = (0, 4, 7, 13)
        suject_index_list1 = (0, 5, 7, 13)
        suject_list0 = [
            sentence0[index0:index1]
            for index0, index1 in zip(suject_index_list0, suject_index_list0[1:])
        ]
        suject_list1 = [
            sentence1[index0:index1]
            for index0, index1 in zip(suject_index_list1, suject_index_list1[1:])
        ]
        return tuple(suject_list0), tuple(suject_list1)

    def make_rhythm_per_suject(self):
        rhythm_list_list = [[], []]
        for suject_duration, suject0, suject1 in zip(
            *((self.suject_duration_tuple,) + self.suject_divided_sentence_tuple)
        ):
            syllable_count0, syllable_count1 = (
                sum(len(word) for word in suject) for suject in (suject0, suject1)
            )
            max_syllable_count = max([syllable_count0, syllable_count1])

            syllable_duration = fractions.Fraction(1, 8)
            while syllable_duration * max_syllable_count > suject_duration:
                syllable_duration *= fractions.Fraction(1, 2)

            for index, syllable_count in enumerate((syllable_count0, syllable_count1)):
                rhythm = core_events.SequentialEvent([])
                rest_duration = suject_duration - (syllable_duration * syllable_count)
                beat_count = rest_duration / fractions.Fraction(1, 8)
                beat_per_rest = beat_count // 2
                rest_left = (beat_per_rest + (beat_count % 2)) * fractions.Fraction(
                    1, 8
                )
                rest_right = beat_per_rest * fractions.Fraction(1, 8)
                rest = core_events.SimpleEvent(rest_left)
                rest.is_rest = True
                rhythm.append(rest)
                for _ in range(syllable_count):
                    syllable = core_events.SimpleEvent(syllable_duration)
                    syllable.is_rest = False
                    rhythm.append(syllable)
                rest = core_events.SimpleEvent(rest_right)
                rest.is_rest = True
                rhythm.append(rest)
                rhythm_list_list[index].append(rhythm)

        return tuple(tuple(rhythm_list) for rhythm_list in rhythm_list_list)

    def make_simple_suject_speaking_voice(self):
        sequential_event = core_events.SequentialEvent([])
        for sentence_lyric, sentence_rhythm in zip(
            self.suject_divided_sentence_tuple, self.rhythm_per_sentence_per_suject
        ):
            for suject_lyric, suject_rhythm in zip(sentence_lyric, sentence_rhythm):
                suject_syllable_list = []
                for word in suject_lyric:
                    suject_syllable_list.extend(word[:])
                lyric_iterator = iter(suject_syllable_list)
                for event in suject_rhythm:
                    if event.is_rest:
                        note_like = music_events.NoteLike(
                            pitch_list=[], duration=event.duration
                        )
                    else:
                        syllable = next(lyric_iterator)
                        note_like = music_events.NoteLike(
                            duration=event.duration, lyric=syllable
                        )
                    sequential_event.append(note_like)
        return sequential_event

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
        return (
            abjad.TimeSignature(
                (15, 4)
            ),
        )
        # time_signature_list = []
        # for _ in range(LOOP_COUNT):
        #     time_signature_list.extend(TIME_SIGNATURE_LOOP)
        # return tuple(time_signature_list)

    def add_metronome_content(self, simultaneous_event):
        for _ in range(LOOP_COUNT):
            simultaneous_event[0].extend(METRONME_LOOP.copy())

    def add_missing_note(self, simultaneous_event):
        simultaneous_event_duration = simultaneous_event.duration
        for event in simultaneous_event:
            difference = simultaneous_event_duration - event.duration
            if difference:
                event.append(music_events.NoteLike(pitch_list=[], duration=difference))

    def make_simultaneous_event(self) -> core_events.SimultaneousEvent:
        simultaneous_event = self._get_empty_simultaneous_event()
        simple_voice = self.make_simple_suject_speaking_voice()
        for sequential_event in simultaneous_event[1:]:
            sequential_event.extend(simple_voice.copy())
        self.add_metronome_content(simultaneous_event)
        self.add_missing_note(simultaneous_event)
        cdd.utilities.add_instrument_name(simultaneous_event)
        # We don't need short instrument name notation for this score
        [setattr(event, "short_instrument_name", "") for event in simultaneous_event]
        return simultaneous_event

    tempo_envelope = expenvelope.Envelope.from_points(
        [2, core_parameters.TempoPoint(70)]
    )

    instruction_text = r"""
speak text clearly \& naturally; avoid theatric, monotonous or mechanical voice.\\
singer leads group by playing the additional percussion line.\\
instrument can be any (but only one) percussive sound, e.g. clapping, wood block, a tiny bell, \dots\\
"""
