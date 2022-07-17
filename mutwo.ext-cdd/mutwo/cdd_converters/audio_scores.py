import math
import os
import uuid

import geometer
import gtts
import progressbar
import pydub
import sox

from mutwo import cdd_events
from mutwo import cdd_parameters
from mutwo import core_converters
from mutwo import core_events
from mutwo import csound_converters

KEY_WAIT = "wait"
KEY_CONTINUE = "continue"
KEY_PLAY_BELL = "play_bell"
KEY_INTERACT = "interact"

WAIT_TIME = 8


class PointPairToWatchDegree(core_converters.abc.Converter):
    def convert(self, point0: cdd_parameters.Point, point1: cdd_parameters.Point):
        line0 = geometer.Line(point0, geometer.Point(point0.x, point0.y + 100))
        line1 = geometer.Line(point0, point1)
        try:
            degree = geometer.angle(line0, line1) * (180 / math.pi)
        except geometer.exceptions.LinearDependenceError:
            degree = 0 if point1.y > point0.y else 180
        else:
            absolute_degree = abs(degree)
            if point1.x > point0.x:
                degree = absolute_degree
            else:
                degree = -absolute_degree

        return degree


class PointEventCollectionAndPersonToCommandSequentialEvent(
    core_converters.abc.Converter
):
    def __init__(
        self,
        circular_route: cdd_parameters.CircularRoute,
        walk_duration_for_one: int,
        point_to_object: dict[cdd_parameters.Point, cdd_parameters.Object],
    ):
        self._walk_duration_for_one = walk_duration_for_one
        self._circular_route = circular_route
        self._point_to_object = point_to_object

    def convert(
        self,
        point_event_collection: cdd_parameters.PointEventCollection,
        person: cdd_parameters.Person,
    ) -> core_events.SequentialEvent[cdd_events.Command]:
        route = self._circular_route.path_to_route(
            cdd_parameters.Path(
                person.position,
                point_event_collection.point,
                point_event_collection.direction,
            )
        )
        watch_degree = PointPairToWatchDegree()(*route[:2])

        difference = watch_degree - person.watch_degree
        if difference < 0:
            difference = 360 + difference
        command_sequential_event = core_events.SequentialEvent([])
        if difference:
            command_sequential_event.append(cdd_events.TurnTo(difference))

        person.position = point_event_collection.point
        # After walking the person will have a new watch degree
        # (the person will look in the opposite direction from he or she came)
        person.watch_degree = PointPairToWatchDegree()(route[-2], route[-1])

        distance = 0
        for point0, point1 in zip(route, route[1:]):
            distance += abs(geometer.dist(point0, point1))

        walk_duration = max((distance * self._walk_duration_for_one, 4))
        command_sequential_event.append(
            cdd_events.MoveTo(walk_duration, point_event_collection.point)
        )

        added_event_list = point_event_collection.event_list
        for event_key in point_event_collection.event_key_list:
            if event_key == KEY_CONTINUE:
                continue
            if event_key == KEY_INTERACT:
                object_to_interact_with = self._point_to_object[
                    point_event_collection.point
                ]
                added_event_list.extend(
                    object_to_interact_with.get_command_sequential_event(person)
                )
            if event_key == KEY_PLAY_BELL:
                added_event_list.append(cdd_events.PLAY_BELL)
            if event_key == KEY_WAIT:
                added_event_list.append(cdd_events.Wait(WAIT_TIME))

        command_sequential_event.extend(added_event_list)
        for event in added_event_list:
            if isinstance(event, cdd_events.TurnTo):
                person.watch_degree = (person.watch_degree + event.degree) % 360
            if isinstance(event, cdd_events.MoveTo):
                raise NotImplementedError()
        return command_sequential_event


