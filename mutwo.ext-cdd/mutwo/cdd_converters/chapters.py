import num2words
import pylatex

from mutwo import cdd_interfaces
from mutwo import core_converters


__all__ = ("ChapterToLatexDocument",)


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
                    pylatex.NoEscape(r"a4"),
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
            # r"\fancyhead{}",
            r"\fancyfoot{}",
            r"\fancyhead[CO,CE]{cdd: " + instrument_name + " part book}",
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
