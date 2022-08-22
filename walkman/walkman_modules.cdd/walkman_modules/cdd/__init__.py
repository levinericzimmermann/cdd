from __future__ import annotations
import random
import typing

import pyo

import walkman


def get_dynamic_panning(
    audio_input: pyo.PyoObject,
    lfo_frequency: float = 0.2,
    lfo_type: int = 0,
    channel_count: int = 4,
) -> typing.Tuple[pyo.PyoObject, typing.List[pyo.PyoObject]]:
    lfo = pyo.LFO(lfo_frequency, mul=0.5, add=1, type=lfo_type)
    panner = pyo.Pan(audio_input, outs=channel_count, spread=lfo)
    return panner, [panner, lfo]


class MonochordEbow(
    walkman.ModuleWithDecibel,
    audio_input=walkman.Catch(walkman.constants.EMPTY_MODULE_INSTANCE_NAME),
):
    def _setup_pyo_object(
        self,
    ):
        super()._setup_pyo_object()
        self.feedback = 0.1
        self.min_delay_time = 1 / 44100
        self.max_delay_time = 1.5
        self.delay_time_factor = self.max_delay_time - self.min_delay_time

        # def pyo_object_to_delay_time(pyo_object: pyo.PyoObject) -> pyo.PyoObject:
        #     pyo_object.setMul(0.5)
        #     pyo_object.setAdd(1)
        #     return (pyo_object * self.delay_time_factor) + self.min_delay_time

        # self.delay_time_list = [
        #     pyo_object_to_delay_time(pyo_object)
        #     for pyo_object in [
        #         pyo.LFO(freq=0.15, type=7),
        #         pyo.LFO(freq=0.23, type=0),
        #         pyo.LFO(freq=0.17, type=3),
        #     ]
        # ]

        self.delay_time_list = [0.005, 0.03, 0.1]

        self.delay = pyo.Delay(
            self.audio_input.pyo_object,
            delay=self.delay_time_list,
            maxdelay=self.max_delay_time,
            feedback=self.feedback,
        )

        internal_pyo_object_list = [self.delay]
        self.panning_list = []
        for delay_index, _ in enumerate(self.delay_time_list):
            lfo_frequency = random.uniform(0.1, 0.9)
            lfo_type = random.choice([0, 1, 3])
            panning, new_internal_pyo_object_list = get_dynamic_panning(
                self.delay[delay_index], lfo_frequency=lfo_frequency, lfo_type=lfo_type
            )
            internal_pyo_object_list.extend(new_internal_pyo_object_list)
            self.panning_list.append(panning)

        self.panning = sum(self.panning_list)
        internal_pyo_object_list.append(self.panning)
        self.internal_pyo_object_list.extend(internal_pyo_object_list)

    @property
    def _pyo_object(self) -> pyo.PyoObject:
        return self.panning


class MonochordHammer(
    walkman.ModuleWithDecibel,
    audio_input=walkman.Catch(walkman.constants.EMPTY_MODULE_INSTANCE_NAME),
):
    def _setup_pyo_object(
        self,
    ):
        super()._setup_pyo_object()
        self.drive = 0.45
        self.slope = 0.3
        self.distortion = pyo.Disto(
            self.audio_input.pyo_object, drive=self.drive, mul=self.amplitude_signal_to, slope=self.slope
        )
        self.internal_pyo_object_list.append(self.distortion)

    @property
    def _pyo_object(self) -> pyo.PyoObject:
        return self.distortion


class Harmonizer(
    walkman.ModuleWithDecibel,
    audio_input=walkman.Catch(walkman.constants.EMPTY_MODULE_INSTANCE_NAME),
):
    def _setup_pyo_object(
        self,
    ):
        super()._setup_pyo_object()
        self.harmonizer = pyo.Harmonizer(
            self.audio_input.pyo_object, transpo=0, mul=self.amplitude_signal_to
        )
        self.internal_pyo_object_list.append(self.harmonizer)

    def _initialise(
        self, transposition_list: typing.Union[typing.List[float], float] = 0, **kwargs
    ):
        self.harmonizer.setTranspo(transposition_list)
        super()._initialise(**kwargs)

    @property
    def _pyo_object(self) -> pyo.PyoObject:
        return self.harmonizer


