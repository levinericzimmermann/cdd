import dataclasses
import typing

from mutwo import music_parameters


@dataclasses.dataclass()
class CentDeviation(music_parameters.abc.ImplicitPlayingIndicator):
    deviation: typing.Optional[float] = None


@dataclasses.dataclass(frozen=False)
class CDDNotationIndicatorCollection(music_parameters.NotationIndicatorCollection):
    cent_deviation: CentDeviation = dataclasses.field(default_factory=CentDeviation)
