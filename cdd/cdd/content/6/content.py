import abjad

from mutwo import core_events
from mutwo import music_events
from mutwo import music_parameters

import cdd


class Chapter6(cdd.chapters.Chapter):
    simultaneous_event = core_events.SimultaneousEvent(
        [
            core_events.TaggedSequentialEvent(
                [music_events.NoteLike()],
                tag=cdd.constants.ADDED_INSTRUMENT_NAME_TO_SHORT_INSTRUMENT_NAME[
                    "percussion"
                ],
            ),
            core_events.TaggedSequentialEvent(
                [music_events.NoteLike(lyric=music_parameters.DirectLyric("hello"))],
                tag=cdd.constants.INSTRUMENT_NAME_TO_SHORT_INSTRUMENT_NAME["soprano"],
            ),
            core_events.TaggedSequentialEvent(
                [music_events.NoteLike()],
                tag=cdd.constants.INSTRUMENT_NAME_TO_SHORT_INSTRUMENT_NAME["clarinet"],
            ),
            core_events.TaggedSequentialEvent(
                [music_events.NoteLike()],
                tag=cdd.constants.INSTRUMENT_NAME_TO_SHORT_INSTRUMENT_NAME[
                    "clavichord"
                ],
            ),
        ]
    )

    time_signature_sequence = (abjad.TimeSignature((4, 4)),)

    # ; avoid theatric or monotonous
    instruction_text = r"""
speak text clearly \& naturally; avoid theatric, monotonous or mechanical voice.\\
a natural intonation is more important than a precise rhythm.\\
singer leads group by playing the additional percussion line.\\
instrument can be any (but only one) percussive sound, e.g. clapping, wood block, a tiny bell, \dots\\
"""
