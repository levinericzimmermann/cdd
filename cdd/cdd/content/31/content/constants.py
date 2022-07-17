import functools
import operator

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

HPSS_MARGIN_MAXIMA = 12


# X Length between bell table & tuning fork box
LONG_LINE_LENGTH = 10
# Length between tuning fork box corners
SHORT_LINE_LENGHT = 1
MIDDLE_LINE_LENGTH = LONG_LINE_LENGTH - SHORT_LINE_LENGHT

# How long it takes to walk one x or y
WALK_DURATION_FOR_ONE = 0.815  # in seconds

CORNER_ROUTE = cdd_parameters.CircularRoute(
    [
        cdd_parameters.Corner(1, 0, 0),
        cdd_parameters.Corner(2, LONG_LINE_LENGTH, 0),
        cdd_parameters.Corner(3, LONG_LINE_LENGTH, SHORT_LINE_LENGHT),
        cdd_parameters.Corner(4, SHORT_LINE_LENGHT, SHORT_LINE_LENGHT),
        cdd_parameters.Corner(5, SHORT_LINE_LENGHT, LONG_LINE_LENGTH),
        cdd_parameters.Corner(6, 0, LONG_LINE_LENGTH),
    ]
)

MIDWAY_ROUTE = cdd_parameters.CircularRoute(
    [
        cdd_parameters.Midway(
            index + 1, (point0.x + point1.x) / 2, (point0.y + point1.y) / 2
        )
        for index, point0, point1 in zip(
            range(len(CORNER_ROUTE)),
            CORNER_ROUTE,
            CORNER_ROUTE[1:] + (CORNER_ROUTE[0],),
        )
    ]
)

CIRCULAR_ROUTE = cdd_parameters.CircularRoute(
    functools.reduce(operator.add, zip(CORNER_ROUTE, MIDWAY_ROUTE))
)

DIRECTION_CLOCKWISE = cdd_parameters.Direction(1)
DIRECTION_COUNTER_CLOCKWISE = cdd_parameters.Direction(-1)


BELL_TABLE = cdd_parameters.BellTable(
    cdd_parameters.Point(
        (CIRCULAR_ROUTE[0].x + CIRCULAR_ROUTE[6].x) / 2,
        (CIRCULAR_ROUTE[0].y + CIRCULAR_ROUTE[6].y) / 2,
    )
)

POINT_TO_OBJECT = {
    CIRCULAR_ROUTE[0]: BELL_TABLE,
    CIRCULAR_ROUTE[3]: cdd_parameters.TuningFork(
        cdd_parameters.Point(CIRCULAR_ROUTE[3].x + 0.5, CIRCULAR_ROUTE[3].y)
    ),
    CIRCULAR_ROUTE[5]: cdd_parameters.Monochord(
        cdd_parameters.Point(CIRCULAR_ROUTE[5].x, CIRCULAR_ROUTE[5].y - 0.5)
    ),
    CIRCULAR_ROUTE[6]: BELL_TABLE,
    CIRCULAR_ROUTE[9]: cdd_parameters.TuningFork(
        cdd_parameters.Point(CIRCULAR_ROUTE[9].x, CIRCULAR_ROUTE[9].y + 0.5)
    ),
}
