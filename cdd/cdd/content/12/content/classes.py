from __future__ import annotations
import dataclasses
import functools
import itertools
import typing
import warnings

import abjad
import expenvelope
import quicktions as fractions

from mutwo import cdd_converters
from mutwo import cdd_interfaces
from mutwo import common_generators
from mutwo import core_converters
from mutwo import core_events
from mutwo import core_utilities
from mutwo import music_events
from mutwo import music_parameters

import cdd

from . import configurations


@dataclasses.dataclass()
class LongTone(object):
    pitch: music_parameters.JustIntonationPitch
    dynamic_curve: typing.Literal["<", ">", "<>"]
    duration: fractions.Fraction
    delay: fractions.Fraction

    @functools.cached_property
    def to_sequential_event(self) -> core_events.SequentialEvent:
        sequential_event = core_events.SequentialEvent([])
        if self.delay:
            sequential_event.append(music_events.NoteLike([], self.delay))

        note_like = music_events.NoteLike(self.pitch, self.duration)
        note_like.playing_indicator_collection.hairpin.symbol = self.dynamic_curve
        note_like.playing_indicator_collection.hairpin.niente = True

        sequential_event.append(note_like)
        return sequential_event


@dataclasses.dataclass()
class Transformer(core_converters.abc.Converter):
    transform: typing.Callable[
        [core_events.SequentialEvent], core_events.SequentialEvent
    ]
    beat_count_in: int
    beat_count_out: int

    def convert(
        self, event_to_convert: core_events.SequentialEvent
    ) -> tuple[core_events.SequentialEvent, abjad.TimeSignature]:
        fraction_as_tuple = (self.beat_count_out, configurations.BEAT_SIZE.denominator)
        transformed_sequential_event = self.transform(event_to_convert)

        try:
            assert transformed_sequential_event.duration == fractions.Fraction(
                *fraction_as_tuple
            )
        except AssertionError:
            raise Exception(
                f"DIFFERENCE OF {transformed_sequential_event.duration - fractions.Fraction(*fraction_as_tuple)}"
            )

        return (
            transformed_sequential_event,
            abjad.TimeSignature(fraction_as_tuple),
        )


@dataclasses.dataclass()
class TransformerCollection(core_converters.abc.Converter):
    transformer_tuple: tuple[Transformer]

    def __post_init__(self):
        beat_count_in_set = set(
            [transformer.beat_count_in for transformer in self.transformer_tuple]
        )
        beat_count_in_to_transformer_list_dict = {
            beat_count_in: [] for beat_count_in in beat_count_in_set
        }
        for transformer in self.transformer_tuple:
            beat_count_in_to_transformer_list_dict[transformer.beat_count_in].append(
                transformer
            )

        self.beat_count_in_to_transformer_tuple_dict = {
            beat_count_in: tuple(transformer_list)
            for beat_count_in, transformer_list in beat_count_in_to_transformer_list_dict.items()
        }

        self._beat_count_in_to_transformer_cycle_dict = {
            beat_count_in: itertools.cycle(transformer_list)
            for beat_count_in, transformer_list in beat_count_in_to_transformer_list_dict.items()
        }

    def convert(
        self,
        event_to_convert: core_events.SequentialEvent,
        time_signature: abjad.TimeSignature,
    ) -> tuple[core_events.SequentialEvent, abjad.TimeSignature]:
        beat_count = time_signature.numerator
        try:
            transformer = next(
                self._beat_count_in_to_transformer_cycle_dict[beat_count]
            )
        except KeyError:
            warnings.warn(
                f"No transformer defined for beat_count = {beat_count}.", RuntimeWarning
            )
            return event_to_convert, time_signature
        else:
            return transformer.convert(event_to_convert)


TRANSFORMER_COLLECTION = TransformerCollection(
    [Transformer(*data) for data in configurations.TRANSFORMER_DATA_TUPLE]
)


@dataclasses.dataclass()
class Pattern(object):
    pattern: tuple[typing.Union[int, tuple[int, ...]], ...]

    def reverse(self) -> Pattern:
        return type(self)(tuple(reversed(self.pattern)))

    def to_sequential_event(
        self, pitch_tuple: tuple[music_parameters.abc.Pitch, ...]
    ) -> core_events.SequentialEvent:
        pattern_maxima = max(
            [item if isinstance(item, int) else max(item) for item in self.pattern]
        )
        assert pattern_maxima < len(pitch_tuple)

        sequential_event = core_events.SequentialEvent([])
        for index_or_index_tuple in self.pattern:
            if isinstance(index_or_index_tuple, int):
                index_tuple = (index_or_index_tuple,)
            else:
                index_tuple = index_or_index_tuple
            note_like = music_events.NoteLike(
                [pitch_tuple[index] for index in index_tuple], configurations.BEAT_SIZE
            )
            sequential_event.append(note_like)
        return sequential_event

    @property
    def time_signature(self) -> abjad.TimeSignature:
        return abjad.TimeSignature(
            (len(self.pattern), configurations.BEAT_SIZE.denominator)
        )


