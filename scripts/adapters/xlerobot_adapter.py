import threading
from lerobot.robots.lekiwi.lekiwi import LeKiwi
from lerobot.robots.lekiwi.config_lekiwi import LeKiwiConfig


class XLerobotAdapter:
    def __init__(self):
        self._connected = False
        self.io_lock = threading.RLock()

        self.config = LeKiwiConfig(
            port="/dev/ttyACM0",
            use_degrees=True,
        )
        self.robot = LeKiwi(self.config)

    def _require_connected(self):
        if not self._connected:
            raise RuntimeError("robot is not connected")

    def connect(self):
        with self.io_lock:
            if not self._connected:
                self.robot.connect(calibrate=False)
                self._connected = True

    def disconnect(self):
        with self.io_lock:
            if self._connected:
                try:
                    # 直接做底层停机，不再重复走 stop_all 语义
                    self.robot.send_action({
                        "x.vel": 0.0,
                        "y.vel": 0.0,
                        "theta.vel": 0.0,
                    })
                    self.robot.stop_base()
                finally:
                    self.robot.disconnect()
                    self._connected = False

    def get_observation(self) -> dict:
        with self.io_lock:
            if not self._connected:
                return {"connected": False}
            raw_obs = self.robot.get_observation()

        safe_obs = {"connected": self._connected}

        allowed_suffixes = (".pos", ".vel")
        allowed_exact_keys = {"timestamp", "battery"}
        allowed_prefixes = ("battery.",)

        for key, value in raw_obs.items():
            allowed = (
                key.endswith(allowed_suffixes)
                or key in allowed_exact_keys
                or key.startswith(allowed_prefixes)
            )
            if not allowed:
                continue

            if isinstance(value, (int, float)) and not isinstance(value, bool):
                safe_obs[key] = round(float(value), 3)
            elif isinstance(value, (bool, str)):
                safe_obs[key] = value
            elif hasattr(value, "item"):
                try:
                    val = value.item()
                    if isinstance(val, (int, float)) and not isinstance(val, bool):
                        safe_obs[key] = round(float(val), 3)
                    elif isinstance(val, (bool, str)):
                        safe_obs[key] = val
                except Exception:
                    pass

        return safe_obs

    def send_base(self, vx: float, vy: float, wz: float):
        self._require_connected()
        action = {
            "x.vel": vx,
            "y.vel": vy,
            "theta.vel": wz,  # deg/s
        }
        with self.io_lock:
            self.robot.send_action(action)

    def send_head(self, head_motor_1: float, head_motor_2: float):
        self._require_connected()
        action = {
            "head_motor_1.pos": head_motor_1,
            "head_motor_2.pos": head_motor_2,
        }
        with self.io_lock:
            self.robot.send_action(action)

    def reset_arm(self):
        self._require_connected()
        reset_action = {
            "arm_shoulder_pan.pos": 0.0,
            "arm_shoulder_lift.pos": 0.0,
            "arm_elbow_flex.pos": 0.0,
            "arm_wrist_flex.pos": 0.0,
            "arm_wrist_roll.pos": 0.0,
            "arm_gripper.pos": 100.0,
        }
        with self.io_lock:
            self.robot.send_action(reset_action)

    def stop_base(self):
        self._require_connected()
        with self.io_lock:
            self.robot.send_action({
                "x.vel": 0.0,
                "y.vel": 0.0,
                "theta.vel": 0.0,
            })
            self.robot.stop_base()

    def stop_all(self):
        self._require_connected()
        # 第一版仍然保持“强制停底盘”语义
        self.stop_base()