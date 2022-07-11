from __future__ import annotations

import dataclasses
import functools

import librosa
import numpy as np
import pyo
import soundfile

from mutwo import core_events

FrameCount = int
DurationInSeconds = float
SamplingRate = int
ChannelCount = int
FileFormat = str
SampleType = str

__all__ = ("SoundFile", "MonoSoundFileContainer")


@dataclasses.dataclass(frozen=True)
class SoundFile(object):
    """Initialize a sound file"""

    path: str

    @functools.cached_property
    def information_tuple(
        self,
    ) -> tuple[
        FrameCount,
        DurationInSeconds,
        SamplingRate,
        ChannelCount,
        FileFormat,
        SampleType,
    ]:
        return pyo.sndinfo(self.path)

    @functools.cached_property
    def frame_count(self) -> FrameCount:
        return self.information_tuple[0]

    @functools.cached_property
    def duration_in_seconds(self) -> DurationInSeconds:
        return self.information_tuple[1]

    @functools.cached_property
    def sampling_rate(self) -> SamplingRate:
        return int(self.information_tuple[2])

    @functools.cached_property
    def channel_count(self) -> ChannelCount:
        return self.information_tuple[3]

    @functools.cached_property
    def file_format(self) -> FileFormat:
        return self.information_tuple[4]

    @functools.cached_property
    def sample_type(self) -> SampleType:
        return self.information_tuple[5]

    @functools.cached_property
    def array(self) -> np.array:
        array, sampling_rate = soundfile.read(self.path)
        assert self.sampling_rate == sampling_rate
        return array

    @functools.cached_property
    def mono_array(self) -> np.array:
        array, sampling_rate = librosa.load(self.path, sr=self.sampling_rate)
        assert self.sampling_rate == sampling_rate
        return array

    @functools.cached_property
    def spectrogram_magnitude(self) -> np.ndarray:
        spectrogram_magnitude, _ = librosa.magphase(librosa.stft(self.array))
        return spectrogram_magnitude

    @functools.cached_property
    def rms_envelope(self) -> core_events.Envelope:
        from mutwo import cdd_converters

        return cdd_converters.SoundFileToRMSEnvelope()(self)

    @functools.cached_property
    def spectral_centroid_envelope(self) -> core_events.Envelope:
        from mutwo import cdd_converters

        return cdd_converters.SoundFileToSpectralCentroidEnvelope()(self)

    @functools.cached_property
    def spectral_flatness_envelope(self) -> core_events.Envelope:
        from mutwo import cdd_converters

        return cdd_converters.SoundFileToSpectralFlatnessEnvelope()(self)

    @functools.cached_property
    def spectral_contrast_envelope(self) -> core_events.Envelope:
        from mutwo import cdd_converters

        return cdd_converters.SoundFileToSpectralContrastEnvelope()(self)

    @functools.cached_property
    def attack_sequential_event(self) -> core_events.Envelope:
        from mutwo import cdd_converters

        return cdd_converters.SoundFileToAttackSequentialEvent(delta=0.2)(self)


class MonoSoundFileContainer(tuple[SoundFile]):
    def __repr__(self) -> str:
        return f"{type(self).__name__}{super().__repr__()}"

    def __str__(self) -> str:
        return f"{type(self).__name__}{super().__str__()}"

    @functools.cached_property
    def channel_count(self) -> int:
        return len(self)

    @functools.cached_property
    def frame_count(self) -> FrameCount:
        return self[0].frame_count

    @functools.cached_property
    def duration_in_seconds(self) -> DurationInSeconds:
        return self[0].duration_in_seconds

    @functools.cached_property
    def sampling_rate(self) -> SamplingRate:
        return self[0].sampling_rate
