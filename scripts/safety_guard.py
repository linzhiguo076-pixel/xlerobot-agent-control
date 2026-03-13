ALLOWED_ACTIONS = {
    "move_base",
    "stop_base",
    "set_head",
    "reset_head",
    "reset_arm",
    "get_robot_state",
    "stop_all",
    "clear_estop",
}

BASE_DIRECTIONS = {
    "forward",
    "backward",
    "left",
    "right",
    "rotate_left",
    "rotate_right",
}

HEAD_MOTOR_1_RANGE = (-45.0, 45.0)
HEAD_MOTOR_2_RANGE = (-30.0, 30.0)


def _require_number(value, name: str) -> float:
    if not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a number")
    return float(value)


def _require_in_range(value: float, name: str, low: float, high: float) -> float:
    if not (low <= value <= high):
        raise ValueError(f"{name} must be between {low} and {high}")
    return value


def validate_request(request: dict) -> dict:
    if not isinstance(request, dict):
        raise ValueError("request must be a dict")

    action_type = request.get("action_type")
    parameters = request.get("parameters", {})

    if action_type not in ALLOWED_ACTIONS:
        raise ValueError(f"unsupported action_type: {action_type}")
    if not isinstance(parameters, dict):
        raise ValueError("parameters must be a dict")

    normalized = {"action_type": action_type, "parameters": dict(parameters)}

    if action_type == "move_base":
        direction = parameters.get("direction")
        if direction not in BASE_DIRECTIONS:
            raise ValueError(f"direction must be one of {sorted(BASE_DIRECTIONS)}")

        duration = _require_number(parameters.get("duration"), "duration")
        if not (0.1 <= duration <= 3.0):
            raise ValueError("duration must be between 0.1 and 3.0 seconds")

        speed = parameters.get("speed")
        is_rotation = str(direction).startswith("rotate")

        if speed is None:
            speed = 30.0 if is_rotation else 0.15

        speed = _require_number(speed, "speed")

        if is_rotation:
            max_angular_speed = 60.0
            if not (0.01 <= speed <= max_angular_speed):
                raise ValueError(
                    f"rotation speed must be between 0.01 and {max_angular_speed} deg/s"
                )
        else:
            max_linear_speed = 0.3
            if not (0.01 <= speed <= max_linear_speed):
                raise ValueError(
                    f"linear speed must be between 0.01 and {max_linear_speed} m/s"
                )

        normalized["parameters"] = {
            "direction": direction,
            "duration": duration,
            "speed": speed,
        }

    elif action_type == "set_head":
        hm1 = _require_number(parameters.get("head_motor_1"), "head_motor_1")
        hm2 = _require_number(parameters.get("head_motor_2"), "head_motor_2")

        hm1 = _require_in_range(hm1, "head_motor_1", *HEAD_MOTOR_1_RANGE)
        hm2 = _require_in_range(hm2, "head_motor_2", *HEAD_MOTOR_2_RANGE)

        normalized["parameters"] = {
            "head_motor_1": hm1,
            "head_motor_2": hm2,
        }

    elif action_type in {"reset_arm", "stop_base", "reset_head", "get_robot_state", "stop_all", "clear_estop"}:
        normalized["parameters"] = {}

    else:
        normalized["parameters"] = {}

    return normalized