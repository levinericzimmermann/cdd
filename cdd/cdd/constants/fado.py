import os

from mutwo import core_events
from mutwo import core_utilities
from mutwo import midi_converters

import cdd


def _get_fado_event(
    fado_directory_path: str, midi_file_to_event: midi_converters.MidiFileToEvent
) -> core_events.SimultaneousEvent:
    for path in os.listdir(fado_directory_path):
        if path[-3:] == "mid":
            fado_midi_file_path = f"{fado_directory_path}/{path}"
            break
    return midi_file_to_event.convert(fado_midi_file_path)


@core_utilities.compute_lazy(
    path=f"{cdd.configurations.PATH.BUILDS.PICKLED}/fado.pickle",
    force_to_compute=cdd.configurations.FORCE_TO_COMPUTE_FADO,
)
def _get_fado_event_tuple(path: str):
    midi_file_to_event = midi_converters.MidiFileToEvent()
    return tuple(
        [
            _get_fado_event(
                f"{cdd.configurations.PATH.CDD.DATA.FADO}/{fado_directory_path}",
                midi_file_to_event,
            )
            for fado_directory_path in os.listdir(path)
        ]
    )


# FADO_EVENT_TUPLE = _get_fado_event_tuple(cdd.configurations.PATH.CDD.DATA.FADO)
