from bs4 import BeautifulSoup
import ebooklib
from ebooklib import epub

from mutwo import core_converters

__all__ = ("EpubToDict",)


class EpubToDict(core_converters.abc.Converter):
    def convert(self, epub_path: str) -> dict[str, str]:
        loaded_epub = epub.read_epub(epub_path)
        header_to_content_dict = {}
        for document in loaded_epub.get_items_of_type(ebooklib.ITEM_DOCUMENT):
            document_content = document.get_content()
            document_soup = BeautifulSoup(document_content, "lxml")
            try:
                header = document_soup.body.h2.string
            except AttributeError:
                pass
            else:
                content = document_soup.body.p.string
                header_to_content_dict.update({header: content})
        return header_to_content_dict
