from mutwo import music_parameters

CLAVICHORD_PITCH_TUPLE = tuple(
    sorted(
        [
            music_parameters.JustIntonationPitch(ratio)
            for ratio in "1/1 3/2 4/3 7/4 8/7 7/6 12/7 14/9 9/7 28/27 27/14 112/81".split(
                " "
            )
        ]
    )
)


def print_tuning():
    for pitch in CLAVICHORD_PITCH_TUPLE:
        print(
            pitch.ratio,
            '\t',
            round(pitch.cent_deviation_from_closest_western_pitch_class, 1),
            '\t',
            pitch.get_closest_pythagorean_pitch_name(),
        )


def write_scl():
    with open('clavichord.scl', 'w') as f:
        f.write('! clavichord.scl\n!\nLevin clavichord tuning\n 12\n!\n')
        for pitch in CLAVICHORD_PITCH_TUPLE[1:]:
            f.write(str(pitch.ratio))
            f.write('\n')
        f.write('2/1\n')

# write_scl()
print_tuning()
