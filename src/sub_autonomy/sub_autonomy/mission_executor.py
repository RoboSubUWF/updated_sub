import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import time

class MissionExecutor(Node):
    def __init__(self):
        super().__init__('mission_executor')
        self.publisher = self.create_publisher(String, 'sub_commands', 10)
        self.subscription = self.create_subscription(String, 'sub_status', self.status_callback, 10)
        self.ready = False

        self.get_logger().info("Waiting for sub to be ready...")

    def status_callback(self, msg):
        """Wait for confirmation that the sub is ready before starting the mission."""
        if msg.data == "ready":
            self.get_logger().info("Sub is ready. Starting mission...")
            self.ready = True
            self.execute_mission()

    def execute_mission(self):
        if not self.ready:
            return  # Do nothing if not ready

        command = String()

        # Step 1: Move forward
        command.data = "move_forward"
        self.publisher.publish(command)
        self.get_logger().info("Commanding forward movement...")
        time.sleep(3)

        # Step 2: Turn left
        command.data = "turn_left"
        self.publisher.publish(command)
        self.get_logger().info("Commanding left turn...")
        time.sleep(3)

        # Step 3: Stop
        command.data = "stop"
        self.publisher.publish(command)
        self.get_logger().info("Commanding stop...")
        time.sleep(2)

        self.get_logger().info("Mission complete. Shutting down.")
        rclpy.shutdown()

def main(args=None):
    rclpy.init(args=args)
    node = MissionExecutor()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
