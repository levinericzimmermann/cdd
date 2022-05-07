import abjad
import quicktions as fractions

from mutwo import common_generators
from mutwo import core_converters
from mutwo import core_events
from mutwo import music_events
from mutwo import music_parameters

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
                note_like = music_events.NoteLike("4/1", configurations.BEAT_SIZE)
                if beat_index == 0:
                    note_like.notation_indicator_collection.note_head.style = "triangle"
                    note_like.pitch_list[0] -= music_parameters.JustIntonationPitch(
                        "2/1"
                    )
                    filter_bandwidth = 200
                    volume = music_parameters.DecibelVolume(-6)
                else:
                    filter_bandwidth = 80
                    volume = music_parameters.DecibelVolume(-15)
                note_like.filter_bandwidth = filter_bandwidth
                note_like.volume = volume
                sequential_event.append(note_like)

        note_like_count = len(sequential_event)
        activity_level = common_generators.ActivityLevel()
        for index, note_like in enumerate(sequential_event):
            percentage = index / note_like_count
            level = int(
                configurations.METRONOME_ACTIVITY_LEVEL_ENVELOPE.value_at(percentage)
            )
            if not activity_level(level):
                note_like.pitch_list = []
                note_like.volume = music_parameters.DirectVolume(0)

        return sequential_event
