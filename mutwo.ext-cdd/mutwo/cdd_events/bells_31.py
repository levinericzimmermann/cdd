from mutwo import cdd_parameters
from mutwo import core_events
from mutwo import music_parameters

__all__ = ("BellEvent", "BellCsoundEvent", "MonoBellCsoundEvent")


class BellEvent(core_events.SimpleEvent):
    def __init__(
        self,
        pitch: music_parameters.abc.Pitch = music_parameters.DirectPitch(440),
        duration: float = 0,
        distance: float = 0,
        panning_start: cdd_parameters.Panning = cdd_parameters.Panning([1]),
        panning_end: cdd_parameters.Panning = cdd_parameters.Panning([1]),
        volume: music_parameters.abc.Volume = music_parameters.DirectVolume(0),
    ):
        self.pitch = pitch
        self.distance = distance
        self.panning_start = panning_start
        self.panning_end = panning_end
        self.volume = volume
        super().__init__(duration)


class BellCsoundEventBase(core_events.SimpleEvent):
    def __init__(
        self,
        duration: float = 1,
        pitch_factor: float = 1,
        sample_path: str = "",
        amplitude: float = 0,
        panning_start: cdd_parameters.Panning = cdd_parameters.Panning([1]),
        panning_end: cdd_parameters.Panning = cdd_parameters.Panning([1]),
        filter_frequency: float = 10000,
        convolution_reverb_mix: float = 0,
    ):
        self.sample_path = sample_path
        self.pitch_factor = pitch_factor
        self.panning_start = panning_start
        self.panning_end = panning_end
        self.amplitude = amplitude
        self.filter_frequency = filter_frequency
        self.convolution_reverb_mix = convolution_reverb_mix
        super().__init__(duration)


class MonoBellCsoundEvent(BellCsoundEventBase):
    def __init__(self, *args, channel_index: int = 0, **kwargs):
        self.channel_index = channel_index
        super().__init__(*args, **kwargs)


class BellCsoundEvent(BellCsoundEventBase):
    def split_to(self, channel_count: int = 2) -> tuple[MonoBellCsoundEvent, ...]:
        mono_bell_csound_event_list = []
        panning_start_tuple, panning_end_tuple = (
            panning.split_to(channel_count)
            for panning in (self.panning_start, self.panning_end)
        )
        for channel_index, panning_start, panning_end in zip(
            range(channel_count), panning_start_tuple, panning_end_tuple
        ):
            mono_bell_csound_event = MonoBellCsoundEvent(
                duration=self.duration,
                pitch_factor=self.pitch_factor,
                sample_path=self.sample_path,
                amplitude=self.amplitude,
                panning_start=panning_start,
                panning_end=panning_end,
                channel_index=channel_index,
                filter_frequency=self.filter_frequency,
                convolution_reverb_mix=self.convolution_reverb_mix,
            )
            mono_bell_csound_event_list.append(mono_bell_csound_event)

        return tuple(mono_bell_csound_event_list)
