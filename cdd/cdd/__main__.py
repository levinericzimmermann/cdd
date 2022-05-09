import os
import typing
import warnings

import natsort
from PyPDF2 import PdfFileMerger

import cdd


def chapter_name_to_chapter(chapter_name: str) -> typing.Optional[cdd.chapters.Chapter]:
    try:
        return getattr(cdd.content, str(chapter_name)).CHAPTER
    except AttributeError:
        warnings.warn(f"Can't find chapter: {chapter_name}.", RuntimeWarning)
        return None


def render(render_method_list):
    for chapter_to_render_name in cdd.configurations.CHAPTER_TO_RENDER_TUPLE:
        chapter = chapter_name_to_chapter(chapter_to_render_name)
        if chapter:
            for render_method in render_method_list:
                getattr(chapter, render_method)()


def concatenate_part_books():
    instrument_name_to_score_list = {
        instrument_name: []
        for instrument_name in cdd.constants.INSTRUMENT_NAME_TO_SHORT_INSTRUMENT_NAME.keys()
    }
    for chapter_to_render_name in natsort.natsorted(
        cdd.configurations.CHAPTER_TO_RENDER_TUPLE
    ):
        chapter = chapter_name_to_chapter(chapter_to_render_name)
        if chapter:
            for instrument_name in instrument_name_to_score_list.keys():
                notation_path = f"{chapter.get_notation_path(instrument_name)}.pdf"
                if os.path.exists(notation_path):
                    instrument_name_to_score_list[instrument_name].append(notation_path)

    part_book_path_list = []
    for instrument_name, score_list in instrument_name_to_score_list.items():
        if score_list:
            path = f"{cdd.configurations.PATH.BUILDS.SCORES}/cdd_{instrument_name}_part_book.pdf"
            merger = PdfFileMerger()
            for pdf in score_list:
                merger.append(pdf)
            merger.write(path)
            merger.close()
            part_book_path_list.append(path)


def main():
    import logging
    import warnings

    logging.root.setLevel(logging.DEBUG)
    render_method_list = cdd.configurations.RENDER_METHOD_LIST

    if len(render_method_list) == 2:
        warnings.warn(
            "Mixing rendering notation and sound can lead "
            "to unexpected side effects, be careful!",
            RuntimeWarning,
        )

    render(render_method_list)
    if "render_notation" in render_method_list:
        concatenate_part_books()
