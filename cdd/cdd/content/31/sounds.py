from mutwo import cdd_converters

import cdd


def render_bells(chapter: cdd.chapters.Chapter):
    mono_bell_csound_simultaneous_event = cdd_converters.BellCsoundSequentialEventToMonoBellCsoundSimultaneousEvent().convert(
        chapter.bell_csound_sequential_event

    )

    cdd_converters.MonoBellCsoundSimultaneousEventToBellSoundFile().convert(
        mono_bell_csound_simultaneous_event, chapter.get_sound_file_path("bells")
    )


def main(chapter: cdd.chapters.Chapter):
    render_bells(chapter)