ACTIVITY_OBJECT = common_generators.ActivityLevel()
TRANSFORM_ACTIVITY_OBJECT = common_generators.ActivityLevel()


@dataclasses.dataclass()
class ClavichordPart(object):
    pitch: music_parameters.JustIntonationPitch
    pattern: Pattern
    density_envelope: core_events.Envelope
    pattern_count: int
    transform_activity_level: int

    time_signature_tuple: tuple[abjad.TimeSignature, ...] = dataclasses.field(
        init=False
    )
    sequential_event: core_events.SequentialEvent = dataclasses.field(init=False)

    def __post_init__(self):
        pitch_tuple = cdd.constants.CLAVICHORD_AMBITUS.get_pitch_variant_tuple(
            self.pitch
        )

        time_signature_list, sequential_event = [], core_events.SequentialEvent([])
        pattern_sequential_event = self.pattern.to_sequential_event(pitch_tuple)
        pattern_time_signature = self.pattern.time_signature

        for pattern_index in range(self.pattern_count):
            (
                processed_sequential_event,
                processed_time_signature,
            ) = self._process_pattern(
                pattern_index / self.pattern_count,
                pattern_sequential_event.copy(),
                pattern_time_signature,
            )
            sequential_event.extend(processed_sequential_event)
            time_signature_list.append(processed_time_signature)

        self._post_process_sequential_event(sequential_event)
        self.time_signature_tuple = tuple(time_signature_list)
        self.sequential_event = sequential_event

        # self.sequential_event = core_events.SequentialEvent(
        #     [
        #         music_events.NoteLike(pitch_tuple[-1], fractions.Fraction(1, 6))
        #         for _ in range(
        #             int(self.sequential_event.duration / fractions.Fraction(1, 6))
        #         )
        #     ]
        # )

        # for index, note_like in enumerate(self.sequential_event):
        #     if index % 3 == 0:
        #         note_like.pitch_list = []
        #     elif (index - 1) % 3 ==0:
        #         note_like.pitch_list[0] -= music_parameters.JustIntonationPitch('3/2')

        time_signature_duration = sum(
            [
                fractions.Fraction(time_signature.duration)
                for time_signature in self.to_time_signature_tuple
            ]
        )

        assert self.sequential_event.duration == time_signature_duration

    def _process_pattern(
        self,
        _: float,  # percentage
        sequential_event: core_events.SequentialEvent,
        time_signature: abjad.TimeSignature,
    ) -> tuple[core_events.SequentialEvent, abjad.TimeSignature]:
        if TRANSFORM_ACTIVITY_OBJECT(self.transform_activity_level):
            return TRANSFORMER_COLLECTION.convert(sequential_event, time_signature)
        else:
            return sequential_event, time_signature

    def _post_process_sequential_event(
        self, sequential_event: core_events.SequentialEvent
    ):
        event_count = len(sequential_event)
        for index, note_like in enumerate(sequential_event):
            percentage = index / event_count
            level = int(self.density_envelope.value_at(percentage) * 10)
            if not ACTIVITY_OBJECT(level):
                note_like.pitch_list = []

    @property
    def to_time_signature_tuple(self) -> tuple[abjad.TimeSignature, ...]:
        return self.time_signature_tuple

    @property
    def to_sequential_event(self):
        return self.sequential_event


@dataclasses.dataclass()
class Chord(object):
    long_tone_soprano: LongTone
    long_tone_clarinet: LongTone
    clavichord_part: ClavichordPart

    @functools.cached_property
    def to_tempo_envelope(self) -> core_events.Envelope:
        return core_events.Envelope(
            [
                [0, configurations.BASE_TEMPO],
                [self.to_simultaneous_event.duration, configurations.BASE_TEMPO],
            ]
        )

    @functools.cached_property
    def to_time_signature_tuple(self) -> tuple[abjad.TimeSignature, ...]:
        return self.clavichord_part.to_time_signature_tuple

    @functools.cached_property
    def to_simultaneous_event(self) -> core_events.SimultaneousEvent:
        simultaneous_event = core_events.SimultaneousEvent([])

        for part, tag in (
            (self.long_tone_soprano, "soprano"),
            (self.long_tone_clarinet, "clarinet"),
            (self.clavichord_part, "clavichord"),
        ):
            simultaneous_event.append(
                core_events.TaggedSequentialEvent(part.to_sequential_event[:], tag=tag)
            )

        duration = simultaneous_event.duration
        for sequential_event in simultaneous_event:
            if difference := duration - sequential_event.duration:
                sequential_event.append(
                    music_events.NoteLike(pitch_list=[], duration=difference)
                )

        return simultaneous_event


