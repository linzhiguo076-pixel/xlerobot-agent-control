#!/usr/bin/env python3
import json
import os
import urllib.request
<<<<<<< HEAD
import urllib.error
=======
>>>>>>> dd16e05aaf40379b75f9d0087fe621b1add582f9

DEFAULT_URL = os.environ.get("XLEROBOT_SERVER_URL", "http://127.0.0.1:8765/action")


def send_request(payload: dict) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        DEFAULT_URL,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
<<<<<<< HEAD
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as e:
        raise RuntimeError(
            f"failed to reach robot server at {DEFAULT_URL}. "
            f"make sure scripts/robot_server.py is running. original error: {e}"
        ) from e
=======
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode("utf-8"))
>>>>>>> dd16e05aaf40379b75f9d0087fe621b1add582f9