class CrossSynthesis(
    walkman.ModuleWithDecibel,
    audio_input_microphone=walkman.Catch(walkman.constants.EMPTY_MODULE_INSTANCE_NAME),
    audio_input_field_recording=walkman.Catch(
        walkman.constants.EMPTY_MODULE_INSTANCE_NAME
    ),
):
    """
    def _setup_pyo_object(
        self,
    ):
        super()._setup_pyo_object()

        (
            self.phase_vocoder_analysis_microphone,
            self.phase_vocoder_analysis_field_recording,
        ) = (
            pyo.PVAnal(audio_input.pyo_object)
            for audio_input in (
                self.audio_input_microphone,
                self.audio_input_field_recording,
            )
        )

        # same like morph, it barely mixes
        # self.phase_vocoder_mix = pyo.PVMix(
        #     self.phase_vocoder_analysis_field_recording, self.phase_vocoder_analysis_microphone
        # )

        # sounds different, but doesn't sound too much like the
        # field recording anymore?
        self.phase_vocoder_mix = pyo.PVCross(
            self.phase_vocoder_analysis_field_recording,
            self.phase_vocoder_analysis_microphone,
            fade=0.985
        )

        # barely mixes, sounds like two separate signals
        # self.phase_vocoder_mix = pyo.PVMorph(
        #     self.phase_vocoder_analysis_field_recording,
        #     self.phase_vocoder_analysis_microphone,
        #     fade=0.85
        # )

        self.phase_vocoder_synthesizer = (
            pyo.PVSynth(self.phase_vocoder_mix) * self.amplitude_signal_to
        )

        self.internal_pyo_object_list.extend(
            [
                self.phase_vocoder_analysis_microphone,
                self.phase_vocoder_analysis_field_recording,
                self.phase_vocoder_mix,
                self.phase_vocoder_synthesizer,
            ]
        )
    """

    def _setup_pyo_object(
        self,
    ):
        super()._setup_pyo_object()
        self.pitch_tracker = pyo.Yin(self.audio_input_microphone.pyo_object)
        self.envelope_follower = pyo.Follower(self.audio_input_microphone.pyo_object)

        partial_count = 32

        import random

        self.q_sine_list = [
            ((pyo.Sine(freq=random.uniform(2, 6), add=1) / 2) + 1) * 2
            for _ in range(partial_count)
        ]

        self.mul_sine_list = [
            (pyo.Sine(freq=random.uniform(1, 4), add=1) / 2) / (_ * 0.5)
            for _ in range(partial_count)
        ]

        self.frequency_list = [
            self.pitch_tracker * (index + 1) for index in range(partial_count)
        ]

        self.resonance_filter = (
            pyo.Resonx(
                self.audio_input_field_recording.pyo_object,
                freq=self.frequency_list,
                # mul=[1 / (partial_index + 1) for partial_index in range(partial_count)],
                mul=self.mul_sine_list,
                q=self.q_sine_list,
                # q=self.q_sine,
                stages=1,
                # decay=0.1
            ).mix(1)
            * self.envelope_follower
            * 8
        )

        self.amplitude_to_decibel = pyo.Min(
            (pyo.Abs(pyo.AToDB(self.envelope_follower)) - 60) * 1.5, 0
        )
        self.print_pitch = pyo.Print(self.amplitude_to_decibel)

        self.filtered_tape = pyo.EQ(
            self.audio_input_field_recording.pyo_object,
            freq=self.frequency_list,
            type=0,
            boost=self.amplitude_to_decibel,
            mul=0.2,
            q=15,
        )

        self.mixed_output = (
            self.filtered_tape
            + self.resonance_filter
            + (self.audio_input_microphone.pyo_object * 0.05)
        ) * self.amplitude_signal_to
        # self.mixed_output = self.resonance_filter
        self.internal_pyo_object_list.extend(
            [self.pitch_tracker, self.envelope_follower, self.resonance_filter]
        )

    @property
    def _pyo_object(self) -> pyo.PyoObject:
        # return self.phase_vocoder_synthesizer
        return self.mixed_output
