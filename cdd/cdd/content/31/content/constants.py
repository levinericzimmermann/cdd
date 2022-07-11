from mutwo import cdd_converters
from mutwo import cdd_parameters
from mutwo import music_parameters

SOUND_FILE_PATH = "cdd/data/31/field_recording_5_channel.wav"

SOUND_FILE = cdd_parameters.SoundFile(SOUND_FILE_PATH)

MONO_SOUND_FILE_COLLECTION = cdd_converters.SoundFileToMonoSoundFileContainer()(
    SOUND_FILE
)

CHAPTER_DURATION_IN_SECONDS = SOUND_FILE.duration_in_seconds

# For bell synthesis
BELL_DIRECTORY_PATH = "etc/samples/bells"
BELL_COLLECTION = cdd_converters.BellCollection(
    [
        cdd_converters.Bell.from_directory_path_and_pitch(directory_path, pitch)
        for directory_path, pitch in (
            (
                f"{BELL_DIRECTORY_PATH}/0_a",
                music_parameters.WesternPitch("a", octave=5),
            ),
            (
                f"{BELL_DIRECTORY_PATH}/1_as_m32",
                music_parameters.WesternPitch(10.7, octave=5),
            ),
            (
                f"{BELL_DIRECTORY_PATH}/2_d",
                music_parameters.WesternPitch("d", octave=5),
            ),
            (
                f"{BELL_DIRECTORY_PATH}/3_fs_p43",
                music_parameters.WesternPitch(6.43, octave=6),
            ),
            (
                f"{BELL_DIRECTORY_PATH}/4_a_m40",
                music_parameters.WesternPitch(11.6, octave=6),
            ),
        )
    ]
)
BELL_PITCH_AMBITUS = music_parameters.OctaveAmbitus(
    music_parameters.DirectPitch(BELL_COLLECTION.minima_pitch.frequency)
    - music_parameters.DirectPitchInterval(200),
    music_parameters.DirectPitch(BELL_COLLECTION.maxima_pitch.frequency)
    + music_parameters.DirectPitchInterval(200),
)


PITCH_COLLECTION_DESCRIPTION_TUPLE = (
    (
        (
            (music_parameters.JustIntonationPitch("1/1"), 1),
            (music_parameters.JustIntonationPitch("28/27"), 0.7),
            (music_parameters.JustIntonationPitch("7/6"), 0.5),
            (music_parameters.JustIntonationPitch("4/3"), 0.8),
            (music_parameters.JustIntonationPitch("14/9"), 0.5),
            (music_parameters.JustIntonationPitch("7/4"), 0.5),
        ),
        "I.",
    ),
    (
        (
            (music_parameters.JustIntonationPitch("1/1"), 1),
            (music_parameters.JustIntonationPitch("16/15"), 0.5),
            (music_parameters.JustIntonationPitch("4/3"), 0.8),
            (music_parameters.JustIntonationPitch("13/8"), 0.5),
            (music_parameters.JustIntonationPitch("26/15"), 0.7),
        ),
        "II.",
    ),
    (
        (
            (music_parameters.JustIntonationPitch("1/1"), 1),
            (music_parameters.JustIntonationPitch("12/11"), 0.5),
            (music_parameters.JustIntonationPitch("4/3"), 0.8),
            (music_parameters.JustIntonationPitch("16/11"), 0.5),
            (music_parameters.JustIntonationPitch("64/33"), 0.7),
        ),
        "III.",
    ),
)


CHAPTER_PART_DATA_TUPLE = (
    # pitch collection index, duration
    (0, 2),
    (1, 2),
    (2, 2),
    (1, 1.5),
    (2, 1.75),
    (0, 1.25),
)
