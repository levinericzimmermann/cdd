from __future__ import annotations
import bisect
import dataclasses

import abjad
import expenvelope
import quicktions as fractions

from mutwo import core_converters
from mutwo import core_events
from mutwo import core_parameters
from mutwo import music_parameters

from . import classes
from . import configurations


@dataclasses.dataclass
class ClavichordTimeBracket(object):
    # variables specific to time bracket content
    group_index: int
    delay: fractions.Fraction
    sequential_event: core_events.SequentialEvent
    notate_metronome: bool

    # global group attributes
    group_simultaneous_event_tuple: tuple[core_events.SimultaneousEvent, ...]
    group_absolute_time_tuple: tuple[fractions.Fraction, ...]
    group_tempo_envelope: expenvelope.Envelope
    group_sequential_event_grid: core_events.SequentialEvent
    group_sequential_event_grid_with_applied_tempo_envelope: core_events.SequentialEvent

    def __post_init__(self):
        is_rest_list = [
            not (hasattr(note_like, "pitch_list") and note_like.pitch_list)
            for note_like in self.sequential_event
        ]
        is_rest_list_reversed = list(reversed(is_rest_list))
        first_tone_index = is_rest_list_reversed.index(False)
        if first_tone_index > 0:
            self.sequential_event = self.sequential_event[:-first_tone_index]

    @property
    def time_signature_sequence(self) -> tuple[abjad.TimeSignature, ...]:
        duration = fractions.Fraction(self.sequential_event.duration)
        time_signature = abjad.TimeSignature((duration.numerator, duration.denominator))
        return (time_signature,)

    @property
    def absolute_time_in_beats(self) -> fractions.Fraction:
        return self.group_absolute_time_tuple[self.group_index] + self.delay

    @property
    def start_time(self) -> float:
        return float(
            self.group_sequential_event_grid_with_applied_tempo_envelope.absolute_time_tuple[
                self.group_sequential_event_grid.get_event_index_at(
                    self.absolute_time_in_beats
                )
            ]
        )

    @property
    def tempo_envelope(self) -> expenvelope.Envelope:
        if self.notate_metronome:
            point_list = []
        else:
            tempo = self.group_tempo_envelope.value_at(self.absolute_time_in_beats)
            point_list = [
                [
                    0,
                    core_parameters.TempoPoint(
                        tempo / configurations.TEMPO_REFERENCE,
                        reference=configurations.TEMPO_REFERENCE,
                    ),
                ]
            ]
        return expenvelope.Envelope.from_points(*point_list)


@dataclasses.dataclass
class ClavichordTimeBracketContainer(object):
    # global group attributes
    group_simultaneous_event_tuple: tuple[core_events.SimultaneousEvent, ...]
    group_absolute_time_tuple: tuple[fractions.Fraction, ...]
    group_tempo_envelope: expenvelope.Envelope
    group_sequential_event_grid: core_events.SequentialEvent
    group_sequential_event_grid_with_applied_tempo_envelope: core_events.SequentialEvent

    clavichord_time_bracket_list: list[ClavichordTimeBracket] = tuple([])

    def __post_init__(self):
        self.clavichord_time_bracket_list = list(self.clavichord_time_bracket_list)
        self._sort()

        self._group_tempo_envelope_for_clavichord_time_bracket = (
            expenvelope.Envelope.from_points(
                *[
                    [time, value.absolute_tempo_in_beat_per_minute]
                    for time, value in zip(
                        self.group_tempo_envelope.times,
                        self.group_tempo_envelope.levels,
                    )
                ]
            )
        )

    @classmethod
    def from_sequential_event_and_group(
        cls,
        sequential_event: core_events.SequentialEvent,
        group_collection: classes.GroupCollection,
        group_tempo_envelope: expenvelope.Envelope,
    ) -> ClavichordTimeBracketContainer:
        group_sequential_event_grid = group_collection.to_sequential_event_grid
        group_sequential_event_grid_with_applied_tempo_envelope = (
            core_converters.TempoConverter(group_tempo_envelope)(
                group_sequential_event_grid
            )
        )
        group_absolute_time_tuple = group_collection.to_group_absolute_time_tuple
        group_sequential_event_grid_with_applied_tempo_envelope.duration *= 4
        clavichord_time_bracket_container = ClavichordTimeBracketContainer(
            group_collection.to_simultaneous_event_tuple,
            group_absolute_time_tuple,
            group_tempo_envelope,
            group_sequential_event_grid,
            group_sequential_event_grid_with_applied_tempo_envelope,
        )

        # tie rests together
        sequential_event = sequential_event.tie_by(
            lambda event0, event1: not event0.pitch_list and not event1.pitch_list,
            mutate=False,
        )
        start_beat, local_sequential_event = None, core_events.SequentialEvent([])
        clavichord_time_bracket_arguments_list = []
        for absolute_time, note_like in zip(
            sequential_event.absolute_time_tuple, sequential_event
        ):
            if note_like.pitch_list:
                if start_beat is None:
                    start_beat = absolute_time
                local_sequential_event.append(note_like)
            else:
                if note_like.duration > fractions.Fraction(1, 1):
                    if local_sequential_event:
                        group_index = (
                            bisect.bisect_right(group_absolute_time_tuple, start_beat)
                            - 1
                        )
                        delay = start_beat - group_absolute_time_tuple[group_index]
                        notate_metronome = False
                        argument_list = [
                            group_index,
                            delay,
                            local_sequential_event,
                            notate_metronome,
                        ]
                        clavichord_time_bracket_arguments_list.append(argument_list)
                        (
                            start_beat,
                            local_sequential_event,
                        ) = None, core_events.SequentialEvent([])
        clavichord_time_bracket_container.extend_clavichord_time_bracket(
            clavichord_time_bracket_arguments_list
        )
        return clavichord_time_bracket_container

    @property
    def sequential_event(self) -> core_events.SequentialEvent:
        sequential_event = core_events.SequentialEvent([])
        for index, clavichord_time_bracket in enumerate(
            self.clavichord_time_bracket_list
        ):
            start_time = clavichord_time_bracket.start_time
            difference = start_time - sequential_event.duration
            if difference > 0:
                sequential_event.append(core_events.SimpleEvent(difference))
            elif difference < 0:
                raise ValueError(
                    "Found overlapping clavichord time brackets! "
                    f"Number: {index}. TimeBracket: {clavichord_time_bracket}"
                )
            local_sequential_event = core_converters.TempoConverter(
                clavichord_time_bracket.tempo_envelope
            )(clavichord_time_bracket.sequential_event)
            local_sequential_event.duration *= 4
            sequential_event.extend(local_sequential_event)
        return sequential_event

    def _sort(self):
        self.clavichord_time_bracket_list.sort(
            key=lambda clavichord_time_bracket: clavichord_time_bracket.start_time
        )

    def _add_clavichord_time_bracket(self, *args, **kwargs):
        self.clavichord_time_bracket_list.append(
            ClavichordTimeBracket(
                *args,
                group_simultaneous_event_tuple=self.group_simultaneous_event_tuple,
                group_absolute_time_tuple=self.group_absolute_time_tuple,
                group_tempo_envelope=self._group_tempo_envelope_for_clavichord_time_bracket,
                group_sequential_event_grid=self.group_sequential_event_grid,
                group_sequential_event_grid_with_applied_tempo_envelope=self.group_sequential_event_grid_with_applied_tempo_envelope,
                **kwargs,
            )
        )

    def append_clavichord_time_bracket(self, *args, **kwargs):
        self._add_clavichord_time_bracket(*args, **kwargs)
        self._sort()

    def extend_clavichord_time_bracket(self, arguments_sequence: list[list]):
        for args in arguments_sequence:
            self._add_clavichord_time_bracket(*args)
        self._sort()

    def remove(self, index: int):
        del self.clavichord_time_bracket_list[index]

    def __iter__(self):
        return iter(self.clavichord_time_bracket_list)

    def __getitem__(self, index):
        return self.clavichord_time_bracket_list[index]


