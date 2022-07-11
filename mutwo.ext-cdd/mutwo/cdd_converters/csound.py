import os
import typing
import uuid

import jinja2

from mutwo import cdd_events
from mutwo import cdd_parameters
from mutwo import core_converters
from mutwo import core_constants
from mutwo import core_events
from mutwo import core_utilities
from mutwo import csound_converters
from mutwo import isis_converters
from mutwo import mbrola_converters


__all__ = (
    "EnvelopeToFunctionTable",
    "EventToCsoundScoreWithFunctionTables",
    "EventToSafeSynthesis",
    "EventToSafeSpeakingSynthesis",
    "EventToSafeSingingSynthesis",
    "MonoBellCsoundSimultaneousEventToBellSoundFile",
    "ResonatorSequentialEventToResonatorSoundFile",
)


# MONKEY PATCH: Allow csound converter to parse jinja2 files
def EventToSoundFile_convert(
    self,
    event_to_convert: core_events.abc.Event,
    path: str,
    score_path: typing.Optional[str] = None,
) -> None:
    """Render sound file from the mutwo event.

    :param event_to_convert: The event that shall be rendered.
    :type event_to_convert: core_events.abc.Event
    :param path: where to write the sound file
    :type path: str
    :param score_path: where to write the score file
    :type score_path: typing.Optional[str]
    """

    environment = jinja2.Environment(loader=jinja2.FileSystemLoader("./"))
    template = environment.get_template(self.csound_orchestra_path)
    csound_orchestra_str = template.render()
    split_csound_orchestra_path = self.csound_orchestra_path.split("/")
    csound_orchestra_directory_path, csound_orchestra_file_path = (
        "/".join(split_csound_orchestra_path[:-1]),
        split_csound_orchestra_path[-1],
    )
    if not csound_orchestra_directory_path:
        csound_orchestra_directory_path = "."
    csound_orchestra_path = f"{csound_orchestra_directory_path}/.{csound_orchestra_file_path.split('.')[0]}.orc"

    with open(csound_orchestra_path, "w") as csound_orchestra_file:
        csound_orchestra_file.write(csound_orchestra_str)

    if not score_path:
        score_path = path + ".sco"

    self.csound_score_converter.convert(event_to_convert, score_path)
    flag_string = " ".join(self.flags)
    command = f"csound -o {path} {flag_string}" f" {csound_orchestra_path} {score_path}"

    os.system(command)

    if self.remove_score_file:
        os.remove(score_path)


