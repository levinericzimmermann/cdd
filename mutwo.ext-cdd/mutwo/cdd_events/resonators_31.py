from mutwo import cdd_parameters
from mutwo import core_events
from mutwo import music_parameters

__all__ = ("ResonatorEvent",)


class ResonatorEvent(core_events.SimpleEvent):
    CHANNEL_COUNT = 5

    # Global counter: now two events will have the same base function table index.
    # XXX: Start with 1, otherwise 000 will be 0 which will create an error.
    class_function_table_index = 1

    spectral_centroid_envelope_function_table_index = 0
    spectral_contrast_envelope_function_table_index = 1

    def __init__(
        self,
        pitch: music_parameters.abc.Pitch = music_parameters.DirectPitch(440),
        duration: float = 0,
        bandwidth_start: float = 200,
        bandwidth_end: float = 50,
        filter_layer_count: int = 4,
        panning_start: cdd_parameters.Panning = cdd_parameters.Panning([1]),
        panning_end: cdd_parameters.Panning = cdd_parameters.Panning([1]),
        volume: music_parameters.abc.Volume = music_parameters.DirectVolume(0),
        spectral_centroid_envelope_tuple: tuple[core_events.Envelope, ...] = (
            core_events.Envelope([]),
            core_events.Envelope([]),
            core_events.Envelope([]),
            core_events.Envelope([]),
            core_events.Envelope([]),
        ),
        spectral_contrast_envelope_tuple: tuple[core_events.Envelope, ...] = (
            core_events.Envelope([]),
            core_events.Envelope([]),
            core_events.Envelope([]),
            core_events.Envelope([]),
            core_events.Envelope([]),
        ),
        partial_count: int = 4,
    ):
        self.instrument = 1 + partial_count
        self.bandwidth_start = bandwidth_start
        self.bandwidth_end = bandwidth_end
        self.pitch = pitch
        self.panning_start = panning_start
        self.panning_end = panning_end
        self.volume = volume
        self.filter_layer_count = filter_layer_count
        self.spectral_centroid_envelope_tuple = spectral_centroid_envelope_tuple
        self.spectral_contrast_envelope_tuple = spectral_contrast_envelope_tuple
        super().__init__(duration)
        self.instance_function_table_index = self.class_function_table_index
        ResonatorEvent.class_function_table_index += 1

    @property
    def spectral_centroid_envelope_function_table_index_tuple(self) -> tuple[int, ...]:
        return tuple(
            int(
                f"{self.instance_function_table_index}"
                f"{self.spectral_centroid_envelope_function_table_index}"
                f"{channel_index}"
            )
            for channel_index in range(self.CHANNEL_COUNT)
        )

    @property
    def spectral_contrast_envelope_function_table_index_tuple(self) -> tuple[int, ...]:
        return tuple(
            int(
                f"{self.instance_function_table_index}"
                f"{self.spectral_contrast_envelope_function_table_index}"
                f"{channel_index}"
            )
            for channel_index in range(self.CHANNEL_COUNT)
        )
