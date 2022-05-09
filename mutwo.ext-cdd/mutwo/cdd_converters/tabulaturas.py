import copy
import typing
import warnings

from mutwo import core_converters
from mutwo import core_events
from mutwo import music_converters
from mutwo import music_events
from mutwo import music_parameters

__all__ = (
    "PitchToTabulaturaPitch",
    "SequentialEventToTabulaturaBasedEvent",
    "SequentialEventToSplitSequentialEvent",
)


class PitchToTabulaturaPitch(core_converters.abc.Converter):
    ExponentTupleToWesternPitchDict = dict[
        tuple[int, ...], music_parameters.WesternPitch
    ]

    def __init__(
        self, exponent_tuple_to_western_pitch_dict: ExponentTupleToWesternPitchDict
    ):
        self._exponent_tuple_to_western_pitch_dict = (
            exponent_tuple_to_western_pitch_dict
        )

    def convert(
        self, pitch_to_convert: music_parameters.JustIntonationPitch
    ) -> typing.Optional[music_parameters.WesternPitch]:
        try:
            return self._exponent_tuple_to_western_pitch_dict[
                pitch_to_convert.exponent_tuple
            ]
        except KeyError:
            warnings.warn(
                f"Couldn't find any tabulatura pitch for {repr(pitch_to_convert)}!",
                RuntimeWarning,
            )
            return None


class SequentialEventToSplitSequentialEvent(core_converters.abc.Converter):
    def __init__(
        self, border: music_parameters.WesternPitch = music_parameters.WesternPitch("c")
    ):
        self._border = border

    def _split_grace_notes(
        self,
        note_like_or_simple_event: typing.Union[
            music_events.NoteLike, core_events.SimpleEvent
        ],
        simultaneous_event: core_events.SimultaneousEvent[core_events.SequentialEvent],
    ):
        previous_event0, previous_event1 = (
            sequential_event[-1] for sequential_event in simultaneous_event
        )
        is_active0, is_active1 = (
            hasattr(previous_event, "pitch_list") and previous_event.pitch_list
            for previous_event in (previous_event0, previous_event1)
        )
        if not (is_active0 and is_active1):
            if is_active0:
                previous_event0.grace_note_sequential_event = (
                    note_like_or_simple_event.grace_note_sequential_event.copy()
                )
                previous_event0.after_grace_note_sequential_event = (
                    note_like_or_simple_event.after_grace_note_sequential_event.copy()
                )
            elif is_active1:
                previous_event1.grace_note_sequential_event = (
                    note_like_or_simple_event.grace_note_sequential_event.copy()
                )
                previous_event1.after_grace_note_sequential_event = (
                    note_like_or_simple_event.after_grace_note_sequential_event.copy()
                )
            return
        for attribute_name in (
            "grace_note_sequential_event",
            "after_grace_note_sequential_event",
        ):
            if hasattr(note_like_or_simple_event, attribute_name):
                grace_or_after_grace_note_sequential_event = getattr(
                    note_like_or_simple_event, attribute_name
                ).copy()
                split_grace_or_after_grace_note_simultaneous_event = (
                    self._sequential_event_to_simultaneous_event(
                        grace_or_after_grace_note_sequential_event, False
                    )
                )
                for (
                    split_sequential_event,
                    split_grace_or_after_grace_note_sequential_event,
                ) in zip(
                    simultaneous_event,
                    split_grace_or_after_grace_note_simultaneous_event,
                ):
                    # If there are only rests inside the grace_note_sequential_event it
                    # should explicitly defined as an empty sequential_event (in order
                    # to avoid bugs).
                    if not [
                        pitch_list
                        for pitch_list in split_grace_or_after_grace_note_sequential_event.get_parameter(
                            "pitch_list"
                        )
                        if pitch_list
                    ]:
                        split_grace_or_after_grace_note_sequential_event = (
                            core_events.SequentialEvent([])
                        )
                    setattr(
                        split_sequential_event[-1],
                        attribute_name,
                        split_grace_or_after_grace_note_sequential_event,
                    )

    def _sequential_event_to_simultaneous_event(
        self,
        sequential_event_to_convert: core_events.SequentialEvent[
            typing.Union[core_events.SimpleEvent, music_events.NoteLike]
        ],
        split_grace_notes: bool,
    ) -> core_events.SimultaneousEvent[core_events.SequentialEvent]:
        simultaneous_event = core_events.SimultaneousEvent(
            [core_events.SequentialEvent([]), core_events.SequentialEvent([])]
        )
        for note_like_or_simple_event in sequential_event_to_convert:
            if hasattr(note_like_or_simple_event, "pitch_list"):
                pitch_list_list = [[], []]
                for western_pitch in note_like_or_simple_event.pitch_list:
                    pitch_list_list[not (western_pitch >= self._border)].append(
                        western_pitch
                    )
                for index, pitch_list, sequential_event in zip(
                    range(2), pitch_list_list, simultaneous_event
                ):
                    if pitch_list:
                        new_note_like = copy.deepcopy(note_like_or_simple_event)
                        if index == 1:
                            new_note_like.lyric = music_parameters.DirectLyric("")
                        else:
                            new_note_like.lyric = copy.deepcopy(
                                note_like_or_simple_event.lyric
                            )
                        new_note_like.pitch_list = pitch_list
                        sequential_event.append(new_note_like)
                    else:
                        sequential_event.append(
                            core_events.SimpleEvent(note_like_or_simple_event.duration)
                        )
                if split_grace_notes:
                    self._split_grace_notes(
                        note_like_or_simple_event, simultaneous_event
                    )
            else:
                for sequential_event in simultaneous_event:
                    sequential_event.append(copy.deepcopy(note_like_or_simple_event))
        return simultaneous_event

    def convert(
        self,
        sequential_event_to_convert: core_events.SequentialEvent[
            typing.Union[core_events.SimpleEvent, music_events.NoteLike]
        ],
    ) -> core_events.SimultaneousEvent[core_events.SequentialEvent]:
        return self._sequential_event_to_simultaneous_event(
            sequential_event_to_convert, True
        )


