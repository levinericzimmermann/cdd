import itertools
import typing

import numpy as np
import ranges

from mutwo import cdd_converters
from mutwo import cdd_events
from mutwo import cdd_parameters
from mutwo import common_generators
from mutwo import core_converters
from mutwo import core_events
from mutwo import core_generators
from mutwo import core_utilities
from mutwo import music_parameters

__all__ = (
    "PulseToComplementaryPulsePair",
    "PulseToBandpassMelodyEvent",
    "ResampledEnvelopeTuple",
    "ResonatorSequentialEventToResonatorSequentialEventWithEnvelope",
)


class PulseToComplementaryPulsePair(core_converters.abc.Converter):
    def convert(
        self, pulse_to_convert: core_events.SequentialEvent[core_events.SimpleEvent]
    ) -> core_events.SimultaneousEvent[
        core_events.SequentialEvent[core_events.SimpleEvent]
    ]:
        complementary_pulse_pair = core_events.SimultaneousEvent(
            [core_events.SequentialEvent([]) for _ in range(2)]
        )
        switch_cycle = common_generators.ActivityLevel()
        paradiddle_size_cycle = itertools.cycle((6, 8, 10, 6, 8, 12, 10))
        pulse_count = len(pulse_to_convert)
        duration_tuple = pulse_to_convert.get_parameter("duration")
        index = 0
        while index < pulse_count:
            paradiddle_size = next(paradiddle_size_cycle)
            pulse_index_tuple0, pulse_index_tuple1 = common_generators.paradiddle(
                paradiddle_size
            )
            if switch_cycle(5):
                pulse_index_tuple0, pulse_index_tuple1 = (
                    pulse_index_tuple1,
                    pulse_index_tuple0,
                )

            for voice_index, pulse_index_tuple in enumerate(
                (pulse_index_tuple0, pulse_index_tuple1)
            ):
                for index_pair in zip(
                    pulse_index_tuple, pulse_index_tuple[1:] + (paradiddle_size,)
                ):
                    event_index0, event_index1 = (
                        local_index + index for local_index in index_pair
                    )
                    if event_index0 < pulse_count:
                        duration = sum(duration_tuple[event_index0:event_index1])
                        simple_event = pulse_to_convert[event_index0].set_parameter(
                            "duration", duration, mutate=False
                        )
                        complementary_pulse_pair[voice_index].append(simple_event)

            index += paradiddle_size
        return complementary_pulse_pair


class ResampledEnvelopeTuple(tuple):
    def __init__(
        self,
        _: cdd_parameters.MonoSoundFileContainer,
        envelope_name: str,
        *args,
        **kwargs,
    ):
        self.envelope_name = envelope_name
        super().__init__()

    def __new__(
        cls,
        mono_sound_file_container: cdd_parameters.MonoSoundFileContainer,
        envelope_name: str,
        new_minima: float = 0,
        new_maxima: float = 1,
    ):
        envelope_tuple = core_utilities.compute_lazy(
            f"builds/pickled/31_{envelope_name}_tuple.pickle"
        )(
            lambda envelope_name: tuple(
                getattr(soundfile, envelope_name)
                for soundfile in mono_sound_file_container
            )
        )(
            envelope_name
        )

        envelope_minima_tuple = tuple(
            min(envelope.get_parameter("value")) for envelope in envelope_tuple
        )
        envelope_maxima_tuple = tuple(
            max(envelope.get_parameter("value")) for envelope in envelope_tuple
        )

        resampled_envelope_tuple = core_utilities.compute_lazy(
            f"builds/pickled/31_{envelope_name}_tuple_resampled.pickle"
        )(
            lambda _, new_minima, new_maxima: tuple(
                envelope.set_parameter(
                    "value",
                    lambda value: core_utilities.scale(
                        value,
                        envelope_minima,
                        envelope_maxima,
                        new_minima,
                        new_maxima,
                    ),
                    mutate=False,
                )
                for envelope, envelope_minima, envelope_maxima in zip(
                    envelope_tuple,
                    envelope_minima_tuple,
                    envelope_maxima_tuple,
                )
            )
        )(
            envelope_name, new_minima, new_maxima
        )

        return super().__new__(cls, resampled_envelope_tuple)

    def get_local_envelope_tuple(
        self, start_time: float, end_time: float
    ) -> tuple[core_events.Envelope, ...]:
        envelope_tuple = core_utilities.compute_lazy(
            f"builds/pickled/31_{self.envelope_name}_tuple_selection_{start_time}_{end_time}.pickle"
        )(
            lambda: tuple(
                envelope.cut_out(start_time, end_time, mutate=False)
                for envelope in self
            )
        )()
        return envelope_tuple


