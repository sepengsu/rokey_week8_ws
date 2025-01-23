#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import sys
import termios
import tty

# 키보드 명령 매핑
MOVE_BINDINGS = {
    'w': (1, 0),   # 앞으로 이동
    's': (-1, 0),  # 뒤로 이동
    'a': (0, 1),   # 좌회전
    'd': (0, -1),  # 우회전
    'q': (0, 0)    # 정지
}

class KeyboardController(Node):
    def __init__(self):
        super().__init__('keyboard_controller')
        self.publisher_ = self.create_publisher(Twist, 'cmd_vel', 10)
        self.linear_speed = 0.5   # 선속도
        self.angular_speed = 1.0  # 각속도
        self.get_logger().info("Keyboard controller is ready. Use 'w', 's', 'a', 'd' to control, 'q' to stop.")
        self.run()

    def get_key(self):
        # 키보드 입력 읽기
        tty.setraw(sys.stdin.fileno())
        key = sys.stdin.read(1)
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, termios.tcgetattr(sys.stdin))
        return key

    def run(self):
        try:
            while True:
                key = self.get_key()
                if key in MOVE_BINDINGS:
                    linear, angular = MOVE_BINDINGS[key]
                    twist = Twist()
                    twist.linear.x = linear * self.linear_speed
                    twist.angular.z = angular * self.angular_speed
                    self.publisher_.publish(twist)
                    self.get_logger().info(f"Published linear: {twist.linear.x}, angular: {twist.angular.z}")
                elif key == '\x03':  # Ctrl+C
                    break
        except Exception as e:
            self.get_logger().error(f"Exception: {e}")
        finally:
            twist = Twist()
            self.publisher_.publish(twist)
            self.get_logger().info("Node stopped. Robot stopped.")

def main(args=None):
    rclpy.init(args=args)
    node = KeyboardController()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Keyboard interrupt detected. Shutting down...")
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
