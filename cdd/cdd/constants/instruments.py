import copy
import functools
import operator

import gradient_free_optimizers

from mutwo import cdd_converters
from mutwo import music_converters
from mutwo import music_parameters

from .pitches import WESTERN_PITCH_REFERENCE

from .. import configurations


def _western_pitch_to_just_intonation_pitch(
    western_pitch: music_parameters.WesternPitch,
) -> music_parameters.JustIntonationPitch:
    pitch_interval = WESTERN_PITCH_REFERENCE.get_pitch_interval(western_pitch)
    ratio = music_parameters.JustIntonationPitch.cents_to_ratio(pitch_interval.interval)
    just_intonation_pitch = music_parameters.JustIntonationPitch(
        ratio.limit_denominator(10)
    )
    return just_intonation_pitch


def _western_pitch_ambitus_to_just_intonation_ambitus(
    western_pitch_ambitus: music_parameters.OctaveAmbitus,
) -> music_parameters.OctaveAmbitus:
    return music_parameters.OctaveAmbitus(
        _western_pitch_to_just_intonation_pitch(western_pitch_ambitus.minima_pitch),
        _western_pitch_to_just_intonation_pitch(western_pitch_ambitus.maxima_pitch),
    )


CLAVICHORD_CHROMATIC_JUST_INTONATION_PITCH_TUPLE = tuple(
    sorted(
        [
            music_parameters.JustIntonationPitch(ratio).normalize()
            for ratio in "1/1 3/2 4/3 7/4 8/7 7/6 12/7 14/9 9/7 28/27 27/14 112/81".split(
                " "
            )
        ]
    )
)


WESTERN_PITCH_REFERENCE_AS_DIATONIC_PITCH_CLASS = (
    music_parameters.constants.DIATONIC_PITCH_CLASS_CONTAINER[
        WESTERN_PITCH_REFERENCE.pitch_class_name
    ]
)

