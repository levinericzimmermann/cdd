import typing

import abjad
import quicktions as fractions
import ranges

from mutwo import core_events
from mutwo import core_parameters
from mutwo import core_utilities

from cdd import constants

from . import utilities as utilities12


# Add new method to SequentialEvent which in the current
# mutwo.ext-core version doesn't exist yet.
@core_utilities.add_copy_option
def SequentialEvent_set_parameter_sequence(
    self, parameter_name: str, parameter_sequence: typing.Sequence[typing.Any]
):
    for event, value in zip(self, parameter_sequence):
        event.set_parameter(parameter_name, value)
    return self


core_events.SequentialEvent.set_parameter_sequence = (
    SequentialEvent_set_parameter_sequence
)


def set_duration(
    sequential_event: core_events.SequentialEvent,
    fraction_tuple: tuple[tuple[int, int], ...],
):
    return sequential_event.set_parameter_sequence(
        "duration",
        [fractions.Fraction(*duration) for duration in fraction_tuple],
    )


CHORD_MMML = r"""
# For each instrument one pitch.
# Pitch order: clavichord / soprano / clarinet.
# (see also global variable PITCH_ORDER)

1,5-,3+5-
3-,5+3-,5+3--

# --- wolfsquinte ---

7+,7++,3-7++
3-7+,3--,3-7-
3--7+,3---,3--7-
3---7+,3----,3---7-
3----7+,3-----,3----7-

# --- wolfsquinte ---

3+++7-,3++++,3+++7+
3++7-,3+++,3++7+
3+7-,3++,3+7+
7-,7--,3+7--

# --- wolfsquinte ---

3+,3+5+,5+
1,5-,3+5-
"""

PITCH_ORDER = ("clavichord", "soprano", "clarinet")

# How many bars one group encompasses until a rest appears.
# Rest appears when there are wolfsquinten between chords.
GROUP_COUNT_TUPLE = (2, 5, 4, 2)

TEMPO_REFERENCE = fractions.Fraction(2, 1)

BASE_TEMPO = core_parameters.TempoPoint(45, reference=TEMPO_REFERENCE)

MIN_TEMPO_FACTOR = 0.888

MAX_TEMPO_FACTOR = 1.125

TEMPO_POINT_COUNT = 3

TEMPO_CHANGE_LOOP_SIZE_RANGE = ranges.Range(3, 5)

TEMPO_CHANGE_BAR_COUNT_RANGE = ranges.Range(2, 4)

TEMPO_CHANGE_LOOP_BAR_COUNT_RANGE = ranges.Range(
    TEMPO_CHANGE_BAR_COUNT_RANGE.start * TEMPO_CHANGE_LOOP_SIZE_RANGE.start,
    TEMPO_CHANGE_BAR_COUNT_RANGE.end * TEMPO_CHANGE_LOOP_SIZE_RANGE.end,
)

BEAT_SIZE = fractions.Fraction(1, 2)

# Otherwise time_signature_sequence definition is bad
assert BEAT_SIZE.numerator == 1

# How many beats the rest lasts
REST_SIZE_COUNT = 6

# max time singer/clarinet can hold a pitch
#   clarinet: 45 seconds
#   soprano:  15 seconds (MAXIMA)
MAXIMUM_CHORD_DURATION_IN_SECONDS = min(
    (constants.CLARINET_MAXIMUM_TONE_DURATION, constants.SOPRANO_MAXIMUM_TONE_DURATION)
)

