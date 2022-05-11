import typing

import num2words
import pylatex

from mutwo import cdd_interfaces
from mutwo import core_converters


__all__ = (
    "ChapterToLatexDocument",
    "TableChapterToLatexDocument",
    "PDFChapterToLatexDocument",
    "TextChapterToLatexDocument",
    "ScoreChapterToLatexDocument",
    "ScoreListChapterToLatexDocument",
    "PreciseScoreListChapterToLatexDocument",
)


class ChapterToLatexDocument(core_converters.abc.Converter):
    def get_package_name_and_options_tuple(
        self, chapter_to_convert: cdd_interfaces.abc.Chapter, instrument_name: str
    ) -> tuple[tuple[str, list[pylatex.NoEscape]], ...]:
        return (
            ("fancyhdr", []),
            ("ebgaramond", []),
            (
                "geometry",
                [
                    pylatex.NoEscape(r"a4paper"),
                    pylatex.NoEscape(r"top=1cm"),
                    pylatex.NoEscape(r"left=1.5cm"),
                    pylatex.NoEscape(r"right=1.5cm"),
                    pylatex.NoEscape(r"bottom=0.5cm"),
                    pylatex.NoEscape(r"headsep=0.25cm"),
                    pylatex.NoEscape(r"marginparsep=0cm"),
                ],
            ),
        )

    def get_preamble_tuple(
        self, chapter_to_convert: cdd_interfaces.abc.Chapter, instrument_name: str
    ) -> tuple[str, ...]:
        return (
            r"\fancyhead[CO,CE]{cdd no. "
            + f"{chapter_to_convert.index}: "
            + instrument_name
            + " part book}",
            r"\fancyfoot{}",
        )

    def convert(
        self, chapter_to_convert: cdd_interfaces.abc.Chapter, instrument_name: str
    ) -> pylatex.Document:
        document = pylatex.Document(
            page_numbers=False,
            indent=False,
        )
        document.change_page_style("fancy")
        for package_name, options in self.get_package_name_and_options_tuple(
            chapter_to_convert, instrument_name
        ):
            document.packages.append(pylatex.Package(package_name, options=options))
        preamble_tuple = self.get_preamble_tuple(chapter_to_convert, instrument_name)
        document.preamble.extend([pylatex.NoEscape(line) for line in preamble_tuple])
        index = chapter_to_convert.index
        index_text = num2words.num2words(index, lang="pt")
        document.append(pylatex.Section(f"No. {index} [{index_text}]", numbering=False))
        return document


class TableChapterToLatexDocument(ChapterToLatexDocument):
    def __init__(
        self,
        instruction_text: str,
        table: tuple[tuple[str, ...], ...],
        text_size: pylatex.base_classes.latex_object._CreatePackages = pylatex.LargeText,
        row_count: int = 20,
        table_per_page_count: int = 2,
        vspace: str = "4cm",
        hspace: str = "7cm",
        font: str = "\\tt",
        column_space: str = "0.5cm",
        row_height: float = 2,
    ):
        self.instruction_text = instruction_text
        self.text_size = text_size
        self.column_count = len(table[0])
        self.row_count = row_count
        self.table_per_page_count = table_per_page_count
        self.table = table
        self.vspace = vspace
        self.hspace = hspace
        self.font = font
        self.column_space = column_space
        self.row_height = row_height

    def convert(self, *args, **kwargs) -> pylatex.Document:
        latex_document = super().convert(*args, **kwargs)
        latex_document.append(pylatex.NoEscape(self.instruction_text))
        for _ in range(4):
            latex_document.append(pylatex.NoEscape(r"\\"))
        latex_document.append(pylatex.NoEscape(r"\vspace{" + self.vspace + "}"))
        latex_document.append(pylatex.NoEscape(r"\hspace{" + self.hspace + "}"))
        row_iterator = iter(self.table)
        is_running = True
        while is_running:
            tabular = pylatex.Tabular(
                table_spec="c" * self.column_count,
                col_space=self.column_space,
                row_height=self.row_height,
            )
            for _ in range(self.row_count):
                try:
                    row = next(row_iterator)
                except StopIteration:
                    is_running = False
                    break
                else:
                    tabular.add_row(
                        *[
                            self.text_size(pylatex.NoEscape(f"{self.font} {item}"))
                            for item in row
                        ]
                    )
            latex_document.append(tabular)
        return latex_document


class PDFChapterToLatexDocument(ChapterToLatexDocument):
    """Useful if you want to include pdf files"""

    def get_package_name_and_options_tuple(
        self, chapter_to_convert: cdd_interfaces.abc.Chapter, instrument_name: str
    ) -> tuple[tuple[str, list[pylatex.NoEscape]], ...]:
        package_name_and_options_tuple = super().get_package_name_and_options_tuple(
            chapter_to_convert, instrument_name
        )
        return package_name_and_options_tuple + (("graphicx", []),)


