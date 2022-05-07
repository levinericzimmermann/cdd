import dataclasses
import functools
import itertools
import operator
import typing

import abjad
import expenvelope
import quicktions as fractions
import numpy as np
import ranges

from mutwo import core_parameters
from mutwo import core_utilities

from cdd import utilities

from . import configurations
from . import constants


def get_tempo_change_bar_count_tuple_tuple_from_factor_tuple(
    factor_tuple: tuple[int, ...]
) -> tuple[tuple[int, ...], ...]:
    tempo_change_loop_bar_count_list = []
    combination_maxima = 1
    is_too_high = False
    while not is_too_high:
        for combination in itertools.combinations_with_replacement(
            factor_tuple, combination_maxima
        ):
            product = functools.reduce(operator.mul, combination)
            is_too_high = product > configurations.TEMPO_CHANGE_LOOP_BAR_COUNT_RANGE.end
            if is_too_high:
                break
            if (
                product in configurations.TEMPO_CHANGE_LOOP_BAR_COUNT_RANGE
                and product not in tempo_change_loop_bar_count_list
            ):
                tempo_change_loop_bar_count_list.append(product)
        combination_maxima += 1

    tempo_change_bar_count_tuple_list = []
    for tempo_change_loop_bar_count in tempo_change_loop_bar_count_list:
        local_tempo_change_bar_count_tuple_tuple = (
            core_utilities.find_numbers_which_sums_up_to(
                tempo_change_loop_bar_count,
                range(
                    configurations.TEMPO_CHANGE_BAR_COUNT_RANGE.start,
                    configurations.TEMPO_CHANGE_BAR_COUNT_RANGE.end + 1,
                ),
            )
        )
        tempo_change_bar_count_tuple_list.extend(
            local_tempo_change_bar_count_tuple_tuple
        )

    return tuple(tempo_change_bar_count_tuple_list)


def get_tempo_change_bar_count_tuple_tuple(
    time_signature_sequence: tuple[abjad.TimeSignature, ...]
) -> tuple[int, ...]:
    time_signature_count = len(time_signature_sequence)
    factor_tuple = []
    tempo_change_bar_count_tuple_tuple = tuple([])
    while not tempo_change_bar_count_tuple_tuple:
        factor_tuple = core_utilities.factorise(time_signature_count)
        tempo_change_bar_count_tuple_tuple = (
            get_tempo_change_bar_count_tuple_tuple_from_factor_tuple(factor_tuple)
        )
        time_signature_count -= 1

    champion = tempo_change_bar_count_tuple_tuple[0]
    fitness = 0
    for candidate in tempo_change_bar_count_tuple_tuple:
        local_fitness = len(set(candidate))
        if local_fitness > fitness:
            champion = candidate
            fitness = local_fitness
    return utilities.interlock_long_and_short(champion)


def get_tempo_point_tuple_tuple() -> tuple[
    tuple[core_parameters.TempoPoint, ...], tuple[core_parameters.TempoPoint, ...]
]:
    tempo_point_tuple_list = []
    index_tuple = utilities.interlock_long_and_short(
        tuple(range(configurations.TEMPO_POINT_COUNT))
    )
    base_tempo = configurations.BASE_TEMPO.absolute_tempo_in_beat_per_minute
    for tempo_range in (
        ranges.Range(constants.MIN_TEMPO, base_tempo),
        ranges.Range(base_tempo, constants.MAX_TEMPO),
    ):
        tempo_point_list = []
        difference = tempo_range.end / tempo_range.start
        for factor in np.linspace(1, difference, configurations.TEMPO_POINT_COUNT):
            beats_per_minute = round(
                (factor * tempo_range.start) / configurations.TEMPO_REFERENCE
            )
            tempo_point = core_parameters.TempoPoint(
                beats_per_minute, reference=configurations.TEMPO_REFERENCE
            )
            tempo_point_list.append(tempo_point)

        tempo_point_list = [tempo_point_list[index] for index in index_tuple]
        tempo_point_tuple_list.append(tuple(tempo_point_list))

    tempo_point_tuple_list[1] = tuple(
        core_utilities.cyclic_permutations(tempo_point_tuple_list[1])
    )[1]

    return tuple(tempo_point_tuple_list)


SLOW = -1
FAST = 1
REPEAT = 0


@dataclasses.dataclass
class TempoPointGenerator(object):
    slow_tempo_cycle: typing.Generator
    fast_tempo_cycle: typing.Generator

    pattern_tuple = (
        (SLOW, FAST),
        (SLOW, REPEAT, FAST),
        (SLOW, FAST, REPEAT),
        (SLOW, REPEAT, FAST, REPEAT),
    )

    last_tempo_point: typing.Optional[core_parameters.TempoPoint] = None

    direction_cycle: typing.Generator = dataclasses.field(init=False)

    def __post_init__(self):
        self.direction_cycle = itertools.cycle(
            functools.reduce(
                operator.add, [self.pattern_tuple[index] for index in (0, 1, 2, 0, 3)]
            )
        )

    def _direction_to_tempo_point(self, direction: int) -> core_parameters.TempoPoint:
        if direction == REPEAT:
            return self.last_tempo_point
        elif direction == SLOW:
            return next(self.slow_tempo_cycle)
        elif direction == FAST:
            return next(self.fast_tempo_cycle)
        else:
            raise Exception(direction)

    def __next__(self) -> core_parameters.TempoPoint:
        direction = next(self.direction_cycle)
        tempo_point = self._direction_to_tempo_point(direction)
        self.last_tempo_point = tempo_point
        assert isinstance(tempo_point, core_parameters.TempoPoint)
        return tempo_point


def make_tempo_envelope(
    time_signature_sequence: tuple[abjad.TimeSignature, ...]
) -> expenvelope.Envelope:
    slower_tempo_point_cycle, faster_tempo_point_cycle = (
        itertools.cycle(tempo_point_tuple)
        for tempo_point_tuple in get_tempo_point_tuple_tuple()
    )
    bar_count_tuple = get_tempo_change_bar_count_tuple_tuple(time_signature_sequence)
    bar_count_cycle = itertools.cycle(bar_count_tuple)

    bar_duration_tuple = tuple(
        fractions.Fraction(time_signature.duration)
        for time_signature in time_signature_sequence
    )

    time_signature_count = len(time_signature_sequence)

    bar_position_list = [0]
    while bar_position_list[-1] < time_signature_count:
        bar_position_list.append(bar_position_list[-1] + next(bar_count_cycle))

    bar_position_list = bar_position_list[:-1]

    absolute_bar_duration_tuple = tuple(
        core_utilities.accumulate_from_zero(bar_duration_tuple)
    )

    tempo_point_generator = TempoPointGenerator(
        slower_tempo_point_cycle, faster_tempo_point_cycle
    )

    point_list = []
    for bar_position in bar_position_list:
        absolute_time = absolute_bar_duration_tuple[bar_position]
        tempo_point = next(tempo_point_generator)
        point_list.append([absolute_time, tempo_point])

    tempo_envelope = expenvelope.Envelope.from_points(*point_list)
    return tempo_envelope
