import datetime
import typing

import abjad

from mutwo import abjad_converters
from mutwo import cdd_utilities
from mutwo import core_converters
from mutwo import core_constants

# To activate monkey patches!
from . import abjad_patches


class AbjadScoreListToLilyPondFile(core_converters.abc.Converter):
    def get_layout_block(self, margin: float = 1) -> abjad.Block:
        layout_block = abjad.Block("layout")
        layout_block.items.append(r"short-indent = {}\mm".format(margin))
        layout_block.items.append(r"ragged-last = ##f")
        layout_block.items.append(r"indent = {}\mm".format(margin))
        return layout_block

    def get_paper_block(self) -> abjad.Block:
        paper_block = abjad.Block("paper")
        paper_block.items.append(
            r"""#(define fonts
        (make-pango-font-tree "EB Garamond"
                            "Nimbus Sans"
                            "Luxi Mono"
                            (/ staff-height pt 20)))"""
        )
        return paper_block

    def get_header_block(self) -> abjad.Block:
        header_block = abjad.Block("header")
        header_block.items.append(r"tagline = ##f")
        return header_block

    def get_includes(
        self,
        add_book_preamble: bool,
        add_ekmelily: bool,
        add_fancy_glissando: bool,
    ) -> list[str]:
        includes = []
        if add_book_preamble:
            includes.append("etc/lilypond/lilypond-book-preamble.ly")
        if add_ekmelily:
            includes.append("etc/lilypond/ekme-heji-ref-c.ily")
        if add_fancy_glissando:
            includes.append("etc/lilypond/fancy-glissando.ly")
        return includes

    def convert(
        self,
        abjad_score_list: list[abjad.Score],
        add_book_preamble: bool = False,
        add_ekmelily: bool = False,
        add_fancy_glissando: bool = False,
        margin: float = 1,
    ) -> abjad.LilyPondFile:
        includes = self.get_includes(
            add_ekmelily=add_ekmelily,
            add_book_preamble=add_book_preamble,
            add_fancy_glissando=add_fancy_glissando,
        )
        lilypond_file = abjad.LilyPondFile(includes=includes)

        for abjad_score in abjad_score_list:
            score_block = abjad.Block("score")
            score_block.items.append(abjad_score)
            lilypond_file.items.append(score_block)

        paper_block = self.get_paper_block()
        layout_block = self.get_layout_block(margin)
        header_block = self.get_header_block()

        lilypond_file.items.extend([header_block, paper_block, layout_block])

        return lilypond_file


class AddTimeBracketMarks(abjad_converters.ProcessAbjadContainerRoutine):
    def __init__(self, start_or_start_range, end_or_end_range):
        self.start_or_start_range = start_or_start_range
        self.end_or_end_range = end_or_end_range

    # ###################################################################### #
    #                     private static methods                             #
    # ###################################################################### #

    @staticmethod
    def _format_time(
        time: core_constants.Real,
        round_function: typing.Callable[[float], int] = round,
    ) -> str:
        return format(datetime.timedelta(seconds=round_function(time)))[2:]

    @staticmethod
    def _attach_time_bracket_mark(
        leaf_to_attach_to: abjad.Leaf,
        time_bracket_mark: abjad.RehearsalMark,
        format_slot: str,
    ):
        abjad.attach(
            abjad.LilyPondLiteral(format(time_bracket_mark), format_slot=format_slot),
            leaf_to_attach_to,
        )

    @staticmethod
    def _add_time_bracket_mark_for_time(
        leaf_to_attach_to: abjad.Leaf,
        time: core_constants.DurationType,
        format_slot: str,
    ):
        if time is not None:
            formated_time = cdd_utilities.duration_in_seconds_to_readable_duration(time)
            time_bracket_mark = (
                r"\mark \markup { \typewriter " r" { \small { " f"{formated_time} " r"} } }"
            )
            AddTimeBracketMarks._attach_time_bracket_mark(
                leaf_to_attach_to, time_bracket_mark, format_slot
            )

    @staticmethod
    def _add_time_bracket_mark_for_time_range(
        leaf_to_attach_to: abjad.Leaf,
        time_range: typing.Tuple[
            core_constants.DurationType, core_constants.DurationType
        ],
        format_slot: str,
    ):
        if format_slot == "after":
            hint = "\\hspace #-10 end in range: "
            hint = "\\hspace #-7"
        else:
            hint = "\\hspace #-10 start in range: "
            hint = "\\hspace #-10"

        formated_time_range = tuple(
            cdd_utilities.duration_in_seconds_to_readable_duration(time)
            for time in time_range
        )
        time_bracket_mark = (
            f"\\mark \\markup {{ \\small {{ {hint} }} \\override #'(font-family ."
            f" typewriter) \\small {{ {formated_time_range[0]}"
            " } \n\\raise #0.55 \n\\teeny { \\concat { \\arrow-head #X #LEFT ##t"
            " \\draw-line #'(1 . 0) \\arrow-head #X #RIGHT ##t } }\n\\override"
            " #'(font-family . typewriter) \\small {"
            f" {formated_time_range[1]} }} }}"
        )
        AddTimeBracketMarks._attach_time_bracket_mark(
            leaf_to_attach_to, time_bracket_mark, format_slot
        )

    @staticmethod
    def _add_time_bracket_mark_for_time_or_time_range(
        leaf_to_attach_to: abjad.Leaf,
        time_or_time_range,
        format_slot: str,
    ):
        if hasattr(time_or_time_range, "__getitem__"):
            AddTimeBracketMarks._add_time_bracket_mark_for_time_range(
                leaf_to_attach_to, time_or_time_range, format_slot
            )
        else:
            AddTimeBracketMarks._add_time_bracket_mark_for_time(
                leaf_to_attach_to, time_or_time_range, format_slot
            )

    # ###################################################################### #
    #                         private methods                                #
    # ###################################################################### #

    def __call__(
        self,
        _,
        container_to_process: abjad.Container,
    ):
        first_leaf = abjad.get.leaf(container_to_process[0], 0)
        last_leaf = abjad.get.leaf(container_to_process[0], -1)
        for leaf_to_attach_to, time_or_time_range, format_slot in (
            (
                first_leaf,
                self.start_or_start_range,
                "before",
            ),
            (
                last_leaf,
                self.end_or_end_range,
                "after",
            ),
        ):
            AddTimeBracketMarks._add_time_bracket_mark_for_time_or_time_range(
                leaf_to_attach_to, time_or_time_range, format_slot
            )