def post_process(clavichord_time_bracket_container: ClavichordTimeBracketContainer):
    pass
    # clavichord_time_bracket_container.remove(3)
    # clavichord_time_bracket_container.remove(1)
    # clavichord_time_bracket_container.remove(6)

    # clavichord_time_bracket_container[1].sequential_event[2].pitch_list[0].register(-1)
    # clavichord_time_bracket_container[1].sequential_event.set_parameter(
    #     "duration", fractions.Fraction(3, 2)
    # )
    # clavichord_time_bracket_container[1].sequential_event[1].duration = fractions.Fraction(2, 1)
    # clavichord_time_bracket_container[1].sequential_event[2].duration = fractions.Fraction(1, 1)

    clavichord_time_bracket_container[0].delay += fractions.Fraction(2, 1)
    # clavichord_time_bracket_container[2].delay += fractions.Fraction(4, 1)
    clavichord_time_bracket_container[2].delay += fractions.Fraction(8, 4)
    clavichord_time_bracket_container[2].sequential_event[
        0
    ].duration -= fractions.Fraction(1, 4)
    clavichord_time_bracket_container[
        2
        # ].sequential_event = clavichord_time_bracket_container[2].sequential_event[2:]
    ].sequential_event = clavichord_time_bracket_container[2].sequential_event[1:]

    clavichord_time_bracket_container[2].sequential_event[4].set_parameter(
        "pitch_list",
        lambda pitch_list: [
            pitch_list[0] + music_parameters.JustIntonationPitch("3/2"),
            pitch_list[0],
            pitch_list[0] + music_parameters.JustIntonationPitch("2/1"),
            pitch_list[0] + music_parameters.JustIntonationPitch("4/1"),
        ],
    )
    clavichord_time_bracket_container[2].sequential_event[
        4
    ].playing_indicator_collection.arpeggio.direction = "up"
    clavichord_time_bracket_container[2].sequential_event[6].pitch_list = (
        clavichord_time_bracket_container[2].sequential_event[4].pitch_list
    )
    clavichord_time_bracket_container[2].sequential_event[
        6
    ].playing_indicator_collection.arpeggio.direction = "down"

    # clavichord_time_bracket_container[4].delay += fractions.Fraction(1, 2)
    clavichord_time_bracket_container[5].delay += fractions.Fraction(1, 2)
    clavichord_time_bracket_container[
        5
    ].sequential_event = clavichord_time_bracket_container[5].sequential_event[:-1]
    clavichord_time_bracket_container[5].sequential_event[-1].set_parameter(
        "pitch_list",
        lambda pitch_list: [
            pitch_list[0] + music_parameters.JustIntonationPitch("3/2"),
            pitch_list[0] - music_parameters.JustIntonationPitch("3/2"),
            pitch_list[0] - music_parameters.JustIntonationPitch("2/1"),
            pitch_list[0] - music_parameters.JustIntonationPitch("8/1"),
            pitch_list[0],
        ],
    )
    clavichord_time_bracket_container[5].sequential_event[
        -1
    ].playing_indicator_collection.arpeggio.direction = "up"
