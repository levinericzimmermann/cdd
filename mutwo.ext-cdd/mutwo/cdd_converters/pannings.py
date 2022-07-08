import collections

import numpy as np

from mutwo import cdd_parameters
from mutwo import common_generators
from mutwo import core_converters
from mutwo import core_events
from mutwo import core_generators
from mutwo import core_utilities


__all__ = ("AbsolutePositionToPanning",)


class AbsolutePositionToPanning(core_converters.abc.Converter):
    CHANNEL_COUNT = 5

    def __init__(self):
        self.channel_count_dynamic_choice = core_generators.DynamicChoice(
            [1, 2, 3, 4],
            [
                core_events.Envelope([[0, 0.5]]),
                core_events.Envelope([[0, 1]]),
                core_events.Envelope([[0, 0.75]]),
                core_events.Envelope([[0, 0.3]]),
            ],
        )
        self.channel_counter = collections.Counter(
            {index: 0 for index in range(self.CHANNEL_COUNT)}
        )

        self.random = np.random.default_rng(seed=100)

    def convert(self, absolute_position: float) -> cdd_parameters.Panning:
        start_movement_duration = 0.1

        if absolute_position < start_movement_duration:
            value0, value1 = core_utilities.scale(
                absolute_position, 0, start_movement_duration, 0, 1
            ), core_utilities.scale(absolute_position, 0, start_movement_duration, 1, 0)
            return cdd_parameters.Panning([0, 0, 0, value0, value1]).normalize()

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