def get_tag_to_sequential_event() -> dict[str, core_events.TaggedSequentialEvent]:
    return {
        tag: core_events.TaggedSequentialEvent([], tag=tag)
        for tag in "soprano clarinet clavichord".split(" ")
    }


@dataclasses.dataclass()
class Group(object):
    chord_tuple: tuple[Chord, ...]

    @functools.cached_property
    def to_tempo_envelope(self) -> core_events.Envelope:
        tempo_envelope = core_events.Envelope([])
        for chord in self.chord_tuple:
            tempo_envelope.extend(chord.to_tempo_envelope)
        return tempo_envelope

    @functools.cached_property
    def to_time_signature_tuple(self) -> tuple[abjad.TimeSignature, ...]:
        to_time_signature_list = []
        for chord in self.chord_tuple:
            to_time_signature_list.extend(chord.to_time_signature_tuple)
        return tuple(to_time_signature_list)

    @functools.cached_property
    def to_simultaneous_event(self) -> core_events.SimultaneousEvent:
        tag_to_sequential_event = get_tag_to_sequential_event()

        for chord in self.chord_tuple:
            for tagged_sequential_event in chord.to_simultaneous_event:
                tag_to_sequential_event[tagged_sequential_event.tag].extend(
                    tagged_sequential_event
                )

        return core_events.SimultaneousEvent(tag_to_sequential_event.values())


