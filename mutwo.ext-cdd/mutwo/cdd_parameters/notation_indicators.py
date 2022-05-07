import dataclasses
import typing

from mutwo import music_parameters


@dataclasses.dataclass()
class CentDeviation(music_parameters.abc.ImplicitPlayingIndicator):
    deviation: typing.Optional[float] = None


@dataclasses.dataclass()
class NoteHead(music_parameters.abc.ImplicitPlayingIndicator):
    default_style: str = "default"
    style: typing.Optional[str] = None


@dataclasses.dataclass()
class NoteHeadHintList(music_parameters.abc.ImplicitPlayingIndicator):
    font_size: float = -7
    hint_list: typing.Optional[list[str]] = None


@dataclasses.dataclass(frozen=False)
class CDDNotationIndicatorCollection(music_parameters.NotationIndicatorCollection):
    cent_deviation: CentDeviation = dataclasses.field(default_factory=CentDeviation)
    note_head: NoteHead = dataclasses.field(default_factory=NoteHead)
    note_head_hint_list: NoteHeadHintList = dataclasses.field(
        default_factory=NoteHeadHintList
    )
