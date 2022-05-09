import dataclasses

import abjad
import quicktions as fractions

from mutwo import cdd_utilities
from mutwo import core_events
from mutwo import music_events
from mutwo import music_parameters

from . import SOPRANO


@dataclasses.dataclass(frozen=True)
class LongNote(object):
    sequential_event: core_events.SequentialEvent[music_events.NoteLike]
    start: float
    duration: float

    @property
    def end(self) -> float:
        return self.start + self.duration

    def get_text_content(self, formatted_start: str, formatted_end: str) -> str:
        return f"from {formatted_start} to {formatted_end}"

    def get_sequential_event(self) -> core_events.SequentialEvent:
        sequential_event = self.sequential_event.copy()
        text_content = self.get_text_content(
            *[
                cdd_utilities.duration_in_seconds_to_readable_duration(time)
                for time in (self.start, self.end)
            ]
        )
        sequential_event[0].notation_indicator_collection.markup.content = abjad.Markup(
            # r"\typewriter { \smaller { " f"{text_content}" r"} }"
            r"\typewriter { \normalsize { "
            f"{text_content}"
            r"} }"
        )
        sequential_event[0].notation_indicator_collection.markup.direction = "^"
        return sequential_event


@dataclasses.dataclass(frozen=True)
class GlissandoNote(LongNote):
    def get_sequential_event(self) -> core_events.SequentialEvent:
        sequential_event = super().get_sequential_event()
        sequential_event[0].playing_indicator_collection.irregular_glissando = True
        return sequential_event


@dataclasses.dataclass(frozen=True)
class TimeSpanLongNote(LongNote):
    def get_text_content(self, formatted_start: str, formatted_end: str) -> str:
        return f"within {formatted_start} to {formatted_end}"


instruction_text_sine = r"""
start \& end at given times.
slowly fade in \& slowly fade out.
almost no overtones should be audible (imitate a sine tone).
"""

# Long sine-like whistle notes at the beginning
sine_note_tuple = tuple(
    LongNote(
        core_events.SequentialEvent(
            [
                music_events.NoteLike(
                    pitch, duration=fractions.Fraction(1, 1), volume="ppp"
                )
            ]
        ),
        start,
        duration,
    )
    for pitch, start, duration in (("3/1", 40, 35), ("8/3", (1 * 60) + 25, 25))
)

instruction_text_glissando = r"""
start \& end at given times.
make irregular glissandi (circle the written pitch).
be closer to nature than music (e.g. avoid intention).
short pauses between sounds are acceptable.
"""

# one glissando note after long rest
glissando_note_tuple = (
    GlissandoNote(
        core_events.SequentialEvent(
            [
                music_events.NoteLike(
                    "3/1", duration=fractions.Fraction(1, 1), volume="mp"
                )
            ]
        ),
        (2 * 60) + 50,
        60,
    ),
)


instruction_text_unisono = fr"""
start at given time; play with singer.
dynamics should be equally balanced.
tempo: {SOPRANO.tempo_range.start} to {SOPRANO.tempo_range.end} bpm (= 1/4) [adjust to singer].
"""

# Then: unisono event with soprano (event is defined in content/__init__.py)

# repeat pattern up to 4 times within given time span.
instruction_text_slap = r"""
repeat pattern up to 4 times.
use slap tongue.
use different tempi when repeating the pattern.
parenthesized note is optional; can or can not be played.
"""


# slaps
slap_sequential_event = core_events.SequentialEvent(
    [
        music_events.NoteLike(pitch, duration=fractions.Fraction(1, 2), volume="p")
        for pitch in ("3/4", "2/3")
    ]
)
slap_note_head = "cross"
for note_like in slap_sequential_event:
    note_like.notation_indicator_collection.note_head.style = slap_note_head
slap_optional_note = music_events.NoteLike("f", fractions.Fraction(1, 8))
slap_optional_note.playing_indicator_collection.optional = True
# slap_optional_note.notation_indicator_collection.note_head.style = slap_note_head
slap_sequential_event[1].grace_note_sequential_event = core_events.SequentialEvent(
    [slap_optional_note]
)

slap_long_note = TimeSpanLongNote(slap_sequential_event, (6 * 60) + 10, 45)

# finally there are unisonos again with the singer
# we will use the same instruction like previously

clarinet_unisono_interval_tuple = (
    music_parameters.JustIntonationPitch("1/1"),
    music_parameters.JustIntonationPitch("4/5"),
    music_parameters.JustIntonationPitch("1/1"),
    music_parameters.JustIntonationPitch("3/4"),
)

unisono_part_index_tuple = (6, 7, 8, 10)
