from __future__ import annotations
import bisect
import copy
import dataclasses

import abjad
import expenvelope
import quicktions as fractions

from mutwo import core_converters
from mutwo import core_events
from mutwo import core_parameters
from mutwo import core_utilities
from mutwo import music_events
from mutwo import music_parameters

from cdd import constants as cdd_constants

from . import classes
from . import configurations
from . import constants


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
    group_metronome_sequential_event: core_events.SequentialEvent
    group_time_signature_sequence: tuple
    group_time_signature_absolute_time_sequence: tuple

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
        if self.notate_metronome:
            time_signature_sequence = self.group_time_signature_sequence[
                self.start_time_signature_index :
            ]
        else:
            duration = fractions.Fraction(self.sequential_event.duration)
            time_signature_sequence = (
                abjad.TimeSignature((duration.numerator, duration.denominator)),
            )
        return time_signature_sequence

    @property
    def base_absolute_time_in_beats(self) -> fractions.Fraction:
        return self.group_absolute_time_tuple[self.group_index] + self.delay

    @property
    def start_time_signature_index(self) -> int:
        base_absolute_time_in_beats = self.base_absolute_time_in_beats
        index = (
            bisect.bisect_right(
                self.group_time_signature_absolute_time_sequence,
                base_absolute_time_in_beats,
            )
            - 1
        )
        if (
            self.group_time_signature_absolute_time_sequence[index]
            - base_absolute_time_in_beats
        ) == 0:
            index -= 1
        return index

    @property
    def end_time_signature_index(self) -> int:
        end_time = self.base_absolute_time_in_beats + self.sequential_event.duration
        return bisect.bisect_right(
            self.group_time_signature_absolute_time_sequence,
            end_time,
        )

    @property
    def absolute_time_in_beats(self) -> fractions.Fraction:
        if self.notate_metronome:
            return self.group_time_signature_absolute_time_sequence[
                self.start_time_signature_index
            ]
        else:
            return self.base_absolute_time_in_beats

    @property
    def absolute_end_time_in_beats(self) -> fractions.Fraction:
        return self.group_time_signature_absolute_time_sequence[
            self.end_time_signature_index
        ]

    @property
    def absolute_duration(self) -> fractions.Fraction:
        return self.absolute_end_time_in_beats - self.absolute_time_in_beats

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
            envelope_hint = self.group_tempo_envelope.split_at(
                self.absolute_time_in_beats
            )[1].split_at(self.absolute_end_time_in_beats)[0]
            extrema_point_time_list = [0]
            # extrema_point_time_list = envelope_hint.local_extrema()
            # duration = float(self.absolute_duration)
            # if 0 not in extrema_point_time_list:
            #     extrema_point_time_list.append(0)
            # if duration not in extrema_point_time_list:
            #     extrema_point_time_list.append(duration)
            # extrema_point_time_list = sorted(extrema_point_time_list)
            point_list = [
                [
                    time,
                    core_parameters.TempoPoint(
                        envelope_hint.value_at(time) / configurations.TEMPO_REFERENCE,
                        reference=configurations.TEMPO_REFERENCE,
                    ),
                ]
                for time in extrema_point_time_list
            ]
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
        envelope = expenvelope.Envelope.from_points(*point_list)
        return envelope

    @property
    def metronome_sequential_event(self) -> core_events.SequentialEvent:
        start = self.absolute_time_in_beats
        end = start + self.sequential_event.duration
        return self.group_metronome_sequential_event.cut_out(start, end, mutate=False)

    def get_sequential_event(self) -> core_events.SequentialEvent:
        if self.notate_metronome:
            new_sequential_event = self.sequential_event.copy()
            difference = self.base_absolute_time_in_beats - self.absolute_time_in_beats
            if difference:
                new_sequential_event.insert(0, music_events.NoteLike([], difference))
            # expected_duration = (
            #     self.absolute_end_time_in_beats - self.absolute_time_in_beats
            # )
            # difference = expected_duration - new_sequential_event.duration
            # if difference:
            #     new_sequential_event.append(music_events.NoteLike([], difference))
            return new_sequential_event
        else:
            return self.sequential_event


