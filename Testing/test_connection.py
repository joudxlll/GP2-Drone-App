from djitellopy import Tello

tello = Tello()
try:
    tello.connect()
except Exception as e:
    print(f"Connection error: {e}")

tello.takeoff()

# Move to the left
tello.move_left(20)
tello.send_control_command("left 20")  # Alternatively, you can use the send_control_command method

# Rotate clockwise
tello.rotate_clockwise(90)
tello.send_control_command("cw 90")  # Alternatively, you can use the send_control_command method

# Move forward
tello.move_forward(20)
tello.send_control_command("forward 20")  # Alternatively, you can use the send_control_command method

tello.land()
