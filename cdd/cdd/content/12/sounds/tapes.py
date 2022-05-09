from mutwo import core_converters
from mutwo import csound_converters
from mutwo import midi_converters
from mutwo import music_events

from cdd import configurations


def render_metronome(chapter):
    event_to_csound_score = csound_converters.EventToCsoundScore(
        p4=lambda note_like: note_like.pitch_list[0].frequency
        if note_like.pitch_list
        else 0,
        p5=lambda note_like: note_like.volume.amplitude if note_like.pitch_list else 0,
        p6=lambda note_like: note_like.filter_bandwidth,
    )
    event_to_sound_file = csound_converters.EventToSoundFile(
        f"{configurations.PATH.ETC.CSOUND}/12_metronome.orc", event_to_csound_score
    )
    sound_file_path = chapter.get_sound_file_path("metronome")
    sequential_event = chapter.metronome_sequential_event.copy()
    [note_like.set_parameter("duration", float) for note_like in sequential_event]
    sequential_event = core_converters.TempoConverter(chapter.tempo_envelope)(
        sequential_event
    )
    sequential_event.duration *= 4
    event_to_sound_file.convert(sequential_event, sound_file_path)


def render_midi_tones(chapter):
    configurations.PATH.BUILDS.MIDI.C12 = "12"
    event_to_midi_file = midi_converters.EventToMidiFile()
    for chord_index, chord in enumerate(chapter.chord_sequential_event):
        for instrument_name, pitch in zip(chapter.pitch_order, chord.pitch_list):
            for octave in (-3, -2, -1, 0, 1, 2, 3):
                note_like = music_events.NoteLike(
                    pitch.register(octave, mutate=False), 180
                )
                path = f"{configurations.PATH.BUILDS.MIDI.C12}/{instrument_name}_{chord_index}_{octave}.mid"
                event_to_midi_file.convert(note_like, path)

    event_to_csound_score = csound_converters.EventToCsoundScore(
        p4=lambda note_like: note_like.pitch_list[0].frequency
        if note_like.pitch_list
        else 0,
        p5=lambda note_like: note_like.volume.amplitude if note_like.pitch_list else 0,
        p6=lambda note_like: note_like.filter_bandwidth,
    )
    event_to_sound_file = csound_converters.EventToSoundFile(
        f"{configurations.PATH.ETC.CSOUND}/12_metronome.orc", event_to_csound_score
    )
    sound_file_path = chapter.get_sound_file_path("metronome")
    sequential_event = chapter.metronome_sequential_event.copy()
    [note_like.set_parameter("duration", float) for note_like in sequential_event]
    sequential_event = core_converters.TempoConverter(chapter.tempo_envelope)(
        sequential_event
    )
    sequential_event.duration *= 4
    event_to_sound_file.convert(sequential_event, sound_file_path)


def main(chapter):
    render_midi_tones(chapter)
    render_metronome(chapter)
