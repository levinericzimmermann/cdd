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


@dataclasses.dataclass()
class DurationLine(music_parameters.abc.ImplicitPlayingIndicator):
    style: str = "line"
    thickness: float = 3
    dash_period: int = 2
    end_style: str = "none"
    hook_direction: str = "DOWN"


@dataclasses.dataclass(frozen=False)
class CDDNotationIndicatorCollection(music_parameters.NotationIndicatorCollection):
    cent_deviation: CentDeviation = dataclasses.field(default_factory=CentDeviation)
    duration_line: DurationLine = dataclasses.field(default_factory=DurationLine)
    note_head: NoteHead = dataclasses.field(default_factory=NoteHead)
    note_head_hint_list: NoteHeadHintList = dataclasses.field(
        default_factory=NoteHeadHintList
    )
