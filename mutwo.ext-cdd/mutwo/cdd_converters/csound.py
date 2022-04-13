import os
import typing
import uuid

from mutwo import core_converters
from mutwo import core_constants
from mutwo import core_events
from mutwo import csound_converters
from mutwo import isis_converters
from mutwo import mbrola_converters


__all__ = (
    "EventToSafeSynthesis",
    "EventToSafeSpeakingSynthesis",
    "EventToSafeSingingSynthesis",
)


class EventToSafeSynthesis(csound_converters.EventToSoundFile):
    class EventToSplitEvent(core_converters.abc.EventConverter):
        def __init__(
            self,
            is_rest: typing.Callable[[core_events.SimpleEvent], bool],
            split_duration: core_constants.DurationType = 2,
        ):
            self._split_duration = split_duration
            self._is_rest = is_rest

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
                    and not hasattr(
                        csound_concatenation_event[-1], "event_to_synthesize"
                    )
                    or not is_long_rest
                    and hasattr(csound_concatenation_event[-1], "event_to_synthesize")
                )
            ):
                csound_concatenation_event[-1].duration += original_event.duration
                if not is_long_rest:
                    csound_concatenation_event[-1].event_to_synthesize.append(
                        original_event
                    )
            else:
                if is_long_rest:
                    concatenation_event = core_events.SimpleEvent(
                        original_event.duration
                    )
                else:
                    concatenation_event = core_events.SimpleEvent(
                        original_event.duration
                    )
                    concatenation_event.event_to_synthesize = (
                        core_events.SequentialEvent([original_event])
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
                if hasattr(event, "event_to_synthesize"):
                    event.sound_file_path = f".safe_synthesized_{uuid.uuid4()}.wav"

            synthesized_sound_file_path_tuple = (
                csound_concatenation_event.get_parameter("sound_file_path", flat=True)
            )
            event_to_render_with_sound_engine_tuple = (
                csound_concatenation_event.get_parameter(
                    "event_to_synthesize", flat=True
                )
            )
            return (
                synthesized_sound_file_path_tuple,
                event_to_render_with_sound_engine_tuple,
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
        event_to_sound_file: core_converters.abc.Converter,
        is_rest: typing.Callable[[core_events.SimpleEvent], bool],
    ):
        self._event_to_sound_file = event_to_sound_file
        self._is_rest = is_rest
        temporary_csound_orchestra_path = f".{uuid.uuid4()}.orc"
        super().__init__(
            temporary_csound_orchestra_path,
            csound_converters.EventToCsoundScore(
                p4=lambda event: event.sound_file_path
            ),
        )

    def _render_synthesizer(
        self,
        event_to_render_with_synthesizer_tuple: tuple[core_events.abc.Event, ...],
        synthesizer_sound_file_path_tuple: tuple[str, ...],
    ):
        for event_to_render_with_synthesizer, synthesizer_sound_file_path in zip(
            event_to_render_with_synthesizer_tuple, synthesizer_sound_file_path_tuple
        ):
            if event_to_render_with_synthesizer is not None:
                self._event_to_sound_file.convert(
                    event_to_render_with_synthesizer, synthesizer_sound_file_path
                )

    def _save_csound_orchestra(self):
        with open(self.csound_orchestra_path, "w") as f:
            f.write(self.csound_orchestra)

    def _remove_temporary_sound_files(
        self, synthesizer_sound_file_path_tuple: tuple[str, ...]
    ):
        for sound_file_path in synthesizer_sound_file_path_tuple:
            try:
                os.remove(sound_file_path)
            except TypeError:
                pass

    def _remove_csound_orchestra(self):
        os.remove(self.csound_orchestra_path)

    def convert(self, event_to_convert: str, sound_file_path: str):
        (
            synthesizer_sound_file_path_tuple,
            event_to_render_with_synthesizer_tuple,
            csound_concatenation_event,
        ) = self.EventToSplitEvent(self._is_rest)(event_to_convert)
        self._render_synthesizer(
            event_to_render_with_synthesizer_tuple, synthesizer_sound_file_path_tuple
        )
        self._save_csound_orchestra()
        super().convert(csound_concatenation_event, sound_file_path)
        self._remove_temporary_sound_files(synthesizer_sound_file_path_tuple)
        self._remove_csound_orchestra()


class EventToSafeSpeakingSynthesis(EventToSafeSynthesis):
    def __init__(
        self,
        event_to_speak_synthesis: mbrola_converters.EventToSpeakSynthesis = mbrola_converters.EventToSpeakSynthesis(),
    ):
        is_rest = (
            lambda simple_event: not event_to_speak_synthesis._event_to_phoneme_list._simple_event_to_pitch(
                simple_event
            )
            or event_to_speak_synthesis._event_to_phoneme_list._simple_event_to_phoneme_string(
                simple_event
            )
            == "_"
        )
        super().__init__(event_to_speak_synthesis, is_rest)


class EventToSafeSingingSynthesis(EventToSafeSynthesis):
    csound_orchestra = r"""
0dbfs=1
instr 1
    ; 1 second skip time because isis always starts one second late!
    asig diskin2 p4, 1, 1
    out asig
endin
"""


    def __init__(
        self,
        event_to_singing_synthesis: isis_converters.EventToSingingSynthesis = isis_converters.EventToSingingSynthesis(
            isis_converters.EventToIsisScore(
                simple_event_to_vowel=lambda simple_event: simple_event.lyric.vowel,
                simple_event_to_consonant_tuple=lambda simple_event: simple_event.lyric.consonant_tuple,
            ),
            "--cfg_synth etc/isis-cfg-synth.cfg",
            "--cfg_style etc/isis-cfg-style.cfg",
            "--seed 100",
        ),
    ):
        def is_rest(simple_event: core_events.SimpleEvent) -> bool:
            try:
                pitch = event_to_singing_synthesis.isis_score_converter._extraction_function_dict[
                    "pitch"
                ](
                    simple_event
                )
            except AttributeError:
                return True
            try:
                volume = event_to_singing_synthesis.isis_score_converter._extraction_function_dict[
                    "volume"
                ](
                    simple_event
                )
            except AttributeError:
                return True
            return pitch is None or volume is None or volume.amplitude == 0

        super().__init__(event_to_singing_synthesis, is_rest)

    def convert(self, event_to_convert: core_events.abc.Event, *args, **kwargs):
        return super().convert(event_to_convert, *args, **kwargs)
