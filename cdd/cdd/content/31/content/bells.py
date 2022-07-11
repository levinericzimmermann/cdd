from mutwo import cdd_converters
from mutwo import common_generators
from mutwo import core_events
from mutwo import core_generators
from mutwo import core_utilities


def main(chapter) -> core_events.SequentialEvent:
    COMPUTE_ALL = True  # except rms_envelope_tuple
    COMPUTE_BELL_SEQUENTIAL_EVENT = False

    attack_dynamic_choice = core_generators.DynamicChoice(
        [0, 1],
        [
            core_events.Envelope(
                [
                    [0, 0.3],
                    [0.2, 0.2],
                    [0.3, 0.2],
                    [0.4, 0.4],
                    [0.45, 0.5],
                    [0.5, 0.3],
                    [0.52, 0],
                    [0.54, 0.2],
                    [0.6, 0.35],
                    [0.7, 0.2],
                    [0.8, 0.1],
                    [0.9, 0.12],
                    [1, 0],
                ]
            ),
            core_events.Envelope([[0, 1], [0, 1]]),
        ],
    )

    distance_tendency = common_generators.Tendency(
        core_events.Envelope(
            [
                # [0, 0.8],
                # [0.2, 0.4],
                # [0.4, 0.1],
                # [0.6, 0],
                # [0.7, 0.09],
                # [0.8, 0],
                # [1, 0.3],
                [0, 0],
                [0.1, 0],
                [0.3, 0.1],
                [0.4, 0.5],
                [0.6, 0.7],
                [0.8, 0.9],
                [1, 0.99],
            ]
        ),
        core_events.Envelope(
            [
                [0, 0.1],
                [0.1, 0.2],
                [0.2, 0.5],
                [0.3, 0.4],
                [0.35, 1],
                [0.4, 0.6],
                [0.45, 1],
                [0.6, 0.8],
                [0.7, 0.9],
                [0.8, 1],
                [1, 1],
            ]
        ),
    )

    pitch_dynamic_choice = chapter.chapter_part_sequence.get_pitch_dynamic_choice(
        chapter.constants.BELL_PITCH_AMBITUS
    )

    # for curve in pitch_dynamic_choice._curve_sequence:
    #     print(curve)

    bell_sample_family_dynamic_choice = core_generators.DynamicChoice(
        ["single", "cloud"],
        [
            core_events.Envelope(
                [
                    [0, 0.5],
                    [0.15, 0.5],
                    [0.2, 0.4],
                    [0.35, 0.5],
                    [0.5, 0.5],
                    [0.55, 0.4],
                    [0.65, 0.5],
                    [1, 0.5],
                ]
            ),
            core_events.Envelope(
                [
                    [0, 0],
                    [0.2, 0.095],
                    [0.3, 0.2],
                    [0.5, 0.5],
                    [0.6, 0.3],
                    [0.8, 0.5],
                    [1, 0.4],
                ]
            ),
        ],
    )

    panning_to_mutated_panning_dynamic_choice = core_generators.DynamicChoice(
        [
            cdd_converters.PanningToScaledPanning(),
            cdd_converters.PanningToMovedPanning(),
            cdd_converters.PanningToUnchangedPanning(),
        ],
        [
            core_events.Envelope([[0, 0], [0.1, 1], [1, 1]]),
            core_events.Envelope([[0, 0], [0.1, 1], [1, 1]]),
            core_events.Envelope([[0, 1], [0.1, 0.3], [1, 0.3]]),
        ],
    )

    attack_sequential_event_selector_envelope = core_events.Envelope(
        [
            [0, 0],
            [0.1, 0],
            [0.2, 1],
            [0.3, 1],
            [0.5, 2],
            [0.55, 3],
            [0.575, 3],
            [0.6, 2],
            [0.7, 1],
            [0.78, 3],
            [0.8, 3],
            [0.83, 2],
            [0.86, 3],
            [1, 3],
        ]
    )

    # Analysis data from sound files
    hop_length = 512
    sound_file_to_attack_sequential_event_tuple = (
        cdd_converters.SoundFileToAttackSequentialEvent(
            delta=0.131,
            pre_avg=1 * chapter.constants.SOUND_FILE.sampling_rate // hop_length,
            post_avg=1 * chapter.constants.SOUND_FILE.sampling_rate // hop_length,
            wait=0.04 * chapter.constants.SOUND_FILE.sampling_rate // hop_length,
        ),
        cdd_converters.SoundFileToAttackSequentialEvent(
            delta=0.12,
            pre_avg=1 * chapter.constants.SOUND_FILE.sampling_rate // hop_length,
            post_avg=1 * chapter.constants.SOUND_FILE.sampling_rate // hop_length,
            wait=0.04 * chapter.constants.SOUND_FILE.sampling_rate // hop_length,
        ),
        cdd_converters.SoundFileToAttackSequentialEvent(
            delta=0.0995,
            pre_avg=1 * chapter.constants.SOUND_FILE.sampling_rate // hop_length,
            post_avg=1 * chapter.constants.SOUND_FILE.sampling_rate // hop_length,
            wait=0.04 * chapter.constants.SOUND_FILE.sampling_rate // hop_length,
        ),
        cdd_converters.SoundFileToAttackSequentialEvent(
            delta=0.085,
            pre_avg=1 * chapter.constants.SOUND_FILE.sampling_rate // hop_length,
            post_avg=1 * chapter.constants.SOUND_FILE.sampling_rate // hop_length,
            wait=0.04 * chapter.constants.SOUND_FILE.sampling_rate // hop_length,
        ),
    )

    sound_file_to_dynamic_attack_sequential_event = (
        cdd_converters.SoundFileToDynamicAttackSequentialEvent(
            sound_file_to_attack_sequential_event_tuple,
        )
    )

    attack_sequential_event_tuple = core_utilities.compute_lazy(
        "builds/pickled/31_bell_attack_sequential_event.pickle",
        force_to_compute=False or COMPUTE_ALL,
    )(
        lambda: tuple(
            sound_file_to_dynamic_attack_sequential_event.convert(
                sound_file,
                attack_sequential_event_selector_envelope=attack_sequential_event_selector_envelope,
            )
            for sound_file in chapter.constants.MONO_SOUND_FILE_COLLECTION
        )
    )()

    rms_envelope_tuple = core_utilities.compute_lazy(
        "builds/pickled/31_bell_rms_envelope_tuple.pickle",
        force_to_compute=False,
    )(
        lambda: tuple(
            sound_file.rms_envelope
            for sound_file in chapter.constants.MONO_SOUND_FILE_COLLECTION
        )
    )()

    # Generate bell sequential event
    bell_sequential_event_blueprint = core_utilities.compute_lazy(
        "builds/pickled/31_bell_sequential_event_blueprint.pickle",
        force_to_compute=False or COMPUTE_ALL or COMPUTE_BELL_SEQUENTIAL_EVENT,
    )(
        lambda: cdd_converters.AttackDynamicChoiceAndAttackSequentialEventTupleToBellSequentialEventBlueprint(
            cdd_converters.AbsoluteBellPositionToPanning()
        ).convert(
            attack_dynamic_choice, attack_sequential_event_tuple
        )
    )()

    bell_sequential_event = core_utilities.compute_lazy(
        "builds/pickled/31_bell_sequential_event.pickle",
        force_to_compute=False or COMPUTE_ALL or COMPUTE_BELL_SEQUENTIAL_EVENT,
    )(
        lambda: cdd_converters.BellSequentialEventBlueprintToBellSequentialEvent(
            pitch_dynamic_choice,
            distance_tendency,
            rms_envelope_tuple,
            panning_to_mutated_panning_dynamic_choice=panning_to_mutated_panning_dynamic_choice,
        ).convert(bell_sequential_event_blueprint)
    )()

    bell_csound_sequential_event = core_utilities.compute_lazy(
        "builds/pickled/31_bell_csound_sequential_event.pickle",
        force_to_compute=False or COMPUTE_ALL or COMPUTE_BELL_SEQUENTIAL_EVENT,
    )(
        lambda: cdd_converters.BellSequentialEventToBellCsoundSequentialEvent(
            chapter.constants.BELL_COLLECTION, bell_sample_family_dynamic_choice
        ).convert(bell_sequential_event)
    )()

    return bell_csound_sequential_event