CLAVICHORD_CHROMATIC_WESTERN_PITCH_TUPLE = tuple(
    sorted(
        [
            music_parameters.WesternPitch(
                pitch_class_number % 12, octave=4 + (pitch_class_number // 12)
            )
            for pitch_class_number in range(
                WESTERN_PITCH_REFERENCE_AS_DIATONIC_PITCH_CLASS.pitch_class,
                WESTERN_PITCH_REFERENCE_AS_DIATONIC_PITCH_CLASS.pitch_class + 12,
            )
        ]
    )
)

CLARINET_WESTERN_PITCH_AMBITUS = music_parameters.OctaveAmbitus(
    music_parameters.WesternPitch("d", 3), music_parameters.WesternPitch("bf", 6)
)


SOPRAN_WESTERN_PITCH_AMBITUS = music_parameters.OctaveAmbitus(
    music_parameters.WesternPitch("c", 4), music_parameters.WesternPitch("a", 5)
)


CLAVICHORD_WESTERN_PITCH_AMBITUS = music_parameters.OctaveAmbitus(
    # music_parameters.WesternPitch("c", 3), music_parameters.WesternPitch("b", 6)
    music_parameters.WesternPitch("c", 3),
    music_parameters.WesternPitch("f", 6),
)

CLARINET_AMBITUS = _western_pitch_ambitus_to_just_intonation_ambitus(
    CLARINET_WESTERN_PITCH_AMBITUS
)

SOPRAN_AMBITUS = _western_pitch_ambitus_to_just_intonation_ambitus(
    SOPRAN_WESTERN_PITCH_AMBITUS
)

CLAVICHORD_AMBITUS = _western_pitch_ambitus_to_just_intonation_ambitus(
    CLAVICHORD_WESTERN_PITCH_AMBITUS
)

CLAVICHORD_PITCH_TUPLE = tuple(
    sorted(
        functools.reduce(
            operator.add,
            (
                CLAVICHORD_AMBITUS.get_pitch_variant_tuple(pitch)
                for pitch in CLAVICHORD_CHROMATIC_JUST_INTONATION_PITCH_TUPLE
            ),
        )
    )
)


def clavichord_just_intonation_pitch_to_clavichord_western_pitch(
    clavichord_just_intonation_pitch: music_parameters.JustIntonationPitch,
) -> music_parameters.WesternPitch:
    clavichord_western_pitch = copy.deepcopy(
        CLAVICHORD_CHROMATIC_WESTERN_PITCH_TUPLE[
            CLAVICHORD_CHROMATIC_JUST_INTONATION_PITCH_TUPLE.index(
                clavichord_just_intonation_pitch.normalize(mutate=False)
            )
        ]
    )
    clavichord_western_pitch.octave += clavichord_just_intonation_pitch.octave
    return clavichord_western_pitch


CLAVICHORD_PITCH_TO_TABULATURA_PITCH = cdd_converters.PitchToTabulaturaPitch(
    {
        clavichord_pitch.exponent_tuple: clavichord_just_intonation_pitch_to_clavichord_western_pitch(
            clavichord_pitch
        )
        for clavichord_pitch in CLAVICHORD_PITCH_TUPLE
    }
)

CLAVICHORD_SEQUENTIAL_EVENT_TO_TABULATURA_BASED_EVENT = cdd_converters.SequentialEventToTabulaturaBasedEvent(
    CLAVICHORD_PITCH_TO_TABULATURA_PITCH,
    music_converters.ImproveWesternPitchListSequenceReadability(
        sequential_pitch_weight=0.64,
        optimizer_class=gradient_free_optimizers.RandomSearchOptimizer,
        # optimizer_class=gradient_free_optimizers.RepulsingHillClimbingOptimizer,
        # optimizer_class=gradient_free_optimizers.HillClimbingOptimizer,
        # optimizer_class=gradient_free_optimizers.ParticleSwarmOptimizer,
        # optimizer_class=gradient_free_optimizers.BayesianOptimizer,
        # optimizer_class=gradient_free_optimizers.EvolutionStrategyOptimizer,
        # optimizer_class=gradient_free_optimizers.SimulatedAnnealingOptimizer,
        # optimizer_class=gradient_free_optimizers.ParallelAnnealingOptimizer,
        # optimizer_class=gradient_free_optimizers.GridSearchOptimizer,
        # optimizer_class=gradient_free_optimizers.RandomRestartHillClimbingOptimizer,
        # verbosity_list=["progress_bar", "print_results", "print_times"],
        iteration_count=configurations.IMPROVE_WESTERN_PITCH_LIST_ITERATION_COUNT,
    ),
)

INSTRUMENT_NAME_TO_SHORT_INSTRUMENT_NAME = {
    "soprano": "s.",
    "clarinet": "cl.",
    "clavichord": "cv.",
    "noise": "n.",
}

ADDED_INSTRUMENT_NAME_TO_SHORT_INSTRUMENT_NAME = {"percussion": "perc."}

SHORT_INSTRUMENT_NAME_TO_INSTRUMENT_NAME = {
    short_instrument_name: instrument_name
    for instrument_name, short_instrument_name in INSTRUMENT_NAME_TO_SHORT_INSTRUMENT_NAME.items()
}
SHORT_INSTRUMENT_NAME_TO_INSTRUMENT_NAME.update(
    {
        short_instrument_name: instrument_name
        for instrument_name, short_instrument_name in ADDED_INSTRUMENT_NAME_TO_SHORT_INSTRUMENT_NAME.items()
    }
)

CLARINET_EVENT_TO_TRANSPOSED_CLARINET_EVENT = cdd_converters.EventToTransposedEvent(
    music_parameters.JustIntonationPitch("9/8")
)

CLARINET_EXPONENT_TUPLE_TO_WOODWIND_FINGERING_DICT: dict[
    tuple[int, ...], music_parameters.WoodwindFingering
] = {}

CLARINET_EVENT_TO_CLARINET_EVENT_WITH_FINGERING = (
    cdd_converters.EventToEventWithWoodwindFingering(
        CLARINET_EXPONENT_TUPLE_TO_WOODWIND_FINGERING_DICT
    )
)