class SequentialEventToTabulaturaBasedEvent(core_converters.abc.Converter):
    def __init__(
        self,
        pitch_to_tabulatura_pitch: PitchToTabulaturaPitch,
        improve_western_pitch_list_sequence_readability: music_converters.ImproveWesternPitchListSequenceReadability,
    ):
        self._improve_western_pitch_list_sequence_readability = (
            improve_western_pitch_list_sequence_readability
        )
        self._pitch_to_tabulatura_pitch = pitch_to_tabulatura_pitch

    def _get_pitch_list_tuple(
        self,
        sequential_event_to_convert: core_events.SequentialEvent,
        fetch_grace_notes: bool,
    ) -> tuple[list[music_parameters.JustIntonationPitch], ...]:
        just_intonation_pitch_list = []
        for note_like_or_simple_event in sequential_event_to_convert:
            if fetch_grace_notes:
                if hasattr(note_like_or_simple_event, "grace_note_sequential_event"):
                    just_intonation_pitch_list.extend(
                        self._get_pitch_list_tuple(
                            note_like_or_simple_event.grace_note_sequential_event, False
                        )
                    )
            if hasattr(note_like_or_simple_event, "pitch_list"):
                just_intonation_pitch_list.append(note_like_or_simple_event.pitch_list)
            if fetch_grace_notes:
                if hasattr(
                    note_like_or_simple_event, "after_grace_note_sequential_event"
                ):
                    just_intonation_pitch_list.extend(
                        self._get_pitch_list_tuple(
                            note_like_or_simple_event.after_grace_note_sequential_event,
                            False,
                        )
                    )
        return tuple(just_intonation_pitch_list)

    def _set_pitch_list_tuple(
        self,
        sequential_event_to_convert: core_events.SequentialEvent,
        apply_grace_notes: bool,
        pitch_list_iterator: typing.Iterator[list[music_parameters.WesternPitch]],
    ):
        for note_like_or_simple_event in sequential_event_to_convert:
            if apply_grace_notes:
                if hasattr(note_like_or_simple_event, "grace_note_sequential_event"):
                    self._set_pitch_list_tuple(
                        note_like_or_simple_event.grace_note_sequential_event,
                        False,
                        pitch_list_iterator,
                    )
            if hasattr(note_like_or_simple_event, "pitch_list"):
                note_like_or_simple_event.pitch_list = next(pitch_list_iterator)
            if apply_grace_notes:
                if hasattr(
                    note_like_or_simple_event, "after_grace_note_sequential_event"
                ):
                    self._set_pitch_list_tuple(
                        note_like_or_simple_event.after_grace_note_sequential_event,
                        False,
                        pitch_list_iterator,
                    )

    def _pitch_list_tuple_to_tabulatura_pitch_list_tuple(
        self, pitch_list_tuple: tuple[list[music_parameters.abc.Pitch], ...]
    ) -> tuple[list[music_parameters.abc.Pitch], ...]:
        return tuple(
            list(
                filter(
                    lambda pitch: pitch is not None,
                    (
                        self._pitch_to_tabulatura_pitch.convert(pitch)
                        for pitch in pitch_list
                    ),
                )
            )
            for pitch_list in pitch_list_tuple
        )

    def _tabulatura_pitch_list_to_improved_readability_pitch_list(
        self, western_pitch_list_tuple: tuple[list[music_parameters.WesternPitch], ...]
    ) -> tuple[list[music_parameters.WesternPitch], ...]:
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
                ] = self._improve_western_pitch_list_sequence_readability.convert(
                    western_pitch_list_tuple[x + 1 : y]
                )
        return tuple(western_pitch_list_list)

    def convert(
        self,
        sequential_event_to_convert: core_events.SequentialEvent[
            typing.Union[music_events.NoteLike, core_events.SimpleEvent]
        ],
    ) -> core_events.SequentialEvent[
        typing.Union[music_events.NoteLike, core_events.SimpleEvent]
    ]:
        sequential_event_to_convert = sequential_event_to_convert.copy()
        just_intonation_pitch_list_tuple = self._get_pitch_list_tuple(
            sequential_event_to_convert, True
        )
        western_pitch_list_tuple = (
            self._pitch_list_tuple_to_tabulatura_pitch_list_tuple(
                just_intonation_pitch_list_tuple
            )
        )
        western_pitch_list_tuple = (
            self._tabulatura_pitch_list_to_improved_readability_pitch_list(
                western_pitch_list_tuple
            )
        )

        self._set_pitch_list_tuple(
            sequential_event_to_convert, True, iter(western_pitch_list_tuple)
        )
        return sequential_event_to_convert
