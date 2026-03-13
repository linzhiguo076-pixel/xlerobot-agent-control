from handlers.arm_handler import handle_arm_action
from handlers.base_handler import handle_base_action
from handlers.global_handler import handle_global_action
from handlers.head_handler import handle_head_action


def route_action(request: dict) -> dict:
    action_type = request["action_type"]

    if action_type in {"move_base", "stop_base"}:
        return handle_base_action(request)
    if action_type in {"set_head", "reset_head"}:
        return handle_head_action(request)
    if action_type in {"reset_arm"}:
        return handle_arm_action(request)
    if action_type in {"get_robot_state", "stop_all", "clear_estop"}:
        return handle_global_action(request)

    raise ValueError(f"unsupported action_type: {action_type}")