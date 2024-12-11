import time
from djitellopy import Tello
import cv2  # Using cv2 for key press handling

def circle_motion(drone, speed, yaw_speed, duration):
    """
    Perform a circular motion with the Tello drone.

    Args:
        drone (Tello): The Tello drone instance.
        speed (int): Linear speed in cm/s.
        yaw_speed (int): Yaw rotation speed in degrees per second.
        duration (int): Duration of the motion in seconds.
    """
    print(f"Starting circular motion with speed={speed} cm/s, yaw_speed={yaw_speed} deg/s, and duration={duration} seconds")

    start_time = time.time()

    try:
        while time.time() - start_time < duration:
            # Check if "q" is pressed to stop
            if cv2.waitKey(1) & 0xFF == ord("q"):
                print("[DEBUG] 'q' pressed, stopping and landing...")
                break

            # Send RC control commands: move forward and yaw
            drone.send_rc_control(speed, 0, 0, yaw_speed)
            time.sleep(0.05)  # Maintain smooth control by sending commands frequently

    except Exception as e:
        print(f"[ERROR] An error occurred during circular motion: {e}")

    finally:
        # Stop the motion
        print("[DEBUG] Stopping drone...")
        drone.send_rc_control(0, 0, 0, 0)

if __name__ == "__main__":
    drone = Tello()

    try:
        # Connect to the drone
        print("[DEBUG] Connecting to drone...")
        drone.connect()
        print(f"[DEBUG] Battery level: {drone.get_battery()}%")

        # Start video streaming
        print("[DEBUG] Starting video stream...")
        drone.streamon()

        # Take off
        print("[DEBUG] Taking off...")
        drone.takeoff()
        drone.move_up(50)  # Optional: Move up for better clearance

        # Perform circular motion
        print("[DEBUG] Executing circular motion. Press 'q' to stop and land.")
        circle_motion(drone, speed=30, yaw_speed=30, duration=24)  # Adjust speed, yaw speed, and duration as needed

    except Exception as e:
        print(f"[ERROR] An error occurred: {e}")

    finally:
        # Land the drone
        print("[DEBUG] Landing...")
        try:
            drone.land()
        except Exception as e:
            print(f"[ERROR] An error occurred while landing: {e}")

        # Stop video stream
        print("[DEBUG] Stopping video stream...")
        try:
            drone.streamoff()
        except Exception as e:
            print(f"[ERROR] An error occurred while stopping stream: {e}")
