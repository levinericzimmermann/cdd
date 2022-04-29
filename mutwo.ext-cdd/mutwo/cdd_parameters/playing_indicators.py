import dataclasses

from mutwo import music_parameters


@dataclasses.dataclass(frozen=False)
class CDDPlayingIndicatorCollection(music_parameters.PlayingIndicatorCollection):
    irregular_glissando: music_parameters.abc.ExplicitPlayingIndicator = (
        dataclasses.field(default_factory=music_parameters.abc.ExplicitPlayingIndicator)
    )
