"""Test how to parse the pessoa book into strings"""

from bs4 import BeautifulSoup
import ebooklib
from ebooklib import epub

pessoa_ebook = epub.read_epub("cdd/data/pessoa/Livro_do_Desassossego.epub")

document = list(pessoa_ebook.get_items_of_type(ebooklib.ITEM_DOCUMENT))[20]
document_content = document.get_content()

document_soup = BeautifulSoup(document_content, "lxml")

# print(document_soup)
print(document_soup.body.h2.string)
print('')
print(document_soup.body.p.string)
