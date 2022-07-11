from mutwo import cdd_converters
from mutwo import common_generators
from mutwo import core_events
from mutwo import core_generators
from mutwo import core_utilities


def get_resonator_melody_pair_0(
    chapter,
) -> core_events.SimultaneousEvent[core_events.SequentialEvent]:
    pulse = core_utilities.compute_lazy("builds/pickled/31_sound_file_pulse.pickle")(
        lambda: cdd_converters.SoundFileToPulse().convert(chapter.constants.SOUND_FILE)
    )()

    panning_to_mutated_panning_dynamic_choice = core_generators.DynamicChoice(
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
    )

    panning_generator = cdd_converters.AbsolutePositionToPanning()

    # How often activities change
    heat_envelope: core_events.Envelope = core_events.Envelope(
        [
            [0, 0.1],
            [0.1, 0.1],
            [0.185, 0.2],
            [0.225, 0.5],
            [0.3, 0.7],
            [0.4, 0.6],
            [0.45, 0.4],
            [0.6, 0.8],
            [0.65, 1],
            [0.69, 0.7],
            [0.75, 0.6],
            [0.9, 0.95],
            [0.975, 0.93],
            [1, 0.5],
        ]
    )
    # How many partials a tone has
    partial_count_tendency: common_generators.Tendency = common_generators.Tendency(
        core_events.Envelope(
            [
                [0, 1],
                [0.1, 1],
                [0.2, 3],
                [0.3, 4],
                [0.4, 3],
                [0.5, 5],
                [0.52, 12],
                [0.6, 4],
                [0.7, 15],
                [0.8, 5],
                [0.82, 1],
                [0.9, 15],
                [1, 20],
            ]
        ),
        core_events.Envelope(
            [
                [0, 2],
                [0.2, 5],
                [0.3, 8],
                [0.4, 5],
                [0.5, 12],
                [0.52, 14],
                [0.6, 8],
                [0.7, 22],
                [0.8, 18],
                [0.85, 25],
                [0.9, 18],
                [1, 32],
            ]
        ),
    )
    # Higher values = less silence
    tone_activity_envelope: core_events.Envelope = core_events.Envelope(
        [
            [0, 0.1],
            [0.1, 0.4],
            [0.25, 0.6],
            [0.3, 0.2],
            [0.4, 0.7],
            [0.5, 0.9],
            [0.6, 0.5],
            [0.7, 0.7],
            [0.8, 0.95],
            [1, 1],
        ]
    )
    # For initial register and this also the allowed register range!
    register_tendency: common_generators.Tendency = common_generators.Tendency(
        core_events.Envelope(
            [[0, 0], [0.35, 0], [0.4, -1], [0.6, -1], [0.65, 0], [0.785, -1], [1, -1]]
        ),
        core_events.Envelope(
            [
                [0, 2],
                [0.2, 2],
                [0.3, 2],
                [0.4, 1],
                [0.475, 0],
                [0.525, 0],
                [0.65, 1],
                [0.825, 1],
                [0.895, 1],
                [0.925, 1],
                [1, 1],
            ]
        ),
    )
    # How many filter layers to use
    filter_layer_count_tendency: common_generators.Tendency = (
        common_generators.Tendency(
            core_events.Envelope(
                [
                    [0, 1],
                    [0.1, 2],
                    [0.2, 3],
                    [0.3, 4],
                    [0.4, 3],
                    [0.5, 5],
                    [0.6, 3],
                    [0.7, 4],
                    [0.8, 6],
                    [1, 7],
                ]
            ),
            core_events.Envelope(
                [
                    [0, 2],
                    [0.1, 3],
                    [0.2, 4],
                    [0.3, 5],
                    [0.4, 8],
                    [0.55, 8],
                    [0.6, 12],
                    [0.7, 10],
                    [1, 15],
                ]
            ),
        )
    )
    # Set bandwidth
    bandwidth_start_tendency: common_generators.Tendency = common_generators.Tendency(
        core_events.Envelope(
            [
                [0, 700],
                [0.1, 700],
                [0.2, 120],
                [0.3, 120],
                [0.4, 80],
                [0.45, 50],
                [0.5, 100],
                [0.525, 34],
                [0.6, 24],
                [1, 50],
            ]
        ),
        core_events.Envelope(
            [
                [0, 1500],
                [0.1, 1500],
                [0.2, 130],
                [0.3, 130],
                [0.4, 140],
                [0.45, 600],
                [0.5, 600],
                [0.525, 70],
                [0.6, 43],
                [1, 100],
            ]
        ),
    )
    bandwidth_end_tendency: common_generators.Tendency = common_generators.Tendency(
        core_events.Envelope(
            [
                [0, 120],
                [0.1, 120],
                [0.2, 700],
                [0.3, 700],
                [0.3, 100],
                [0.45, 250],
                [0.53, 70],
                [0.6, 25],
                [0.8, 25],
                [1, 22],
            ]
        ),
        core_events.Envelope(
            [
                [0, 250],
                [0.1, 200],
                [0.2, 1200],
                [0.3, 1200],
                [0.3, 200],
                [0.45, 700],
                [0.53, 100],
                [0.6, 40],
                [0.8, 40],
                [1, 80],
            ]
        ),
    )

    resampled_spectral_centroid_envelope_tuple = cdd_converters.ResampledEnvelopeTuple(
        chapter.constants.MONO_SOUND_FILE_COLLECTION, "spectral_centroid_envelope", 0, 1
    )

    resampled_spectral_contrast_envelope_tuple = cdd_converters.ResampledEnvelopeTuple(
        chapter.constants.MONO_SOUND_FILE_COLLECTION, "spectral_contrast_envelope", 5, 1
    )

    pulse_pair = cdd_converters.PulseToComplementaryPulsePair().convert(pulse)
    simultaneous_event = core_events.SimultaneousEvent([])
    for pulse in pulse_pair:

        pitch_walk_generator_sequential_event = core_events.SequentialEvent([])
        for simple_event in chapter.chapter_part_sequence:
            pitch_walk_generator_sequential_event.append(
                core_events.SimpleEvent(duration=simple_event.duration).set_parameter(
                    "pitch_walk_generator", None
                )
            )

        sequential_event = cdd_converters.PulseToBandpassMelodyEvent(
            heat_envelope=heat_envelope,
            tone_activity_envelope=tone_activity_envelope,
            partial_count_tendency=partial_count_tendency,
            bandwidth_start_tendency=bandwidth_start_tendency,
            bandwidth_end_tendency=bandwidth_end_tendency,
            filter_layer_count_tendency=filter_layer_count_tendency,
            register_tendency=register_tendency,
            panning_generator=panning_generator,
            panning_to_mutated_panning_dynamic_choice=panning_to_mutated_panning_dynamic_choice,
        ).convert(
            pulse,
            chapter.chapter_part_sequence.deterministic_pitch_class_markov_chain_range,
            chapter.chapter_part_sequence.pitch_collection_range,
            pitch_walk_generator_sequential_event,
            resampled_spectral_centroid_envelope_tuple,
            resampled_spectral_contrast_envelope_tuple,
        )
        simultaneous_event.append(sequential_event)

    return simultaneous_event


