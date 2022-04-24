import copy

from mutwo import core_converters
from mutwo import core_events
from mutwo import music_events


__all__ = ("SimpleEventToPhonemeString", "SequentialEventToMbrolaFriendlyEvent")


class SimpleEventToPhonemeString(core_converters.SimpleEventToAttribute):
    """Convert a simple event to a phoneme string."""

    def __init__(
        self,
        attribute_name: str = "phonetic_representation",
        exception_value: str = "_",
    ):
        super().__init__(attribute_name, exception_value)


class SequentialEventToMbrolaFriendlyEvent(core_converters.abc.EventConverter):
    def _convert_simple_event(self, event_to_convert, _):
        event_to_convert = event_to_convert.set_parameter(
            "duration", lambda duration: float(duration), mutate=False
        )
        sequential_event = core_events.SequentialEvent([])
        try:
            phonetic_representation = event_to_convert.lyric.phonetic_representation
        except AttributeError:
            phonetic_representation = None
        if phonetic_representation:
            # phonetic_representation = [
            #     phoneme for phoneme in phonetic_representation if phoneme != "~"
            # ]
            duration_per_event = event_to_convert.duration / len(
                phonetic_representation
            )
            for phoneme in phonetic_representation:
                new_event = music_events.NoteLike(
                    copy.deepcopy(event_to_convert.pitch_list),
                    duration=duration_per_event,
                )
                new_event.phoneme = phoneme
                sequential_event.append(new_event)
        else:
            sequential_event.append(event_to_convert)
        return sequential_event

    def _convert_sequential_event(self, event_to_convert, absolute_entry_delay):
        return core_events.SequentialEvent(
            super()._convert_sequential_event(event_to_convert, absolute_entry_delay)
        )

    def convert(self, event_to_convert):
        return self._convert_event(event_to_convert, 0)
