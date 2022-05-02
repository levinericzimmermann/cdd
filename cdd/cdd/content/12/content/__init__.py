import quicktions as fractions

from mutwo import core_events
from mutwo import music_parameters

import cdd

from . import constants
from . import configurations
from . import classes


class Chapter(cdd.chapters.Chapter):
    instruction_text = r"""as quiet as possible.
repeat song ad libitum.
"""

    instrument_name_to_instruction_text = {
        "soprano": rf"""{instruction_text} only sing vowels (pass parenthetical letters).
if a note has multiple vowels, interpolate between them over the course of the tone.
""",
        "clarinet": instruction_text,
        "clavichord": instruction_text,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.group_collection = self.get_group_collection()
        self.simultaneous_event = self.group_collection.to_simultaneous_event
        self.tempo_envelope = self.group_collection.to_tempo_envelope
        self.time_signature_sequence = self.group_collection.to_time_signature_tuple
        # Ensure order of instruments is correct
        self.sort_simultaneous_event()

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
            maxima_duration = configurations.MAXIMUM_CHORD_DURATION_IN_SECONDS
        else:
            if instrument_name == "soprano":
                maxima_duration = cdd.constants.SOPRANO_MAXIMUM_TONE_DURATION
            else:
                maxima_duration = cdd.constants.CLARINET_MAXIMUM_TONE_DURATION

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
        group_list = []
        chord_list = []
        chord_count = len(constants.CHORD_SEQUENTIAL_EVENT)
        last_index = chord_count - 1
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
            if index and (
                index in constants.NEW_GROUP_INDEX_TUPLE or index == last_index
            ):
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
