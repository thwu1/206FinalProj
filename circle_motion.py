import time
from djitellopy import Tello
import numpy as np

def circle_motion(drone, radius, speed, duration):
    """
    Perform a circular motion with the Tello drone.
    Args:
        drone (Tello): The Tello drone instance.
        radius (int): Radius of the circle in cm.
        speed (int): Linear speed in cm/s.q
        duration (int): Duration of the circular motion in seconds.
    """
    try:
        # Calculate yaw speed based on the desired radius and speed
        angular_velocity = speed / radius  # rad/s
        yaw_speed = int(np.degrees(angular_velocity))  # Convert rad/s to deg/s

        print(f"[DEBUG] Starting circle motion with parameters:")
        print(f"        - Radius: {radius} cm")
        print(f"        - Speed: {speed} cm/s")
        print(f"        - Duration: {duration} seconds")
        print(f"        - Calculated Yaw Speed: {yaw_speed} deg/s")

        # Track start time
        start_time = time.time()

        # Loop for the duration of the motion
        while time.time() - start_time < duration:
            # Send RC control commands: Move forward and yaw
            print("[DEBUG] Sending control command: rc 0 {} 0 {}".format(speed, yaw_speed))
            drone.send_rc_control(0, speed, 0, yaw_speed)

            # Add debug info for current loop time
            elapsed_time = time.time() - start_time
            print(f"[DEBUG] Elapsed Time: {elapsed_time:.2f} seconds")

            time.sleep(0.05)  # Maintain smooth control by sending commands frequently

        # Stop the motion after the duration
        print("[DEBUG] Stopping motion...")
        drone.send_rc_control(0, 0, 0, 0)
        print("Circle motion completed.")
    except Exception as e:
        print(f"[ERROR] An error occurred in circle_motion: {e}")
        drone.send_rc_control(0, 0, 0, 0)

if __name__ == "__main__":
    me = Tello()

    try:
        # Connect to the drone
        print("[DEBUG] Connecting to drone...")
        me.connect()
        print(f"[DEBUG] Battery level: {me.get_battery()}%")

        # Start video streaming
        print("[DEBUG] Starting video stream...")
        me.streamon()

        # Take off
        print("[DEBUG] Taking off...")
        me.takeoff()
        me.move_up(50)  # Optional: Move up for better clearance

        # Perform circular motion
        print("[DEBUG] Executing circular motion...")
        circle_motion(me, radius=200, speed=35, duration=10)

        # Land the droneq
        print("[DEBUG] Landing...")
        me.land()

    except Exception as e:
        print(f"[ERROR] An error occurred in main: {e}")

    finally:
        # Ensure stream is stopped in case of an error
        print("[DEBUG] Stopping video stream...")
        try:
            me.streamoff()
        except Exception as e:
            print(f"[ERROR] An error occurred while stopping stream: {e}")
