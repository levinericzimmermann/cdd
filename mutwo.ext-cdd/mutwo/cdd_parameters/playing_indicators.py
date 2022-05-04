import dataclasses
import typing

from mutwo import music_parameters


@dataclasses.dataclass()
class FancyGlissando(music_parameters.abc.ImplicitPlayingIndicator):
    command: typing.Optional[tuple[tuple[float, ...], ...]] = None


@dataclasses.dataclass(frozen=False)
class CDDPlayingIndicatorCollection(music_parameters.PlayingIndicatorCollection):
    fancy_glissando: FancyGlissando = dataclasses.field(default_factory=FancyGlissando)
    irregular_glissando: music_parameters.abc.ExplicitPlayingIndicator = (
        dataclasses.field(default_factory=music_parameters.abc.ExplicitPlayingIndicator)
    )
