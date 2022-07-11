from mutwo import cdd_converters
from mutwo import isis_converters

import cdd


def render_voices(chapter: cdd.chapters.Chapter):
    for voice_index, sequential_event in enumerate(chapter.voice_simultaneous_event):
        event_to_singing_synthesis = cdd_converters.EventToSafeSingingSynthesis(
            isis_converters.EventToSingingSynthesis(
                isis_converters.EventToIsisScore(),
                "--cfg_synth etc/isis/isis-cfg-synth-31.cfg",
                "--cfg_style etc/isis/isis-cfg-style-31.cfg",
                "--seed 100",
                f"-sv {sequential_event.voice}"
            )
        )
        event_to_singing_synthesis.convert(
            sequential_event, chapter.get_sound_file_path(f"voice_{voice_index}")
        )


def render_bells(chapter: cdd.chapters.Chapter):
    mono_bell_csound_simultaneous_event = cdd_converters.BellCsoundSequentialEventToMonoBellCsoundSimultaneousEvent().convert(
        chapter.bell_csound_sequential_event
    )

    cdd_converters.MonoBellCsoundSimultaneousEventToBellSoundFile().convert(
        mono_bell_csound_simultaneous_event, chapter.get_sound_file_path("bells")
    )


def render_bandpass_filter(chapter: cdd.chapters.Chapter):
    for resonator_sequential_event_index, resonator_sequential_event in enumerate(
        chapter.resonator_bandpass_melody_simultaneous_event
    ):
        cdd_converters.ResonatorSequentialEventToResonatorSoundFile().convert(
            resonator_sequential_event,
            chapter.get_sound_file_path(
                f"resonators_{resonator_sequential_event_index}"
            ),
        )


def main(chapter: cdd.chapters.Chapter):
    print("START RENDER SOUND")
    # render_bandpass_filter(chapter)
    render_bells(chapter)
    # render_voices(chapter)
