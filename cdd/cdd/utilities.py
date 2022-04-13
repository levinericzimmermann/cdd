import typing

from mutwo import core_events

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
