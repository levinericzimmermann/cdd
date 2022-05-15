import cdd

from . import simulations
from . import tapes


def main(chapter: cdd.chapters.Chapter):
    tapes.render(chapter)
    simulations.render(chapter)
