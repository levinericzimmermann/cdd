import abjad
import quicktions as fractions

from mutwo import core_converters
from mutwo import core_events
from mutwo import music_events

from . import configurations


class TimeSignatureSequenceToSequentialEvent(core_converters.abc.Converter):
    """Make metronome-like tape"""

    def convert(
        self, time_signature_sequence: tuple[abjad.TimeSignature, ...]
    ) -> core_events.SequentialEvent:
        sequential_event = core_events.SequentialEvent([])

        for time_signature in time_signature_sequence:
            duration = fractions.Fraction(time_signature.duration)
            beat_count = int(duration / configurations.BEAT_SIZE)
            for beat_index in range(beat_count):
                note_like = music_events.NoteLike("c", configurations.BEAT_SIZE)
                if beat_index == 0:
                    note_like.notation_indicator_collection.note_head.style = "triangle"
                sequential_event.append(note_like)

        return sequential_event
