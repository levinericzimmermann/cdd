"""Monkey patch ComplexEvent by adding new methods to the class

Mostly for catching events with specific characteristics
"""

import typing

from mutwo import core_events


def ComplexEvent_get_event_iterator_by(
    self, **parameter_to_value
) -> typing.Iterator[core_events.abc.Event]:
    def test(event_to_test: core_events.abc.Event) -> bool:
        for parameter, value in parameter_to_value.items():
            if not (
                hasattr(event_to_test, parameter)
                and getattr(event_to_test, parameter) == value
            ):
                return False
        return True

    return (event for event in self if test(event))


core_events.abc.ComplexEvent.get_event_iterator_by = ComplexEvent_get_event_iterator_by
