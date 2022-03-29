from mutwo import music_parameters

CLAVICHORD_CHROMATIC_PITCH_TUPLE = tuple(
    sorted(
        [
            music_parameters.JustIntonationPitch(ratio)
            for ratio in "1/1 3/2 4/3 7/4 8/7 7/6 12/7 14/9 9/7 28/27 27/14 112/81".split(
                " "
            )
        ]
    )
)