TRANSFORMER_DATA_TUPLE = (
    # transform, beat_count_in, beat_count_out
    #
    # ############################################################# #
    # 3 to ...
    # ############################################################# #
    (
        lambda sequential_event: set_duration(
            sequential_event, ((1, 1), (1, 2), (1, 2))
        ),
        3,
        4,
    ),
    (
        lambda sequential_event: set_duration(
            sequential_event, ((1, 4), (1, 1), (1, 4))
        ),
        3,
        3,
    ),
    # ############################################################# #
    # 4 to ...
    # ############################################################# #
    (
        lambda sequential_event: set_duration(
            sequential_event, ((1, 2), (1, 1), (1, 2), (1, 2))
        ),
        4,
        5,
    ),
    (
        lambda sequential_event: set_duration(
            sequential_event, ((1, 2), (1, 4), (1, 4), (1, 2))
        ),
        4,
        3,
    ),
    # ############################################################# #
    # 5 to ...
    # ############################################################# #
    (
        lambda sequential_event: set_duration(
            sequential_event, ((1, 2), (1, 4), (1, 2), (1, 2), (1, 4))
        ),
        5,
        4,
    ),
    # ############################################################# #
    # 6 to ...
    # ############################################################# #
)


LONG_TONE_DATA_TUPLE = (
    # (duration_percentage, delay_percentage, hairpin)
    # (soprano, clarinet, are_locked)
    # NEW GROUP
    ((1, 1, "<>"), (1, 1, "<>"), True),
    ((0.8, 0.7, "<>"), (0.5, 0.7, "<>"), False),
    # NEW GROUP
    ((1, 1, "<"), (1, 1, "<"), True),
    ((0.99, 0, ">"), (1, 0, "<"), True),
    ((1, 0, "<"), (1, 0, ">"), True),
    ((1, 0, ">"), (1, 0, ">"), True),
    # CENTER
    ((0.85, 0.8, "<>"), (1, 0, "<>"), False),
)
LONG_TONE_DATA_TUPLE += utilities12.reverse_long_tone_data_tuple(LONG_TONE_DATA_TUPLE)

PATTERN_TUPLE = (
    # NEW GROUP
    (((0, 1, 2, 3), 1, 2, 3), 4),
    ((1, 0, 1, 0, 2), 3),
    # NEW GROUP
    ((3, 2, 1, 0), 3),
    ((0, 1, 2), 3),
    (((1, 2), (0, 3), 1, 0), 2),
    ((2, 2, 1, 3, 0), 3),
    # CENTER
    (((0, 1, 2, 3), 0, 1, 1, (0, 1, 2, 3), 2, 3, 3), 2),
)
PATTERN_TUPLE += utilities12.reverse_tuple(PATTERN_TUPLE)

TRANSFORM_ACTIVITY_LEVEL_TUPLE = (
    # new group
    4,
    6,
    # new group
    4,
    3,
    8,
    4,
    # center!
    4,
)
TRANSFORM_ACTIVITY_LEVEL_TUPLE += utilities12.reverse_tuple(
    TRANSFORM_ACTIVITY_LEVEL_TUPLE
)

DENSITY_ENVELOPE_TUPLE = (
    # NEW GROUP
    [[0, 0.3], [0.9, 0.6]],
    [[0, 0.5], [0.3, 0.3], [0.8, 0.1], [1, 0]],
    # NEW GROUP
    [[0, 0.3], [1, 0.8]],
    [[0, 0.8], [0.8, 0.5], [1, 0.4]],
    [[0, 0.35], [1, 0.6]],
    [[0, 0.6], [1, 0.1]],
    # CENTER
    [[0, 0.3], [1, 0.3]],
)
DENSITY_ENVELOPE_TUPLE += utilities12.reverse_density_envelope_tuple(
    DENSITY_ENVELOPE_TUPLE
)

# There are 3 rests
REST_TIME_SIGNATURE_TUPLE = (
    abjad.TimeSignature((2, 2)),
    abjad.TimeSignature((7, 2)),
    abjad.TimeSignature((2, 2)),
)


METRONOME_ACTIVITY_LEVEL_ENVELOPE = core_events.Envelope(
    [
        [0, 10],
        [0.1, 10],
        [0.2, 10],
        [0.3, 9],
        [0.5, 8],
        [0.66, 7],
        [0.7, 8],
        [0.8, 10],
        [0.9, 10],
        [1, 0],
    ]
)
