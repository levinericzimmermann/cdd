"""Patch abjad and abjad_converters to fix various bugs"""

import collections
import numbers
import typing

import abjad

from mutwo import abjad_converters
from mutwo import core_events

__all__ = ("AbjadScoreListToLilyPondFile",)


# Monkey patch abjads LeafMaker '_make_tied_leaf`
# in order to allow not-assignable duration and duration
# with numerator > 1 for forbidden_duration
def LeafMaker__make_tied_leaf(
    class_,
    duration,
    increase_monotonic=None,
    forbidden_duration=None,
    multiplier=None,
    pitches=None,
    tag=None,
    tie_parts=True,
):
    duration = abjad.Duration(duration)

    # ###### MONKEY PATCH ##### #
    # if forbidden_duration is not None:
    #     assert forbidden_duration.is_assignable
    #     assert forbidden_duration.numerator == 1
    # ###### MONKEY PATCH ##### #

    # find preferred numerator of written durations if necessary
    if forbidden_duration is not None and forbidden_duration <= duration:
        denominators = [
            2 * forbidden_duration.denominator,
            duration.denominator,
        ]
        denominator = abjad.math.least_common_multiple(*denominators)
        forbidden_duration = abjad.NonreducedFraction(forbidden_duration)
        forbidden_duration = forbidden_duration.with_denominator(denominator)
        duration = abjad.NonreducedFraction(duration)
        duration = duration.with_denominator(denominator)
        forbidden_numerator = forbidden_duration.numerator
        assert forbidden_numerator % 2 == 0
        preferred_numerator = forbidden_numerator / 2
    # make written duration numerators
    numerators = []
    parts = abjad.math.partition_integer_into_canonic_parts(duration.numerator)
    if forbidden_duration is not None and forbidden_duration <= duration:
        for part in parts:
            if forbidden_numerator <= part:
                better_parts = abjad.LeafMaker._partition_less_than_double(
                    part, preferred_numerator
                )
                numerators.extend(better_parts)
            else:
                numerators.append(part)
    else:
        numerators = parts
    # reverse numerators if necessary
    if increase_monotonic:
        numerators = list(reversed(numerators))
    # make one leaf per written duration
    result = []
    for numerator in numerators:
        written_duration = abjad.Duration(numerator, duration.denominator)
        if pitches is not None:
            arguments = (pitches, written_duration)
        else:
            arguments = (written_duration,)
        result.append(class_(*arguments, multiplier=multiplier, tag=tag))
    result = abjad.Selection(result)
    # tie if required
    if tie_parts and 1 < len(result):
        if not issubclass(class_, (abjad.Rest, abjad.Skip)):
            abjad.tie(result)
    return result


abjad.LeafMaker._make_tied_leaf = LeafMaker__make_tied_leaf


# Monkey patch LeafMakers __call__ method in order to parse
# prohibited durations to tuplets
#
# MAYBE THIS MONKEY PATCH IS USELESS;
# this patch only messes up all tuplets; it seems to be a valid
# decision to skip adjusting tuplets

# def LeafMaker__call__(self, pitches, durations) -> abjad.Selection:
#     """
#     Calls leaf-maker on ``pitches`` and ``durations``.
# 
#     Returns selection.
#     """
#     if isinstance(pitches, str):
#         pitches = pitches.split()
#     if not isinstance(pitches, collections.abc.Iterable):
#         pitches = [pitches]
#     if isinstance(durations, (numbers.Number, tuple)):
#         durations = [durations]
#     nonreduced_fractions = abjad.Sequence(
#         [abjad.NonreducedFraction(_) for _ in durations]
#     )
#     size = max(len(nonreduced_fractions), len(pitches))
#     nonreduced_fractions = nonreduced_fractions.repeat_to_length(size)
#     pitches = abjad.Sequence(pitches).repeat_to_length(size)
#     duration_groups = abjad.Duration._group_by_implied_prolation(nonreduced_fractions)
#     result: typing.List[typing.Union[abjad.Tuplet, abjad.Leaf]] = []
#     for duration_group in duration_groups:
#         # get factors in denominator of duration group other than 1, 2.
#         factors_ = abjad.math.factors(duration_group[0].denominator)
#         factors = set(factors_)
#         factors.discard(1)
#         factors.discard(2)
#         current_pitches = pitches[0 : len(duration_group)]
#         pitches = pitches[len(duration_group) :]
#         if len(factors) == 0:
#             for pitch, duration in zip(current_pitches, duration_group):
#                 leaves = self._make_leaf_on_pitch(
#                     pitch,
#                     duration,
#                     increase_monotonic=self.increase_monotonic,
#                     forbidden_note_duration=self.forbidden_note_duration,
#                     forbidden_rest_duration=self.forbidden_rest_duration,
#                     skips_instead_of_rests=self.skips_instead_of_rests,
#                     tag=self.tag,
#                     use_multimeasure_rests=self.use_multimeasure_rests,
#                 )
#                 result.extend(leaves)
#         else:
#             # compute tuplet prolation
#             denominator = duration_group[0].denominator
#             numerator = abjad.math.greatest_power_of_two_less_equal(denominator)
#             multiplier = (numerator, denominator)
#             ratio = 1 / abjad.Duration(*multiplier)
#             duration_group = [
#                 ratio * abjad.Duration(duration) for duration in duration_group
#             ]
#             # make tuplet leaves
#             tuplet_leaves: typing.List[abjad.Leaf] = []
#             for pitch, duration in zip(current_pitches, duration_group):
#                 leaves = self._make_leaf_on_pitch(
#                     pitch,
#                     duration,
#                     increase_monotonic=self.increase_monotonic,
#                     skips_instead_of_rests=self.skips_instead_of_rests,
#                     tag=self.tag,
#                     use_multimeasure_rests=self.use_multimeasure_rests,
#                     forbidden_note_duration=self.forbidden_note_duration,
#                     forbidden_rest_duration=self.forbidden_rest_duration,
#                 )
#                 tuplet_leaves.extend(leaves)
#             tuplet = abjad.Tuplet(multiplier, tuplet_leaves)
#             result.append(tuplet)
#     return abjad.Selection(result)
# 
# 
# abjad.LeafMaker.__call__ = LeafMaker__call__

# Monkey patch RMakersSequentialEventToQuantizedAbjadContainer in order
# to avoid the following exception for long notes or rests:
#
# abjad.exceptions.AssignabilityError: not assignable duration: Duration(32, 1).
#
# This monkey patch is furthermore valueable because it removes
# the usage of abjadext.rmakers in this method (only pure abjad functions
# are used)!
def RMakersSequentialEventToQuantizedAbjadContainer__make_notes(
    self, sequential_event_to_convert: core_events.SequentialEvent
) -> abjad.Selection:
    leaf_maker = abjad.LeafMaker(
        # could also be: abjad.Duration(16, 1)
        forbidden_note_duration=abjad.Duration(8, 1),
        forbidden_rest_duration=abjad.Duration(8, 1),
    )
    pitch_list = [
        None if event.is_rest else "c" for event in sequential_event_to_convert
    ]
    # It has to be a list! Otherwise abjad will raise an exception.
    duration_list = list(
        map(
            lambda duration: abjad.Duration(duration),
            sequential_event_to_convert.get_parameter("duration"),
        )
    )
    notes = leaf_maker(pitch_list, duration_list)
    return notes


abjad_converters.RMakersSequentialEventToQuantizedAbjadContainer._make_notes = (
    RMakersSequentialEventToQuantizedAbjadContainer__make_notes
)


