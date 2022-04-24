import itertools
import warnings

import abjad

from mutwo import abjad_converters
from mutwo import abjad_parameters
from mutwo import cdd_parameters


# Monkey patch Arpeggio process_leaf, so that
# arpeggio above staves can handle direction.
# Furthermore minimal length of arpeggio is defined here.
def Arpeggio_process_leaf_monkey_patched(self, leaf: abjad.Leaf):
    # Sometimes we want to have only one note head with arpeggio: For arpeggio
    # over staves.
    # if not hasattr(leaf, "note_heads"):
    #     warnings.warn(
    #         f"You tried to attach an arpeggio to the Note '{leaf}' (with"
    #         " only one pitch). This is impossible. Note skipped."
    #     )
    #     return leaf
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
                "\\tiny { " + f"{prefix}{adjusted_deviation} ct" + " } ", direction="up"
            )
            abjad.attach(
                markup,
                leaf,
            )
        return leaf


# override mutwo default value
abjad_converters.configurations.DEFAULT_ABJAD_ATTACHMENT_CLASS_TUPLE = (
    abjad_converters.configurations.DEFAULT_ABJAD_ATTACHMENT_CLASS_TUPLE
    + (CentDeviation,)
)
