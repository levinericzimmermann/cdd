import copy
import typing

from mutwo import core_converters
from mutwo import core_constants
from mutwo import core_events
from mutwo import music_converters
from mutwo import music_parameters


__all__ = (
    "EventToTransposedEvent",
    "EventToEventWithWoodwindFingering",
)


class EventToTransposedEvent(core_converters.abc.SymmetricalEventConverter):
    def __init__(
        self,
        transposition_interval: music_parameters.abc.PitchInterval,
        simple_event_to_pitch_list: typing.Callable[
            [core_events.SimpleEvent], list[music_parameters.abc.Pitch]
        ] = music_converters.SimpleEventToPitchList(),
    ):
        self._transposition_interval = transposition_interval
        self._simple_event_to_pitch_list = simple_event_to_pitch_list

    def _convert_simple_event(
        self,
        event_to_convert: core_events.SimpleEvent,
        _: core_constants.DurationType,
    ) -> core_events.SimpleEvent:
        pitch_list = self._simple_event_to_pitch_list(event_to_convert)
        if pitch_list:
            # We can change the actual objects, because we copy
            # the input event in the public 'convert' method.
            for pitch in pitch_list:
                pitch.add(self._transposition_interval)
        return event_to_convert

    def convert(self, event_to_convert: core_events.abc.Event) -> core_events.abc.Event:
        return self._convert_event(copy.deepcopy(event_to_convert), 0)


class EventToEventWithWoodwindFingering(core_converters.abc.SymmetricalEventConverter):
    def __init__(
        self,
        exponent_tuple_to_woodwind_fingering: dict[
            tuple[int, ...], music_parameters.WoodwindFingering
        ],
    ):
        self._exponent_tuple_to_woodwind_fingering = (
            exponent_tuple_to_woodwind_fingering
        )

    def _convert_simple_event(
        self,
        event_to_convert: core_events.SimpleEvent,
        _: core_constants.DurationType,
    ) -> core_events.SimpleEvent:
        if hasattr(event_to_convert, "playing_indicator_collection"):
            woodwind_fingering = None
            for pitch in event_to_convert.pitch_list:
                if pitch.exponent_tuple in self._exponent_tuple_to_woodwind_fingering:
                    woodwind_fingering = self._exponent_tuple_to_woodwind_fingering[
                        pitch.exponent_tuple
                    ]
                    break
            if woodwind_fingering:
                event_to_convert.playing_indicator_collection.woodwind_fingering.right_hand = (
                    woodwind_fingering.right_hand
                )
                event_to_convert.playing_indicator_collection.woodwind_fingering.left_hand = (
                    woodwind_fingering.left_hand
                )
                event_to_convert.playing_indicator_collection.woodwind_fingering.cc = (
                    woodwind_fingering.cc
                )
        return event_to_convert

    def convert(self, event_to_convert: core_events.abc.Event) -> core_events.abc.Event:
        return self._convert_event(copy.deepcopy(event_to_convert), 0)
