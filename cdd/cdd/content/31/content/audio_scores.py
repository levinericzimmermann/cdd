import itertools

from mutwo import cdd_converters
from mutwo import cdd_events
from mutwo import cdd_parameters
from mutwo import core_events


def unrepeat_position_generator(start_position: cdd_parameters.Point, chapter):
    last_position = start_position
    second_last_position = None
    direction = chapter.constants.DIRECTION_CLOCKWISE
    while True:
        route = chapter.constants.CIRCULAR_ROUTE.path_to_route(
            cdd_parameters.Path(last_position, last_position, direction)
        )
        route = iter(route)
        new_position = None
        while new_position is None:
            next_position = next(route)
            if (
                next_position.identity != last_position.identity
                and next_position.x != last_position.x
                and next_position.y != last_position.y
                and next_position != second_last_position
            ):
                new_position = next_position
        yield (new_position, direction)
        second_last_position = last_position
        last_position = new_position
        direction = (
            chapter.constants.DIRECTION_COUNTER_CLOCKWISE
            if direction == chapter.constants.DIRECTION_CLOCKWISE
            else chapter.constants.DIRECTION_CLOCKWISE
        )


def get_point_tuple(
    start_position: cdd_parameters.Point, chapter, position_count: int = 12
) -> tuple[cdd_parameters.Point, ...]:
    position_generator = unrepeat_position_generator(start_position, chapter)
    return tuple(next(position_generator) for _ in range(position_count))


def get_point_event_collection_list(
    instrument_name: str, point_and_direction_tuple: tuple, chapter
):

    event_key_list_cycle = itertools.cycle(
        (
            [cdd_converters.KEY_PLAY_BELL],
            [cdd_converters.KEY_WAIT],
            [cdd_converters.KEY_PLAY_BELL],
            [cdd_converters.KEY_CONTINUE],
            [cdd_converters.KEY_CONTINUE],
            [cdd_converters.KEY_WAIT, cdd_converters.KEY_PLAY_BELL],
        )
    )

    point_event_collection_list = []
    for point, direction in point_and_direction_tuple:
        if point in chapter.constants.POINT_TO_OBJECT and not (
            # I don't want the tuning forks so early, they should appear later,
            # so this is a little asymmetry.
            instrument_name == "soprano"
            and point == chapter.constants.CIRCULAR_ROUTE[3]
        ):
            event_key_list = [cdd_converters.KEY_INTERACT]
        else:
            event_key_list = next(event_key_list_cycle)

        point_event_collection = cdd_parameters.PointEventCollection(
            point=point,
            direction=direction,
            event_list=[],
            event_key_list=event_key_list,
        )
        point_event_collection_list.append(point_event_collection)
    return point_event_collection_list


def add_end_events(point_event_collection_list, chapter):
    # End events (move to chairs and sit down)
    point_event_collection_list.append(
        cdd_parameters.PointEventCollection(
            chapter.constants.CIRCULAR_ROUTE[1],
            direction=chapter.constants.DIRECTION_COUNTER_CLOCKWISE,
            event_list=[cdd_events.TurnTo(90), cdd_events.SIT_DOWN],
        )
    )


def main(chapter) -> dict[str, core_events.SequentialEvent]:
    point_event_collection_list_to_command_sequential_event = (
        cdd_converters.PointEventCollectionListToCommandSequentialEvent(
            cdd_converters.PointEventCollectionAndPersonToCommandSequentialEvent(
                chapter.constants.CIRCULAR_ROUTE,
                chapter.constants.WALK_DURATION_FOR_ONE,
                chapter.constants.POINT_TO_OBJECT,
            )
        )
    )
    instrument_name_to_command_sequential_event = {}
    for instrument_name in ("soprano", "clarinet"):

        # Player enters the room from the kitchen
        start_position = chapter.constants.CIRCULAR_ROUTE[2]
        start_watch_degree = 0

        point_and_direction_tuple = get_point_tuple(start_position, chapter, 12)
        if instrument_name == "clarinet":
            point_and_direction_tuple = point_and_direction_tuple[:-1]
        point_event_collection_list = get_point_event_collection_list(
            instrument_name, point_and_direction_tuple, chapter
        )
        add_end_events(point_event_collection_list, chapter)
        sequential_event = (
            point_event_collection_list_to_command_sequential_event.convert(
                point_event_collection_list,
                start_position=start_position,
                start_watch_degree=start_watch_degree,
                person_name=instrument_name,
            )
        )
        # START EVENT
        sequential_event.insert(0, cdd_events.Command(4, "enter the room"))
        instrument_name_to_command_sequential_event.update(
            {instrument_name: sequential_event}
        )
    return instrument_name_to_command_sequential_event