class ResonatorSequentialEventToResonatorSequentialEventWithEnvelope(
    core_converters.abc.Converter
):
    def convert(
        self,
        resonator_sequential_event: core_events.SequentialEvent,
        resampled_spectral_centroid_envelope_tuple: ResampledEnvelopeTuple,
        resampled_spectral_contrast_envelope_tuple: ResampledEnvelopeTuple,
    ) -> core_events.SequentialEvent:
        resonator_sequential_event = resonator_sequential_event.copy()
        absolute_time_tuple = resonator_sequential_event.absolute_time_tuple
        for start, end, simple_event in zip(
            absolute_time_tuple, absolute_time_tuple[1:], resonator_sequential_event
        ):
            if isinstance(simple_event, cdd_events.ResonatorEvent):
                local_spectral_centroid_envelope_tuple = (
                    resampled_spectral_centroid_envelope_tuple.get_local_envelope_tuple(
                        start, end
                    )
                )
                local_spectral_contrast_envelope_tuple = (
                    resampled_spectral_contrast_envelope_tuple.get_local_envelope_tuple(
                        start, end
                    )
                )
                simple_event.spectral_centroid_envelope_tuple = (
                    local_spectral_centroid_envelope_tuple
                )
                simple_event.spectral_contrast_envelope_tuple = (
                    local_spectral_contrast_envelope_tuple
                )

        return resonator_sequential_event


