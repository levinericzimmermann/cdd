from mutwo import cdd_converters

import cdd


def main(chapter: cdd.chapters.Chapter):
    chapter_to_latex_document = cdd_converters.ChapterToLatexDocument()
    latex_document = chapter_to_latex_document.convert(chapter, "clarinet")
    latex_document.generate_pdf(chapter.get_notation_path("clarinet"), clean_tex=False)
