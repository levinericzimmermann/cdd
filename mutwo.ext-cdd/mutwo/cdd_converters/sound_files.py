import abc
import functools
import operator
import tempfile
import typing

import librosa
import numpy as np
import soundfile

from mutwo import cdd_parameters
from mutwo import cdd_utilities
from mutwo import core_converters
from mutwo import core_events
from mutwo import core_utilities


__all__ = (
    "SoundFileToMonoSoundFileContainer",
    "SoundFileToRMSEnvelope",
    "SoundFileToSpectralFlatnessEnvelope",
    "SoundFileToSpectralCentroidEnvelope",
    "SoundFileToSpectralContrastEnvelope",
    "SoundFileToAttackSequentialEvent",
    "SoundFileToDynamicAttackSequentialEvent",
    "SoundFileToPulse",
)


class SoundFileToMonoSoundFileContainer(core_converters.abc.Converter):
    def convert(
        self, sound_file_to_convert: cdd_parameters.SoundFile
    ) -> cdd_parameters.MonoSoundFileContainer:
        original_sound_file, _ = soundfile.read(sound_file_to_convert.path)
        if original_sound_file.ndim == 1:
            new_sound_file = original_sound_file[..., np.newaxis]
        else:
            new_sound_file = original_sound_file

        mono_sound_file_list = []
        for channel_index in range(sound_file_to_convert.channel_count):
            mono_sound_file_data = new_sound_file[:, channel_index]
            temporary_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            mono_sound_file_path = temporary_file.name
            soundfile.write(
                mono_sound_file_path,
                mono_sound_file_data,
                sound_file_to_convert.sampling_rate,
                format="wav",
            )
            mono_sound_file = cdd_parameters.SoundFile(mono_sound_file_path)
            mono_sound_file_list.append(mono_sound_file)

        return cdd_parameters.MonoSoundFileContainer(mono_sound_file_list)


class SoundFileToAnalysisEnvelope(core_converters.abc.Converter):
    def __init__(self, window_size: int = 512, cleanup_factor: float = 2.5, **kwargs):
        self._window_size = window_size
        self._kwargs = kwargs
        self._cleanup_factor = cleanup_factor

    @abc.abstractmethod
    def _sound_file_to_data_array(
        self, sound_file_to_convert: cdd_parameters.SoundFile
    ) -> np.ndarray:
        ...

    def convert(
        self, sound_file_to_convert: cdd_parameters.SoundFile
    ) -> core_events.Envelope:
        # XXX: I'm not 100% sure, but perhaps this method will break
        # if non mono files are passed.
        assert sound_file_to_convert.channel_count == 1
        value_tuple = tuple(
            map(
                float,
                cdd_utilities.reject_outliers(
                    self._sound_file_to_data_array(sound_file_to_convert),
                    self._cleanup_factor,
                )[0],
            )
        )
        window_duration = self._window_size / sound_file_to_convert.sampling_rate
        absolute_duration_tuple = tuple(
            core_utilities.accumulate_from_zero([window_duration for _ in value_tuple])
        )
        analysis_envelope = core_events.Envelope(
            [
                [absolute_duration, value]
                for absolute_duration, value in zip(
                    absolute_duration_tuple, value_tuple
                )
            ]
        )
        return analysis_envelope


class SoundFileToRMSEnvelope(SoundFileToAnalysisEnvelope):
    def _sound_file_to_data_array(
        self, sound_file_to_convert: cdd_parameters.SoundFile
    ) -> np.ndarray:
        return librosa.feature.rms(
            S=sound_file_to_convert.spectrogram_magnitude,
            hop_length=self._window_size,
            **self._kwargs,
        )


class SoundFileToSpectralFlatnessEnvelope(SoundFileToAnalysisEnvelope):
    def _sound_file_to_data_array(
        self, sound_file_to_convert: cdd_parameters.SoundFile
    ) -> np.ndarray:
        return librosa.feature.spectral_flatness(
            y=sound_file_to_convert.mono_array,
            S=sound_file_to_convert.spectrogram_magnitude,
            hop_length=self._window_size,
            **self._kwargs,
        )


class SoundFileToSpectralCentroidEnvelope(SoundFileToAnalysisEnvelope):
    def _sound_file_to_data_array(
        self, sound_file_to_convert: cdd_parameters.SoundFile
    ) -> np.ndarray:
        return librosa.feature.spectral_centroid(
            y=sound_file_to_convert.mono_array,
            S=sound_file_to_convert.spectrogram_magnitude,
            hop_length=self._window_size,
            **self._kwargs,
        )


class SoundFileToSpectralContrastEnvelope(SoundFileToAnalysisEnvelope):
    def _sound_file_to_data_array(
        self, sound_file_to_convert: cdd_parameters.SoundFile
    ) -> np.ndarray:
        return librosa.feature.spectral_contrast(
            y=sound_file_to_convert.mono_array,
            S=sound_file_to_convert.spectrogram_magnitude,
            hop_length=self._window_size,
            **self._kwargs,
        )


