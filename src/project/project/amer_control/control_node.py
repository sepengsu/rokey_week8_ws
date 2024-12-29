import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class ControlNode(Node):

    def __init__(self):
        super().__init__('control_node')
        self.get_logger().info('Control node started')
        self.init_subscribers()

    def init_subscribers(self):
        """Initialize subscribers"""
        self.create_subscription(
            String,
            '/control/commands',
            self.commands_callback,
            5
        )

    def commands_callback(self, msg):
        """Callback for control commands"""
        self.get_logger().info(f'Received command: {msg.data}')