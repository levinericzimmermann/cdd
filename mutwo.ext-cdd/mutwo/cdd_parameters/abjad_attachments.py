# import itertools
import warnings

import abjad
import quicktions as fractions

from mutwo import abjad_converters
from mutwo import abjad_parameters
from mutwo import cdd_parameters
from mutwo import music_parameters


# Monkey patch Arpeggio process_leaf, so that
# arpeggio above staves can handle direction.
# Furthermore minimal length of arpeggio is defined here.
def Arpeggio_process_leaf_monkey_patched(self, leaf: abjad.Leaf):
    thickness = 3
    abjad.attach(
        abjad.LilyPondLiteral("\\override Arpeggio.thickness = #'{}".format(thickness)),
        leaf,
    )
    direction = self.direction
    if direction in self._string_to_direction:
        direction = self._string_to_direction[direction]
        move_direction = "UP" if direction == abjad.enums.Up else "DOWN"
        abjad.attach(
            abjad.LilyPondLiteral(
                r"\override PianoStaff.Arpeggio.arpeggio-direction = #" + move_direction
            ),
            leaf,
        )
    else:
        warnings.warn(f"Found unknown direction '{direction}'.")
    abjad.attach(abjad.Arpeggio(direction=direction), leaf)

    # If interval is small (smaller than a third) arpeggio will
    # be very short. This is an ugly tweak to increase length
    # of arpeggio line.
    # See https://lists.gnu.org/archive/html/lilypond-user/2006-05/msg00181.html

    # THIS DOESN'T WORK DUE TO DURATION LINES

    # if leaf.note_heads:
    #     named_pitch_list = sorted(
    #         [note_head.named_pitch for note_head in leaf.note_heads]
    #     )
    #     interval_list = [
    #         pitch0 - pitch1
    #         for pitch0, pitch1 in itertools.combinations(named_pitch_list, 2)
    #     ]
    #     max_interval = max([abs(interval.cents) for interval in interval_list])
    #     if max_interval < 500:
    #         new_pitch = named_pitch_list[0] + abjad.NumberedInterval(10)
    #         new_note_head = abjad.NoteHead(new_pitch)
    #         abjad.tweak(new_note_head).transparent = "##t"
    #         leaf.note_heads.append(new_note_head)
    return leaf


abjad_parameters.Arpeggio.process_leaf = Arpeggio_process_leaf_monkey_patched


class CentDeviation(
    cdd_parameters.CentDeviation, abjad_parameters.abc.BangFirstAttachment
):
    def process_leaf(self, leaf: abjad.Leaf) -> abjad.Leaf:
        if self.deviation % 100 != 0:
            if self.deviation > 0:
                prefix = "+"
            else:
                prefix = "-"
            adjusted_deviation = round(abs(self.deviation))
            markup = abjad.Markup(
                "\\tiny { " + f"{prefix}{adjusted_deviation}" + " } ", direction="up"
            )
            abjad.attach(
                markup,
                leaf,
            )
        return leaf


class FancyGlissando(
    cdd_parameters.FancyGlissando, abjad_parameters.abc.BangFirstAttachment
):
    @staticmethod
    def _command_to_lilypond_string(command: tuple[tuple[float, ...], ...]):
        lilypond_string = ""
        for part in command:
            lilypond_string += "({})\n".format(" ".join(map(str, part)))
        return fr"\fancy-gliss #'({lilypond_string})"

    def process_leaf(self, leaf: abjad.Leaf) -> abjad.Leaf:
        leaf = abjad.mutate.copy(leaf)
        fancy_glissando = FancyGlissando._command_to_lilypond_string(self.command)
        abjad.attach(abjad.LilyPondLiteral(fancy_glissando, format_slot="before"), leaf)
        abjad.attach(abjad.Glissando(), leaf)
        return leaf


class IrregularGlissando(
    music_parameters.abc.ExplicitPlayingIndicator,
    abjad_parameters.abc.BangFirstAttachment,
):
    def process_leaf(self, leaf: abjad.Leaf) -> abjad.Leaf:
        leaf = abjad.mutate.copy(leaf)
        fancy_glissando = r"""
\fancy-gliss
        #'(
            (1 3 0.2 2 1 1)
            (2 -2)
            (3 2)
            (4 1)
            (5 2.5)
            (6 0)
            (7 0 8 6 12 0))
"""
        abjad.attach(
            abjad.LilyPondLiteral(fancy_glissando, format_slot="before"),
            leaf,
        )
        if hasattr(leaf, "note_head"):
            pitch = leaf.note_head.written_pitch
        elif hasattr(leaf, "note_heads"):
            pitch = leaf.note_heads[0].written_pitch
        else:
            raise NotImplementedError()
        hidden_leaf = abjad.Note(pitch, fractions.Fraction(1, 64))
        omit = r"\once \omit"
        abjad.attach(
            abjad.LilyPondLiteral(
                (
                    f"{omit} Accidental "
                    f"{omit} NoteHead "
                    f"{omit} Beam "
                    f"{omit} Stem "
                    f"{omit} Flag "
                ),
                format_slot="before",
            ),
            hidden_leaf,
        )

        voice = abjad.Voice([leaf, hidden_leaf])

        abjad.attach(abjad.Glissando(), leaf)

        return voice


# override mutwo default value
abjad_converters.configurations.DEFAULT_ABJAD_ATTACHMENT_CLASS_TUPLE = (
    abjad_converters.configurations.DEFAULT_ABJAD_ATTACHMENT_CLASS_TUPLE
    + (CentDeviation, FancyGlissando, IrregularGlissando)
)
