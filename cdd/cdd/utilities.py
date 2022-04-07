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
