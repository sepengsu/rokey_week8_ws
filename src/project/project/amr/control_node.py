import rclpy, sys, os
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import PoseWithCovarianceStamped, Quaternion, PoseStamped
from nav2_msgs.action import NavigateToPose
mother_path = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(mother_path)) # project 디렉토리 추가
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__)))) # project 디렉토리 추가
from project.project.amr.function import add_methods_from, CommandFunction

@add_methods_from(CommandFunction)
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
            String,'/control/commands',
            self.cmd_callback,5)

    def init_publishers(self):
        """Initialize publishers"""
        self.initpose_pub = self.create_publisher(
            PoseWithCovarianceStamped,'/initialpose',5)
        self.cmd_vel_pub = self.create_publisher(
            PoseStamped,'/cmd_vel',5)
    
    def action_clients(self):
        '''
        /navigate_to_pose
        '''
        self.navi_action_clients  = self.create_client(NavigateToPose, '/navigate_to_pose')

def main(args=None):
    rclpy.init(args=args)
    control_node = ControlNode()
    rclpy.spin(control_node)
    control_node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()