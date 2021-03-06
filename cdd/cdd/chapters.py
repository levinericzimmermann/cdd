import dataclasses
import importlib

import cdd

from mutwo import cdd_interfaces
from mutwo import cdd_parameters

__all__ = ("Chapter",)


@dataclasses.dataclass
class Chapter(cdd_interfaces.abc.Chapter):
    index: int

    @property
    def pessoa_lyric(self) -> cdd_parameters.NestedLanguageBasedLyric:
        return cdd.constants.CHAPTER_TO_LYRICS_DICT[f"[{self.index}]"]

    def get_notation_path(self, instrument_name: str) -> str:
        return f"{cdd.configurations.PATH.BUILDS.NOTATIONS}/{self.index}_{instrument_name}"

    def get_midi_path(self, instrument_name: str) -> str:
        return (
            f"{cdd.configurations.PATH.BUILDS.MIDI}/{self.index}_{instrument_name}.mid"
        )

    def get_sound_file_path(self, instrument_name: str) -> str:
        return f"{cdd.configurations.PATH.BUILDS.SOUND_FILES}/{self.index}_{instrument_name}.wav"

    def get_reaper_marker_path(self, reaper_marker_name: str) -> str:
        return f"{cdd.configurations.PATH.BUILDS.REAPER}/{self.index}_{reaper_marker_name}"

    def render_notation(self):
        importlib.import_module(f"cdd.content.{self.index}.notations").main(self)

    def render_sound(self):
        importlib.import_module(f"cdd.content.{self.index}.sounds").main(self)
