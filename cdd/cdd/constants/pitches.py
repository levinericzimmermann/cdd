from mutwo import music_parameters

music_parameters.configurations.DEFAULT_CONCERT_PITCH = CONCERT_PITCH = 440

PITCH_REFERENCE_STRING = "a"

WESTERN_PITCH_REFERENCE = music_parameters.WesternPitch(
    PITCH_REFERENCE_STRING, octave=4
)
