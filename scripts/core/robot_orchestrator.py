from adapters.xlerobot_adapter import XLerobotAdapter
from controllers.arm_controller import ArmController
from controllers.base_controller import BaseController
from controllers.head_controller import HeadController
from state_manager import StateManager
import threading


class RobotOrchestrator:
    def __init__(self):
        self.state = StateManager()
        self.adapter = XLerobotAdapter()
        self.adapter.connect()
        self.base = BaseController(self.adapter)
        self.head = HeadController(self.adapter)
        self.arm = ArmController(self.adapter)

        # 普通动作互斥锁
        self.action_lock = threading.RLock()

    def refresh_state(self):
        self.state.last_observation = self.adapter.get_observation()

    def _with_state(self, result_dict: dict, error_msg: str = None) -> dict:
        self.refresh_state()
        self.state.last_error = error_msg if error_msg else None
        return {
            "action_result": result_dict,
            "robot_state": self.state.snapshot(),
        }

    def move_base(self, direction: str, duration: float, speed: float) -> dict:
        with self.action_lock:
            if self.state.estop:
                return self._with_state(
                    {"executed": "move_base", "status": "rejected"},
                    "robot is in estop state"
                )

            self.state.busy = True
            try:
                result = self.base.move(direction=direction, duration=duration, speed=speed)
                return self._with_state(result)
            except Exception as e:
                return self._with_state(
                    {"executed": "move_base", "status": "failed"},
                    str(e)
                )
            finally:
                self.state.busy = False

    def stop_base(self) -> dict:
        # stop_base 允许在普通动作执行期间抢占
        result = self.base.stop()
        return self._with_state(result)

    def set_head(self, head_motor_1: float, head_motor_2: float) -> dict:
        with self.action_lock:
            if self.state.estop:
                return self._with_state(
                    {"executed": "set_head", "status": "rejected"},
                    "robot is in estop state"
                )
            try:
                result = self.head.set_head(head_motor_1=head_motor_1, head_motor_2=head_motor_2)
                return self._with_state(result)
            except Exception as e:
                return self._with_state(
                    {"executed": "set_head", "status": "failed"},
                    str(e)
                )

    def reset_head(self) -> dict:
        with self.action_lock:
            if self.state.estop:
                return self._with_state(
                    {"executed": "reset_head", "status": "rejected"},
                    "robot is in estop state"
                )
            try:
                result = self.head.reset()
                return self._with_state(result)
            except Exception as e:
                return self._with_state(
                    {"executed": "reset_head", "status": "failed"},
                    str(e)
                )

    def reset_arm(self) -> dict:
        with self.action_lock:
            if self.state.estop:
                return self._with_state(
                    {"executed": "reset_arm", "status": "rejected"},
                    "robot is in estop state"
                )
            try:
                result = self.arm.reset_arm()
                return self._with_state(result)
            except Exception as e:
                return self._with_state(
                    {"executed": "reset_arm", "status": "failed"},
                    str(e)
                )

    def stop_all(self) -> dict:
        # 全局急停：先打断 controller 循环，再停硬件
        self.state.estop = True
        self.base.stop()
        self.adapter.stop_all()
        self.state.busy = False
        return self._with_state({"executed": "stop_all", "status": "completed"})

    def clear_estop(self) -> dict:
        self.state.estop = False
        return self._with_state({"executed": "clear_estop", "status": "completed"})

    def get_robot_state(self) -> dict:
        return self._with_state({"executed": "get_robot_state"})