class TextChapterToLatexDocument(ChapterToLatexDocument):
    def __init__(self, text: str):
        self.text = text

    def convert(
        self, chapter_to_convert: cdd_interfaces.abc.Chapter, instrument_name: str
    ) -> pylatex.Document:
        latex_document = super().convert(chapter_to_convert, instrument_name)
        instruction_mini_page = pylatex.MiniPage(
            fontsize="large",
            # width="10cm",
            # height="20cm",
            # align="c",
            content_pos="c",
            pos="c",
            data=[pylatex.NoEscape(self.text)],
        )
        pessoa_mini_page = pylatex.MiniPage(
            fontsize="small",
            # width="10cm",
            # height="20cm",
            align="r",
            content_pos="c",
            pos="c",
            data=[
                pylatex.NoEscape(
                    f"``{chapter_to_convert.pessoa_lyric.written_representation}''"
                )
            ],
        )
        latex_document.append(pylatex.NoEscape(r"\vfill"))
        latex_document.append(instruction_mini_page)
        latex_document.append(pylatex.NoEscape(r"\vfill"))
        latex_document.append(pylatex.NoEscape(r"\vfill"))
        latex_document.append(pessoa_mini_page)
        latex_document.append(pylatex.NoEscape(r"\vfill"))
        return latex_document


class ScoreChapterToLatexDocument(PDFChapterToLatexDocument):
    def __init__(
        self,
        score_path: str,
        instruction_text: str = "",
        width: float = 1,
        hspace: str = None,
    ):
        self.width = width
        self.instruction_text = instruction_text
        self.score_path = score_path
        self._hspace = hspace

    def get_preamble_tuple(self, *args, **kwargs):
        preamble_tuple = super().get_preamble_tuple(*args, **kwargs)
        preamble_tuple += (
            r"\renewcommand\textfraction{0}",
            r"\setlength{\floatsep}{0pt plus 0.0pt minus 0.0pt}",
            r"\setlength{\textfloatsep}{0pt plus 0.0pt minus 0.0pt}",
        )
        return preamble_tuple

    def convert(
        self, chapter_to_convert: cdd_interfaces.abc.Chapter, instrument_name: str
    ) -> pylatex.Document:
        latex_document = super().convert(chapter_to_convert, instrument_name)
        # latex_document.append(pylatex.NoEscape())
        # latex_document.append(pylatex.NoEscape())
        # latex_document.append(pylatex.NoEscape())
        latex_document.append(pylatex.NoEscape(self.instruction_text))
        figure = pylatex.Figure(position="h!")
        if self._hspace:
            figure.append(pylatex.NoEscape(r"\hspace{" + self._hspace + "}"))
        figure.append(
            pylatex.NoEscape(
                r"\includegraphics[width="
                + str(self.width)
                + r"\textwidth]{"
                + self.score_path
                + "}"
            )
        )
        latex_document.append(figure)
        latex_document.append(pylatex.NoEscape(r"\clearpage"))
        return latex_document


class ScoreListChapterToLatexDocument(ScoreChapterToLatexDocument):
    def __init__(self, *args, vspace: typing.Optional[str] = None, **kwargs):
        self._vspace = vspace
        super().__init__(*args, **kwargs)

    def convert(
        self, chapter_to_convert: cdd_interfaces.abc.Chapter, instrument_name: str
    ) -> pylatex.Document:
        latex_document = ChapterToLatexDocument.convert(
            self, chapter_to_convert, instrument_name
        )
        latex_document.append(pylatex.NoEscape(self.instruction_text))
        figure = pylatex.Figure(position="h!")
        for score_path in self.score_path:
            try:
                score_path, width = score_path
            except ValueError:
                score_path, width = score_path, self.width
            if self._hspace:
                figure.append(pylatex.NoEscape(r"\hspace{" + self._hspace + "}"))
            figure.append(
                pylatex.NoEscape(
                    r"\includegraphics[width="
                    + str(width)
                    + r"\textwidth]{"
                    + score_path
                    + "}"
                )
            )
            if self._vspace:
                figure.append(pylatex.NoEscape(r"\vspace{" + self._vspace + "}"))
        latex_document.append(figure)
        latex_document.append(pylatex.NoEscape(r"\clearpage"))
        return latex_document


class PreciseScoreListChapterToLatexDocument(ScoreChapterToLatexDocument):
    """Set width for each score individually"""

    def convert(
        self, chapter_to_convert: cdd_interfaces.abc.Chapter, instrument_name: str
    ) -> pylatex.Document:
        latex_document = ChapterToLatexDocument.convert(
            self, chapter_to_convert, instrument_name
        )
        latex_document.append(pylatex.NoEscape(self.instruction_text))
        for score_path, width in self.score_path.items():
            figure = pylatex.Figure(position="h!")
            if self._hspace:
                figure.append(pylatex.NoEscape(r"\hspace{" + self._hspace + "}"))
            figure.append(
                pylatex.NoEscape(
                    r"\includegraphics[width="
                    + str(width)
                    + r"\textwidth]{"
                    + score_path
                    + "}"
                )
            )
            latex_document.append(figure)
        latex_document.append(pylatex.NoEscape(r"\clearpage"))
        return latex_document
