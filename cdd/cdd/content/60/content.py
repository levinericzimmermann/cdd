import cdd


class Chapter60(cdd.chapters.Chapter):
    @property
    def pessoa_lyric(self):
        return cdd.constants.CHAPTER_TO_LYRICS_DICT["[60] Intervalo doloroso"]
