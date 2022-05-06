import abjad

from mutwo import core_converters

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
