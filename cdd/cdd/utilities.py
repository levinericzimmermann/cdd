import datetime
import typing

import abjad
import gradient_free_optimizers

from mutwo import core_events
from mutwo import music_converters

import cdd


def add_instrument_name(
    simultaneous_event: core_events.SimultaneousEvent[
        typing.Union[
            core_events.TaggedSequentialEvent, core_events.TaggedSimultaneousEvent
        ]
    ]
):
    for tagged_event in simultaneous_event:
        if tagged_event.tag in cdd.constants.SHORT_INSTRUMENT_NAME_TO_INSTRUMENT_NAME:
            tagged_event.instrument_name = (
                cdd.constants.SHORT_INSTRUMENT_NAME_TO_INSTRUMENT_NAME[tagged_event.tag]
            )
            tagged_event.short_instrument_name = tagged_event.tag


def add_cent_deviation_to_sequential_event(
    sequential_event_to_process: core_events.SequentialEvent,
    process_grace_notes: bool = True,
):
    for event in sequential_event_to_process:
        if hasattr(event, "pitch_list") and event.pitch_list:
            pitch_to_process = event.pitch_list[0]
            if len(pitch_to_process.exponent_tuple) > 2 and any(
                pitch_to_process.exponent_tuple[2:]
            ):
                deviation = (
                    pitch_to_process.cent_deviation_from_closest_western_pitch_class
                )
                event.notation_indicator_collection.cent_deviation.deviation = deviation

        if process_grace_notes:
            for grace_note_attribute in (
                "grace_note_sequential_event",
                "after_grace_note_sequential_event",
            ):
                if hasattr(event, grace_note_attribute):
                    add_cent_deviation_to_sequential_event(
                        getattr(event, grace_note_attribute), False
                    )


def clavichord_sequential_event_to_tabulatura(
    sequential_event_to_process: core_events.SequentialEvent[core_events.SimpleEvent],
) -> core_events.SequentialEvent:
    just_intonation_pitch_list_tuple = tuple(
        pitch_list if pitch_list else []
        for pitch_list in sequential_event_to_process.get_parameter("pitch_list")
    )
    western_pitch_list_tuple = tuple(
        [
            cdd.constants.CLAVICHORD_PITCH_TO_TABULATURA_PITCH.convert(
                just_intonation_pitch
            )
            for just_intonation_pitch in pitch_list
        ]
        for pitch_list in just_intonation_pitch_list_tuple
    )
    # filtered_western_pitch_list_tuple = tuple(
    #     western_pitch_list
    #     for western_pitch_list in western_pitch_list_tuple
    #     if western_pitch_list
    # )
    improve_western_pitch_list_sequence_readability = music_converters.ImproveWesternPitchListSequenceReadability(
        sequential_pitch_weight=0.64,
        optimizer_class=gradient_free_optimizers.RandomSearchOptimizer,
        # optimizer_class=gradient_free_optimizers.RepulsingHillClimbingOptimizer,
        # optimizer_class=gradient_free_optimizers.HillClimbingOptimizer,
        # optimizer_class=gradient_free_optimizers.ParticleSwarmOptimizer,
        # optimizer_class=gradient_free_optimizers.BayesianOptimizer,
        # optimizer_class=gradient_free_optimizers.EvolutionStrategyOptimizer,
        # optimizer_class=gradient_free_optimizers.SimulatedAnnealingOptimizer,
        # optimizer_class=gradient_free_optimizers.ParallelAnnealingOptimizer,
        # optimizer_class=gradient_free_optimizers.GridSearchOptimizer,
        # optimizer_class=gradient_free_optimizers.RandomRestartHillClimbingOptimizer,
        verbosity_list=["progress_bar", "print_results", "print_times"],
        iteration_count=cdd.configurations.IMPROVE_WESTERN_PITCH_LIST_ITERATION_COUNT,
    )
    # filtered_western_pitch_list_tuple = (
    #     improve_western_pitch_list_sequence_readability.convert(
    #         filtered_western_pitch_list_tuple
    #     )
    # )

    western_pitch_list_list = list(western_pitch_list_tuple)
    rest_index_list = [
        index
        for index, pitch_list in enumerate(western_pitch_list_list)
        if not pitch_list
    ]
    for x, y in zip([0] + rest_index_list, rest_index_list):
        difference = y - x
        if difference > 1:
            western_pitch_list_list[
                x + 1 : y
            ] = improve_western_pitch_list_sequence_readability.convert(
                western_pitch_list_tuple[x + 1 : y]
            )
    western_pitch_list_tuple = tuple(western_pitch_list_list)
    # western_pitch_list_tuple = (
    #     improve_western_pitch_list_sequence_readability.convert(
    #         western_pitch_list_tuple
    #     )
    # )

    # western_pitch_list_iterator = iter(filtered_western_pitch_list_tuple)

    new_sequential_event = sequential_event_to_process.copy()
    for index, pitch_list in enumerate(western_pitch_list_tuple):
        if pitch_list:
            # new_sequential_event[index].pitch_list = next(western_pitch_list_iterator)
            new_sequential_event[index].pitch_list = pitch_list

    return new_sequential_event


def clarinet_event_to_notatable_clarinet_event(
    clarinet_event_to_process: core_events.abc.Event,
) -> core_events.abc.Event:
    clarinet_event_with_fingering = (
        cdd.constants.CLARINET_EVENT_TO_CLARINET_EVENT_WITH_FINGERING(
            clarinet_event_to_process
        )
    )
    transposed_clarinet_event = (
        cdd.constants.CLARINET_EVENT_TO_TRANSPOSED_CLARINET_EVENT(
            clarinet_event_with_fingering
        )
    )
    return transposed_clarinet_event


def duration_in_seconds_to_readable_duration(duration_in_seconds: float) -> str:
    _, minutes, seconds = str(datetime.timedelta(seconds=duration_in_seconds)).split(
        ":"
    )
    return f"{minutes}'{seconds[:2]}"


def is_rest(event: core_events.SimpleEvent) -> bool:
    if hasattr(event, "pitch_list"):
        return not bool(event.pitch_list)
    return True


def add_last_bar_line(last_leaf: abjad.Leaf, barline: str = "|."):
    abjad.attach(
        abjad.LilyPondLiteral(
            (
                r"\undo \omit StaffGroup.SpanBar "
                r"\undo \omit PianoStaff.SpanBar "
                r"\undo \omit Staff.BarLine \bar "
                f'"{barline}"'
            ),
            format_slot="after",
        ),
        last_leaf,
    )
