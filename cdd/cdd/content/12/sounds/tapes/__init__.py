from distutils.dir_util import copy_tree

from mutwo import core_converters
from mutwo import core_events
from mutwo import csound_converters
from mutwo import midi_converters
from mutwo import music_events

from cdd import configurations

from . import chords


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


def render_intonation_help(chapter):
    event_to_csound_score = csound_converters.EventToCsoundScore(
        p4=lambda note_like: note_like.pitch_list[0].frequency
        if note_like.pitch_list
        else 0,
        p5=lambda note_like: note_like.volume.amplitude if note_like.pitch_list else 0,
    )
    event_to_sound_file = csound_converters.EventToSoundFile(
        f"{configurations.PATH.ETC.CSOUND}/12_intonation.orc", event_to_csound_score
    )
    duration_per_tone = 25  # seconds
    duration_per_rest = 2  # seconds

    simultaneous_event = core_events.SimultaneousEvent(
        [core_events.SequentialEvent([]) for _ in range(3)]
    )
    for index, time_bracket_tuple in enumerate(
        zip(*chapter.sustaining_instrument_dict.values())
    ):
        note_like = music_events.NoteLike(
            [time_bracket[2][0].pitch_list[0] for time_bracket in time_bracket_tuple],
            duration_per_tone,
        )
        note_like.pitch_list.append(
            chapter.chord_sequential_event[index].pitch_list[
                chapter.pitch_order.index("clavichord")
            ]
        )
        for sequential_event, pitch in zip(simultaneous_event, note_like.pitch_list):
            local_note_like = note_like.set_parameter("pitch_list", pitch, mutate=False)
            sequential_event.append(local_note_like)
            sequential_event.append(music_events.NoteLike([], duration_per_rest))

    for duration, sequential_event in zip((0.2, 0.1, 0.04), simultaneous_event):
        sequential_event.insert(0, music_events.NoteLike([], duration))

    sound_file_path = chapter.get_sound_file_path("intonation")
    event_to_sound_file.convert(simultaneous_event, sound_file_path)

    note_index = 0
    intonation_directory = "12_intonation"
    intonation_file_path = (
        f"{configurations.PATH.BUILDS.SOUND_FILES}/{intonation_directory}"
    )
    intonation_soprano_file_path = (
        f"{configurations.PATH.BUILDS.SOUND_FILES}/12_intonation-solo-soprano"
    )
    for absolute_time, note_like in zip(
        simultaneous_event[0].absolute_time_tuple, simultaneous_event[0]
    ):
        if note_like.pitch_list:
            end_time = absolute_time + note_like.duration
            new_simultaneous_event = core_events.SimultaneousEvent(
                [
                    sequential_event.cut_out(absolute_time, end_time, mutate=False)
                    for sequential_event in simultaneous_event
                ]
            )
            sound_file_path = f"{intonation_file_path}/12_intonation_{note_index}.wav"
            sound_file_path_soprano = f"{intonation_soprano_file_path}/12_intonation_soprano_pitch_{note_index}.wav"
            event_to_sound_file.convert(new_simultaneous_event, sound_file_path)
            event_to_sound_file.convert(note_like, sound_file_path_soprano)
            note_index += 1

    # Copy data for walkman file
    copy_tree(
        intonation_file_path,
        f"{configurations.PATH.WALKMAN.TAPES}/{intonation_directory}",
    )


def main(chapter):
    chords.main(chapter)
    render_midi_tones(chapter)
    render_metronome(chapter)
    render_intonation_help(chapter)
