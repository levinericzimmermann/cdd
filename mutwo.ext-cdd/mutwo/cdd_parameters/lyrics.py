__all__ = ("Sylablle", "Word", "Sentence", "Lyrics")


class LyricPart(object):
    pass


class NestedLyricPart(list, LyricPart):
    def __repr__(self) -> str:
        return f"{type(self).__name__}({list(self)})"


class Sylablle(LyricPart):
    def __init__(self, sylablle: int):
        self._sylablle = sylablle

    def __repr__(self) -> str:
        return f"{type(self).__name__}({str(self)})"

    def __str__(self) -> str:
        return self._sylablle


class Word(NestedLyricPart):
    def __str__(self) -> str:
        return "".join([str(sylablle) for sylablle in self])


class Sentence(NestedLyricPart):
    def __str__(self) -> str:
        return " ".join([str(word) for word in self])


class Lyrics(NestedLyricPart):
    def __str__(self) -> str:
        return "".join(["{}. ".format(str(sentence)) for sentence in self])
