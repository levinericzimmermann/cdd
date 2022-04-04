from mutwo import cdd_converters
from mutwo import core_utilities
from mutwo import music_parameters

import cdd

# Set to portugese
music_parameters.configurations.DEFAULT_LANGUAGE_CODE = LANGUAGE_CODE = "mb-pt1"


CHAPTER_TO_LYRICS_DICT = core_utilities.compute_lazy(
    f"{cdd.configurations.PATH.BUILDS.PICKLED}/chapter_to_lyrics.pickled",
    force_to_compute=cdd.configurations.FORCE_TO_COMPUTE_PESSOA,
)(
    lambda: {
        chapter: cdd_converters.LyricsStringToLyrics()(content)
        for chapter, content in cdd_converters.EpubToDict()(
            cdd.configurations.PATH.CDD.DATA.PESSOA.BOOK
        ).items()
    }
)()
