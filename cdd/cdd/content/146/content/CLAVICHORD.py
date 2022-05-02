# We have a scale with pitches we can use

# We want to have a varying density throughout the composition

# The materials to use are:

#   Chords
#       /w Grace notes
#   Arpeggi
#   Single Tones
#   Spoken Words

#   Vary ambitus, vary pitches, vary durations, vary voicing


# Chords
#   - shouldn't be too tonal (not only minor/major chord)
#   - should embrace vibrations, but no minor seconds, better use seventh
#   - should avoid repeating pitches between two sequential chords
#   - well..when moving, maybe we could use feldmans rule:
#     only seconds (or sevenths) are allowed when moving

# It is necessary to have a certain set of repeating
# detectable motives which can appear multiple times
# at the "sonho" parts of the singing.

import collections
import copy
import functools
import itertools
import operator
import math

import numpy as np
import ranges
import quicktions as fractions

from mutwo import common_generators
from mutwo import core_converters
from mutwo import core_events
from mutwo import core_utilities
from mutwo import music_events
from mutwo import music_parameters

from cdd import configurations
from cdd import constants
from cdd import utilities

from . import SOPRANO


ClavichordLine = core_events.SimultaneousEvent[core_events.SequentialEvent]


class DataToClavichordLine(core_converters.abc.Converter):
    diatonic_pitch_class_tuple = tuple(
        music_parameters.JustIntonationPitch(ratio)
        for ratio in ("1/1 8/7 7/6 4/3 3/2 14/9 7/4 27/14").split(" ")
    )

    chromatic_pitch_class_tuple = tuple(
        music_parameters.JustIntonationPitch(ratio)
        for ratio in ("28/27 112/81 12/7 9/7").split(" ")
    )

    pitch_class_tuple = tuple(
        sorted(diatonic_pitch_class_tuple + chromatic_pitch_class_tuple)
    )

    prohibited_pitch_class_combination_tuple = (
        # no simple minor chord
        [
            music_parameters.JustIntonationPitch(ratio)
            for ratio in "1/1 7/6 3/2".split(" ")
        ],
        # no simple major chord
        [
            music_parameters.JustIntonationPitch(ratio)
            for ratio in "1/1 7/6 14/9".split(" ")
        ],
    )

    # feldmans rule: max movement between two sequencing pitches
    # (can be registered)
    maximum_interval_deviation = 220  # cents
    inverse_maximum_interval_deviation = 1200 - maximum_interval_deviation

    # Weight dictionaries
    pitch_count_to_weight_dict = {1: 2.5, 2: 2, 3: 1.5, 4: 1, 5: 1, 6: 1.5, 7: 2, 8: 3}
    block_size_to_weight_dict = {1: 2, 2: 0.95, 3: 1, 4: 1.55, 5: 1.75, 6: 2}

    def __init__(
        self,
        block_size_range: ranges.Range = ranges.Range(1, 4),
        line_duration: fractions.Fraction = fractions.Fraction(8, 1),
        grid_size: fractions.Fraction = fractions.Fraction(1, 16),
        seed: int = 987654321,
    ):
        self._block_size_range = block_size_range
        self._line_duration = line_duration
        self._grid_size = grid_size
        self._grid_count = line_duration / grid_size

        self._last_chord_duration_is_longest_cycle = itertools.cycle((0, 1))

        # Counters for balanced results
        self._exponent_tuple_counter = collections.Counter()
        self._octave_counter = collections.Counter()
        self._block_size_counter = collections.Counter(
            {
                block_size: 0
                for block_size in range(block_size_range.start, block_size_range.end)
            }
        )
        self._pitch_count_counter = collections.Counter()
        self._chord_duration_counter = collections.Counter()

        self._random = np.random.default_rng(seed=seed)

        self.exponent_tuple_to_allowed_neighbours = {
            pitch0.exponent_tuple: [
                pitch1
                for pitch1 in self.pitch_class_tuple
                if (
                    abs((pitch0 - pitch1).interval) < self.maximum_interval_deviation
                    or abs((pitch0 - pitch1).interval)
                    > self.inverse_maximum_interval_deviation
                )
                and pitch1 != pitch0
            ]
            for pitch0 in self.pitch_class_tuple
        }

        pitch_list = []
        for pitch_class in self.pitch_class_tuple:
            pitch_list.extend(
                constants.CLAVICHORD_AMBITUS.get_pitch_variant_tuple(pitch_class)
            )

        self.pitch_tuple = tuple(pitch_list)

        self.exponent_tuple_to_normalized_pitch = {
            pitch.exponent_tuple: pitch.normalize(mutate=False)
            for pitch in self.pitch_tuple
        }

        self.exponent_tuple_tuple_to_pitch_interval = {
            tuple(pitch.exponent_tuple for pitch in sorted([pitch0, pitch1])): abs(
                pitch0 - pitch1
            )
            for pitch0, pitch1 in itertools.combinations_with_replacement(
                self.pitch_tuple, 2
            )
        }

        self.exponent_tuple_tuple_to_pitch_interval.update(
            {
                tuple(reversed(exponent_tuple_tuple)): pitch_interval
                for exponent_tuple_tuple, pitch_interval in self.exponent_tuple_tuple_to_pitch_interval.items()
            }
        )

        self.exponent_tuple_tuple_to_pitch_interal_category = {
            exponent_tuple_tuple: abs(pitch_interval.interval) < 250
            for exponent_tuple_tuple, pitch_interval in self.exponent_tuple_tuple_to_pitch_interval.items()
        }

        self.exponent_tuple_to_octave = {
            pitch.exponent_tuple: pitch.octave for pitch in self.pitch_tuple
        }

    def _get_event_count_per_block(self, event_count: int) -> tuple[int, ...]:
        event_count_tuple_solution_tuple = core_utilities.find_numbers_which_sums_up_to(
            event_count,
            tuple(range(self._block_size_range.start, self._block_size_range.end)),
        )
        fitness_list = []
        for event_count_tuple in event_count_tuple_solution_tuple:
            fitness = np.average(
                [
                    self._block_size_counter[block_size]
                    for block_size in event_count_tuple
                ]
            )
            fitness_list.append(fitness)
        min_fitness = min(fitness_list)
        event_count_tuple_solution_tuple = sorted(
            [
                event_count_tuple
                for fitness, event_count_tuple in zip(
                    fitness_list, event_count_tuple_solution_tuple
                )
                if fitness == min_fitness
            ],
            key=lambda event_count_tuple: len(event_count_tuple),
            reverse=True,
        )
        champion = list(event_count_tuple_solution_tuple[0])
        for block_size in champion:
            weight = self.block_size_to_weight_dict.get(block_size, 1)
            self._block_size_counter.update({block_size: weight})

        # Finally we have to change the champions order.
        # Random is okay here, because I only want to avoid expectable
        # solutions (e.g. something like (1, 2, 2, 3, 4)), I want to
        # have a certain level of noise here.
        self._random.shuffle(champion)
        return tuple(champion)

    def _distribute_block_and_rest_duration(
        self,
        event_count_tuple: tuple[int, ...],
        density: float,
        add_rest_after_last_block: bool,
    ):
        # We need at least a little bit of rest and at least a little
        # bit of content (if we have an event_count_tuple).
        assert (not event_count_tuple or density > 0) and density <= 1

        block_count = len(event_count_tuple)

        rest_count = block_count - (not add_rest_after_last_block)
        rest_duration_percentage = (1 - density) / rest_count
        rest_duration = (
            int(rest_duration_percentage * self._grid_count) * self._grid_size
        )

        block_duration_percentage = density / block_count
        block_duration = (
            int(block_duration_percentage * self._grid_count) * self._grid_size
        )

        block_duration_tuple = tuple(block_duration for _ in range(block_count))
        rest_duration_tuple = tuple(rest_duration for _ in range(rest_count))

        return block_duration_tuple, rest_duration_tuple

    def _get_unsorted_pitch_count_tuple(
        self, event_count: int, pitch_count_range: ranges.Range
    ) -> tuple[int, ...]:
        pitch_count_tuple = tuple(pitch_count_range.start for _ in range(event_count))
        fitness = float("inf")
        for pitch_count_tuple_candidate in itertools.combinations_with_replacement(
            tuple(range(pitch_count_range.start, pitch_count_range.end)), event_count
        ):
            fitness_candidate = np.average(
                [
                    self._pitch_count_counter[pitch_count]
                    for pitch_count in pitch_count_tuple_candidate
                ]
            )
            if fitness_candidate < fitness:
                pitch_count_tuple = pitch_count_tuple_candidate
                fitness = fitness_candidate
            elif fitness_candidate == fitness:
                if len(set(pitch_count_tuple_candidate)) > len(set(pitch_count_tuple)):
                    pitch_count_tuple = pitch_count_tuple_candidate
        for pitch_count in pitch_count_tuple:
            self._pitch_count_counter.update(
                {pitch_count: self.pitch_count_to_weight_dict.get(pitch_count, 1)}
            )
        return pitch_count_tuple

    def _get_allowed_chord_duration_tuple(
        self, chord_rhythm_range: ranges.Range
    ) -> tuple[fractions.Fraction, ...]:
        grid_count = 1
        allowed_chord_duration_list = []
        while True:
            duration = self._grid_size * grid_count
            if duration > chord_rhythm_range.end:
                break
            if duration > chord_rhythm_range.start:
                allowed_chord_duration_list.append(duration)
            grid_count += 1
        return tuple(allowed_chord_duration_list)

    def _get_chord_duration_tuple(
        self,
        event_count: int,
        block_duration: fractions.Fraction,
        allowed_chord_duration_tuple: tuple[fractions.Fraction, ...],
        last_chord_duration_is_longest: bool,
    ) -> tuple[fractions.Fraction, ...]:
        solution_list = []
        difference = float("inf")
        for chord_duration_tuple in itertools.combinations_with_replacement(
            allowed_chord_duration_tuple, event_count
        ):
            duration = sum(chord_duration_tuple)
            candidate_difference = abs(duration - block_duration)
            if candidate_difference < difference:
                difference = candidate_difference
                solution_list = [chord_duration_tuple]
            elif candidate_difference == difference:
                solution_list.append([chord_duration_tuple])
        fitness = float("inf")
        champion = tuple([])
        for candidate in solution_list:
            fitness_candidate = np.average(
                [self._chord_duration_counter[duration] for duration in candidate]
            )
            if fitness_candidate < fitness:
                champion = candidate
                fitness = fitness_candidate
            elif fitness_candidate == fitness:
                if len(set(candidate)) > len(set(champion)):
                    champion = candidate
        chord_duration_tuple = utilities.interlock_long_and_short(champion)
        if last_chord_duration_is_longest:
            chord_duration_tuple = tuple(reversed(chord_duration_tuple))
        return chord_duration_tuple

    def _get_chord_duration_tuple_per_block(
        self,
        chord_rhythm_range: ranges.Range,
        block_duration_tuple: tuple[fractions.Fraction, ...],
        event_count_tuple: tuple[int, ...],
    ):
        allowed_chord_duration_tuple = self._get_allowed_chord_duration_tuple(
            chord_rhythm_range
        )
        index, block_count = 1, len(block_duration_tuple)
        chord_duration_tuple_per_block = []
        for block_duration, block_event_count in zip(
            block_duration_tuple, event_count_tuple
        ):
            if index == 1:  # is first
                last_chord_duration_is_longest = False
            elif index == block_count:  # is last
                last_chord_duration_is_longest = True
            else:
                last_chord_duration_is_longest = next(
                    self._last_chord_duration_is_longest_cycle
                )
            chord_duration_tuple = self._get_chord_duration_tuple(
                block_event_count,
                block_duration,
                allowed_chord_duration_tuple,
                last_chord_duration_is_longest,
            )
            chord_duration_tuple_per_block.append(chord_duration_tuple)
            index += 1
        return tuple(chord_duration_tuple_per_block)

    def _get_pitch_count_tuple_per_block(
        self,
        chord_duration_tuple_per_block: tuple[tuple[fractions.Fraction, ...], ...],
        event_count: int,
        pitch_count_range: ranges.Range,
    ) -> tuple[tuple[int, ...], ...]:
        pitch_count_tuple = sorted(
            self._get_unsorted_pitch_count_tuple(event_count, pitch_count_range)
        )
        # now we'll map duration on pitch count: longer chords will get more pitches
        chord_duration_tuple = sorted(
            functools.reduce(operator.add, chord_duration_tuple_per_block)
        )
        chord_duration_to_pitch_count_list = {}
        for pitch_count, chord_duration in zip(pitch_count_tuple, chord_duration_tuple):
            if chord_duration not in chord_duration_to_pitch_count_list:
                chord_duration_to_pitch_count_list.update({chord_duration: []})
            chord_duration_to_pitch_count_list[chord_duration].append(pitch_count)
        for pitch_count_list in chord_duration_to_pitch_count_list.values():
            self._random.shuffle(pitch_count_list)
        chord_duration_to_pitch_count_iterator = {
            chord_duration: iter(pitch_count_list)
            for chord_duration, pitch_count_list in chord_duration_to_pitch_count_list.items()
        }
        pitch_count_tuple_per_block = []
        for chord_duration_tuple in chord_duration_tuple_per_block:
            pitch_count_list = []
            for chord_duration in chord_duration_tuple:
                pitch_count = next(
                    chord_duration_to_pitch_count_iterator[chord_duration]
                )
                pitch_count_list.append(pitch_count)
            pitch_count_tuple_per_block.append(tuple(pitch_count_list))
        return pitch_count_tuple_per_block

    def _get_allowed_pitch_tuple(
        self,
        last_pitch_list: list[music_parameters.JustIntonationPitch],
        ambitus: music_parameters.OctaveAmbitus,
    ):
        previous_pitch_class_list = core_utilities.uniqify_sequence(
            [
                self.exponent_tuple_to_normalized_pitch[pitch.exponent_tuple]
                for pitch in last_pitch_list
            ]
        )

        pitch_class_neighbour_list = []

        allowed_pitch_list = []
        for previous_pitch_class in previous_pitch_class_list:
            neighbour_pitch_class_tuple = self.exponent_tuple_to_allowed_neighbours[
                previous_pitch_class.exponent_tuple
            ]
            for neighbour_pitch_class in neighbour_pitch_class_tuple:
                if (
                    neighbour_pitch_class not in previous_pitch_class_list
                    and neighbour_pitch_class not in pitch_class_neighbour_list
                ):
                    pitch_class_neighbour_list.append(neighbour_pitch_class)
                    allowed_pitch_list.extend(
                        ambitus.get_pitch_variant_tuple(neighbour_pitch_class)
                    )

        return tuple(allowed_pitch_list)

    def _is_pitch_list_playable(
        self, pitch_list: list[music_parameters.JustIntonationPitch]
    ) -> bool:
        # e.g. are two hands enough to catch all pitches
        return True

    def _get_pitch_list_fitness(
        self, pitch_list: list[music_parameters.JustIntonationPitch]
    ) -> float:
        # SHOULD BE PLAYABLE
        if not self._is_pitch_list_playable(pitch_list):
            return float("inf")

        pitch_class_tuple = tuple(
            self.exponent_tuple_to_normalized_pitch[pitch.exponent_tuple]
            for pitch in pitch_list
        )

        # PREFER NOT OFTEN USED PITCH CLASSES
        fitness = np.average(
            [
                self._exponent_tuple_counter[pitch_class.exponent_tuple]
                for pitch_class in pitch_class_tuple
            ]
        )

        # PREFER NOT OFTEN USED OCTAVES
        fitness += np.average(
            [
                self._octave_counter[
                    self.exponent_tuple_to_octave[pitch.exponent_tuple]
                ]
                for pitch in pitch_list
            ]
        )

        # AVOID TOO MANY CHROMATIC PITCHES

        # AVOID SECONDS
        interval_category_tuple = tuple(
            self.exponent_tuple_tuple_to_pitch_interal_category[
                tuple(pitch.exponent_tuple for pitch in [pitch0, pitch1])
            ]
            for pitch0, pitch1 in itertools.combinations(pitch_list, 2)
        )
        if any(interval_category_tuple):
            fitness += 100

        # AVOID ONLY OCTAVES
        pitch_class_count = len(core_utilities.uniqify_sequence(pitch_class_tuple))
        if pitch_class_count < len(pitch_list) * 0.7:
            fitness += 1000

        return fitness

    def _get_pitch_list(
        self,
        pitch_count: int,
        ambitus: music_parameters.OctaveAmbitus,
        last_pitch_list: list[music_parameters.JustIntonationPitch],
    ) -> list[music_parameters.JustIntonationPitch]:
        allowed_pitch_tuple = self._get_allowed_pitch_tuple(last_pitch_list, ambitus)
        if len(allowed_pitch_tuple) <= pitch_count:
            return list(allowed_pitch_tuple)
        pitch_list = []
        fitness = float("inf")
        for pitch_list_candidate in itertools.combinations(
            allowed_pitch_tuple, pitch_count
        ):
            fitness_candidate = self._get_pitch_list_fitness(pitch_list_candidate)
            if fitness_candidate < fitness:
                fitness = fitness_candidate
                pitch_list = pitch_list_candidate
        return list(sorted(pitch_list))

    def _get_pitch_list_tuple(
        self,
        pitch_count_tuple: tuple[int, ...],
        ambitus: music_parameters.OctaveAmbitus,
        last_pitch_list: list[music_parameters.JustIntonationPitch],
    ) -> tuple[list[music_parameters.JustIntonationPitch], ...]:
        pitch_list_list = []
        for pitch_count in pitch_count_tuple:
            pitch_list = self._get_pitch_list(pitch_count, ambitus, last_pitch_list)
            print(pitch_list)
            for pitch in pitch_list:
                self._exponent_tuple_counter.update(
                    {
                        self.exponent_tuple_to_normalized_pitch[
                            pitch.exponent_tuple
                        ].exponent_tuple: 1
                    }
                )
                self._octave_counter.update(
                    {self.exponent_tuple_to_octave[pitch.exponent_tuple]: 1}
                )
            if pitch_list:
                last_pitch_list = pitch_list
            pitch_list_list.append(last_pitch_list)
        return tuple(pitch_list_list)

    def _get_pitch_list_tuple_per_block(
        self,
        chord_duration_tuple_per_block: tuple[tuple[fractions.Fraction, ...], ...],
        event_count: int,
        ambitus: music_parameters.OctaveAmbitus,
        last_pitch_list: list[music_parameters.JustIntonationPitch],
        pitch_count_range: ranges.Range,
    ) -> tuple[tuple[list[music_parameters.JustIntonationPitch], ...], ...]:
        pitch_count_tuple_per_block = self._get_pitch_count_tuple_per_block(
            chord_duration_tuple_per_block, event_count, pitch_count_range
        )
        pitch_list_tuple_per_block = []
        for pitch_count_tuple in pitch_count_tuple_per_block:
            pitch_list_tuple = self._get_pitch_list_tuple(
                pitch_count_tuple, ambitus, last_pitch_list
            )
            if pitch_list_tuple:
                last_pitch_list = pitch_list_tuple[-1]
            pitch_list_tuple_per_block.append(pitch_list_tuple)
        return tuple(pitch_list_tuple_per_block)

    def _get_block_content_tuple(
        self,
        event_count: int,
        event_count_tuple: tuple[int, ...],
        block_duration_tuple: tuple[fractions.Fraction, ...],
        ambitus: music_parameters.OctaveAmbitus,
        last_pitch_list: list[music_parameters.JustIntonationPitch],
        chord_rhythm_range: ranges.Range,
        pitch_count_range: ranges.Range,
    ):
        chord_duration_tuple_per_block = self._get_chord_duration_tuple_per_block(
            chord_rhythm_range, block_duration_tuple, event_count_tuple
        )
        pitch_list_tuple_per_block = self._get_pitch_list_tuple_per_block(
            chord_duration_tuple_per_block,
            event_count,
            ambitus,
            last_pitch_list,
            pitch_count_range,
        )
        block_content_list = []
        for chord_duration_tuple, pitch_list_tuple in zip(
            chord_duration_tuple_per_block, pitch_list_tuple_per_block
        ):
            sequential_event = core_events.SequentialEvent([])
            for chord_duration, pitch_list in zip(
                chord_duration_tuple, pitch_list_tuple
            ):
                note_like = music_events.NoteLike(
                    pitch_list=pitch_list, duration=chord_duration
                )
                sequential_event.append(note_like)
            block_content_list.append(sequential_event)
        return tuple(block_content_list)

    def convert(
        self,
        density: float = 0.5,
        event_count: int = 7,
        ambitus: music_parameters.OctaveAmbitus = constants.CLAVICHORD_AMBITUS,
        last_pitch_list: list[music_parameters.JustIntonationPitch] = [
            music_parameters.JustIntonationPitch("1/1"),
            music_parameters.JustIntonationPitch("7/12"),
            music_parameters.JustIntonationPitch("3/4"),
        ],
        chord_rhythm_range: ranges.Range = ranges.Range(
            fractions.Fraction(1, 4), fractions.Fraction(2, 1)
        ),
        pitch_count_range: ranges.Range = ranges.Range(2, 5),
        add_rest_after_last_block: bool = True,
    ):
        if not event_count:
            return core_events.SequentialEvent(
                [core_events.SimpleEvent(fractions.Fraction(1, 1))]
            )
        event_count_tuple = self._get_event_count_per_block(event_count)
        (
            block_duration_tuple,
            rest_duration_tuple,
        ) = self._distribute_block_and_rest_duration(
            event_count_tuple, density, add_rest_after_last_block
        )
        block_content_tuple = self._get_block_content_tuple(
            event_count,
            event_count_tuple,
            block_duration_tuple,
            ambitus,
            last_pitch_list,
            chord_rhythm_range,
            pitch_count_range,
        )
        clavichord_line = core_events.SequentialEvent([])
        for block_content, rest_duration in zip(
            block_content_tuple, rest_duration_tuple
        ):
            clavichord_line.extend(block_content)
            if rest_duration:
                clavichord_line.append(
                    music_events.NoteLike(pitch_list=[], duration=rest_duration)
                )
        return clavichord_line


