"""Create singing synthesis for tape"""

from mutwo import core_converters
from mutwo import core_events
from mutwo import music_events


class ChapterPartSequenceToSingingSynthesis(
    core_converters.abc.SymmetricalEventConverter
):
    def __init__(
        self,
        pitch_collection_to_pitch=lambda pitch_collection: pitch_collection.pitch_tuple_sorted_by_weight[
            -1
        ].register(
            0
        ),
    ):
        self.pitch_collection_to_pitch = pitch_collection_to_pitch

    def _convert_simple_event(
        self, simple_event_to_convert: core_events.SimpleEvent, absolute_time: float
    ) -> core_events.SimpleEvent:
        pitch_collection = simple_event_to_convert.pitch_collection
        pitch = self.pitch_collection_to_pitch(pitch_collection)
        note_like = (
            music_events.NoteLike(
                duration=simple_event_to_convert.duration, pitch_list=[pitch]
            )
            .set_parameter("vowel", "a", mutate=False)
            .set_parameter("consonant_tuple", ("k",))
        )
        return note_like

    def convert(
        self, chapter_part_sequence_to_convert: core_events.SequentialEvent
    ) -> core_events.SequentialEvent:
        return core_events.SequentialEvent(
            self._convert_event(chapter_part_sequence_to_convert, 0)[:]
        )


def main(chapter) -> core_events.SequentialEvent:
    pitch_collection_to_pitch_tuple = (
        lambda pitch_collection: pitch_collection.pitch_tuple_sorted_by_weight[
            -1
        ].register(0, mutate=False),
        lambda pitch_collection: pitch_collection.pitch_tuple_sorted_by_weight[
            -2
        ].register(-1, mutate=False),
        lambda pitch_collection: pitch_collection.pitch_tuple_sorted_by_weight[
            -1
        ].register(-1, mutate=False),
        lambda pitch_collection: pitch_collection.pitch_tuple_sorted_by_weight[
            -2
        ].register(0, mutate=False),
        lambda pitch_collection: pitch_collection.pitch_tuple_sorted_by_weight[
            -3
        ].register(0, mutate=False),
    )

    # RT: a tenor male pop singer: (download), and
    # MS: a female mezzo-soprano pop singer (download), and
    # EL: a female soprano lyrical singer (download).

    voice_list = ["MS", "RT", "MS", "EL", "RT"]
    chapter_part_sequence_to_singing_synthesis_tuple = tuple(
        ChapterPartSequenceToSingingSynthesis(pitch_collection_to_pitch)
        for pitch_collection_to_pitch in pitch_collection_to_pitch_tuple
    )

    simultaneous_event = core_events.SimultaneousEvent(
        [
            chapter_part_sequence_to_singing_synthesis.convert(
                chapter.chapter_part_sequence
            )
            for chapter_part_sequence_to_singing_synthesis in chapter_part_sequence_to_singing_synthesis_tuple
        ]
    )

    for sequential_event, voice in zip(simultaneous_event, voice_list):
        sequential_event.voice = voice
        print(sequential_event)
        print(sequential_event.get_parameter('pitch_list'))
        print('')

    return simultaneous_event
