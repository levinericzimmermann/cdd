import abc
import dataclasses

from mutwo import cdd_parameters

__all__ = ("Chapter",)


@dataclasses.dataclass
class Chapter(abc.ABC):
    index: int

    @property
    @abc.abstractmethod
    def pessoa_lyric(self) -> cdd_parameters.NestedLanguageBasedLyric:
        raise NotImplementedError

    @abc.abstractmethod
    def render_notation(self):
        raise NotImplementedError

    @abc.abstractmethod
    def render_sound(self):
        raise NotImplementedError
