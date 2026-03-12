import logging
import numpy as np
from lerobot.robots.lekiwi.lekiwi import LeKiwi
from lerobot.robots.lekiwi.config_lekiwi import LeKiwiConfig

class XLerobotAdapter:
    def __init__(self):
        self._connected = False
        
        self.config = LeKiwiConfig(
            port="/dev/ttyACM0",  # Linux 默认端口，Mac 可能是 /dev/tty.usbmodemXXX
            use_degrees=True      # 统一使用角度 (degrees) 作为关节单位
        )
        self.robot = LeKiwi(self.config)

    def connect(self):
        if not self._connected:
            self.robot.connect(calibrate=False)
            self._connected = True

    def disconnect(self):
        if self._connected:
            self.robot.disconnect()
            self._connected = False

    def get_observation(self) -> dict:
        if not self._connected:
            return {"connected": False}
        
        raw_obs = self.robot.get_observation()
        safe_obs = {"connected": self._connected}

        allowed_suffixes = (".pos", ".vel")
        allowed_keys = ("battery", "timestamp")
        
        for key, value in raw_obs.items():
            if key.endswith(allowed_suffixes) or key in allowed_keys:
                if isinstance(value, (int, float)) and not isinstance(value, bool):
                    safe_obs[key] = round(value, 3)
                elif isinstance(value, (bool, str)):
                    safe_obs[key] = value
                elif hasattr(value, "item"):
                    try:
                        val = value.item()
                        if isinstance(val, (int, float)) and not isinstance(val, bool):
                            safe_obs[key] = round(val, 3)
                        else:
                            safe_obs[key] = val
                    except (ValueError, TypeError):
                        pass
        return safe_obs

    def send_base(self, vx: float, vy: float, wz: float):
        if not self._connected:
            return
        
        # LeKiwi 要求 theta.vel 的单位是度/秒 (deg/s)。
        # 如果你的 LLM Agent 发送的是 rad/s，需要在这里转换 wz = wz * (180 / np.pi)
        action = {
            "x.vel": vx,          # m/s
            "y.vel": vy,          # m/s
            "theta.vel": wz       # deg/s 
        }
        self.robot.send_action(action)

    def send_head(self, head_motor_1: float, head_motor_2: float):
        if not self._connected:
            return
        action = {
            "head_motor_1.pos": head_motor_1,
            "head_motor_2.pos": head_motor_2,
        }
        if hasattr(self, 'robot'):
            self.robot.send_action(action)


    def reset_arm(self):
        if not self._connected:
            return
        reset_action = {
            "arm_shoulder_pan.pos": 0.0,
            "arm_shoulder_lift.pos": 0.0,
            "arm_elbow_flex.pos": 0.0,
            "arm_wrist_flex.pos": 0.0,
            "arm_wrist_roll.pos": 0.0,
            "arm_gripper.pos": 100.0,
        }
        if hasattr(self, 'robot'):
            self.robot.send_action(reset_action)

    def stop_base(self):
        if not self._connected:
            return
        # 发送 0 速度
        self.send_base(0.0, 0.0, 0.0)
        # 调用原生刹车
        if hasattr(self, 'robot'):
            self.robot.stop_base()

    def stop_all(self):
        """全局急停：停止底盘，后续可加入停止双臂的逻辑"""
        if not self._connected:
            return

        # 1. 停止底盘
        self.stop_base()