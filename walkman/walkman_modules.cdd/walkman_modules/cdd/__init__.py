from __future__ import annotations

import pyo

import walkman


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
