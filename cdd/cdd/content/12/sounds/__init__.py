import cdd

from . import instruments
from . import tapes


def main(chapter: cdd.chapters.Chapter):
    tapes.main(chapter)
    instruments.main(chapter)
