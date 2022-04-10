import os
import typing
import uuid

from mutwo import core_converters
from mutwo import core_constants
from mutwo import core_events
from mutwo import csound_converters
from mutwo import mbrola_converters
from mutwo import music_parameters


__all__ = ("EventToSafeSpeakingSynthesis",)


class EventToSafeSpeakingSynthesis(csound_converters.EventToSoundFile):
    class EventToSplitEvent(core_converters.abc.EventConverter):
        def __init__(
            self,
            simple_event_to_pitch: typing.Callable[
                [core_events.SimpleEvent], typing.Optional[music_parameters.abc.Pitch]
            ] = mbrola_converters.SimpleEventToPitch(),
            simple_event_to_phoneme_string: typing.Callable[
                [core_events.SimpleEvent], str
            ] = mbrola_converters.SimpleEventToPhonemeString(),
            split_duration: core_constants.DurationType = 2,
        ):
            self._split_duration = split_duration
            self._is_rest = (
                lambda simple_event: not simple_event_to_pitch(simple_event)
                or simple_event_to_phoneme_string(simple_event) == "_"
            )

        def _convert_simple_event(
            self,
            simple_event_to_convert: core_events.SimpleEvent,
            _: core_constants.DurationType,
        ) -> bool:
            is_simple_event_rest = self._is_rest(simple_event_to_convert)
            return (
                is_simple_event_rest
                and simple_event_to_convert.duration > self._split_duration,
            )

        def _add_simple_event_to_csound_concatenation_event(
            self,
            original_event: core_events.SimpleEvent,
            converted_event: bool,
            csound_concatenation_event: core_events.SequentialEvent,
        ):
            is_long_rest = converted_event
            if (
                csound_concatenation_event
                and isinstance(csound_concatenation_event[-1], core_events.SimpleEvent)
                and (
                    is_long_rest
                    and not hasattr(csound_concatenation_event[-1], "mbrola_event")
                    or not is_long_rest
                    and hasattr(csound_concatenation_event[-1], "mbrola_event")
                )
            ):
                csound_concatenation_event[-1].duration += original_event.duration
                if not is_long_rest:
                    csound_concatenation_event[-1].mbrola_event.append(original_event)
            else:
                if is_long_rest:
                    concatenation_event = core_events.SimpleEvent(
                        original_event.duration
                    )
                else:
                    concatenation_event = core_events.SimpleEvent(
                        original_event.duration
                    )
                    concatenation_event.mbrola_event = core_events.SequentialEvent(
                        [original_event]
                    )
                csound_concatenation_event.append(concatenation_event)

        def _convert_sequential_event(
            self,
            sequential_event_to_convert: core_events.SequentialEvent,
            absolute_entry_delay: core_constants.DurationType,
        ) -> core_events.SequentialEvent:
            converted_sequential_event = super()._convert_sequential_event(
                sequential_event_to_convert, absolute_entry_delay
            )
            csound_concatenation_event = core_events.SequentialEvent([])
            for original_event, converted_event in zip(
                sequential_event_to_convert, converted_sequential_event
            ):
                if isinstance(original_event, core_events.SimpleEvent):
                    self._add_simple_event_to_csound_concatenation_event(
                        original_event, converted_event, csound_concatenation_event
                    )
                else:
                    csound_concatenation_event.append(converted_event)
            return csound_concatenation_event

        def _convert_simultaneous_event(
            self,
            simultaneous_event_to_convert: core_events.SimultaneousEvent,
            absolute_entry_delay: core_constants.DurationType,
        ) -> core_events.SimultaneousEvent:
            converted_simultaneous_event = super()._convert_simultaneous_event(
                simultaneous_event_to_convert, absolute_entry_delay
            )
            csound_concatenation_event = core_events.SimultaneousEvent([])
            for original_event, converted_event in zip(
                simultaneous_event_to_convert, converted_simultaneous_event
            ):
                if isinstance(original_event, core_events.SimpleEvent):
                    new_sequential_event = core_events.SequentialEvent([])
                    self._add_simple_event_to_csound_concatenation_event(
                        original_event, converted_event, new_sequential_event
                    )
                    converted_simultaneous_event.append(new_sequential_event)
                else:
                    csound_concatenation_event.append(converted_event)

            return csound_concatenation_event

        def convert(self, event_to_convert: core_events.abc.Event):
            if isinstance(event_to_convert, core_events.SimpleEvent):
                csound_concatenation_event = core_events.SequentialEvent([])
                self._add_simple_event_to_csound_concatenation_event(
                    event_to_convert,
                    self._convert_simple_event(event_to_convert, 0),
                    csound_concatenation_event,
                )
            else:
                csound_concatenation_event = self._convert_event(event_to_convert, 0)

            def add_event(event):
                for event in csound_concatenation_event:
                    if isinstance(event, core_events.SimpleEvent):
                        flat_event_list.append(event)
                    else:
                        add_event(event)

            flat_event_list = []
            add_event(csound_concatenation_event)
            for event in flat_event_list:
                event.duration = float(event.duration)
                if hasattr(event, "mbrola_event"):
                    event.sound_file_path = f".safe_mbrola_{uuid.uuid4()}.wav"

            mbrola_sound_file_path_tuple = csound_concatenation_event.get_parameter(
                "sound_file_path", flat=True
            )
            event_to_render_with_mbrola_tuple = (
                csound_concatenation_event.get_parameter("mbrola_event", flat=True)
            )
            return (
                mbrola_sound_file_path_tuple,
                event_to_render_with_mbrola_tuple,
                csound_concatenation_event,
            )

    csound_orchestra = r"""
0dbfs=1
instr 1
    asig diskin2 p4
    out asig
endin
"""

    def __init__(
        self,
        event_to_speak_synthesis: mbrola_converters.EventToSpeakSynthesis = mbrola_converters.EventToSpeakSynthesis(),
    ):
        self._event_to_speak_synthesis = event_to_speak_synthesis
        temporary_csound_orchestra_path = f".{uuid.uuid4()}.orc"
        super().__init__(
            temporary_csound_orchestra_path,
            csound_converters.EventToCsoundScore(
                p4=lambda event: event.sound_file_path
            ),
        )

    def _render_mbrola(
        self,
        event_to_render_with_mbrola_tuple: tuple[core_events.abc.Event, ...],
        mbrola_sound_file_path_tuple: tuple[str, ...],
    ):
        for event_to_render_with_mbrola, mbrola_sound_file_path in zip(
            event_to_render_with_mbrola_tuple, mbrola_sound_file_path_tuple
        ):
            if event_to_render_with_mbrola is not None:
                self._event_to_speak_synthesis.convert(
                    event_to_render_with_mbrola, mbrola_sound_file_path
                )

    def _save_csound_orchestra(self):
        with open(self.csound_orchestra_path, "w") as f:
            f.write(self.csound_orchestra)

    def _remove_temporary_sound_files(
        self, mbrola_sound_file_path_tuple: tuple[str, ...]
    ):
        for sound_file_path in mbrola_sound_file_path_tuple:
            try:
                os.remove(sound_file_path)
            except TypeError:
                pass

    def _remove_csound_orchestra(self):
        os.remove(self.csound_orchestra_path)

    def convert(self, event_to_convert: str, sound_file_path: str):
        (
            mbrola_sound_file_path_tuple,
            event_to_render_with_mbrola_tuple,
            csound_concatenation_event,
        ) = self.EventToSplitEvent(
            self._event_to_speak_synthesis._event_to_phoneme_list._simple_event_to_pitch,
            self._event_to_speak_synthesis._event_to_phoneme_list._simple_event_to_phoneme_string,
        )(
            event_to_convert
        )
        self._render_mbrola(
            event_to_render_with_mbrola_tuple, mbrola_sound_file_path_tuple
        )
        self._save_csound_orchestra()
        super().convert(csound_concatenation_event, sound_file_path)
        self._remove_temporary_sound_files(mbrola_sound_file_path_tuple)
        self._remove_csound_orchestra()
