import functools
import operator

from mutwo import music_parameters

from .pitches import WESTERN_PITCH_REFERENCE


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


CLAVICHORD_CHROMATIC_PITCH_TUPLE = tuple(
    sorted(
        [
            music_parameters.JustIntonationPitch(ratio).normalize()
            for ratio in "1/1 3/2 4/3 7/4 8/7 7/6 12/7 14/9 9/7 28/27 27/14 112/81".split(
                " "
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
    music_parameters.WesternPitch("c", 3), music_parameters.WesternPitch("b", 6)
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
                for pitch in CLAVICHORD_CHROMATIC_PITCH_TUPLE
            ),
        )
    )
)

INSTRUMENT_NAME_TO_SHORT_INSTRUMENT_NAME = {
    "soprano": "s.",
    "clarinet": "cl.",
    "clavichord": "cv.",
}

ADDED_INSTRUMENT_NAME_TO_SHORT_INSTRUMENT_NAME = {"percussion": "perc."}
