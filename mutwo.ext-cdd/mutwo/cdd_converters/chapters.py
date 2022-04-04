import num2words
import pylatex

from mutwo import cdd_interfaces
from mutwo import core_converters


__all__ = (
    "ChapterToLatexDocument",
    "TextChapterToLatexDocument",
    "ScoreChapterToLatexDocument",
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
                    pylatex.NoEscape(r"top=2cm"),
                    pylatex.NoEscape(r"left=1.5cm"),
                    pylatex.NoEscape(r"right=1.5cm"),
                    pylatex.NoEscape(r"bottom=2cm"),
                ],
            ),
        )

    def get_preamble_tuple(
        self, chapter_to_convert: cdd_interfaces.abc.Chapter, instrument_name: str
    ) -> tuple[str, ...]:
        return (
            r"\fancyhead[CO,CE]{cdd: " + instrument_name + " part book}",
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


class ScoreChapterToLatexDocument(ChapterToLatexDocument):
    def __init__(self, score_path: str, instruction_text: str = ""):
        self.instruction_text = instruction_text
        self.score_path = score_path

    def get_package_name_and_options_tuple(
        self, chapter_to_convert: cdd_interfaces.abc.Chapter, instrument_name: str
    ) -> tuple[tuple[str, list[pylatex.NoEscape]], ...]:
        package_name_and_options_tuple = super().get_package_name_and_options_tuple(
            chapter_to_convert, instrument_name
        )
        return package_name_and_options_tuple + (("graphicx", []),)

    def convert(
        self, chapter_to_convert: cdd_interfaces.abc.Chapter, instrument_name: str
    ) -> pylatex.Document:
        latex_document = super().convert(chapter_to_convert, instrument_name)
        latex_document.append(pylatex.NoEscape(self.instruction_text))
        figure = pylatex.Figure(position="h")
        figure.append(
            pylatex.NoEscape(
                r"\includegraphics[width=0.8\textwidth]{" + self.score_path + "}"
            )
        )
        latex_document.append(figure)
        return latex_document
