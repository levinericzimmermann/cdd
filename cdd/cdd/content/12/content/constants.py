import abjad
import expenvelope

from mutwo import core_converters
from mutwo import core_events
from mutwo import core_utilities
from mutwo import mmml_converters

from . import configurations

CHORD_SEQUENTIAL_EVENT = mmml_converters.MMMLEventsConverter(
    mmml_converters.MMMLPitchesConverter(mmml_converters.MMMLSingleJIPitchConverter())
)(configurations.CHORD_MMML)


NEW_GROUP_INDEX_TUPLE = tuple(
    core_utilities.accumulate_from_zero(configurations.GROUP_COUNT_TUPLE)
)

REST_SIZE = configurations.BEAT_SIZE * configurations.REST_SIZE_COUNT

# How many beats of BEAT_SIZE can a bar be long
MAXIMUM_BAR_SIZE = int(
    configurations.MAXIMUM_CHORD_DURATION_IN_SECONDS
    / core_converters.TempoConverter(
        expenvelope.Envelope.from_points(
            [0, configurations.BASE_TEMPO.absolute_tempo_in_beat_per_minute / 4]
        )
    )(core_events.SimpleEvent(configurations.BEAT_SIZE)).duration,
)

REST_TIME_SIGNATURE = abjad.TimeSignature(
    (configurations.REST_SIZE_COUNT, configurations.BEAT_SIZE.denominator)
)

MAX_TEMPO = (
    configurations.BASE_TEMPO.absolute_tempo_in_beat_per_minute
    * configurations.MAX_TEMPO_FACTOR
)

MIN_TEMPO = (
    configurations.BASE_TEMPO.absolute_tempo_in_beat_per_minute
    * configurations.MIN_TEMPO_FACTOR
)