class SoundFileToAttackSequentialEvent(core_converters.abc.Converter):
    def __init__(self, **kwargs):
        self._kwargs = kwargs

    def convert(
        self, sound_file_to_convert: cdd_parameters.SoundFile
    ) -> core_events.SequentialEvent[core_events.SimpleEvent]:
        absolute_time_list = list(
            map(
                float,
                librosa.onset.onset_detect(
                    y=sound_file_to_convert.mono_array,
                    sr=sound_file_to_convert.sampling_rate,
                    units="time",
                    **self._kwargs,
                ),
            )
        )
        if is_first_event_rest := (0 not in absolute_time_list):
            absolute_time_list.insert(0, 0)
        attack_sequential_event = core_events.SequentialEvent(
            [
                core_events.SimpleEvent(absolute_time1 - absolute_time0)
                for absolute_time0, absolute_time1 in zip(
                    absolute_time_list, absolute_time_list[1:]
                )
            ]
        )
        is_first = True
        for simple_event in attack_sequential_event:
            is_attack = True
            if is_first:
                is_attack = not is_first_event_rest
                is_first = False
            simple_event.is_attack = is_attack
        return attack_sequential_event


class SoundFileToDynamicAttackSequentialEvent(core_converters.abc.Converter):
    """Switch between various SoundFileToAttackSequentialEvent

    (To vary sensitivity of detector).
    """

    def __init__(
        self,
        sound_file_to_attack_sequential_event_tuple: tuple[
            SoundFileToAttackSequentialEvent, ...
        ] = (SoundFileToAttackSequentialEvent(delta=0.11),),
    ):
        assert sound_file_to_attack_sequential_event_tuple
        self._sound_file_to_attack_sequential_event_tuple = (
            sound_file_to_attack_sequential_event_tuple
        )

    def convert(
        self,
        sound_file_to_convert: cdd_parameters.SoundFile,
        attack_sequential_event_selector_envelope: typing.Optional[
            core_events.Envelope
        ] = None,
    ) -> core_events.SequentialEvent[core_events.SimpleEvent]:
        attack_sequential_event_tuple = tuple(
            sound_file_to_attack_sequential_event(sound_file_to_convert)
            for sound_file_to_attack_sequential_event in self._sound_file_to_attack_sequential_event_tuple
        )
        attack_sequential_event_duration = attack_sequential_event_tuple[0].duration
        if not attack_sequential_event_selector_envelope:
            attack_sequential_event_selector_envelope = core_events.Envelope(
                [[0, 0], [attack_sequential_event_duration, 0]]
            )
        attack_sequential_event_selector_envelope.duration = (
            attack_sequential_event_duration
        )

        attack_sequential_event = core_events.SequentialEvent(
            [core_events.SimpleEvent(attack_sequential_event_duration)]
        )
        attack_sequential_event[0].is_attack = False

        absolute_time_tuple_tuple = tuple(
            attack_sequential_event.absolute_time_tuple
            for attack_sequential_event in attack_sequential_event_tuple
        )
        absolute_time_tuple = tuple(
            sorted(set(functools.reduce(operator.add, absolute_time_tuple_tuple)))
        )

        for absolute_time in absolute_time_tuple:
            attack_sequential_event_index = int(
                attack_sequential_event_selector_envelope.value_at(absolute_time)
            )
            try:
                event_index = absolute_time_tuple_tuple[
                    attack_sequential_event_index
                ].index(absolute_time)
            except ValueError:
                continue
            simple_event = attack_sequential_event_tuple[attack_sequential_event_index][
                event_index
            ]
            if simple_event.is_attack:
                attack_sequential_event.squash_in(absolute_time, simple_event)

        return attack_sequential_event


class SoundFileToPulse(core_converters.abc.Converter):
    def convert(
        self, sound_file_to_convert: cdd_parameters.SoundFile
    ) -> core_events.SequentialEvent[core_events.SimpleEvent]:
        hop_length = 512
        pulse_array = librosa.beat.plp(
            y=sound_file_to_convert.mono_array,
            sr=sound_file_to_convert.sampling_rate,
            hop_length=hop_length,
        )
        is_local_maxima_array = librosa.util.localmax(pulse_array)

        absolute_time_list, onset_strength_list = [], []
        for frame_index, is_local_maxima in enumerate(is_local_maxima_array):
            if is_local_maxima:
                absolute_time = frame_index * (
                    hop_length / sound_file_to_convert.sampling_rate
                )
                absolute_time_list.append(absolute_time)
                onset_strength_list.append(pulse_array[frame_index])

        if 0 not in absolute_time_list:
            absolute_time_list.insert(0, 0)
            onset_strength_list.insert(0, 0)

        sequential_event = core_events.SequentialEvent([])
        for absolute_time0, absolute_time1, onset_strength in zip(
            absolute_time_list,
            absolute_time_list[1:] + [sound_file_to_convert.duration_in_seconds],
            onset_strength_list,
        ):
            duration = absolute_time1 - absolute_time0
            sequential_event.append(
                core_events.SimpleEvent(duration).set_parameter(
                    "onset_strength", onset_strength
                )
            )

        return sequential_event
