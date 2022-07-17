__all__ = ("Chapter",)

import dataclasses
import functools
import itertools

import ranges
import yamm

from mutwo import core_events
from mutwo import core_generators
from mutwo import core_utilities
from mutwo import music_parameters

import cdd


@dataclasses.dataclass
class PitchCollection(object):
    name: str
    pitch_class_to_weight_dict: dict[tuple[int, ...], float]

    def get_pitch_weight(
        self, pitch_class: music_parameters.JustIntonationPitch
    ) -> float:
        return self.pitch_class_to_weight_dict[pitch_class.normalize().exponent_tuple]

    def get_pitch_to_weight_dict(
        self, pitch_ambitus: music_parameters.abc.PitchAmbitus
    ) -> dict[tuple[int, ...], float]:
        pitch_to_weight_dict = {}
        for pitch_class, weight in self.pitch_class_to_weight_dict.items():
            pitch_tuple = pitch_ambitus.get_pitch_variant_tuple(
                music_parameters.JustIntonationPitch(pitch_class)
            )
            for pitch in pitch_tuple:
                pitch_to_weight_dict.update({pitch.exponent_tuple: weight})
        return pitch_to_weight_dict

    @functools.cached_property
    def pitch_tuple(self) -> tuple[music_parameters.JustIntonationPitch, ...]:
        return tuple(
            sorted(
                [
                    music_parameters.JustIntonationPitch(pitch_class).normalize()
                    for pitch_class in self.pitch_class_to_weight_dict.keys()
                ]
            )
        )

    @functools.cached_property
    def pitch_tuple_sorted_by_weight(
        self,
    ) -> tuple[music_parameters.JustIntonationPitch, ...]:
        return tuple(
            sorted(self.pitch_tuple, key=lambda pitch: self.get_pitch_weight(pitch))
        )

    @functools.cached_property
    def pitch_count(self) -> int:
        return len(self.pitch_tuple)

    @property
    def deterministic_pitch_class_markov_chain(self) -> yamm.chain.Chain:
        markov_mapping: dict[tuple[tuple[int, ...]], dict[tuple[int, ...], int]] = {}
        for unsorted_pitch_pair in itertools.combinations(self.pitch_tuple, 2):
            pitch_index0, pitch_index1 = (
                self.pitch_tuple.index(pitch) for pitch in unsorted_pitch_pair
            )
            if abs(pitch_index0 - pitch_index1) == 1 or (
                pitch_index0 in (0, self.pitch_count - 1)
                and pitch_index1 in (0, self.pitch_count - 1)
                and pitch_index0 != pitch_index1
            ):
                for pitch0, pitch1 in itertools.permutations(unsorted_pitch_pair):
                    weight = int(self.get_pitch_weight(pitch1) * 10)
                    key = (pitch0.exponent_tuple,)
                    update_value = {pitch1.exponent_tuple: weight}
                    try:
                        markov_mapping[key].update(update_value)
                    except KeyError:
                        markov_mapping.update({key: update_value})
        markov_chain = yamm.chain.Chain(markov_mapping)
        markov_chain.make_deterministic_map()
        return markov_chain


class ChapterPart(core_events.SimpleEvent):
    def __init__(self, duration: float, pitch_collection: PitchCollection):
        super().__init__(duration)
        self.pitch_collection = pitch_collection


