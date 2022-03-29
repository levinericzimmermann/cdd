from mutwo import cdd_converters

import cdd

CHAPTER_TO_LYRICS_DICT = {
    chapter: cdd_converters.LyricsStringToLyrics()(content)
    for chapter, content in cdd_converters.EpubToDict()(
        cdd.configurations.PATH.CDD.DATA.PESSOA.BOOK
    ).items()
}
