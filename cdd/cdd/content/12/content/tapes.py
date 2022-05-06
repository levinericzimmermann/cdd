import abjad
import quicktions as fractions

from mutwo import core_converters
from mutwo import core_events
from mutwo import music_events

from . import configurations


class TimeSignatureSequenceToSimultaneousEvent(core_converters.abc.Converter):
    """Make metronome-like tape"""

    def convert(
        self, time_signature_sequence: tuple[abjad.TimeSignature, ...]
    ) -> core_events.SimultaneousEvent:
        first_beat_sequential_event = core_events.SequentialEvent([])
        beats_sequential_event = core_events.SequentialEvent([])

        for time_signature in time_signature_sequence:
            duration = fractions.Fraction(time_signature.duration)
            beat_count = duration / configurations.BEAT_SIZE

            first_beat_part = [music_events.NoteLike("c", configurations.BEAT_SIZE)]
            if beat_count > 1:
                first_beat_part.append(
                    music_events.NoteLike(
                        [], (beat_count - 1) * configurations.BEAT_SIZE
                    )
                )
            first_beat_sequential_event.extend(first_beat_part)

            beats_part = [music_events.NoteLike([], configurations.BEAT_SIZE)]
            for _ in range(beat_count - 1):
                beats_part.append(music_events.NoteLike("c", configurations.BEAT_SIZE))
            beats_sequential_event.extend(beats_part)

        return core_events.SimultaneousEvent(
            [first_beat_sequential_event, beats_sequential_event]
        )
