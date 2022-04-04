import cdd


class Chapter60(cdd.chapters.Chapter):
    @property
    def pessoa_lyric(self):
        return cdd.constants.CHAPTER_TO_LYRICS_DICT["[60] Intervalo doloroso"]

    text = r"""
play or don't play a tape of recorded silence.\\

open or don't open a window.\\

keep focused, present, listening to silence.\\

(up to 4'33; should neither be played at the beginning nor ending of a performance)\\
"""
