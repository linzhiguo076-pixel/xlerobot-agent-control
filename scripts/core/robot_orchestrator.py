from adapters.xlerobot_adapter import XLerobotAdapter
from controllers.arm_controller import ArmController
from controllers.base_controller import BaseController
from controllers.head_controller import HeadController
from state_manager import StateManager


class RobotOrchestrator:
    def __init__(self):
        self.state = StateManager()
        self.adapter = XLerobotAdapter()
        self.adapter.connect()
        self.base = BaseController(self.adapter)
        self.head = HeadController(self.adapter)
        self.arm = ArmController(self.adapter)

    def refresh_state(self):
        self.state.last_observation = self.adapter.get_observation()
    
    def _with_state(self, result_dict: dict, error_msg: str = None) -> dict:
        self.refresh_state()
        if error_msg:
            self.state.last_error = error_msg # 建议 10
        else:
            self.state.last_error = None
            
        return {
            "action_result": result_dict,
            "robot_state": self.state.snapshot()
        }

    def move_base(self, direction: str, duration: float, speed: float) -> dict:
        self.state.busy = True
        try:
            result = self.base.move(direction=direction, duration=duration, speed=speed)
            return self._with_state(result)
        except Exception as e:
            return self._with_state({"executed": "move_base", "status": "failed"}, str(e))
        finally:
            self.state.busy = False

    def stop_base(self) -> dict:
        result = self.base.stop()
        self.refresh_state()
        return result

    def set_head(self, head_motor_1: float, head_motor_2: float) -> dict:
        result = self.head.set_head(head_motor_1=head_motor_1, head_motor_2=head_motor_2)
        self.refresh_state()
        return result

    def reset_head(self) -> dict:
        result = self.head.reset()
        self.refresh_state()
        return result

    def reset_arm(self, side: str) -> dict:
        result = self.arm.reset_arm(side)
        self.refresh_state()
        return result

    def get_robot_state(self) -> dict:
        self.refresh_state()
        return self.state.snapshot()

    def stop_all(self) -> dict:
        self.adapter.stop_all()
        self.refresh_state()
        return {"executed": "stop_all", "state": self.state.snapshot()}
