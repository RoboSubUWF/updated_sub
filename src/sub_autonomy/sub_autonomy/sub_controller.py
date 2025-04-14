import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import time
from pymavlink import mavutil

class SubController(Node):
    def __init__(self):
        super().__init__('sub_controller')
        self.publisher = self.create_publisher(String, 'sub_status', 10)

        self.get_logger().info("Connecting to Pixhawk...")
        self.master = mavutil.mavlink_connection('/dev/ttyTHS1', baud=115200)

        # Wait for connection
        self.master.wait_heartbeat()
        self.get_logger().info("Heartbeat received. Connected to Pixhawk.")

        # Ensure running ArduSub firmware
        if not self.check_ardusub():
            self.get_logger().error("Not running ArduSub! Exiting.")
            return

        # Set mode to GUIDED_NOGPS
        if not self.set_mode('GUIDED_NOGPS'):
            self.get_logger().error("Failed to set GUIDED_NOGPS mode. Exiting.")
            return

        # Arm the vehicle
        if not self.arm():
            self.get_logger().error("Failed to arm thrusters. Exiting.")
            return

        # Publish ready status
        ready_msg = String()
        ready_msg.data = "ready"
        self.publisher.publish(ready_msg)
        self.get_logger().info("Pixhawk is ready. Waiting for mission commands...")

        # Subscribe to mission commands
        self.subscription = self.create_subscription(
            String,
            'sub_commands',
            self.command_callback,
            10)

    def check_ardusub(self):
        """Verify the vehicle is running ArduSub firmware."""
        msg = self.master.recv_match(type='HEARTBEAT', blocking=True, timeout=2)
        return msg and msg.autopilot == mavutil.mavlink.MAV_AUTOPILOT_ARDUPILOTMEGA

    def set_mode(self, mode):
        """Set the vehicle mode."""
        self.get_logger().info(f"Setting mode to {mode}...")
        mode_id = self.master.mode_mapping().get(mode)
        if mode_id is None:
            self.get_logger().error(f"Mode {mode} not available.")
            return False

        self.master.mav.set_mode_send(
            self.master.target_system,
            mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
            mode_id
        )
        time.sleep(2)

        for _ in range(5):
            msg = self.master.recv_match(type='HEARTBEAT', blocking=True, timeout=1)
            if msg and msg.custom_mode == mode_id:
                self.get_logger().info(f"Successfully set mode to {mode}.")
                return True

        self.get_logger().error(f"Failed to switch to {mode} mode.")
        return False

    def arm(self):
        """Arm the vehicle and verify."""
        self.get_logger().info("Arming thrusters...")
        self.master.mav.param_set_send(
            self.master.target_system,
            self.master.target_component,
            b'ARMING_CHECK',
            0,
            mavutil.mavlink.MAV_PARAM_TYPE_REAL32
        )
        time.sleep(2)

    # Send arm command
        self.master.mav.command_long_send(
            self.master.target_system,
            self.master.target_component,
            mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
            0,
            1,  # 1 = arm
            0, 0, 0, 0, 0, 0
        )
        time.sleep(2)
        
        for _ in range(5):
            msg = self.master.recv_match(type='HEARTBEAT', blocking=True, timeout=1)
            if msg and (msg.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED):
                self.get_logger().info("Thrusters armed successfully.")
                return True

        self.get_logger().error("Failed to arm thrusters.")
        return False

    def command_callback(self, msg):
        """Handle movement commands from mission_executor."""
        command = msg.data
        self.get_logger().info(f"Received command: {command}")

        if command == "move_forward":
            self.move_forward(2)
        elif command == "turn_left":
            self.turn_left()
        elif command == "stop":
            self.stop()
        else:
            self.get_logger().warn(f"Unknown command: {command}")

    def move_forward(self, distance):
        """Move forward using thrust control in GUIDED_NOGPS mode."""
        self.get_logger().info(f"Moving forward {distance} feet...")
        velocity = 0.3
        duration = distance / velocity

        self.master.mav.set_attitude_target_send(
            0, self.master.target_system, self.master.target_component,
            0b00000000, [1.0, 0.0, 0.0, 0.0], 0, -0.3, 0, 0.6
        )
        time.sleep(duration)
        self.stop()

    def turn_left(self):
        """Turn left using yaw control in GUIDED_NOGPS mode."""
        self.get_logger().info("Turning left...")

        self.master.mav.set_attitude_target_send(
            0, self.master.target_system, self.master.target_component,
            0b00000000, [1.0, 0.0, 0.0, 0.0], 0, 0, 0.5, 0.5
        )
        time.sleep(2)
        self.stop()

    def stop(self):
        """Stop all movement."""
        self.get_logger().info("Stopping movement.")

        self.master.mav.set_attitude_target_send(
            0, self.master.target_system, self.master.target_component,
            0b00000000, [1.0, 0.0, 0.0, 0.0], 0, 0, 0, 0.5
        )
        time.sleep(0.5)

def main(args=None):
    rclpy.init(args=args)
    node = SubController()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
