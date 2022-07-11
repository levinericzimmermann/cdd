from __future__ import annotations

import functools

from mutwo import core_utilities

__all__ = ("Panning",)


class Panning(tuple[float]):
    """Each element represents the amplitude on the respective channel"""

    @functools.cached_property
    def channel_count(self) -> int:
        return len(self)

    @functools.cached_property
    def active_panning_index_tuple(self) -> tuple[int, ...]:
        return tuple(index for index, value in enumerate(self) if value > 0)

    @functools.cached_property
    def active_panning_value_tuple(self) -> tuple[float, ...]:
        return tuple(self[index] for index in self.active_panning_index_tuple)

    @functools.cached_property
    def active_channel_count(self) -> int:
        return len(self.active_panning_index_tuple)

    def normalize(self) -> Panning:
        return type(self)(core_utilities.scale_sequence_to_sum(self, 1))

    def split_to(self, channel_count: int) -> tuple[Panning, ...]:
        normalized_panning = list(self.normalize())
        value = sum(normalized_panning) / channel_count
        panning_list = []
        for _ in range(channel_count):
            remaining_value = float(value)
            new_panning: list[float] = [0 for _ in normalized_panning]
            for channel_index, channel_value in enumerate(normalized_panning):
                to_remove = min((remaining_value, channel_value))

                new_panning[channel_index] += to_remove

                remaining_value -= to_remove
                normalized_panning[channel_index] -= to_remove

            panning_list.append(Panning(new_panning))

        return tuple(panning_list)
