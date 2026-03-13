# Action schema

All requests use this envelope:

```json
{
  "action_type": "...",
  "parameters": { ... }
}
```

## move_base

```json
{
  "action_type": "move_base",
  "parameters": {
    "direction": "forward",
    "duration": 1.0,
    "speed": 0.15
  }
}
```

Allowed directions:
- `forward`
- `backward`
- `left`
- `right`
- `rotate_left`
- `rotate_right`

## stop_base

```json
{
  "action_type": "stop_base",
  "parameters": {}
}
```

## set_head

```json
{
  "action_type": "set_head",
  "parameters": {
    "head_motor_1": 10,
    "head_motor_2": -5
  }
}
```

## reset_head

```json
{
  "action_type": "reset_head",
  "parameters": {}
}
```

## reset_arm

```json
{
  "action_type": "reset_arm",
  "parameters": {}
}
```

## get_robot_state

```json
{
  "action_type": "get_robot_state",
  "parameters": {}
}
```

## stop_all

```json
{
  "action_type": "stop_all",
  "parameters": {}
}
```

## clear_estop

```json
{
  "action_type": "clear_estop",
  "parameters": {}
}