from __future__ import annotations
import dataclasses
import typing

import geometer

from mutwo import core_events


__all__ = (
    "Point",
    "PointWithPositionDescription",
    "Corner",
    "Midway",
    "Direction",
    "Path",
    "Route",
    "CircularRoute",
    "Person",
    "PointEventCollection",
    "Object",
    "TuningFork",
    "BellTable",
    "Monochord",
)


class Point(geometer.Point):
    @property
    def x(self) -> float:
        return float(self.array[0])

    @property
    def y(self) -> float:
        return float(self.array[1])

    def __hash__(self) -> int:
        return hash((self.x, self.y))

    def __sub__(self, other: Point) -> Point:
        return Point(super().__sub__(other))

    def __add__(self, other: Point) -> Point:
        return Point(super().__add__(other))


class PointWithPositionDescription(Point):
    def __init__(self, position_description: str, identity: str, *args, **kwargs):
        self.identity = identity
        self.position_description = position_description
        super().__init__(*args, **kwargs)


class Corner(PointWithPositionDescription):
    def __init__(self, corner_index: int, *args, **kwargs):
        self.corner_index = corner_index
        position_description = f"corner {self.corner_index}"
        super().__init__(position_description, "corner", *args, **kwargs)


class Midway(PointWithPositionDescription):
    def __init__(self, midway_index: int, *args, **kwargs):
        self.midway_index = midway_index
        position_description = f"midway {self.midway_index}"
        super().__init__(position_description, "midway", *args, **kwargs)


@dataclasses.dataclass(frozen=True)
class Direction(object):
    difference_per_movement: int = 1

    def __hash__(self) -> int:
        return hash(self.difference_per_movement)


@dataclasses.dataclass(frozen=True)
class Path(object):
    start: Point
    end: Point
    direction: Direction


class Route(tuple[Point]):
    ...


class CircularRoute(tuple[Point]):
    def path_to_route(self, path: Path) -> Route:
        start_index, end_index = (self.index(point) for point in (path.start, path.end))
        point_list = []
        point_count = len(self)
        point_list.append(self[start_index])
        current_index = (
            start_index + path.direction.difference_per_movement
        ) % point_count
        while current_index != end_index:
            point_list.append(self[current_index])
            current_index = (
                current_index + path.direction.difference_per_movement
            ) % point_count
        point_list.append(path.end)
        return Route(point_list)


@dataclasses.dataclass
class Person(object):
    name: str
    # Where the person is
    position: Point
    # To which direction the person looks
    watch_degree: float
    bell: typing.Optional[int] = None


@dataclasses.dataclass
class PointEventCollection(object):
    point: PointWithPositionDescription
    direction: Direction
    event_list: list[core_events.SimpleEvent]
    event_key_list: list[str] = dataclasses.field(default_factory=list)


@dataclasses.dataclass()
class Object(object):
    position: Point

    def get_action_command_sequential_event(
        self, person: Person
    ) -> core_events.SequentialEvent:
        return core_events.SequentialEvent([])

    def get_command_sequential_event(
        self, person: Person
    ) -> core_events.SequentialEvent:
        from mutwo import cdd_converters
        from mutwo import cdd_events

        command_sequential_event = core_events.SequentialEvent([])
        watch_degree = cdd_converters.PointPairToWatchDegree()(
            person.position, self.position
        )

        difference = watch_degree - person.watch_degree
        if difference < 0:
            difference = 360 + difference
        if difference:
            command_sequential_event.append(cdd_events.TurnTo(difference))
            command_sequential_event.extend(
                self.get_action_command_sequential_event(person)
            )
            # command_sequential_event.append(cdd_events.TurnTo((360 - difference) % 360))
            # person.watch_degree = (360 - watch_degree)
        else:
            command_sequential_event.extend(
                self.get_action_command_sequential_event(person)
            )

        return command_sequential_event


class KneeDownObject(Object):
    def get_object_interaction_command_sequential_event(self, person: Person):
        command_sequential_event = core_events.SequentialEvent([])
        return command_sequential_event

    def get_action_command_sequential_event(
        self, person: Person
    ) -> core_events.SequentialEvent:
        from mutwo import cdd_events

        command_sequential_event = core_events.SequentialEvent([])
        command_sequential_event.append(cdd_events.KNEE_DOWN)
        command_sequential_event.extend(
            self.get_object_interaction_command_sequential_event(person)
        )
        command_sequential_event.append(cdd_events.STAND_UP)
        return command_sequential_event


class TuningFork(KneeDownObject):
    def get_object_interaction_command_sequential_event(
        self, person: Person
    ) -> core_events.SequentialEvent:
        from mutwo import cdd_events

        # hard coded hidden algorithm
        if self.position.x == 0.5:
            command_sequential_event = core_events.SequentialEvent(
                [cdd_events.PLAY_TUNING_FORK, cdd_events.PLAY_TUNING_FORK]
            )
        else:
            command_sequential_event = core_events.SequentialEvent(
                [cdd_events.PLAY_TUNING_FORK]
            )
        return command_sequential_event


class Monochord(KneeDownObject):
    def get_object_interaction_command_sequential_event(
        self, person: Person
    ) -> core_events.SequentialEvent:
        from mutwo import cdd_events

        command_sequential_event = core_events.SequentialEvent(
            [cdd_events.PLAY_MONOCHORD]
        )
        return command_sequential_event


class BellTable(Object):
    def get_action_command_sequential_event(
        self, person: Person
    ) -> core_events.SequentialEvent:

        from mutwo import cdd_events

        command_sequential_event = core_events.SequentialEvent([])
        person_name = person.name

        if person.bell:
            command_sequential_event.append(cdd_events.LEAVE_BELL)
            if person_name == "soprano":
                bell_index = 2
            elif person_name == "clarinet":
                bell_index = 4
            else:
                raise NotImplementedError(person_name)
        else:
            if person_name == "soprano":
                bell_index = 1
            elif person_name == "clarinet":
                bell_index = 3
            else:
                raise NotImplementedError(person_name)

        person.bell = bell_index
        command_sequential_event.append(cdd_events.TakeBell(bell_index))
        return command_sequential_event
