---
name: xlerobot-agent-control
description: unified control skill for xlerobot on jetson. use when chatgpt needs to control the robot body through natural language or structured actions, including base motion, head motion, arm reset, robot state queries, and global stop. especially useful when the robot base, arms, and head share one hardware connection and require centralized arbitration, shared observations, and safe execution.
---

# Overview

Use this skill to control xlerobot as one embodied system. The robot runs on a jetson device, and a single local robot server owns the hardware connection. This avoids serial-port conflicts and makes it possible to share observations and safety checks across base, arms, and head.

This skill uses one structured request shape:

```json
{
  "action_type": "...",
  "parameters": { ... }
}
```

Always convert user intent into exactly one supported action request unless an emergency stop is needed.

# Supported actions

Use one of these `action_type` values:

- `move_base`
- `stop_base`
- `set_head`
- `reset_head`
- `reset_arm`
- `get_robot_state`
- `stop_all`
- `clear_estop`

# Action schemas

## move_base

Parameters:
- `direction`: one of `forward`, `backward`, `left`, `right`, `rotate_left`, `rotate_right`
- `duration`: float seconds, must be between `0.1` and `3.0`
- `speed`: optional float. keep conservative. do not exceed configured safe limits.

Use for short, deliberate motions. Prefer the smallest valid duration and speed that satisfies the user request.

## stop_base

Parameters: `{}`

Use when the user asks to stop only the base.

## set_head

Parameters:
- `head_motor_1`: target angle in degrees
- `head_motor_2`: target angle in degrees

Use for camera or head orientation changes.

## reset_head

Parameters: `{}`

Use to return the head to its neutral position.

## reset_arm

Parameters: `{}`

Use to move the currently supported arm back to its neutral pose.

## get_robot_state

Parameters: `{}`

Use when the user asks about the robot’s current state, current pose, whether a body part has moved, or before planning a careful next motion.

## stop_all

Parameters: `{}`

Use immediately for emergency stop requests. In this version, it prioritizes cancelling ongoing base motion and forcing the base to stop through the centralized server.


## clear_estop

Parameters: `{}`
Use after a deliberate emergency stop when it is safe to resume motion.

# Execution rules

- Always use the local robot server. Do not open the hardware connection directly from per-call scripts.
- Never invent unsupported `action_type` values.
- Never emit raw low-level motor commands.
- Reject requests that exceed configured limits.
- Prefer one safe body action at a time.
- For ambiguous movement requests, choose conservative defaults.
- For emergency language such as “stop now”, “freeze”, “halt”, or possible collision risk, use `stop_all`.
- If the user asks what the robot is doing or where a body part is, use `get_robot_state`.
- After `stop_all`, do not resume motion until `clear_estop` is used explicitly.

# Execution

Run the entrypoint script with one JSON payload:

```bash
python scripts/execute_action.py '{"action_type":"get_robot_state","parameters":{}}'
```

The script validates the payload, routes the action, asks the local server to execute it, and returns structured JSON.

# Files to consult

- `references/action_schema.md`: detailed payload shapes and examples
- `references/safety_rules.md`: safety rules and conservative defaults
- `references/hardware_notes.md`: why a single server owns the hardware connection
- `references/teleop_mapping.md`: how the old keyboard mapping maps into the new action model
