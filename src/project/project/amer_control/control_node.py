import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import PoseWithCovarianceStamped, Quaternion

class ControlNode(Node):

    def __init__(self):
        super().__init__('control_node')
        self.get_logger().info('Control node started')
        self.cmd = 'Standby'
        self.init_publishers()
        self.init_subscribers()
        self.publish_initpose()

    def init_subscribers(self):
        """Initialize subscribers"""
        self.create_subscription(
            String,
            '/control/commands',
            self.commands_callback,
            5
        )

    def commands_callback(self, msg):
        self.cmd = msg.data

    def init_publishers(self):
        """Initialize publishers"""
        self.initpose_pub = self.create_publisher(
            PoseWithCovarianceStamped,
            '/initialpose',
            5
        )

    def publish_initpose(self):
        initial_pose = PoseWithCovarianceStamped()
        initial_pose.header.frame_id = 'map'  # The frame in which the pose is defined
        initial_pose.header.stamp = self.get_clock().now().to_msg()
        initial_pose.pose.pose.position.x = 0.1750425100326538 # X-coordinate
        initial_pose.pose.pose.position.y = 0.05808566138148308 # Y-coordinate
        initial_pose.pose.pose.position.z = 0.0  # Z should be 0 for 2D navigation

        # Set the orientation (in quaternion form)
        initial_pose.pose.pose.orientation = Quaternion(
            x=0.0,y=0.0,
            z=-0.04688065682721989,  # 90-degree rotation in yaw (example)
            w=0.9989004975549108  # Corresponding quaternion w component
        )
        initial_pose.pose.covariance = [
            0.25, 0.0, 0.0, 0.0, 0.0, 0.0,
            0.0, 0.25, 0.0, 0.0, 0.0, 0.0,
            0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
            0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
            0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
            0.0, 0.0, 0.0, 0.0, 0.0, 0.06853891909122467
        ]
        self.initpose_pub.publish(initial_pose)

def main(args=None):
    rclpy.init(args=args)
    control_node = ControlNode()
    rclpy.spin(control_node)
    control_node.destroy_node()
    rclpy.shutdown()