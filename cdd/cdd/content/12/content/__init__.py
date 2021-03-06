import quicktions as fractions
import ranges

from mutwo import core_converters
from mutwo import core_events
from mutwo import music_events
from mutwo import music_parameters

import cdd

from . import clarinet
from . import clavichord
from . import constants
from . import configurations
from . import classes
from . import tapes
from . import tempos
from . import soprano

StartTime, EndTime = float, float
DoesNextEventFollowsImmediately = bool
SustainingInstrumentData = tuple[
    StartTime,
    EndTime,
    core_events.SequentialEvent,  # sustaining instrument
    core_events.SequentialEvent,  # environment
    DoesNextEventFollowsImmediately,
]
ClavichordTimeBracket = tuple[StartTime, EndTime, core_events.SequentialEvent]


class Chapter(cdd.chapters.Chapter):
    instruction_text = r"""as quiet as possible.
repeat song ad libitum.
"""
    instruction_text = r""""""

    instruction_text_sustaining_instrument = rf"""{instruction_text}
start \& end tones at given times.
if necessary: discreetly interrupt tone to take breath.
arrow = next tone follows immediately.
"""

    instrument_name_to_instruction_text = {
        "soprano": rf"""{instruction_text_sustaining_instrument} only sing vowels (pass parenthesized letters).
if a note has multiple vowels: interpolate between them over the course of the given tone.
if al niente: start or end tone with closed mouth.
""",
        "clarinet": instruction_text_sustaining_instrument,
        "clavichord": instruction_text,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.chord_sequential_event = constants.CHORD_SEQUENTIAL_EVENT
        self.pitch_order = configurations.PITCH_ORDER

        self.group_collection = self.get_group_collection()
        self.simultaneous_event = self.group_collection.to_simultaneous_event
        # self.tempo_envelope = self.group_collection.to_tempo_envelope
        self.time_signature_sequence = self.group_collection.to_time_signature_tuple
        self.tempo_envelope = tempos.make_tempo_envelope(self.time_signature_sequence)

        # Ensure order of instruments is correct
        self.sort_simultaneous_event()

        self.time_range_to_pitch_list_index_dict = (
            self._get_time_range_to_pitch_list_index_dict(
                tuple(self.simultaneous_event.get_event_iterator_by(tag="soprano"))[0],
            )
        )

        self.metronome_sequential_event = (
            tapes.TimeSignatureSequenceToSequentialEvent()(self.time_signature_sequence)
        )

        self.sustaining_instrument_dict = self.make_sustaining_instrument_data()

        clarinet.post_process(self.sustaining_instrument_dict[cdd.constants.CLARINET])
        soprano.post_process(self.sustaining_instrument_dict[cdd.constants.SOPRANO])

        self.clavichord_time_bracket_container = (
            clavichord.ClavichordTimeBracketContainer.from_sequential_event_and_group(
                tuple(
                    self.simultaneous_event.get_event_iterator_by(
                        tag=cdd.constants.CLAVICHORD
                    )
                )[0],
                self.group_collection,
                self.tempo_envelope,
                self.metronome_sequential_event,
                self.time_signature_sequence,
            )
        )

        clavichord.post_process(self.clavichord_time_bracket_container)

    @staticmethod
    def _maxima_and_percentage_to_duration(maxima, percentage):
        return (
            int((maxima / configurations.BEAT_SIZE) * percentage)
            * configurations.BEAT_SIZE
        )

    def _long_tone_data_to_long_tone(
        self,
        pitch: music_parameters.JustIntonationPitch,
        instrument_name: str,
        long_tone_data: tuple[float, float, str],
        are_instruments_locked: bool,
        duration: fractions.Fraction,
    ) -> classes.LongTone:
        if are_instruments_locked:
            maxima_duration_in_seconds = (
                configurations.MAXIMUM_CHORD_DURATION_IN_SECONDS
            )
        else:
            if instrument_name == "soprano":
                maxima_duration_in_seconds = cdd.constants.SOPRANO_MAXIMUM_TONE_DURATION
            else:
                maxima_duration_in_seconds = (
                    cdd.constants.CLARINET_MAXIMUM_TONE_DURATION
                )

        maxima_duration = maxima_duration_in_seconds * (
            configurations.BASE_TEMPO.tempo_in_beats_per_minute / 120
        )
        maxima_duration = min((maxima_duration, duration))

        duration_percentage, delay_percentage, hairpin = long_tone_data
        long_tone_duration = self._maxima_and_percentage_to_duration(
            maxima_duration, duration_percentage
        )
        maxima_delay = duration - long_tone_duration
        long_tone_delay = self._maxima_and_percentage_to_duration(
            maxima_delay, delay_percentage
        )

        return classes.LongTone(pitch, hairpin, long_tone_duration, long_tone_delay)

    def _make_chord(
        self,
        pitch_list: list[music_parameters.JustIntonationPitch],
        long_tone_data: tuple,
        pattern: tuple[int, ...],
        density_envelope: list[list],
        transform_activity_level: int,
    ) -> classes.Chord:
        pitch_dict = {
            instrument_name: pitch_list[
                configurations.PITCH_ORDER.index(instrument_name)
            ]
            for instrument_name in ("soprano", "clavichord", "clarinet")
        }

        pattern_data, pattern_count = pattern

        clavichord_part = classes.ClavichordPart(
            pitch_dict["clavichord"],
            classes.Pattern(pattern_data),
            core_events.Envelope(density_envelope),
            pattern_count,
            transform_activity_level,
        )

        (
            soprano_long_tone_data,
            clarinet_long_tone_data,
            are_instruments_locked,
        ) = long_tone_data

        soprano_long_tone, clarinet_long_tone = (
            self._long_tone_data_to_long_tone(
                pitch_dict[instrument_name],
                instrument_name,
                long_tone_data,
                are_instruments_locked,
                clavichord_part.to_sequential_event.duration,
            )
            for long_tone_data, instrument_name in (
                (soprano_long_tone_data, "soprano"),
                (clarinet_long_tone_data, "clarinet"),
            )
        )

        chord = classes.Chord(
            soprano_long_tone,
            clarinet_long_tone,
            clavichord_part,
        )

        return chord

    def get_group_collection(self) -> classes.GroupCollection:
        chord_count = len(constants.CHORD_SEQUENTIAL_EVENT)
        # assert chord_count == 13
        for sequence in (
            constants.CHORD_SEQUENTIAL_EVENT.get_parameter("pitch_list"),
            configurations.LONG_TONE_DATA_TUPLE,
            configurations.PATTERN_TUPLE,
            configurations.DENSITY_ENVELOPE_TUPLE,
            configurations.TRANSFORM_ACTIVITY_LEVEL_TUPLE,
        ):
            try:
                assert len(sequence) == chord_count
            except AssertionError:
                raise ValueError("sequence is too short: {sequence}")
        group_list = []
        chord_list = []
        for (
            index,
            pitch_list,
            long_tone_data,
            pattern,
            density_envelope,
            transform_activity_level,
        ) in zip(
            range(chord_count),
            constants.CHORD_SEQUENTIAL_EVENT.get_parameter("pitch_list"),
            configurations.LONG_TONE_DATA_TUPLE,
            configurations.PATTERN_TUPLE,
            configurations.DENSITY_ENVELOPE_TUPLE,
            configurations.TRANSFORM_ACTIVITY_LEVEL_TUPLE,
        ):
            if index and (index in constants.NEW_GROUP_INDEX_TUPLE):
                group_list.append(classes.Group(tuple(chord_list)))
                chord_list = []

            chord = self._make_chord(
                pitch_list,
                long_tone_data,
                pattern,
                density_envelope,
                transform_activity_level,
            )
            chord_list.append(chord)

        group_list.append(classes.Group(tuple(chord_list)))

        return classes.GroupCollection(
            group_list, self, configurations.REST_TIME_SIGNATURE_TUPLE
        )

    def sort_simultaneous_event(self):
        self.simultaneous_event = core_events.SimultaneousEvent(
            [
                [
                    sequential_event
                    for sequential_event in self.simultaneous_event
                    if sequential_event.tag == tag
                ][0]
                for tag in ("soprano", "clarinet", "clavichord")
            ]
        )

    def make_sustaining_instrument_data(
        self,
    ) -> dict[str, tuple[SustainingInstrumentData, ...]]:
        instrument_name_to_data = {}

        tempo_converter = core_converters.TempoConverter(self.tempo_envelope)
        for sustaining_instrument_name in (
            cdd.constants.SOPRANO,
            cdd.constants.CLARINET,
        ):
            sequential_event = tuple(
                self.simultaneous_event.get_event_iterator_by(
                    tag=sustaining_instrument_name
                )
            )[0]
            sequential_event_with_correct_tempo = tempo_converter(
                sequential_event.copy()
            )

            sequential_event_with_correct_tempo.duration *= 4

            # content_duration = fractions.Fraction(4, 1)
            content_duration = fractions.Fraction(4, 1)
            environment_duration = content_duration
            event_data_list = []
            event_index = 0
            absolute_time_tuple = (
                sequential_event_with_correct_tempo.absolute_time_tuple
            )
            for (
                absolute_start_time_in_seconds,
                absolute_end_time_in_seconds,
                simple_event_or_note_like,
            ) in zip(absolute_time_tuple, absolute_time_tuple[1:], sequential_event):
                if (
                    hasattr(simple_event_or_note_like, "pitch_list")
                    and simple_event_or_note_like.pitch_list
                ):
                    note_like = simple_event_or_note_like.set_parameter(
                        "duration", content_duration, mutate=False
                    )
                    local_sequential_event = core_events.SequentialEvent([note_like])

                    environment_pitch_list = []
                    instrument_name_list = []
                    for pitch, instrument_name in zip(
                        constants.CHORD_SEQUENTIAL_EVENT[event_index].pitch_list,
                        configurations.PITCH_ORDER,
                    ):
                        if instrument_name != sustaining_instrument_name:
                            environment_pitch_list.append(pitch)
                            instrument_name_list.append(instrument_name)

                    # don't change order of sorting!
                    instrument_name_list = sorted(
                        instrument_name_list,
                        key=lambda instrument_name: environment_pitch_list[
                            instrument_name_list.index(instrument_name)
                        ],
                    )
                    environment_pitch_list = sorted(environment_pitch_list)

                    environment_note_like = music_events.NoteLike(
                        environment_pitch_list, environment_duration
                    )
                    environment_note_like.notation_indicator_collection.note_head_hint_list.hint_list = [
                        # cdd.constants.INSTRUMENT_NAME_TO_SHORT_INSTRUMENT_NAME[
                        #     instrument_name
                        # ]
                        instrument_name.upper()
                        for instrument_name in instrument_name_list
                    ]

                    environment_sequential_event = core_events.SequentialEvent(
                        [environment_note_like]
                    )

                    event_data = [
                        absolute_start_time_in_seconds,
                        absolute_end_time_in_seconds,
                        local_sequential_event,
                        environment_sequential_event,
                    ]
                    event_data_list.append(event_data)
                    event_index += 1

            for event_data0, event_data1 in zip(event_data_list, event_data_list[1:]):
                end0, start1 = event_data0[1], event_data1[0]
                does_next_event_follows_immediately = start1 - end0 < 4
                event_data0.append(does_next_event_follows_immediately)

            event_data_list[-1].append(False)
            event_data_tuple = list(list(event_data) for event_data in event_data_list)

            instrument_name_to_data.update(
                {sustaining_instrument_name: event_data_tuple}
            )

        return instrument_name_to_data

    def _get_time_range_to_pitch_list_index_dict(
        self,
        soprano_sequential_event: core_events.TaggedSequentialEvent,
    ) -> ranges.RangeDict:
        soprano_sequential_event = soprano_sequential_event.tie_by(
            lambda *events: all(
                [
                    not (hasattr(event, "pitch_list") and event.pitch_list)
                    for event in events
                ]
            ),
            mutate=False,
        )

        def get_pitch_list_index_iterator():
            index = 0
            while True:
                yield index
                index += 1

        pitch_list_index_iterator = get_pitch_list_index_iterator()

        range_dict = {}
        previous_pitch_list_index = 0
        next_pitch_list_index = None
        for absolute_time, simple_event_or_note_like in zip(
            soprano_sequential_event.absolute_time_tuple, soprano_sequential_event
        ):
            pitch_list = getattr(simple_event_or_note_like, "pitch_list", [])
            end = absolute_time + simple_event_or_note_like.duration
            if pitch_list:
                if next_pitch_list_index is not None:
                    pitch_list_index = next_pitch_list_index
                    next_pitch_list_index = None
                else:
                    pitch_list_index = next(pitch_list_index_iterator)

                range_dict.update(
                    {
                        ranges.Range(
                            absolute_time,
                            end,
                        ): pitch_list
                    }
                )
            else:
                pitch_list_index = previous_pitch_list_index
                try:
                    next_pitch_list_index = next(pitch_list_index_iterator)
                except StopIteration:
                    next_pitch_list_index = pitch_list_index
                new_start0 = (simple_event_or_note_like.duration * 0.5) + absolute_time

                range_dict.update(
                    {
                        ranges.Range(
                            absolute_time,
                            new_start0,
                        ): pitch_list_index,
                        ranges.Range(
                            new_start0,
                            end,
                        ): next_pitch_list_index,
                    }
                )

            previous_pitch_list_index = pitch_list_index
        return ranges.RangeDict(range_dict)
