from __future__ import annotations

import bisect
import collections
import copy
import dataclasses
import itertools
import os

from mutwo import cdd_converters
from mutwo import cdd_events
from mutwo import cdd_parameters
from mutwo import common_generators
from mutwo import core_converters
from mutwo import core_events
from mutwo import core_generators
from mutwo import core_utilities
from mutwo import music_parameters

__all__ = (
    "BellSample",
    "BellSampleFamily",
    "Bell",
    "BellCollection",
    "AttackDynamicChoiceAndAttackSequentialEventTupleToBellSequentialEventBlueprint",
    "BellSequentialEventBlueprintToBellSequentialEvent",
    "BellSequentialEventToBellCsoundSequentialEvent",
    "BellCsoundSequentialEventToMonoBellCsoundSimultaneousEvent",
)


@dataclasses.dataclass
class BellSample(object):
    path: str
    pitch: music_parameters.abc.Pitch


@dataclasses.dataclass
class BellSampleFamily(object):
    name: str
    bell_sample_tuple: tuple[BellSample, ...]

    def __post_init__(self):
        self.bell_sample_cycle = itertools.cycle(self.bell_sample_tuple)

    def __next__(self) -> BellSample:
        return next(self.bell_sample_cycle)


class Bell(dict[str, BellSampleFamily]):
    def __init__(self, name: str, pitch: music_parameters.abc.Pitch, **kwargs):
        self.__name = name
        self.pitch = pitch
        super().__init__(**kwargs)

    @property
    def name(self) -> str:
        return self.__name

    def __hash__(self) -> int:
        return hash(self.__name)

    @classmethod
    def from_directory_path_and_pitch(
        cls, directory_path: str, pitch: music_parameters.abc.Pitch
    ) -> Bell:
        bell_sample_family_name_to_bell_sample_family_dict = {}
        for family_name in os.listdir(directory_path):
            family_path = f"{directory_path}/{family_name}"
            bell_sample_list = []
            for local_bell_sample_path in os.listdir(family_path):
                bell_sample_path = f"{family_path}/{local_bell_sample_path}"
                bell_sample = BellSample(bell_sample_path, pitch)
                bell_sample_list.append(bell_sample)
            bell_sample_family = BellSampleFamily(family_name, tuple(bell_sample_list))
            bell_sample_family_name_to_bell_sample_family_dict.update(
                {family_name: bell_sample_family}
            )
        return cls(
            name=directory_path,
            pitch=pitch,
            **bell_sample_family_name_to_bell_sample_family_dict,
        )

    def __getattr__(self, name: str):
        try:
            super().__getattr__(name)
        except AttributeError:
            return self[name]


class BellCollection(tuple[Bell]):
    def __init__(self, *_, **__):
        super().__init__()
        self.frequency_to_bell = {bell.pitch.frequency: bell for bell in self}
        self.frequency_tuple = tuple(sorted(self.frequency_to_bell.keys()))
        self.bell_counter = collections.Counter({bell: 0 for bell in self})
        self.bell_count = len(self)

    def get_sample_data(
        self, pitch: music_parameters.abc.Pitch, bell_sample_family_name: str
    ) -> tuple[str, float]:
        pitch_frequency = pitch.frequency
        index1 = bisect.bisect_left(self.frequency_tuple, pitch_frequency)
        index0 = index1 - 1
        champion_frequency = self.frequency_tuple[0]
        champion = self.frequency_to_bell[champion_frequency]
        fitness = float("inf")
        for index in (index0, index1):
            if index >= 0 and index < self.bell_count:
                candidate_frequency = self.frequency_tuple[index]
                candidate = self.frequency_to_bell[candidate_frequency]
                candidate_fitness = self.bell_counter[candidate]
                if candidate_fitness < fitness:
                    champion, champion_frequency, fitness = (
                        candidate,
                        candidate_frequency,
                        candidate_fitness,
                    )

        sample_path = next(champion[bell_sample_family_name]).path
        pitch_factor = pitch_frequency / candidate_frequency

        return (sample_path, pitch_factor)