class PointEventCollectionListToCommandSequentialEvent(core_converters.abc.Converter):
    def __init__(
        self,
        point_event_collection_and_person_to_command_sequential_event: PointEventCollectionAndPersonToCommandSequentialEvent,
    ):
        self._point_event_collection_and_person_to_command_sequential_event = (
            point_event_collection_and_person_to_command_sequential_event
        )

    def convert(
        self,
        point_event_collection_list: list[cdd_parameters.PointEventCollection],
        start_position: cdd_parameters.Point,
        start_watch_degree: float,
        person_name: str,
    ) -> core_events.SequentialEvent:
        person = cdd_parameters.Person(person_name, start_position, start_watch_degree)
        command_sequential_event = core_events.SequentialEvent([])
        for point_event_collection in point_event_collection_list:
            command_sequential_event.extend(
                self._point_event_collection_and_person_to_command_sequential_event.convert(
                    point_event_collection, person
                )
            )

        return command_sequential_event


class CommandToSoundFile(core_converters.abc.Converter):
    def convert(self, command_to_convert: cdd_events.Command, path: str):
        path_mp3 = f"{path.split('.')[0]}.mp3"
        if command_to_convert.command_text:
            tts = gtts.gTTS(command_to_convert.command_text)
            tts.save(path_mp3)
            sox.transform.sox(["sox", path_mp3, "-r", "44100", path])
            os.remove(path_mp3)
        else:
            raise ValueError(str(command_to_convert))


class CommandSequentialEventToSoundFile(csound_converters.EventToSoundFile):
    def __init__(self):
        super().__init__(
            "etc/csound/31_audio_score.orc",
            csound_converters.EventToCsoundScore(
                p3=lambda event: sox.file_info.duration(event.sound_file_path),
                p4=lambda event: event.sound_file_path,
            ),
        )

    def render_empty_sound_file(self, sound_file_path: str, duration: float):
        empty_audio_segment = pydub.AudioSegment.silent(
            duration=duration * 1000,
            frame_rate=44100,
        )
        empty_audio_segment.export(sound_file_path, format="wav")

    def convert(
        self,
        sequential_event_to_convert: core_events.SequentialEvent[cdd_events.Command],
        path: str,
    ):
        new_sequential_event = core_events.SequentialEvent([])

        command_to_soundfile = CommandToSoundFileWithCounting()
        with progressbar.ProgressBar(max_value=len(sequential_event_to_convert)) as bar:
            for command_index, command in enumerate(sequential_event_to_convert):
                sound_file_path = f".{uuid.uuid4()}.wav"
                command_to_soundfile.convert(command, sound_file_path)
                simple_event = core_events.SimpleEvent(command.duration).set_parameter(
                    "sound_file_path", sound_file_path
                )
                new_sequential_event.append(simple_event)
                bar.update(command_index)

        super().convert(new_sequential_event, path)
        for simple_event in new_sequential_event:
            os.remove(simple_event.sound_file_path)


class CommandToSoundFileWithCounting(CommandToSoundFile):
    def convert(self, command_to_convert: cdd_events.Command, path: str):
        base_path = f"_base_{path}"
        super().convert(command_to_convert, base_path)
        base_duration = sox.file_info.duration(base_path)
        pause = 1
        difference = command_to_convert.duration - base_duration - pause
        if difference > 3 and isinstance(command_to_convert, cdd_events.MoveTo):
            rounded_difference = int(difference)
            remainder = difference - rounded_difference
            counter = reversed(range(1, rounded_difference + 1))
            count_down_event_list = [
                cdd_events.Command(1, str(count_index)) for count_index in counter
            ]
            sequential_event_to_convert = core_events.SequentialEvent(
                [
                    command_to_convert.set_parameter(
                        "duration", base_duration + remainder + pause, mutate=False
                    )
                ]
                + count_down_event_list
            )
            CommandSequentialEventToSoundFile().convert(
                sequential_event_to_convert, path
            )
            os.remove(base_path)
        else:
            os.rename(base_path, path)
