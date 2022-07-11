"""Monkey patch ComplexEvent by adding new methods to the class

Mostly for catching events with specific characteristics
"""

import typing

from mutwo import core_events
from mutwo import core_utilities


# Default value is too high, we still have rounding errors
core_events.configurations.ROUND_DURATION_TO_N_DIGITS = 7


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


# Apply bugfix for floating point errors
# (maybe this fix will never be applied to mutwo due to the migration to fractions)
def Envelope__value_at(self, absolute_time):
    absolute_time_tuple = self.absolute_time_tuple

    use_only_first_event = absolute_time <= absolute_time_tuple[0]
    use_only_last_event = absolute_time >= (
        # If the duration of the last event == 0 there is the danger
        # of floating point errors (the value in absolute_time_tuple could
        # be slightly higher than the duration of the Envelope. If this
        # happens the function will raise an AssertionError, because
        # "_get_index_at_from_absolute_time_tuple" will return
        # "None"). With explicitly testing if the last duration
        # equals 0 we can avoid this danger.
        absolute_time_tuple[-1]
        if self[-1].duration > 0
        else self.duration
    )
    if use_only_first_event or use_only_last_event:
        index = 0 if use_only_first_event else -1
        return self._event_to_value(self[index])

    event_0_index = self._get_index_at_from_absolute_time_tuple(
        absolute_time, absolute_time_tuple, self.duration
    )
    assert event_0_index is not None

    # XXX: Prevent floating point errors (for instance if
    # duration of event == 1 and absolute_time == 0.999999999)
    value_list = []
    absolute_time_list = []
    for index_offset in range(2):
        index = event_0_index + index_offset
        try:
            event = self[index]
        except IndexError:
            return value_list[0]
        else:
            value = self._event_to_value(event)
            local_absolute_time = absolute_time_tuple[index]
        value_list.append(value)
        absolute_time_list.append(local_absolute_time)

    curve_shape = self.event_to_curve_shape(self[event_0_index])

    return core_utilities.scale(
        absolute_time,
        *absolute_time_list,
        *value_list,
        curve_shape,
    )


core_events.Envelope.value_at = Envelope__value_at