class AttackDynamicChoiceAndAttackSequentialEventTupleToBellSequentialEventBlueprint(
    core_converters.abc.Converter
):
    """Makes sequential event with bell events with assigned duration and panning

    (But it still misses pitch, distance and amplitude values.)
    """

    def __init__(
        self,
        absolute_position_to_panning: cdd_converters.AbsolutePositionToPanning,
    ):
        self.absolute_position_to_panning = absolute_position_to_panning

    def _is_valid_candidate(
        self,
        absolute_time: float,
        panning: cdd_parameters.Panning,
        absolute_time_tuple_list: list[tuple[float, ...]],
    ) -> bool:
        true_fitness, false_fitness = 0, 0
        for channel_strength, absolute_time_tuple in zip(
            panning, absolute_time_tuple_list
        ):
            if absolute_time in absolute_time_tuple:
                true_fitness += channel_strength
            else:
                false_fitness += channel_strength
        return true_fitness > false_fitness

    def convert(
        self,
        attack_dynamic_choice: core_generators.DynamicChoice,
        attack_sequential_event_tuple: tuple[
            core_events.SequentialEvent[core_events.SimpleEvent], ...
        ],
    ) -> core_events.SequentialEvent[cdd_events.BellEvent]:
        potential_attack_absolute_time_tuple_list = []
        combined_potential_attack_absolute_time_list = []
        for attack_sequential_event in attack_sequential_event_tuple:
            potential_attack_absolute_time_list = []
            for absolute_time, simple_event in zip(
                attack_sequential_event.absolute_time_tuple, attack_sequential_event
            ):
                if simple_event.is_attack:
                    potential_attack_absolute_time_list.append(absolute_time)
            potential_attack_absolute_time_tuple_list.append(
                tuple(potential_attack_absolute_time_list)
            )
            combined_potential_attack_absolute_time_list.extend(
                potential_attack_absolute_time_list
            )

        duration = attack_sequential_event_tuple[0].duration
        bell_sequential_event_blueprint = core_events.SequentialEvent(
            [core_events.SimpleEvent(duration)]
        )
        absolute_time_tuple = tuple(
            sorted(set(combined_potential_attack_absolute_time_list))
        )
        for absolute_time in absolute_time_tuple:
            absolute_position = absolute_time / duration
            panning = self.absolute_position_to_panning(absolute_position)

            try:
                assert len(panning) == len(attack_sequential_event_tuple)
            except AssertionError:
                raise ValueError(
                    "Inconsistent number of channels! Panning: "
                    f"{len(panning)}, Attack sequential event tuple: "
                    f"{len(attack_sequential_event_tuple)}"
                )

            # 1. Check if there is an attack on active channels.
            #    The percentage of channels with attack has to be higher
            #    than channels without attack to be a valid event
            #    candidate. Percentage is relative depending on the panning.

            is_valid_candidate = self._is_valid_candidate(
                absolute_time, panning, potential_attack_absolute_time_tuple_list
            )

            if is_valid_candidate:

                # 2. Not all detected onsets with be transformed to events.
                #    The passed attack_tendency filters events.

                if attack_dynamic_choice.gamble_at(absolute_position):
                    bell_event = cdd_events.BellEvent(
                        duration=4,
                        panning_start=panning,
                        panning_end=panning,
                    )
                    bell_sequential_event_blueprint.squash_in(absolute_time, bell_event)

        return bell_sequential_event_blueprint


class BellSequentialEventBlueprintToBellSequentialEvent(core_converters.abc.Converter):
    def __init__(
        self,
        pitch_dynamic_choice: core_generators.DynamicChoice,
        distance_tendency: common_generators.Tendency,
        # for each channel one envelope
        rms_envelope_tuple: tuple[core_events.Envelope, ...],
    ):
        self.pitch_dynamic_choice = pitch_dynamic_choice
        self.distance_tendency = distance_tendency
        self.rms_envelope_tuple = rms_envelope_tuple

    def convert(
        self,
        bell_sequential_event_blueprint: core_events.SequentialEvent[
            cdd_events.BellEvent
        ],
    ) -> core_events.SequentialEvent[cdd_events.BellEvent]:
        bell_sequential_event = bell_sequential_event_blueprint.copy()
        duration = bell_sequential_event.duration

        for absolute_time, simple_event in zip(
            bell_sequential_event.absolute_time_tuple, bell_sequential_event
        ):
            if isinstance(simple_event, cdd_events.BellEvent):
                absolute_position = absolute_time / duration
                simple_event.pitch = self.pitch_dynamic_choice.gamble_at(
                    absolute_position
                )
                simple_event.distance = self.distance_tendency.value_at(
                    absolute_position
                )
                simple_event.volume = music_parameters.DirectVolume(
                    (
                        sum(
                            rms_envelope.value_at(absolute_time) * channel_strength
                            if channel_strength
                            else 0
                            for rms_envelope, channel_strength in zip(
                                self.rms_envelope_tuple, simple_event.panning_start
                            )
                        )
                        / len(simple_event.panning_start)
                    )
                    * 10
                )

        return bell_sequential_event


