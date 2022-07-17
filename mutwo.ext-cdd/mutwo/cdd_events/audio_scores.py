from mutwo import cdd_parameters
from mutwo import core_events


class Command(core_events.SimpleEvent):
    def __init__(self, duration: float, command_text: str):
        self.command_text = command_text
        super().__init__(duration)


class Wait(Command):
    def __init__(self, duration: float):
        super().__init__(duration, "wait for few seconds")


class TurnTo(Command):
    def __init__(self, degree: float):
        self.degree = float(degree)
        try:
            assert degree >= 0 and degree <= 360
        except AssertionError:
            raise ValueError("Invalid degree: %s" % degree)

        turn_direction = "left"
        if degree > 180:
            turn_direction = "right"
            degree = 360 - degree
        elif degree == 180:
            turn_direction = None
            turn_direction_text = ""

        if turn_direction:
            turn_direction_text = f"to the {turn_direction}"

        command_text = f"turn {int(degree)} degree {turn_direction_text}"
        self.text_degree = degree
        super().__init__(3.85, command_text)


class MoveTo(Command):
    def __init__(
        self,
        duration: float,
        point_with_position_description: cdd_parameters.PointWithPositionDescription,
    ):
        self.point = point_with_position_description
        super().__init__(
            duration,
            "walk the lane until you reach %s"
            % point_with_position_description.position_description,
        )


class TakeBell(Command):
    def __init__(self, bell_index: int):
        super().__init__(4, "take bell number %s" % bell_index)


KNEE_DOWN = Command(5, "kneel down")
STAND_UP = Command(4, "stand up")
PLAY_BELL = Command(10, "ring your bell")
PLAY_MONOCHORD = Command(8, "play one tone with the monochord")
PLAY_TUNING_FORK = Command(
    12, "play the tuning fork"
)
LEAVE_BELL = Command(3, "leave your bell at the table")
SIT_DOWN = Command(2, "sit down on your chair")
