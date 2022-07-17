from mutwo import cdd_converters
from mutwo import isis_converters
from mutwo import reaper_converters

import cdd


def render_audio_scores(chapter: cdd.chapters.Chapter):
    print("render_audio_scores")
    for (
        instrument_name,
        command_sequential_event,
    ) in chapter.command_sequential_event_dict.items():
        cdd_converters.CommandSequentialEventToSoundFile().convert(
            command_sequential_event,
            chapter.get_sound_file_path(f"audio_score_{instrument_name}"),
        )


def render_reaper_marker(chapter: cdd.chapters.Chapter):
    reaper_marker = reaper_converters.ReaperMarkerConverter(
        simple_event_to_marker_name=lambda chapter_part: chapter_part.pitch_collection.name,
        simple_event_to_marker_color=lambda _: r"0 16797088 1 B {A4376701-5AA5-246B-900B-28ABC969123A}",
    ).convert(chapter.chapter_part_sequence)
    with open(chapter.get_reaper_marker_path("pitch_collection_marks"), "w") as f:
        f.write(reaper_marker)


def render_voices(chapter: cdd.chapters.Chapter):
    for voice_index, sequential_event in enumerate(chapter.voice_simultaneous_event):
        event_to_singing_synthesis = cdd_converters.EventToSafeSingingSynthesis(
            isis_converters.EventToSingingSynthesis(
                isis_converters.EventToIsisScore(),
                "--cfg_synth etc/isis/isis-cfg-synth-31.cfg",
                "--cfg_style etc/isis/isis-cfg-style-31.cfg",
                "--seed 100",
                f"-sv {sequential_event.voice}",
            )
        )
        event_to_singing_synthesis.convert(
            sequential_event, chapter.get_sound_file_path(f"voice_{voice_index}")
        )


def render_bells(chapter: cdd.chapters.Chapter):
    print("render_bells")
    mono_bell_csound_simultaneous_event = cdd_converters.BellCsoundSequentialEventToMonoBellCsoundSimultaneousEvent().convert(
        chapter.bell_csound_sequential_event
    )

    cdd_converters.MonoBellCsoundSimultaneousEventToBellSoundFile().convert(
        mono_bell_csound_simultaneous_event, chapter.get_sound_file_path("bells")
    )


def render_bandpass_filter(chapter: cdd.chapters.Chapter):
    print("render_bandpass_filter")
    for resonator_sequential_event_index, resonator_sequential_event in enumerate(
        chapter.resonator_bandpass_melody_simultaneous_event
    ):
        cdd_converters.ResonatorSequentialEventToResonatorSoundFile().convert(
            resonator_sequential_event,
            chapter.get_sound_file_path(
                f"resonators_{resonator_sequential_event_index}"
            ),
        )


def render_harmonic_and_percussive_parts(chapter: cdd.chapters.Chapter):
    print("render_harmonic_and_percussive_parts")
    for margin in range(1, chapter.constants.HPSS_MARGIN_MAXIMA, 3):
        for channel_index, sound_file in enumerate(
            chapter.constants.MONO_SOUND_FILE_COLLECTION
        ):
            sound_file_name_prefix = f"channel_{channel_index}"
            harmonic_sound_file_path, percussive_sound_file_path = (
                chapter.get_sound_file_path(f"{sound_file_name_prefix}_{part}_{margin}")
                for part in "harmonic percussive".split(" ")
            )
            cdd_converters.SoundFileToHarmonicAndPercussiveSoundFile(
                margin, margin
            ).convert(sound_file, harmonic_sound_file_path, percussive_sound_file_path)


def main(chapter: cdd.chapters.Chapter):
    pass
    render_audio_scores(chapter)
    # render_reaper_marker(chapter)
    # render_harmonic_and_percussive_parts(chapter)
    # render_bandpass_filter(chapter)
    # render_bells(chapter)
    # render_voices(chapter)