def _apply_arpeggi(
    sequential_event_tuple: tuple[core_events.SequentialEvent, ...], activity: int
):
    direction = itertools.cycle((True, False, False, True, False, True, True, False))
    activity_level = common_generators.ActivityLevel()
    for sequential_event in sequential_event_tuple:
        for note_like_or_simple_event in sequential_event:
            if (
                hasattr(note_like_or_simple_event, "playing_indicator_collection")
                and len(note_like_or_simple_event.pitch_list) > 1
                and min(note_like_or_simple_event.pitch_list)
                .get_pitch_interval(max(note_like_or_simple_event.pitch_list))
                .interval
                > 500
            ):
                if activity_level(activity):
                    note_like_or_simple_event.playing_indicator_collection.arpeggio.direction = (
                        "down",
                        "up",
                    )[
                        next(direction)
                    ]


class GraceNoteSequentialEventAdder(object):
    INSIDE, OUTSIDE, BALANCED = "inside outside balanced".split(" ")

    def __init__(self):
        self.grace_note_type_counter = collections.Counter(
            {self.INSIDE: 0, self.OUTSIDE: 0, self.BALANCED: 0}
        )

    def _get_neighbour_pitch(
        self, pitch: music_parameters.JustIntonationPitch, is_higher: bool
    ) -> music_parameters.JustIntonationPitch:
        pitch_index = constants.CLAVICHORD_PITCH_TUPLE.index(pitch)
        new_index = pitch_index + (-1, 1)[is_higher]
        if new_index < 0:
            new_index = 0
        try:
            return constants.CLAVICHORD_PITCH_TUPLE[new_index]
        except IndexError:
            return pitch

    def _get_neighbour_pitch_list(
        self,
        pitch_list: list[music_parameters.JustIntonationPitch],
        is_higher_tuple: tuple[bool, bool],
    ):
        try:
            low_pitch, high_pitch = pitch_list[0], pitch_list[-1]
        except IndexError:
            low_pitch, high_pitch = None, pitch_list[0]

        return [
            self._get_neighbour_pitch(pitch, is_higher)
            for pitch, is_higher in (
                (low_pitch, is_higher_tuple[0]),
                (high_pitch, is_higher_tuple[1]),
            )
            if pitch
        ]

    def get_inside_pitch_list(
        self, pitch_list: list[music_parameters.JustIntonationPitch]
    ) -> list[music_parameters.JustIntonationPitch]:
        return self._get_neighbour_pitch_list(pitch_list, (True, False))

    def get_outside_pitch_list(
        self, pitch_list: list[music_parameters.JustIntonationPitch]
    ) -> list[music_parameters.JustIntonationPitch]:
        return self._get_neighbour_pitch_list(pitch_list, (False, True))

    def get_balanced_pitch_list(
        self, pitch_list: list[music_parameters.JustIntonationPitch]
    ) -> list[music_parameters.JustIntonationPitch]:
        return [pitch_list[int(len(pitch_list) // 2)]]

    def __call__(
        self,
        note_like: music_events.NoteLike,
        previous_pitch_list: list[music_parameters.JustIntonationPitch],
    ):
        pitch_list = sorted(note_like.pitch_list)
        type_to_pitch_list = {
            self.INSIDE: self.get_inside_pitch_list(pitch_list),
            self.OUTSIDE: self.get_outside_pitch_list(pitch_list),
            self.BALANCED: self.get_balanced_pitch_list(pitch_list),
        }

        # Avoid grace notes which have pitches that already appeared in
        # previous chord
        to_remove_list = []
        for grace_note_type, grace_note_pitch_list in type_to_pitch_list.items():
            if (
                any([pitch in previous_pitch_list for pitch in grace_note_pitch_list])
                or grace_note_pitch_list == pitch_list
            ):
                to_remove_list.append(grace_note_type)
        for to_remove in to_remove_list:
            del type_to_pitch_list[to_remove]

        if type_to_pitch_list:
            fitness = float("inf")
            for grace_note_type, pitch_list in type_to_pitch_list.items():
                local_fitness = self.grace_note_type_counter[grace_note_type]
                if local_fitness < fitness:
                    fitness = local_fitness
                    champion = pitch_list

            grace_note_sequential_event = core_events.SequentialEvent(
                [music_events.NoteLike(champion, fractions.Fraction(1, 8))]
            )
            note_like.grace_note_sequential_event = grace_note_sequential_event


def _apply_grace_notes(
    sequential_event_tuple: tuple[core_events.SequentialEvent, ...],
    grace_note_likelihood_envelope: core_events.Envelope,
):
    add_grace_note_sequential_event_to_note_like = GraceNoteSequentialEventAdder()
    random = np.random.default_rng(seed=3212321)
    simple_event_count = sum(
        len(sequential_event) for sequential_event in sequential_event_tuple
    )
    index = 0
    previous_pitch_list = []
    is_previous_event_rest = True
    for sequential_event in sequential_event_tuple:
        for note_like_or_simple_event in sequential_event:
            likelihood = grace_note_likelihood_envelope.value_at(
                index / simple_event_count
            )
            if is_previous_event_rest:
                likelihood *= 0.6
            if (
                hasattr(note_like_or_simple_event, "pitch_list")
                and (pitch_list := note_like_or_simple_event.pitch_list)
                and len(pitch_list) > 1
            ):
                if random.random() < likelihood:
                    add_grace_note_sequential_event_to_note_like(
                        note_like_or_simple_event, previous_pitch_list
                    )
                is_previous_event_rest = False
                previous_pitch_list = pitch_list
            else:
                is_previous_event_rest = True
            index += 1


@core_utilities.compute_lazy(
    path=f"{configurations.PATH.BUILDS.PICKLED}/146_clavichord.pickle",
    force_to_compute=False,
    # force_to_compute=True,
)
def _get_sequential_event_tuple(line_count: int, _):
    sequential_event_list = []
    data_to_clavichord_line = DataToClavichordLine()
    for line_index in range(line_count):
        line_percentage = line_index / line_count
        kwargs = {
            attribute: ATTRIBUTE_TO_ENVELOPE_DICT[attribute].value_at(line_percentage)
            for attribute in "event_count density".split(" ")
        }
        kwargs["event_count"] = int(kwargs["event_count"])
        kwargs.update(
            {
                "pitch_count_range": ranges.Range(
                    *[
                        int(
                            ATTRIBUTE_TO_ENVELOPE_DICT[attribute].value_at(
                                line_percentage
                            )
                        )
                        for attribute in ("pitch_count_minima", "pitch_count_maxima")
                    ]
                )
            }
        )
        kwargs.update(
            {
                "ambitus": music_parameters.OctaveAmbitus(
                    *[
                        constants.CLAVICHORD_PITCH_TUPLE[
                            int(
                                core_utilities.scale(
                                    ATTRIBUTE_TO_ENVELOPE_DICT[attribute].value_at(
                                        line_percentage
                                    ),
                                    0,
                                    1,
                                    0,
                                    len(constants.CLAVICHORD_PITCH_TUPLE) - 1,
                                )
                            )
                        ]
                        for attribute in (
                            "ambitus_low_percentage",
                            "ambitus_high_percentage",
                        )
                    ]
                )
            }
        )
        try:
            last_pitch_list = list(
                filter(bool, sequential_event_list[-1].get_parameter("pitch_list"))
            )[-1]
        except Exception:
            last_pitch_list = [
                music_parameters.JustIntonationPitch("1/1"),
                music_parameters.JustIntonationPitch("7/12"),
                music_parameters.JustIntonationPitch("3/4"),
            ]
        sequential_event = data_to_clavichord_line.convert(
            last_pitch_list=last_pitch_list, **kwargs
        )
        sequential_event_list.append(sequential_event)
    return tuple(sequential_event_list)


ATTRIBUTE_TO_ENVELOPE_DICT = {
    "event_count": core_events.Envelope(
        [
            [0, 7],
            [0.1, 6],
            [0.2, 2],
            [0.25, 0],
            [0.3, 0],
            [0.34, 5],
            [0.4, 4],
            [0.43, 19],
            [0.5, 0],
            [0.57, 0],
            [0.63, 0],
            [0.67, 3],
            [0.75, 4],
            [0.79, 6],
            [0.83, 0],
            [1, 0],
        ]
    ),
    "density": core_events.Envelope(
        [
            [0, 1],
            [0.2, 0.55],
            [0.34, 0.65],
            [0.5, 0.4],
            [0.5, 0.7],
            [0.6, 0.9],
            [1, 0.8],
        ]
    ),
    # where 1 equals highest pitch and 0 equals lowest pitch
    "ambitus_high_percentage": core_events.Envelope(
        [
            [0, 0.7],
            [0.4, 0.55],
            [0.5, 0.285],
            [0.6, 0.8],
            [0.65, 0.8],
            [0.66, 1],
            [1, 1],
        ]
    ),
    "ambitus_low_percentage": core_events.Envelope(
        [[0, 0.1], [0.4, 0], [0.6, 0.1], [0.65, 0.4], [0.66, 0], [0.7, 0], [1, 0]]
    ),
    # pitch count min // max
    "pitch_count_maxima": core_events.Envelope(
        [
            [0, 6],
            [0.1, 5],
            [0.2, 4],
            [0.3, 7],
            [0.4, 7],
            [0.55, 3],
            [0.6, 3],
            [0.7, 7],
            [1, 3],
        ]
    ),
    "pitch_count_minima": core_events.Envelope(
        [[0, 2], [0.2, 2], [0.3, 3], [0.4, 2], [0.5, 1], [0.6, 1], [0.7, 3], [1, 1]]
    ),
}

grace_note_likelihood_envelope = core_events.Envelope(
    [[0, 0.5], [0.3, 0.45], [0.38, 0.4], [0.43, 0.1], [0.5, 0.3], [0.7, 0.5], [1, 0.4]]
)

line_duration = 45

line_count = math.ceil(SOPRANO.duration / line_duration)

sequential_event_tuple = _get_sequential_event_tuple(line_count, constants.CLAVICHORD_AMBITUS)

sequential_event_tuple[0][2].duration *= fractions.Fraction(3, 2)
sequential_event_tuple[0][3].duration *= fractions.Fraction(1, 2)
sequential_event_tuple[0][4].duration *= fractions.Fraction(1, 2)
sequential_event_tuple[0][5].duration *= fractions.Fraction(3, 2)

sequential_event_tuple[1][1].pitch_list = []
sequential_event_tuple[1][1].grace_note_sequential_event = core_events.SequentialEvent(
    []
)
# sequential_event_tuple[1][6].pitch_list = []
# sequential_event_tuple[1][6].pitch_list = []
sequential_event_tuple[1][7].pitch_list = []


sequential_event_tuple[5][4].pitch_list = []
sequential_event_tuple[5][14].duration += sequential_event_tuple[5][15].duration
del sequential_event_tuple[5][15]

offset = 0
for event in sequential_event_tuple[5][12:15]:
    sequential_event_tuple[6].squash_in(offset, copy.deepcopy(event))
    offset += event.duration
    event.pitch_list = []

sequential_event_tuple[6].append(core_events.SimpleEvent(fractions.Fraction(4, 1)))


arpeggio_activity = 3

_apply_arpeggi(sequential_event_tuple, arpeggio_activity)
_apply_grace_notes(sequential_event_tuple, grace_note_likelihood_envelope)

sequential_event_absolute_time_tuple = tuple(
    core_utilities.accumulate_from_zero([line_duration for _ in range(line_count)])
)

add_word_likelihood_envelope = core_events.Envelope(
    [[0, 0], [0.3, 0], [0.6, 0.35], [0.7, 0.35], [0.8, 0], [1, 0]]
)

instruction_text = f"""
one line = {line_duration} seconds (use a stop watch).
space in notation = time in music.
"""
# removed following text (because too verbose):
# rhythmic notation is proportional (space in notation = time in music).

del SOPRANO
