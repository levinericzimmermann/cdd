from mutwo import core_utilities


def reverse_tuple(tuple_to_reverse: tuple) -> tuple:
    # [:-1] because the last one is the center which should
    # get duplicated
    return tuple(reversed(tuple_to_reverse[:-1]))


LongToneData = tuple[float, float, str]


def reverse_long_tone_data(long_tone_data: LongToneData) -> LongToneData:
    duration_percentage, delay_percentage, hairpin = long_tone_data

    # reverse asymmetrical hairpin
    if hairpin == "<":
        hairpin = ">"
    elif hairpin == ">":
        hairpin = "<"

    return (
        duration_percentage,
        core_utilities.scale(delay_percentage, 0, 1, 1, 0),
        hairpin,
    )


def reverse_long_tone_data_tuple(
    long_tone_data_tuple: tuple[tuple[LongToneData, LongToneData, bool], ...]
) -> tuple[tuple[LongToneData, LongToneData, bool], ...]:
    reversed_tuple = reverse_tuple(long_tone_data_tuple)
    reversed_long_tone_data_list = []
    for long_tone_data_soprano, long_tone_data_clarinet, are_locked in reversed_tuple:
        # what used to be clarinet is now soprano and vice versa.
        reversed_long_tone_data_list.append(
            (
                reverse_long_tone_data(long_tone_data_clarinet),
                reverse_long_tone_data(long_tone_data_soprano),
                are_locked,
            )
        )
    return tuple(reversed_long_tone_data_list)


def reverse_density_envelope_tuple(
    density_envelope_tuple: tuple[list[tuple[float, float]], ...]
) -> tuple[list[tuple[float, float]], ...]:
    reversed_tuple = reverse_tuple(density_envelope_tuple)
    reversed_density_envelope_list = []
    for point_list in reversed_tuple:
        reversed_point_list = []
        for point in reversed(point_list):
            time, value = point
            reversed_point = (core_utilities.scale(time, 0, 1, 1, 0), value)
            reversed_point_list.append(reversed_point)
        reversed_density_envelope_list.append(reversed_point_list)
    return tuple(reversed_density_envelope_list)