@dataclasses.dataclass
class ClavichordTimeBracketContainer(object):
    # global group attributes
    group_simultaneous_event_tuple: tuple[core_events.SimultaneousEvent, ...]
    group_absolute_time_tuple: tuple[fractions.Fraction, ...]
    group_tempo_envelope: expenvelope.Envelope
    group_sequential_event_grid: core_events.SequentialEvent
    group_sequential_event_grid_with_applied_tempo_envelope: core_events.SequentialEvent
    metronome_sequential_event: core_events.SequentialEvent
    group_time_signature_sequence: tuple

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
        metronome_sequential_event: core_events.SequentialEvent,
        group_time_signature_sequence: tuple,
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
            metronome_sequential_event,
            group_time_signature_sequence,
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
                    f"Number: {index}. TimeBracket: {repr(clavichord_time_bracket)[:30]}"
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
        group_time_signature_absolute_time_sequence = tuple(
            core_utilities.accumulate_from_zero(
                [
                    fractions.Fraction(time_signature.duration)
                    for time_signature in self.group_time_signature_sequence
                ]
            )
        )
        self.clavichord_time_bracket_list.append(
            ClavichordTimeBracket(
                *args,
                group_simultaneous_event_tuple=self.group_simultaneous_event_tuple,
                group_absolute_time_tuple=self.group_absolute_time_tuple,
                group_tempo_envelope=self._group_tempo_envelope_for_clavichord_time_bracket,
                group_sequential_event_grid=self.group_sequential_event_grid,
                group_sequential_event_grid_with_applied_tempo_envelope=self.group_sequential_event_grid_with_applied_tempo_envelope,
                group_metronome_sequential_event=self.metronome_sequential_event.copy(),
                group_time_signature_sequence=self.group_time_signature_sequence,
                group_time_signature_absolute_time_sequence=group_time_signature_absolute_time_sequence,
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


def _split_time_bracket(
    clavichord_time_bracket_container: ClavichordTimeBracketContainer,
    bracket_to_split_index: int,
):
    time_bracket = clavichord_time_bracket_container[bracket_to_split_index]
    time_bracket_data_list = []

    added_delay = 0

    for note_like in time_bracket.sequential_event:
        new_sequential_event = core_events.SequentialEvent([copy.deepcopy(note_like)])
        # new_sequential_event[0].duration = fractions.Fraction(1, 1)
        new_delay = time_bracket.delay + added_delay
        added_delay += note_like.duration
        time_bracket_data_list.append(
            [
                time_bracket.group_index,
                new_delay,
                new_sequential_event,
                time_bracket.notate_metronome,
            ]
        )

    clavichord_time_bracket_container.remove(bracket_to_split_index)

    clavichord_time_bracket_container.extend_clavichord_time_bracket(
        time_bracket_data_list
    )


def _add_repetitions(clavichord_time_bracket_container: ClavichordTimeBracketContainer):
    tremolo0_pitch_list = [
        constants.CHORD_SEQUENTIAL_EVENT[group_index].pitch_list[
            configurations.PITCH_ORDER.index("clavichord")
        ]
        for group_index in (4, 5)
    ]
    # tremolo0_pitch_count_list = [8, 40]
    tremolo0_pitch_count_list = [8, 20]
    tremolo0_duration_list = [fractions.Fraction(1, 4), fractions.Fraction(1, 2)]
    tremolo_sequential_event_list = [
        core_events.SequentialEvent([]),
        core_events.SequentialEvent([]),
    ]
    for tremolo_sequential_event0, pitch, pitch_count, note_duration in zip(
        tremolo_sequential_event_list,
        tremolo0_pitch_list,
        tremolo0_pitch_count_list,
        tremolo0_duration_list,
    ):
        tremolo_sequential_event0.repetition_count = pitch_count
        for _ in range(pitch_count):
            tremolo_sequential_event0.append(
                music_events.NoteLike(
                    cdd_constants.CLAVICHORD_AMBITUS.get_pitch_variant_tuple(pitch)[-1],
                    note_duration,
                )
            )
    clavichord_time_bracket_container[
        4
    ].sequential_event = tremolo_sequential_event_list[0]
    clavichord_time_bracket_container[4].delay += fractions.Fraction(17, 2)

    clavichord_time_bracket_container.remove(2)
    clavichord_time_bracket_container.remove(5)
    clavichord_time_bracket_container.remove(4)

    clavichord_time_bracket_container.append_clavichord_time_bracket(
        2, fractions.Fraction(108, 2), tremolo_sequential_event_list[1], False
    )


def _add_octave_chord(
    clavichord_time_bracket_container: ClavichordTimeBracketContainer,
):
    sequential_event = core_events.SequentialEvent([])
    note_like = music_events.NoteLike([], fractions.Fraction(1, 1))
    base_pitch = constants.CHORD_SEQUENTIAL_EVENT[3].pitch_list[
        configurations.PITCH_ORDER.index("clavichord")
    ]
    note_like.pitch_list = [
        # base_pitch.register(-2, mutate=False),
        # base_pitch.register(-1, mutate=False).add(
        #     music_parameters.JustIntonationPitch("4/3")
        # ),
        base_pitch.register(-1, mutate=False),
        base_pitch.register(-1, mutate=False).add(
            music_parameters.JustIntonationPitch("3/2")
        ),
        base_pitch,
        base_pitch.register(1, mutate=False),
    ]
    # note_like.playing_indicator_collection.arpeggio.direction = "up"
    for _ in range(1):
        sequential_event.append(note_like)
    clavichord_time_bracket_container.append_clavichord_time_bracket(
        2, fractions.Fraction(13, 2), sequential_event, False
    )


def _improve_group_2_beginning(
    clavichord_time_bracket_container: ClavichordTimeBracketContainer,
):
    sequential_event = clavichord_time_bracket_container[8].sequential_event
    sequential_event.set_parameter("duration", fractions.Fraction(2, 1))
    sequential_event.append(sequential_event[-1])


def _add_arpeggio_to_group_2(
    clavichord_time_bracket_container: ClavichordTimeBracketContainer,
):
    sequential_event = clavichord_time_bracket_container[9].sequential_event
    note_like_with_arpeggio = sequential_event[-1]
    note_like_with_arpeggio.playing_indicator_collection.arpeggio.direction = "up"
    main_pitch = note_like_with_arpeggio.pitch_list[0]
    note_like_with_arpeggio.duration = fractions.Fraction(2, 1)
    note_like_with_arpeggio.pitch_list = [
        main_pitch - music_parameters.JustIntonationPitch("2/1"),
        main_pitch,
        main_pitch + music_parameters.JustIntonationPitch("3/2"),
        main_pitch + music_parameters.JustIntonationPitch("2/1"),
        main_pitch + music_parameters.JustIntonationPitch("7/3"),
        main_pitch + music_parameters.JustIntonationPitch("3/1"),
    ]
    # sequential_event.append(music_events.NoteLike([], fractions.Fraction(2, 1)))
    # sequential_event.append(note_like_with_arpeggio)


def _adjust_metronome_part(
    clavichord_time_bracket_container: ClavichordTimeBracketContainer,
):
    clavichord_time_bracket = clavichord_time_bracket_container[10]
    clavichord_time_bracket.notate_metronome = True
    sequential_event = clavichord_time_bracket.sequential_event

    # Increase rest at beginning, easier to start with metronome
    sequential_event[0].pitch_list = []
    sequential_event[0].duration += fractions.Fraction(1, 2)
    sequential_event[1].duration -= fractions.Fraction(1, 2)

    sequential_event[5].duration -= fractions.Fraction(1, 4)
    sequential_event[6].duration += fractions.Fraction(1, 4)

    sequential_event.split_child_at(fractions.Fraction(27, 4))
    sequential_event[7].pitch_list[0] += music_parameters.JustIntonationPitch("3/2")
    sequential_event[10].pitch_list.append(
        sequential_event[10]
        .pitch_list[0]
        .subtract(music_parameters.JustIntonationPitch("4/1"), mutate=False)
    )

    sequential_event.split_child_at(
        sequential_event.absolute_time_tuple[9] + fractions.Fraction(1, 2)
    )
    sequential_event.split_child_at(
        sequential_event.absolute_time_tuple[9] + fractions.Fraction(1, 1)
    )

    for index, duration in enumerate(
        [
            fractions.Fraction(2, 3),
            fractions.Fraction(1, 3),
            fractions.Fraction(1, 3),
            fractions.Fraction(2, 3),
        ]
    ):
        sequential_event[index + 8].duration = duration

    sequential_event[10].pitch_list[0] -= music_parameters.JustIntonationPitch("4/3")
    sequential_event[11].pitch_list[0] -= music_parameters.JustIntonationPitch("2/1")
    sequential_event[12].pitch_list[1] -= music_parameters.JustIntonationPitch("4/3")

    sequential_event.squash_in(
        fractions.Fraction(23, 2), music_events.NoteLike([], fractions.Fraction(1, 4))
    )


def post_process(clavichord_time_bracket_container: ClavichordTimeBracketContainer):
    clavichord_time_bracket_container.remove(5)
    clavichord_time_bracket_container.remove(3)
    clavichord_time_bracket_container.remove(5)
    clavichord_time_bracket_container.remove(4)
    clavichord_time_bracket_container.remove(6)
    clavichord_time_bracket_container.remove(5)

    clavichord_time_bracket_container[0].delay += fractions.Fraction(2, 1)

    # New or changed time brackets
    _add_repetitions(clavichord_time_bracket_container)
    _add_octave_chord(clavichord_time_bracket_container)
    _improve_group_2_beginning(clavichord_time_bracket_container)
    _add_arpeggio_to_group_2(clavichord_time_bracket_container)
    _adjust_metronome_part(clavichord_time_bracket_container)
