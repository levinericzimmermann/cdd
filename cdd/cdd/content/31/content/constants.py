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
            (f"{BELL_DIRECTORY_PATH}/0_a", music_parameters.WesternPitch("a")),
            (f"{BELL_DIRECTORY_PATH}/1_as_m32", music_parameters.WesternPitch(0.7)),
            (f"{BELL_DIRECTORY_PATH}/2_d", music_parameters.WesternPitch("d")),
            (
                f"{BELL_DIRECTORY_PATH}/3_fs_p43",
                music_parameters.WesternPitch(8.57),
            ),
            (f"{BELL_DIRECTORY_PATH}/4_a_m40", music_parameters.WesternPitch(11.6)),
        )
    ]
)