class BellSequentialEventToBellCsoundSequentialEvent(
    core_converters.abc.SymmetricalEventConverter
):
    def __init__(
        self,
        bell_collection: BellCollection,
        bell_sample_family_dynamic_choice: core_generators.DynamicChoice = core_generators.DynamicChoice(
            ["single"],
            [core_events.Envelope([[0, 1], [1, 1]])],
        ),
    ):
        self._bell_collection = bell_collection
        self._bell_sample_family_dynamic_choice = bell_sample_family_dynamic_choice

    def _distance_and_pitch_to_filter_frequency(
        self, distance: float, pitch: music_parameters.abc.Pitch
    ) -> float:
        frequency = pitch.frequency
        partial_index = core_utilities.scale(distance, 0, 1, 42, 2)
        return frequency * partial_index

    def _convert_simple_event(
        self, event_to_convert: core_events.SimpleEvent, absolute_time: float
    ) -> core_events.SimpleEvent:
        if isinstance(event_to_convert, cdd_events.BellEvent):
            absolute_position = absolute_time / self._duration
            bell_sample_family_name = self._bell_sample_family_dynamic_choice.gamble_at(
                absolute_position
            )
            sample_path, pitch_factor = self._bell_collection.get_sample_data(
                event_to_convert.pitch, bell_sample_family_name
            )
            filter_frequency = self._distance_and_pitch_to_filter_frequency(
                event_to_convert.distance, event_to_convert.pitch
            )
            simple_event = cdd_events.BellCsoundEvent(
                sample_path=sample_path,
                pitch_factor=pitch_factor,
                amplitude=music_parameters.DecibelVolume(
                    event_to_convert.volume.decibel
                    + core_utilities.scale(event_to_convert.distance, 0, 1, 0, -12)
                ).amplitude,
                duration=event_to_convert.duration,
                panning_start=event_to_convert.panning_start,
                panning_end=event_to_convert.panning_end,
                filter_frequency=filter_frequency,
                convolution_reverb_mix=core_utilities.scale(
                    event_to_convert.distance, 0, 1, 0.1, 0.85
                ),
            )
        else:
            simple_event = copy.deepcopy(event_to_convert)
        return simple_event

    def convert(
        self,
        bell_sequential_event_to_convert: core_events.SequentialEvent[
            cdd_events.BellEvent
        ],
    ) -> core_events.SequentialEvent[cdd_events.BellCsoundEvent]:
        self._duration = bell_sequential_event_to_convert.duration
        return self._convert_event(bell_sequential_event_to_convert, 0)


class BellCsoundSequentialEventToMonoBellCsoundSimultaneousEvent(
    core_converters.abc.Converter
):
    def __init__(self, channel_count: int = 2):
        self._channel_count = channel_count

    def convert(
        self,
        bell_csound_sequential_event_to_convert: core_events.SequentialEvent[
            cdd_events.BellCsoundEvent
        ],
    ) -> core_events.SimultaneousEvent[
        core_events.SequentialEvent[cdd_events.MonoBellCsoundEvent]
    ]:
        mono_bell_csound_sequential_event_list = [
            core_events.SequentialEvent([]) for _ in range(self._channel_count)
        ]
        for simple_event in bell_csound_sequential_event_to_convert:
            if isinstance(simple_event, cdd_events.BellCsoundEvent):
                for mono_bell_csound_event, mono_bell_csound_sequential_event in zip(
                    simple_event.split_to(self._channel_count),
                    mono_bell_csound_sequential_event_list,
                ):
                    mono_bell_csound_sequential_event.append(mono_bell_csound_event)
            else:
                for (
                    mono_bell_csound_sequential_event
                ) in mono_bell_csound_sequential_event_list:
                    mono_bell_csound_sequential_event.append(
                        copy.deepcopy(simple_event)
                    )

        return core_events.SimultaneousEvent(mono_bell_csound_sequential_event_list)
