import abjad

from mutwo import abjad_converters
from mutwo import abjad_parameters
from mutwo import cdd_parameters


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
