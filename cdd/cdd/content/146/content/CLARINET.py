import abjad
import quicktions as fractions

from mutwo import core_events
from mutwo import mmml_converters
from mutwo import music_events
from mutwo import music_parameters

from cdd import utilities

from . import CLAVICHORD

pedal_tone_tuple = tuple(
    music_parameters.JustIntonationPitch(ratio) for ratio in "1/2 1/3 3/8".split(" ")
)

microtonal_pitch_sequence_tuple = tuple(
    mmml_converters.MMMLEventsConverter(
        mmml_converters.MMMLPitchesConverter(
            mmml_converters.MMMLSingleJIPitchConverter()
        )
    )
    .convert(mmml_string)
    .get_parameter("pitch_list")
    for mmml_string in (
        "7-:1 3++ 7- 7+3-",
        "3--:0 7+ 3+7- 7+",
        "11-:1 3+ 7+3-- 3+",
    )
)

pedal_tone_sequential_event_tuple = tuple(
    core_events.SequentialEvent(
        [
            music_events.NoteLike(
                pedal_tone,
                duration=fractions.Fraction(
                    1,
                    1,
                ),
            )
        ]
    )
    for pedal_tone in pedal_tone_tuple
)

pedal_tone_sequential_event = core_events.SequentialEvent(
    [music_events.NoteLike(list(pedal_tone_tuple), duration=fractions.Fraction(1, 1))]
)

pedal_tone_sequential_event[
    0
].notation_indicator_collection.rehearsal_mark.markup = abjad.Markup(
    r"\small { \caps { pedal tones } }"
)

microtonal_movement_sequential_event_tuple = tuple(
    core_events.SequentialEvent(
        [
            music_events.NoteLike(pitch, duration=fractions.Fraction(1, 1))
            for pitch in microtonal_pitch_sequence
        ]
    )
    for microtonal_pitch_sequence in microtonal_pitch_sequence_tuple
)

instruction_text = f"""
freely choose from given material of pedal notes, hyperchromatic melodies and rising or falling scales;
vary them ad. lib. (e.g.
play a very long and very quiet tone from pedal note material;
play slow ostinati with two alternating pedal notes;
fill rests between clavichord and soprano with hyperchromatic melodies;
listen to beatings between hyperchromatic melodies and sine waves).
duration: {utilities.duration_in_seconds_to_readable_duration(CLAVICHORD.sequential_event_absolute_time_tuple[-1] + CLAVICHORD.line_duration)} minutes.
"""
