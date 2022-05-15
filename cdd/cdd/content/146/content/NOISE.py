from mutwo import core_utilities

from . import SOPRANO

initial_rest = 27

period_in_seconds = 28

duration = SOPRANO.duration

event_to_skip_index_tuple = (4, 5, 9, 10, 11, 12, 13, 14, 15)

absolute_time_tuple = tuple(
    absolute_time
    for index, absolute_time in enumerate(
        core_utilities.accumulate_from_n(
            [
                period_in_seconds
                for _ in range(int((duration - initial_rest) / period_in_seconds))
           ],
            initial_rest,
        )
    )
    if index not in event_to_skip_index_tuple
)

character = "x"

instruction_text = r"""
play metallic, not-pitched percussion (e.g. cymbal) at given times.
always only one attack, damped, calm; repeating the same characteristics, again \& again (imitate a clock).
"""

instruction_text_after = r"""
\begin{center}
    \bigskip
    \bigskip

    play noisy structure from circa

    \bigskip

    { \tt \large 6'20 to 7'10 }

    \bigskip

    with present transients.\\
\end{center}

"""
