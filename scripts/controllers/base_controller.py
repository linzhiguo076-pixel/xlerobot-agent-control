import time
import logging
import threading


class BaseController:
    def __init__(self, adapter, control_hz: int = 10):
        self.adapter = adapter
        self.control_hz = control_hz
        self.cancel_event = threading.Event()

    def move(self, direction: str, duration: float, speed: float) -> dict:
        self.cancel_event.clear()
        duration = min(duration, 10.0)

        vx = vy = wz = 0.0
        if direction == "forward":
            vx = speed
        elif direction == "backward":
            vx = -speed
        elif direction == "left":
            vy = speed
        elif direction == "right":
            vy = -speed
        elif direction == "rotate_left":
            wz = speed
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
            logging.exception("move_base failed")
            raise RuntimeError(f"move_base failed: {e}") from e

        finally:
            # 无论成功、失败还是中断，都确保底盘停下
            try:
                self.stop()
            except Exception:
                logging.exception("failed to stop base in finally")

        return {
            "executed": "move_base",
            "direction": direction,
            "duration": duration,
            "speed": speed,
            "interrupted": interrupted,
            "status": "interrupted" if interrupted else "completed",
        }

    def stop(self) -> dict:
        self.cancel_event.set()
        self.adapter.stop_base()
        return {"executed": "stop_base", "status": "completed"}