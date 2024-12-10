import time
from djitellopy import Tello
import numpy as np

def circle_motion(drone, radius, speed, duration):
    """
    Perform a circular motion with the Tello drone.
    Args:
        drone (Tello): The Tello drone instance.
        radius (int): Radius of the circle in cm.
        speed (int): Linear speed in cm/s.
        duration (int): Duration of the circular motion in seconds.
    """
    # Calculate yaw speed based on the desired radius and speed
    angular_velocity = speed / radius  # rad/s
    yaw_speed = int(np.degrees(angular_velocity))  # Convert rad/s to deg/s

    print(f"Starting circle motion with radius={radius} cm, speed={speed} cm/s, yaw_speed={yaw_speed} deg/s")

    # Track start time
    start_time = time.time()

    # Loop for the duration of the motion
    while time.time() - start_time < duration:
        # Send RC control commands: Move forward and yaw
        drone.send_rc_control(0, speed, 0, yaw_speed)
        time.sleep(0.05)  # Maintain smooth control by sending commands frequently

    # Stop the motion after the duration
    drone.send_rc_control(0, 0, 0, 0)
    print("Circle motion completed.")

if __name__ == "__main__":
    me = Tello()

    try:
        # Connect to the drone
        me.connect()
        print(f"Battery level: {me.get_battery()}%")

        # Start video streaming
        me.streamon()

        # Take off
        print("Taking off...")
        me.takeoff()
        me.move_up(50)  # Optional: Move up for better clearance

        # Perform circular motion
        print("Executing circular motion...")
        circle_motion(me, radius=100, speed=20, duration=10)

        # Land the drone
        print("Landing...")
        me.land()

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Ensure stream is stopped in case of an error
        try:
            me.streamoff()
        except:
            pass