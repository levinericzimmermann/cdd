from .lyrics import *
from .notation_indicators import *
from .playing_indicators import *
from .abjad_attachments import *

# set mutwo default values

from mutwo import music_events

music_events.configurations.DEFAULT_NOTATION_INDICATORS_COLLECTION_CLASS = (
    CDDNotationIndicatorCollection
)

music_events.configurations.DEFAULT_PLAYING_INDICATORS_COLLECTION_CLASS = (
    CDDPlayingIndicatorCollection
)

del music_events


# Monkey patch music_parameters.abc.Lyric

from mutwo import isis_converters
from mutwo import music_parameters

XSAMPA_VOWEL_TUPLE = tuple(
    set("i y i u M u I Y I U e 2 @ 8 7 o E 9 3 V O & 6 a A Q".split(" "))
)

XSAMPA_CONSONANT_TUPLE = tuple(
    set(
        "m F n n` J N p b t d t` d` c J\ k g q G\ >\ ? s z S Z s z s z p B f v T D C j x G X R h K P r j M l l` L L\ 4 r` l\ B\ r R\ H\ <\ O\ ` ` !\ !\` =\ ` |` b_< d_< J\_< g_< G\ p_> t_> t`_> c_> k_> q_> >\_> f_> T_> s_> S_> s`_> x_> X_> K_>".split(
            " "
        )
    )
)

ISIS_CONSONANT_TUPLE = (
    isis_converters.constants.XSAMPA.semi_vowel_tuple
    + isis_converters.constants.XSAMPA.voiced_fricative_tuple
    + isis_converters.constants.XSAMPA.unvoiced_fricative_tuple
    + isis_converters.constants.XSAMPA.voiced_plosive_tuple
    + isis_converters.constants.XSAMPA.unvoiced_plosive_tuple
    + isis_converters.constants.XSAMPA.nasal_tuple
    + isis_converters.constants.XSAMPA.other_tuple
)

CONSONANT_PROHIBITED_TO_ALLOWED = {"r": "R", "J": "j"}

import warnings


def consonant_tuple(self) -> tuple[str, ...]:
    phonetic_representation = self.phonetic_representation
    consonant_list = []
    for xsampa_phoneme in phonetic_representation:
        if xsampa_phoneme in XSAMPA_VOWEL_TUPLE:
            break
        elif xsampa_phoneme in XSAMPA_CONSONANT_TUPLE:
            if xsampa_phoneme not in ISIS_CONSONANT_TUPLE:
                if xsampa_phoneme in CONSONANT_PROHIBITED_TO_ALLOWED:
                    replacement = CONSONANT_PROHIBITED_TO_ALLOWED[xsampa_phoneme]
                else:
                    replacement = ISIS_CONSONANT_TUPLE[0]
                warnings.warn(f"Replaced {xsampa_phoneme} with {replacement}!")
                xsampa_phoneme = replacement
            consonant_list.append(xsampa_phoneme)
    return tuple(consonant_list)


def vowel(self) -> str:
    phonetic_representation = self.phonetic_representation
    vowel = ""
    for xsampa_phoneme in phonetic_representation:
        if xsampa_phoneme in XSAMPA_VOWEL_TUPLE:
            if xsampa_phoneme not in isis_converters.constants.XSAMPA.vowel_tuple:
                replacement = isis_converters.constants.XSAMPA.vowel_tuple[0]
                warnings.warn(f"Replaced {xsampa_phoneme} with {replacement}!")
                xsampa_phoneme = replacement
            vowel = xsampa_phoneme
    return vowel


setattr(music_parameters.abc.Lyric, "consonant_tuple", property(consonant_tuple))
setattr(music_parameters.abc.Lyric, "vowel", property(vowel))


del music_parameters
