from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
import json
import sys
import threading
import uuid
import time
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from core.robot_orchestrator import RobotOrchestrator
from safety_guard import validate_request

ORCH = RobotOrchestrator()


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/action":
            self.send_error(404)
            return
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length)
        request_id = str(uuid.uuid4())
        started_at = time.time()
        try:
            payload = json.loads(body.decode("utf-8"))
            request = validate_request(payload)
            action_type = request["action_type"]
            params = request["parameters"]

            if action_type == "move_base":
                result = ORCH.move_base(**params)
            elif action_type == "stop_base":
                result = ORCH.stop_base()
            elif action_type == "set_head":
                result = ORCH.set_head(**params)
            elif action_type == "reset_head":
                result = ORCH.reset_head()
            elif action_type == "reset_arm":
                result = ORCH.reset_arm(**params)
            elif action_type == "get_robot_state":
                result = ORCH.get_robot_state()
            elif action_type == "stop_all":
                result = ORCH.stop_all()
            elif action_type == "clear_estop":
                result = ORCH.clear_estop()
            else:
                raise ValueError(f"unsupported action_type: {action_type}")
            finished_at = time.time()
            self._send_json(200, {
                "ok": True,
                "request_id": request_id,
                "started_at": started_at,
                "finished_at": finished_at,
                "duration_sec": round(finished_at - started_at, 3),
                "data": result # 这里面已经包含了 action_result 和 robot_state
            })
        except Exception as exc:
            finished_at = time.time()
            self._send_json(400, {
                "ok": False,
                "request_id": request_id,
                "started_at": started_at,
                "finished_at": finished_at,
                "duration_sec": round(finished_at - started_at, 3),
                "error": str(exc),
            })

    def log_message(self, format, *args):
        return

    def _send_json(self, status: int, payload: dict):
        data = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def main():
    server = ThreadingHTTPServer(("127.0.0.1", 8765), Handler)
    print("XLerobot robot_server listening on http://127.0.0.1:8765/action")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
    finally:
        server.server_close()
        # 核心优化：确保退出时硬件断开连接，释放端口，卸载电机扭矩
        print("Releasing robot hardware...")
        #ORCH.stop_all()
        #ORCH.adapter.disconnect()
        try:
            ORCH.stop_all()
        finally:
            ORCH.adapter.disconnect()
        print("Shutdown complete.")

if __name__ == "__main__":
    main()