class PulseToBandpassMelodyEvent(core_converters.abc.Converter):
    def __init__(
        self,
        # Higher values = events are happening faster
        heat_envelope: core_events.Envelope = core_events.Envelope(
            [[0, 0.5], [1, 0.5]]
        ),
        # How many partials a tone has
        partial_count_tendency: common_generators.Tendency = common_generators.Tendency(
            core_events.Envelope([[0, 3], [1, 5]]),
            core_events.Envelope([[0, 6], [1, 8]]),
        ),
        # Higher values = less silence
        tone_activity_envelope: core_events.Envelope = core_events.Envelope(
            [[0, 0.5], [1, 0.85]]
        ),
        # For initial register and this also the allowed register range!
        register_tendency: common_generators.Tendency = common_generators.Tendency(
            core_events.Envelope([[0, 0], [1, 0]]),
            core_events.Envelope([[0, 2], [1, 2]]),
        ),
        # How many filter layers to use
        filter_layer_count_tendency: common_generators.Tendency = common_generators.Tendency(
            core_events.Envelope([[0, 4], [1, 4]]),
            core_events.Envelope([[0, 6], [1, 6]]),
        ),
        # Set bandwidth
        bandwidth_start_tendency: common_generators.Tendency = common_generators.Tendency(
            core_events.Envelope([[0, 50], [1, 50]]),
            core_events.Envelope([[0, 100], [1, 100]]),
        ),
        bandwidth_end_tendency: common_generators.Tendency = common_generators.Tendency(
            core_events.Envelope([[0, 50], [1, 50]]),
            core_events.Envelope([[0, 100], [1, 100]]),
        ),
        panning_to_mutated_panning_dynamic_choice: core_generators.DynamicChoice = core_generators.DynamicChoice(
            [
                cdd_converters.PanningToScaledPanning(),
                cdd_converters.PanningToMovedPanning(),
                cdd_converters.PanningToUnchangedPanning(),
            ],
            [
                core_events.Envelope([[0, 0.7], [1, 0.7]]),
                core_events.Envelope([[0, 1], [1, 1]]),
                core_events.Envelope([[0, 0.2], [0.1, 0.2], [1, 0.2]]),
            ],
        ),
        panning_generator: cdd_converters.AbsolutePositionToPanning = cdd_converters.AbsolutePositionToPanning(),
        # random seed
        seed: int = 436543,
    ):
        self.panning_generator = panning_generator
        self.panning_to_mutated_panning_dynamic_choice = (
            panning_to_mutated_panning_dynamic_choice
        )
        self.heat_envelope = heat_envelope
        self.partial_count_tendency = partial_count_tendency
        self.tone_activity_envelope = tone_activity_envelope
        self.register_tendency = register_tendency
        self.filter_layer_count_tendency = filter_layer_count_tendency
        self.random = np.random.default_rng(seed)
        self.reset_activity_level = common_generators.ActivityLevel()
        self.reset_activity_level_index = 4
        self.bandwidth_start_tendency = bandwidth_start_tendency
        self.bandwidth_end_tendency = bandwidth_end_tendency

    def _get_next_resonator_event(
        self,
        simple_event: core_events.SimpleEvent,
        previous_pitch: typing.Optional[music_parameters.abc.Pitch],
        pitch_walk_generator,
        absolute_position: float,
    ):
        pitch_class = music_parameters.JustIntonationPitch(next(pitch_walk_generator))
        if previous_pitch:
            pitch = pitch_class.move_to_closest_register(previous_pitch)
        else:
            pitch = pitch_class.register(
                int(round(self.register_tendency.value_at(absolute_position)))
            )

        partial_count = int(
            round(self.partial_count_tendency.value_at(absolute_position))
        )
        filter_layer_count = int(
            round(self.filter_layer_count_tendency.value_at(absolute_position))
        )
        bandwidth_start = self.bandwidth_start_tendency.value_at(absolute_position)
        bandwidth_end = self.bandwidth_end_tendency.value_at(absolute_position)
        panning_start = self.panning_generator(absolute_position)
        panning_end = self.panning_to_mutated_panning_dynamic_choice.gamble_at(
            absolute_position
        )(panning_start)
        return cdd_events.ResonatorEvent(
            pitch=pitch,
            panning_start=panning_start,
            panning_end=panning_end,
            duration=simple_event.duration,
            filter_layer_count=filter_layer_count,
            partial_count=partial_count,
            bandwidth_start=bandwidth_start,
            bandwidth_end=bandwidth_end,
            volume=music_parameters.DecibelVolume(-12),
        )

    def _get_pitch_walk_generator_and_previous_pitch(
        self,
        pitch_walk_generator_sequential_event,
        absolute_time,
        is_last_event_active,
        pitch_collection_range,
        deterministic_pitch_class_markov_chain_range,
        previous_pitch,
    ):
        if not (
            pitch_walk_generator := (
                pitch_walk_generator_sequential_event.get_event_at(absolute_time)
                or pitch_walk_generator_sequential_event[-1]
            ).pitch_walk_generator
        ) or (
            not is_last_event_active
            and self.reset_activity_level(self.reset_activity_level_index)
        ):
            pitch_class_to_weight_dict = pitch_collection_range[
                absolute_time
            ].pitch_class_to_weight_dict
            pitch_class_tuple, weight_tuple = (
                tuple(zipped) for zipped in zip(*pitch_class_to_weight_dict.items())
            )
            initial_pitch_class = self.random.choice(
                pitch_class_tuple,
                p=core_utilities.scale_sequence_to_sum(weight_tuple, 1),
            )
            pitch_walk_generator_event_index = (
                pitch_walk_generator_sequential_event.get_event_index_at(absolute_time)
            ) or len(pitch_walk_generator_sequential_event) - 1
            pitch_walk_generator_event = pitch_walk_generator_sequential_event[
                pitch_walk_generator_event_index
            ]

            pitch_walk_generator_event.pitch_walk_generator = (
                pitch_walk_generator
            ) = deterministic_pitch_class_markov_chain_range[
                absolute_time
            ].walk_deterministic(
                (initial_pitch_class,),
            )

            previous_pitch = None

        return pitch_walk_generator, previous_pitch

    def _is_last_event_active(self, sequential_event) -> bool:
        try:
            is_last_event_active = isinstance(
                sequential_event[-1], cdd_events.ResonatorEvent
            )
        except IndexError:
            is_last_event_active = False

        return is_last_event_active

    def _convert_simple_event(
        self,
        simple_event,
        absolute_time,
        duration,
        sequential_event,
        pitch_walk_generator_sequential_event,
        pitch_collection_range,
        deterministic_pitch_class_markov_chain_range,
        previous_pitch,
    ):
        absolute_position = absolute_time / duration
        event_likelihood = simple_event.onset_strength * self.heat_envelope.value_at(
            absolute_position
        )

        is_last_event_active = self._is_last_event_active(sequential_event)
        if not is_last_event_active:
            event_likelihood = (
                event_likelihood
                + self.tone_activity_envelope.value_at(absolute_position)
            ) / 2

        if self.random.uniform(0, 1) <= event_likelihood:
            if is_last_event_active:
                play_tone = self.random.uniform(
                    0, 1
                ) <= self.tone_activity_envelope.value_at(absolute_position)
            else:
                play_tone = True

            if not play_tone:
                if is_last_event_active or not sequential_event:
                    sequential_event.append(
                        core_events.SimpleEvent(simple_event.duration)
                    )
                else:
                    sequential_event[-1].duration += simple_event.duration

            else:
                (
                    pitch_walk_generator,
                    previous_pitch,
                ) = self._get_pitch_walk_generator_and_previous_pitch(
                    pitch_walk_generator_sequential_event,
                    absolute_time,
                    is_last_event_active,
                    pitch_collection_range,
                    deterministic_pitch_class_markov_chain_range,
                    previous_pitch,
                )

                resonator_event = self._get_next_resonator_event(
                    simple_event,
                    previous_pitch,
                    pitch_walk_generator,
                    absolute_position,
                )
                previous_pitch = resonator_event.pitch
                sequential_event.append(resonator_event)

        else:
            try:
                sequential_event[-1].duration += simple_event.duration
            except IndexError:
                sequential_event.append(core_events.SimpleEvent(simple_event.duration))

        return previous_pitch

    def convert(
        self,
        pulse_to_convert: core_events.SequentialEvent[core_events.SimpleEvent],
        deterministic_pitch_class_markov_chain_range: ranges.RangeDict,
        pitch_collection_range: ranges.RangeDict,
        pitch_walk_generator_sequential_event: core_events.SequentialEvent,
        resampled_spectral_centroid_envelope_tuple: ResampledEnvelopeTuple,
        resampled_spectral_contrast_envelope_tuple: ResampledEnvelopeTuple,
    ) -> core_events.SequentialEvent[cdd_events.ResonatorEvent]:
        onset_strength_tuple = pulse_to_convert.get_parameter("onset_strength")
        minimal_onset_strength, maximal_onset_strength = min(onset_strength_tuple), max(
            onset_strength_tuple
        )
        pulse_to_convert = pulse_to_convert.set_parameter(
            "onset_strength",
            lambda onset_strength: core_utilities.scale(
                onset_strength, minimal_onset_strength, maximal_onset_strength, 0, 1
            ),
            mutate=False,
        )
        previous_pitch = None
        duration = pulse_to_convert.duration
        sequential_event = core_events.SequentialEvent([])
        for absolute_time, simple_event in zip(
            pulse_to_convert.absolute_time_tuple, pulse_to_convert
        ):
            previous_pitch = self._convert_simple_event(
                simple_event,
                absolute_time,
                duration,
                sequential_event,
                pitch_walk_generator_sequential_event,
                pitch_collection_range,
                deterministic_pitch_class_markov_chain_range,
                previous_pitch,
            )

        return ResonatorSequentialEventToResonatorSequentialEventWithEnvelope().convert(
            sequential_event,
            resampled_spectral_centroid_envelope_tuple,
            resampled_spectral_contrast_envelope_tuple,
        )