csound_converters.EventToSoundFile.convert = EventToSoundFile_convert


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
    kenv linseg 0, 0.01, 1, p3 - 0.02, 1, 0.01, 0
    out asig * kenv
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

    def _submit_conversion(
        self,
        event_to_render_with_synthesizer: core_events.abc.Event,
        synthesizer_sound_file_path: str,
        *args,
        **kwargs,
    ):
        return self._event_to_sound_file.convert(
            event_to_render_with_synthesizer,
            synthesizer_sound_file_path,
            *args,
            **kwargs,
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
                self._submit_conversion(
                    event_to_render_with_synthesizer,
                    synthesizer_sound_file_path,
                )

    def _save_csound_orchestra(self):
        with open(self.csound_orchestra_path, "w") as f:
            f.write(self.csound_orchestra)

    def _remove_temporary_sound_files(
        self, synthesizer_sound_file_path_tuple: tuple[str, ...]
    ):
        for sound_file_path in synthesizer_sound_file_path_tuple:
            if sound_file_path:
                try:
                    os.remove(sound_file_path)
                except FileNotFoundError:
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
        # Ensure that even when some sound files couldn't be rendered,
        # the converter can still render the complete sound file
        # (avoid csound errors).
        for simple_event in csound_concatenation_event:
            if hasattr(simple_event, "sound_file_path"):
                if not os.path.exists(simple_event.sound_file_path):
                    del simple_event.sound_file_path
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
    kenv linseg 0, 0.02, 1, p3 - 0.04, 1, 0.02, 0
    out asig * kenv
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
        *args,
        **kwargs,
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

        super().__init__(event_to_singing_synthesis, is_rest, *args, **kwargs)

    def _submit_conversion(self, *args, **kwargs):
        return super()._submit_conversion(
            *args, score_path=f".isis_score_{uuid.uuid4()}.cfg", **kwargs
        )

    def convert(self, event_to_convert: core_events.abc.Event, *args, **kwargs):
        return super().convert(event_to_convert, *args, **kwargs)


class MonoBellCsoundSimultaneousEventToBellSoundFile(
    csound_converters.EventToSoundFile
):
    def __init__(self):
        super().__init__(
            "etc/csound/31_bells.orc",
            csound_converters.EventToCsoundScore(
                p3=lambda event: event.duration + 11,
                p4=lambda event: event.sample_path,
                p5=lambda event: event.pitch_factor,
                p6=lambda event: event.amplitude,
                p7=lambda event: event.channel_index,
                # Panning start
                p8=lambda event: event.panning_start[0],
                p9=lambda event: event.panning_start[1],
                p10=lambda event: event.panning_start[2],
                p11=lambda event: event.panning_start[3],
                p12=lambda event: event.panning_start[4],
                # Panning end
                p13=lambda event: event.panning_end[0],
                p14=lambda event: event.panning_end[1],
                p15=lambda event: event.panning_end[2],
                p16=lambda event: event.panning_end[3],
                p17=lambda event: event.panning_end[4],
                # Distance
                p18=lambda event: event.filter_frequency,
                p19=lambda event: event.convolution_reverb_mix,
            ),
        )


class EnvelopeToFunctionTable(core_converters.abc.Converter):
    def __init__(self, gen_routine_index: int = 7):
        self._gen_routine_index = gen_routine_index

    def convert(
        self, envelope_to_convert: core_events.Envelope, function_table_index: int
    ) -> str:
        envelope_duration = envelope_to_convert.duration
        expected_table_size = 100000
        table_size = 0
        # XXX: CSound returns odd error if there are more than x entries
        #       ftable 17203: gen call has negative segment size:
        # even though no segment is negative
        maxima_entry_count = 1000
        function_table_element_list = []
        for value, duration in zip(
            envelope_to_convert.value_tuple,
            envelope_to_convert.get_parameter("duration"),
        ):
            value = str(core_utilities.round_floats(float(value), 8))
            duration = max(int((duration / envelope_duration) * expected_table_size), 1)
            table_size += duration
            if len(function_table_element_list) < maxima_entry_count:
                function_table_element_list.extend([str(value), str(duration)])
            else:
                function_table_element_list[-3] = str(
                    int(function_table_element_list[-3]) + duration
                )

        if function_table_element_list:
            # To have value at the end
            function_table_element_list.append(function_table_element_list[-2])
        else:
            table_size = 10
            function_table_element_list = f"0.5 {table_size} 0.5".split(" ")

        function_table_element_str = " ".join(function_table_element_list)
        return f"f {function_table_index} 0 {table_size} {self._gen_routine_index} {function_table_element_str}"


class EventToCsoundScoreWithFunctionTables(csound_converters.EventToCsoundScore):
    def _convert_simple_event(
        self,
        simple_event: core_events.SimpleEvent,
        absolute_entry_delay: core_constants.DurationType,
    ) -> tuple[str, ...]:
        for function_table_attribute, envelope_attribute in (
            (
                "spectral_centroid_envelope_function_table_index_tuple",
                "spectral_centroid_envelope_tuple",
            ),
            (
                "spectral_contrast_envelope_function_table_index_tuple",
                "spectral_contrast_envelope_tuple",
            ),
        ):
            try:
                function_table_data = zip(
                    getattr(simple_event, function_table_attribute),
                    getattr(simple_event, envelope_attribute),
                )
            except AttributeError:
                continue
            for function_table_index, envelope in function_table_data:
                if function_table_or_none := EnvelopeToFunctionTable()(
                    envelope, function_table_index
                ):
                    self._function_table_definition_list.append(function_table_or_none)

        return super()._convert_simple_event(simple_event, absolute_entry_delay)

    def convert(self, event_to_convert: core_events.abc.Event, path: str) -> None:
        self._function_table_definition_list: list[str] = []
        csound_score_line_tuple = self._convert_event(event_to_convert, 0)
        csound_score_line_tuple = (
            tuple(self._function_table_definition_list) + csound_score_line_tuple
        )

        csound_score_str = "\n".join(csound_score_line_tuple)
        with open(path, "w") as f:
            f.write(csound_score_str)


class ResonatorSequentialEventToResonatorSoundFile(csound_converters.EventToSoundFile):
    def __init__(self):
        super().__init__(
            "etc/csound/31_resonator.orc.j2",
            EventToCsoundScoreWithFunctionTables(
                p1=lambda event: event.instrument,
                p3=lambda event: float(event.duration),
                p4=lambda event: event.pitch.frequency,
                p5=lambda event: event.volume.amplitude,
                p6=lambda event: event.bandwidth_start,
                p7=lambda event: event.bandwidth_end,
                # Panning start
                p8=lambda event: event.panning_start[0],
                p9=lambda event: event.panning_start[1],
                p10=lambda event: event.panning_start[2],
                p11=lambda event: event.panning_start[3],
                p12=lambda event: event.panning_start[4],
                # Panning end
                p13=lambda event: event.panning_end[0],
                p14=lambda event: event.panning_end[1],
                p15=lambda event: event.panning_end[2],
                p16=lambda event: event.panning_end[3],
                p17=lambda event: event.panning_end[4],
                # Other
                p18=lambda event: event.filter_layer_count,
                # Spectral centroid function tables
                p19=lambda event: event.spectral_centroid_envelope_function_table_index_tuple[
                    0
                ],
                p20=lambda event: event.spectral_centroid_envelope_function_table_index_tuple[
                    1
                ],
                p21=lambda event: event.spectral_centroid_envelope_function_table_index_tuple[
                    2
                ],
                p22=lambda event: event.spectral_centroid_envelope_function_table_index_tuple[
                    3
                ],
                p23=lambda event: event.spectral_centroid_envelope_function_table_index_tuple[
                    4
                ],
                # Spectral contrast function tables
                p24=lambda event: event.spectral_contrast_envelope_function_table_index_tuple[
                    0
                ],
                p25=lambda event: event.spectral_contrast_envelope_function_table_index_tuple[
                    1
                ],
                p26=lambda event: event.spectral_contrast_envelope_function_table_index_tuple[
                    2
                ],
                p27=lambda event: event.spectral_contrast_envelope_function_table_index_tuple[
                    3
                ],
                p28=lambda event: event.spectral_contrast_envelope_function_table_index_tuple[
                    4
                ],
            ),
        )

    def convert(self, event_to_convert: core_events.abc.Event, *args, **kwargs):
        field_recording_player_event = cdd_events.ResonatorEvent(
            duration=event_to_convert.duration + 10,
            panning_start=cdd_parameters.Panning([0] * 5),
            panning_end=cdd_parameters.Panning([0] * 5),
        )
        field_recording_player_event.instrument = 1
        new_event = core_events.SimultaneousEvent(
            [event_to_convert, field_recording_player_event]
        )
        return super().convert(new_event, *args, **kwargs)
