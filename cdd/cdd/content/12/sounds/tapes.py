from mutwo import core_converters
from mutwo import csound_converters

from cdd import configurations


def render_metronome(chapter):
    event_to_csound_score = csound_converters.EventToCsoundScore(
        p4=lambda note_like: note_like.pitch_list[0].frequency
        if note_like.pitch_list else 0,
        p5=lambda note_like: note_like.volume.amplitude if note_like.pitch_list else 0,
        p6=lambda note_like: note_like.filter_bandwidth,
    )
    event_to_sound_file = csound_converters.EventToSoundFile(
        f"{configurations.PATH.ETC.CSOUND}/12_metronome.orc", event_to_csound_score
    )
    sound_file_path = chapter.get_sound_file_path("metronome")
    sequential_event = chapter.metronome_sequential_event.copy()
    [note_like.set_parameter("duration", float) for note_like in sequential_event]
    sequential_event = core_converters.TempoConverter(chapter.tempo_envelope)(sequential_event)
    sequential_event.duration *= 4
    event_to_sound_file.convert(sequential_event, sound_file_path)


def main(chapter):
    render_metronome(chapter)
