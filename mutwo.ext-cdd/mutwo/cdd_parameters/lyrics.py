import warnings

from mutwo import music_parameters

__all__ = ("NestedLanguageBasedLyric", "Word", "Sentence")


class NestedLanguageBasedLyric(list, music_parameters.LanguageBasedLyric):
    join_string = " "

    def __init__(self, leaf_list: list[music_parameters.LanguageBasedLyric]):
        list.__init__(self, leaf_list)
        music_parameters.LanguageBasedLyric.__init__(self, "")

    @property
    def written_representation(self) -> str:
        return self.join_string.join(leaf.written_representation for leaf in self)

    @written_representation.setter
    def written_representation(self, _: str) -> str:
        warnings.warn(
            "Can't override 'written_representation' of NestedLanguageBasedLyric"
        )


class Sentence(NestedLanguageBasedLyric):
    def __init__(
        self, leaf_list: list[music_parameters.LanguageBasedLyric], end: str = "."
    ):
        self.end = end

    @property
    def written_representation(self) -> str:
        return super().written_representation + f"{self.end} "


class Word(NestedLanguageBasedLyric):
    join_string = ""
