from mutwo import cdd_converters

import cdd


def main(chapter: cdd.chapters.Chapter):
    chapter_to_latex_document = cdd_converters.SilenceChapterToLatexDocument()
    for (
        instrument_name
    ) in cdd.constants.INSTRUMENT_NAME_TO_SHORT_INSTRUMENT_NAME.keys():
        latex_document = chapter_to_latex_document.convert(chapter, instrument_name)
        latex_document.generate_pdf(
            chapter.get_notation_path(instrument_name), clean_tex=True
        )