class ChapterPartSequence(core_events.SequentialEvent[ChapterPart]):
    @property
    def deterministic_pitch_class_markov_chain_range(self) -> ranges.RangeDict:
        deterministic_pitch_class_markov_chain_range = ranges.RangeDict()
        for time_range, chapter_part in zip(self.start_and_end_time_per_event, self):
            deterministic_pitch_class_markov_chain_range.update(
                {
                    time_range: chapter_part.pitch_collection.deterministic_pitch_class_markov_chain
                }
            )
        return deterministic_pitch_class_markov_chain_range

    @functools.cached_property
    def pitch_collection_range(self) -> ranges.RangeDict:
        pitch_collection_range = ranges.RangeDict()
        for time_range, chapter_part in zip(self.start_and_end_time_per_event, self):
            pitch_collection_range.update({time_range: chapter_part.pitch_collection})
        return pitch_collection_range

    def get_pitch_dynamic_choice(
        self,
        pitch_ambitus: music_parameters.abc.PitchAmbitus,
        crossfade_duration_factor: float = 0.125,
        scale_envelope_duration: float = 1,
    ) -> core_generators.DynamicChoice:
        assert crossfade_duration_factor <= 0.5

        part_duration_list = []
        chapter_part1_crossfade = 0
        for chapter_part0, chapter_part1 in zip(self, self[1:]):
            chapter0_duration, chapter1_duration = (
                chapter_part0.duration - chapter_part1_crossfade,
                chapter_part1.duration,
            )

            chapter_part0_crossfade = chapter0_duration * crossfade_duration_factor
            chapter_part1_crossfade = chapter1_duration * crossfade_duration_factor

            part_duration_list.append(chapter0_duration - chapter_part0_crossfade)
            part_duration_list.append(chapter_part0_crossfade + chapter_part1_crossfade)

        part_duration_list.append(self[-1].duration - chapter_part1_crossfade)

        assert core_utilities.round_floats(
            sum(part_duration_list), 3
        ) == core_utilities.round_floats(self.duration, 3)

        pitch_to_pitch_envelope_dict = {}

        def add_value_to_envelope(
            pitch: tuple[int, ...],
            weight: float,
            absolute_time0: float,
            absolute_time1: float,
        ):
            duration = absolute_time1 - absolute_time0
            try:
                envelope = pitch_to_pitch_envelope_dict[pitch]
            except KeyError:
                pitch_to_pitch_envelope_dict[pitch] = envelope = core_events.Envelope(
                    []
                )

            difference = absolute_time0 - envelope.duration
            if difference > 0.001:
                envelope.append(
                    core_events.SimpleEvent(difference).set_parameter("value", 0)
                )

            envelope.append(
                core_events.SimpleEvent(duration).set_parameter("value", weight)
            )

        absolute_time_tuple = tuple(
            core_utilities.accumulate_from_zero(part_duration_list)
        )
        for absolute_time0, absolute_time1 in zip(
            absolute_time_tuple, absolute_time_tuple[1:]
        ):
            cut_out_chaper_part_sequence = self.cut_out(
                absolute_time0, absolute_time1, mutate=False
            )
            if (chaper_part_count := len(cut_out_chaper_part_sequence)) == 1:
                for pitch, weight in (
                    cut_out_chaper_part_sequence[0]
                    .pitch_collection.get_pitch_to_weight_dict(pitch_ambitus)
                    .items()
                ):
                    add_value_to_envelope(
                        pitch,
                        weight,
                        absolute_time0,
                        absolute_time1,
                    )

            elif chaper_part_count == 2:
                pitch_to_weight_dict0, pitch_to_weight_dict1 = (
                    chapter_part.pitch_collection.get_pitch_to_weight_dict(
                        pitch_ambitus
                    )
                    for chapter_part in cut_out_chaper_part_sequence
                )

                for pitch in set(
                    tuple(pitch_to_weight_dict0.keys())
                    + tuple(pitch_to_weight_dict1.keys())
                ):
                    if pitch not in pitch_to_weight_dict0:
                        add_value_to_envelope(pitch, 0, absolute_time0, absolute_time1)

                    else:
                        add_value_to_envelope(
                            pitch,
                            pitch_to_weight_dict0[pitch],
                            absolute_time0,
                            absolute_time1,
                        )

            else:
                raise AssertionError()

        duration = self.duration

        pitch_list, envelope_list = [], []
        for pitch, pitch_envelope in pitch_to_pitch_envelope_dict.items():
            difference = duration - pitch_envelope.duration
            if difference > 0.001:
                pitch_envelope.append(
                    core_events.SimpleEvent(difference).set_parameter("value", 0)
                )
            pitch_envelope.append(
                core_events.SimpleEvent(0).set_parameter(
                    "value", pitch_envelope[-1].value
                )
            )
            if scale_envelope_duration:
                pitch_envelope.duration = scale_envelope_duration
            pitch_list.append(music_parameters.JustIntonationPitch(pitch))
            envelope_list.append(pitch_envelope)

        return core_generators.DynamicChoice(pitch_list, envelope_list)


class Chapter(cdd.chapters.Chapter):
    from . import constants
    # from . import bells
    # from . import resonators
    # from . import voices
    from . import audio_scores

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setup_chapter_part_sequence()
        # self.bell_csound_sequential_event = self.bells.main(self)
        # self.resonator_bandpass_melody_simultaneous_event = self.resonators.main(self)
        # self.voice_simultaneous_event = self.voices.main(self)
        self.command_sequential_event_dict = self.audio_scores.main(self)

    def setup_chapter_part_sequence(self):
        pitch_collection_tuple = tuple(
            PitchCollection(
                name,
                {
                    pitch.normalize().exponent_tuple: weight
                    for pitch, weight in pitch_and_weight_pair_tuple
                },
            )
            for pitch_and_weight_pair_tuple, name in self.constants.PITCH_COLLECTION_DESCRIPTION_TUPLE
        )

        chapter_part_sequence = ChapterPartSequence(
            [
                ChapterPart(duration, pitch_collection_tuple[pitch_collection_index])
                for pitch_collection_index, duration in self.constants.CHAPTER_PART_DATA_TUPLE
            ]
        )
        chapter_part_sequence.duration = self.constants.CHAPTER_DURATION_IN_SECONDS
        self.chapter_part_sequence = chapter_part_sequence
