import abc
import collections

import numpy as np

from mutwo import cdd_parameters
from mutwo import common_generators
from mutwo import core_converters
from mutwo import core_events
from mutwo import core_generators
from mutwo import core_utilities


__all__ = (
    "AbsolutePositionToPanning",
    "AbsoluteBellPositionToPanning",
    "PanningToMutatedPanning",
    "PanningToScaledPanning",
    "PanningToMovedPanning",
    "PanningToUnchangedPanning",
)


class AbsolutePositionToPanning(core_converters.abc.Converter):
    CHANNEL_COUNT = 5

    def __init__(self, seed: int = 1030405):
        self.channel_count_dynamic_choice = core_generators.DynamicChoice(
            [1, 2, 3, 4],
            [
                core_events.Envelope([[0, 0.7]]),
                core_events.Envelope([[0, 1]]),
                core_events.Envelope([[0, 0.5]]),
                core_events.Envelope([[0, 0.2]]),
            ],
        )
        self.channel_counter = collections.Counter(
            {index: 0 for index in range(self.CHANNEL_COUNT)}
        )

        self.random = np.random.default_rng(seed=seed)

    def convert(self, absolute_position: float) -> cdd_parameters.Panning:
        channel_count = self.channel_count_dynamic_choice.gamble_at(0)

        minima = min(self.channel_counter.values())
        channel_to_choose_from_tuple = tuple(
            channel
            for channel, count in self.channel_counter.items()
            if count == minima
        )
        choosen_channel_index = self.random.choice(channel_to_choose_from_tuple)

        self.channel_counter[choosen_channel_index] += 1

        distribution_size = int(channel_count * self.random.uniform(1, 3))
        distribution = common_generators.euclidean(distribution_size, channel_count)

        panning_list = [0 for _ in range(self.CHANNEL_COUNT)]

        for distribution_index, distribution_value in enumerate(distribution):
            real_index = (
                distribution_index + choosen_channel_index
            ) % self.CHANNEL_COUNT
            panning_list[real_index] = distribution_value

        panning = cdd_parameters.Panning(panning_list).normalize()
        return panning


class AbsoluteBellPositionToPanning(AbsolutePositionToPanning):
    def convert(self, absolute_position: float) -> cdd_parameters.Panning:
        start_movement_duration = 0.2

        if absolute_position < start_movement_duration:
            value0, value1 = core_utilities.scale(
                absolute_position, 0, start_movement_duration, 0, 1
            ), core_utilities.scale(absolute_position, 0, start_movement_duration, 1, 0)
            return cdd_parameters.Panning([0, 0, 0, value0, value1]).normalize()

        return super().convert(absolute_position)


class PanningToMutatedPanning(core_converters.abc.Converter):
    @abc.abstractmethod
    def convert(
        self, panning_to_convert: cdd_parameters.Panning
    ) -> cdd_parameters.Panning:
        ...


class PanningToScaledPanning(PanningToMutatedPanning):
    def __init__(self):
        self.random = np.random.default_rng(seed=3123)

    def convert(
        self, panning_to_convert: cdd_parameters.Panning
    ) -> cdd_parameters.Panning:
        # Expand
        if panning_to_convert.active_channel_count == 1:
            maxima = max(panning_to_convert)
            active_panning_index = panning_to_convert.index(maxima)
            added_index_0, added_index_1 = (
                (active_panning_index + index) % panning_to_convert.channel_count
                for index in (-1, 1)
            )
            new_panning = [
                maxima
                if index in (added_index_0, added_index_1, active_panning_index)
                else 0
                for index in range(panning_to_convert.channel_count)
            ]
        # Shrink
        else:
            new_active_panning_index = self.random.choice(
                panning_to_convert.active_panning_index_tuple
            )
            new_panning = [
                1 if index == new_active_panning_index else 0
                for index, _ in enumerate(panning_to_convert)
            ]
        return cdd_parameters.Panning(new_panning).normalize()


class PanningToMovedPanning(PanningToMutatedPanning):
    def __init__(self):
        self.activity_level = common_generators.ActivityLevel()

    def convert(
        self, panning_to_convert: cdd_parameters.Panning
    ) -> cdd_parameters.Panning:
        index_to_move = (-1, 1)[self.activity_level(5)]
        new_panning_index_tuple = tuple(
            (index + index_to_move) % panning_to_convert.channel_count
            for index in panning_to_convert.active_panning_index_tuple
        )
        new_panning = [
            panning_to_convert.active_panning_value_tuple[
                new_panning_index_tuple.index(index)
            ]
            if index in new_panning_index_tuple
            else 0
            for index in range(panning_to_convert.channel_count)
        ]
        return cdd_parameters.Panning(new_panning).normalize()


class PanningToUnchangedPanning(PanningToMutatedPanning):
    def convert(
        self, panning_to_convert: cdd_parameters.Panning
    ) -> cdd_parameters.Panning:
        return panning_to_convert.normalize()
