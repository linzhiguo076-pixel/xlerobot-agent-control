import time
import logging

class BaseController:
    def __init__(self, adapter, control_hz: int = 10):
        self.adapter = adapter
        self.control_hz = control_hz
        self.cancel_event = threading.Event()

    def move(self, direction: str, duration: float, speed: float) -> dict:
        self.cancel_event.clear()
        duration = min(duration, 10.0) 
        
        vx = vy = wz = 0.0
        # 假设 speed 针对线速度为 m/s，针对角速度为 deg/s
        if direction == "forward":
            vx = speed
        elif direction == "backward":
            vx = -speed
        elif direction == "left":
            vy = speed
        elif direction == "right":
            vy = -speed
        elif direction == "rotate_left":
            wz = speed   # LeKiwi 要求这是度/秒
        elif direction == "rotate_right":
            wz = -speed
        else:
            raise ValueError(f"unsupported direction: {direction}")

        dt = 1.0 / self.control_hz
        end_time = time.time() + duration
        
        interrupted = False
        try:
            while time.time() < end_time and not self.cancel_event.is_set():
                self.adapter.send_base(vx=vx, vy=vy, wz=wz)
                time.sleep(dt)
            if self.cancel_event.is_set():
                interrupted = True
        except Exception as e:
            logging.error(f"Move interrupted: {e}")
        finally:
            # 无论如何，结束时必须发送刹车指令
            self.stop()
            
        return {
            "executed": "move_base",
            "direction": direction,
            "duration": duration,
            "speed": speed,
            "interrupted": interrupted
        }

    def stop(self) -> dict:
        self.cancel_event.set() 
        self.adapter.stop_base() 
        return {"executed": "stop_base"}