@dataclasses.dataclass()
class GroupCollection(object):
    group_tuple: tuple[Group, ...]
    chapter: cdd_interfaces.abc.Chapter
    rest_time_signature_tuple: tuple[abjad.TimeSignature, ...]

    @property
    def rest_duration_tuple(self) -> tuple:
        rest_duration_list = []
        for time_signature in self.rest_time_signature_tuple:
            rest_duration_list.append(
                fractions.Fraction(
                    time_signature.numerator,
                    time_signature.denominator,
                )
            )
        return tuple(rest_duration_list)

    def _add_stop_hairpin(self, sequential_event: core_events.SequentialEvent):
        for note_like in sequential_event:
            if not note_like.pitch_list:
                note_like.playing_indicator_collection.hairpin.symbol = "!"

    def process_clavichord(
        self, clavichord_sequential_event: core_events.TaggedSequentialEvent
    ):
        def is_fraction_acceptable(fraction) -> bool:
            return fraction.denominator % 2 == 0 or fraction.denominator == 1

        def condition(event0, event1):
            summed_duration = event0.duration + event1.duration
            test_list = [
                event0.pitch_list,
                not event1.pitch_list,
                is_fraction_acceptable(summed_duration)
                or all(
                    [
                        is_fraction_acceptable(event.duration)
                        for event in (event0, event1)
                    ]
                ),
                event0.duration < fractions.Fraction(2, 1),
            ]
            return all(test_list)

        clavichord_sequential_event.tie_by(condition)

    def _add_soprano_lyric(
        self, soprano_sequential_event: core_events.TaggedSequentialEvent
    ):
        @core_utilities.compute_lazy(
            path=f"{cdd.configurations.PATH.BUILDS.PICKLED}/12_soprano_lyric_distribution.pickle",
            force_to_compute=False,
        )
        def distribute_sentence(sentence_to_distribute, event_count):
            return cdd_converters.SentenceAndBeatCountToDistributedSentenceTuple()(
                sentence_to_distribute, event_count
            )[0]

        # (1) add lyrics
        syllable_list = []
        sentence = self.chapter.pessoa_lyric[2][5:]
        for word in sentence:
            for syllable in word:
                syllable_list.append(syllable)

        # syllable_iterator = iter(syllable_list)
        event_count = 0
        for note_like in soprano_sequential_event:
            if hasattr(note_like, "pitch_list") and note_like.pitch_list:
                event_count += 1

        lyric_tuple = distribute_sentence(sentence, event_count)
        syllable_iterator = iter(lyric_tuple)

        for note_like in soprano_sequential_event:
            if hasattr(note_like, "pitch_list") and note_like.pitch_list:
                note_like.lyric = next(syllable_iterator)

    def process_soprano(
        self, soprano_sequential_event: core_events.TaggedSequentialEvent
    ):
        self._add_soprano_lyric(soprano_sequential_event)
        soprano_sequential_event.set_parameter(
            "pitch_list",
            lambda pitch_list: [pitch.register(0) for pitch in pitch_list],
        )

        # for event_index in (1, 3, 6, 7):
        #     soprano_sequential_event[event_index].pitch_list[0].register(-1)

        self._add_stop_hairpin(soprano_sequential_event)

    def process_clarinet(
        self, clarinet_sequential_event: core_events.TaggedSequentialEvent
    ):
        clarinet_sequential_event.set_parameter(
            "pitch_list",
            lambda pitch_list: [pitch.register(-1) for pitch in pitch_list]
            if pitch_list
            else [],
        )

        pitch_list_tuple = tuple(
            pitch_list
            for pitch_list in clarinet_sequential_event.get_parameter("pitch_list")
            if pitch_list
        )
        pitch_list_tuple[6][0].register(-2)

        # for event_index in (6,):
        #     clarinet_sequential_event[event_index].pitch_list[0].register(0)

        self._add_stop_hairpin(clarinet_sequential_event)

    @functools.cached_property
    def to_simultaneous_event_tuple(self) -> tuple[core_events.SimultaneousEvent, ...]:
        simultaneous_event_list = []
        last_index = len(self.group_tuple) - 1
        rest_duration_iterator = iter(self.rest_duration_tuple)
        for index, group in enumerate(self.group_tuple):
            simultaneous_event_list.append(group.to_simultaneous_event)
            if index != last_index:
                simultaneous_event = core_events.SimultaneousEvent(
                    get_tag_to_sequential_event().values()
                )
                rest_duration = next(rest_duration_iterator)
                for sequential_event in simultaneous_event:
                    sequential_event.append(music_events.NoteLike([], rest_duration))
                simultaneous_event_list.append(simultaneous_event)
        return tuple(simultaneous_event_list)

    @functools.cached_property
    def to_group_absolute_time_tuple(self) -> tuple[fractions.Fraction, ...]:
        return tuple(
            core_utilities.accumulate_from_zero(
                [
                    simultaneous_event.duration
                    for simultaneous_event in self.to_simultaneous_event_tuple
                ]
            )
        )

    @functools.cached_property
    def to_sequential_event_grid(self) -> core_events.SequentialEvent:
        grid_size = fractions.Fraction(1, 16)
        return core_events.SequentialEvent(
            [
                core_events.SimpleEvent(grid_size)
                for _ in range(int(self.to_simultaneous_event.duration / grid_size))
            ]
        )

    @functools.cached_property
    def to_simultaneous_event(self) -> core_events.SimultaneousEvent:
        tag_to_sequential_event = get_tag_to_sequential_event()

        for simultaneous_event in self.to_simultaneous_event_tuple:
            for tagged_sequential_event in simultaneous_event:
                sequential_event = tag_to_sequential_event[tagged_sequential_event.tag]
                sequential_event.extend(tagged_sequential_event)

        tag_to_process = {
            tag: getattr(self, f"process_{tag}")
            for tag in "soprano clarinet clavichord".split(" ")
        }

        for tagged_sequential_event in tag_to_sequential_event.values():
            tag_to_process[tagged_sequential_event.tag](tagged_sequential_event)

        return core_events.SimultaneousEvent(tag_to_sequential_event.values())

    @functools.cached_property
    def to_time_signature_tuple(self) -> tuple[abjad.TimeSignature, ...]:
        to_time_signature_list = []
        last_index = len(self.group_tuple) - 1
        rest_time_signature_iterator = iter(self.rest_time_signature_tuple)
        for index, group in enumerate(self.group_tuple):
            to_time_signature_list.extend(group.to_time_signature_tuple)
            if index != last_index:
                to_time_signature_list.append(next(rest_time_signature_iterator))
        return tuple(to_time_signature_list)

    @functools.cached_property
    def to_tempo_envelope(self) -> core_events.Envelope:
        tempo_envelope = core_events.Envelope([])
        last_index = len(self.group_tuple) - 1
        rest_duration_iterator = iter(self.rest_duration_tuple)
        for index, group in enumerate(self.group_tuple):
            tempo_envelope.extend(group.to_tempo_envelope)
            if index != last_index:
                tempo_envelope.extend(
                    core_events.Envelope(
                        [
                            [0, configurations.BASE_TEMPO],
                            [next(rest_duration_iterator), configurations.BASE_TEMPO],
                        ]
                    )
                )
        expenvelope_tempo_envelope = expenvelope.Envelope.from_points(
            *[
                [absolute_time, event.value]
                for absolute_time, event in zip(
                    tempo_envelope.absolute_time_tuple, tempo_envelope
                )
            ]
        )
        return expenvelope_tempo_envelope