def get_resonator_melody_pair_1(
    chapter,
) -> core_events.SimultaneousEvent[core_events.SequentialEvent]:
    pulse = core_utilities.compute_lazy("builds/pickled/31_sound_file_pulse.pickle")(
        lambda: cdd_converters.SoundFileToPulse().convert(chapter.constants.SOUND_FILE)
    )()

    panning_to_mutated_panning_dynamic_choice = core_generators.DynamicChoice(
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
    )

    panning_generator = cdd_converters.AbsolutePositionToPanning()

    # How often activites change
    heat_envelope: core_events.Envelope = core_events.Envelope(
        [
            [0, 0.1],
            [0.1, 0.1],
            [0.2, 0.2],
            [0.3, 0.5],
            [0.4, 0.6],
            [0.45, 0.4],
            [0.6, 0.8],
            [0.65, 1],
            [0.69, 0.7],
            [0.75, 0.6],
            [0.9, 0.95],
            [0.975, 0.93],
            [1, 0.5],
        ]
    )
    # How many partials a tone has
    partial_count_tendency: common_generators.Tendency = common_generators.Tendency(
        core_events.Envelope(
            [
                [0, 1],
                [0.1, 1],
                [0.2, 3],
                [0.3, 4],
                [0.4, 3],
                [0.5, 5],
                [0.52, 12],
                [0.6, 4],
                [0.7, 15],
                [0.8, 5],
                [0.82, 1],
                [0.9, 15],
                [1, 20],
            ]
        ),
        core_events.Envelope(
            [
                [0, 2],
                [0.2, 5],
                [0.3, 8],
                [0.4, 5],
                [0.5, 12],
                [0.52, 14],
                [0.6, 8],
                [0.7, 22],
                [0.8, 18],
                [0.85, 25],
                [0.9, 18],
                [1, 32],
            ]
        ),
    )
    # Higher values = less silence
    tone_activity_envelope: core_events.Envelope = core_events.Envelope(
        [
            [0, 0],
            [0.45, 0],
            [0.5, 0.2],
            [0.6, 0.5],
            [0.7, 0.8],
            [0.8, 0.9],
            [1, 0.85],
        ]
    )
    # For initial register and this also the allowed register range!
    register_tendency: common_generators.Tendency = common_generators.Tendency(
        core_events.Envelope(
            [[0, 0], [0.4, -1], [0.6, 0], [0.65, -1], [0.785, 0], [1, 0]]
        ),
        core_events.Envelope(
            [
                [0, 2],
                [0.2, 3],
                [0.3, 2],
                [0.4, 1],
                [0.475, 0],
                [0.525, 0],
                [0.65, 1],
                [0.825, 1],
                [0.895, 1],
                [0.925, 1],
                [1, 2],
            ]
        ),
    )
    # How many filter layers to use
    filter_layer_count_tendency: common_generators.Tendency = (
        common_generators.Tendency(
            core_events.Envelope(
                [
                    [0, 1],
                    [0.1, 2],
                    [0.2, 3],
                    [0.3, 4],
                    [0.4, 3],
                    [0.5, 5],
                    [0.6, 3],
                    [0.7, 4],
                    [0.8, 6],
                    [1, 6],
                ]
            ),
            core_events.Envelope(
                [
                    [0, 3],
                    [0.1, 4],
                    [0.2, 5],
                    [0.3, 6],
                    [0.4, 8],
                    [0.55, 8],
                    [0.6, 12],
                    [0.7, 10],
                    [1, 12],
                ]
            ),
        )
    )
    # Set bandwidth
    bandwidth_start_tendency: common_generators.Tendency = common_generators.Tendency(
        core_events.Envelope(
            [
                [0, 700],
                [0.1, 700],
                [0.2, 30],
                [0.3, 30],
                [0.4, 20],
                [0.45, 200],
                [0.5, 100],
                [0.525, 34],
                [0.6, 24],
                [1, 50],
            ]
        ),
        core_events.Envelope(
            [
                [0, 1500],
                [0.1, 1500],
                [0.2, 80],
                [0.3, 80],
                [0.4, 120],
                [0.45, 600],
                [0.5, 600],
                [0.525, 70],
                [0.6, 43],
                [1, 100],
            ]
        ),
    )
    bandwidth_end_tendency: common_generators.Tendency = common_generators.Tendency(
        core_events.Envelope(
            [
                [0, 100],
                [0.1, 80],
                [0.2, 700],
                [0.3, 700],
                [0.3, 100],
                [0.45, 250],
                [0.53, 70],
                [0.6, 25],
                [0.8, 25],
                [1, 22],
            ]
        ),
        core_events.Envelope(
            [
                [0, 250],
                [0.1, 200],
                [0.2, 1200],
                [0.3, 1200],
                [0.3, 200],
                [0.45, 700],
                [0.53, 100],
                [0.6, 40],
                [0.8, 40],
                [1, 80],
            ]
        ),
    )

    resampled_spectral_centroid_envelope_tuple = cdd_converters.ResampledEnvelopeTuple(
        chapter.constants.MONO_SOUND_FILE_COLLECTION, "spectral_centroid_envelope", 0, 1
    )

    resampled_spectral_contrast_envelope_tuple = cdd_converters.ResampledEnvelopeTuple(
        chapter.constants.MONO_SOUND_FILE_COLLECTION, "spectral_contrast_envelope", 5, 1
    )

    pulse_pair = cdd_converters.PulseToComplementaryPulsePair().convert(pulse)
    simultaneous_event = core_events.SimultaneousEvent([])
    for pulse in pulse_pair:

        pitch_walk_generator_sequential_event = core_events.SequentialEvent([])
        for simple_event in chapter.chapter_part_sequence:
            pitch_walk_generator_sequential_event.append(
                core_events.SimpleEvent(duration=simple_event.duration).set_parameter(
                    "pitch_walk_generator", None
                )
            )

        sequential_event = cdd_converters.PulseToBandpassMelodyEvent(
            heat_envelope=heat_envelope,
            tone_activity_envelope=tone_activity_envelope,
            partial_count_tendency=partial_count_tendency,
            bandwidth_start_tendency=bandwidth_start_tendency,
            bandwidth_end_tendency=bandwidth_end_tendency,
            filter_layer_count_tendency=filter_layer_count_tendency,
            register_tendency=register_tendency,
            panning_generator=panning_generator,
            panning_to_mutated_panning_dynamic_choice=panning_to_mutated_panning_dynamic_choice,
        ).convert(
            pulse,
            chapter.chapter_part_sequence.deterministic_pitch_class_markov_chain_range,
            chapter.chapter_part_sequence.pitch_collection_range,
            pitch_walk_generator_sequential_event,
            resampled_spectral_centroid_envelope_tuple,
            resampled_spectral_contrast_envelope_tuple,
        )
        simultaneous_event.append(sequential_event)

    return simultaneous_event


def main(chapter) -> core_events.SimultaneousEvent[core_events.SequentialEvent]:
    resonator_melody_pair_0 = get_resonator_melody_pair_0(chapter)
    resonator_melody_pair_1 = get_resonator_melody_pair_1(chapter)
    return resonator_melody_pair_0 + resonator_melody_pair_1
