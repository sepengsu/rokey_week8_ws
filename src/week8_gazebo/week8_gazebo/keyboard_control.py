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

INSTRUCTIONS = """
======================================
Keyboard Control Instructions:
--------------------------------------
'w' : Move forward
's' : Move backward
'a' : Turn left
'd' : Turn right
'q' : Stop
CTRL+C : Exit the program
======================================
"""

class KeyboardController(Node):
    def __init__(self):
        super().__init__('keyboard_controller')
        self.publisher_ = self.create_publisher(Twist, 'rc_car/cmd_vel', 10)
        self.linear_speed = 0.5   # 선속도
        self.angular_speed = 1.0  # 각속도

        # 안내문 출력
        self.get_logger().info(INSTRUCTIONS)

    def get_key(self):
        """키보드 입력 읽기"""
        try:
            tty.setraw(sys.stdin.fileno())
            key = sys.stdin.read(1)
        except Exception as e:
            self.get_logger().error(f"Error reading key: {e}")
            key = ''
        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, termios.tcgetattr(sys.stdin))
        return key

    def run(self):
        """키보드 입력에 따라 로봇 제어"""
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
                    raise KeyboardInterrupt  # Ctrl+C를 인식해 종료
        except KeyboardInterrupt:
            self.get_logger().info("Keyboard interrupt detected. Shutting down...")
        except Exception as e:
            self.get_logger().error(f"Unexpected exception: {e}")
        finally:
            twist = Twist()  # 로봇을 멈추기 위해 정지 메시지 발행
            self.publisher_.publish(twist)
            self.get_logger().info("Node stopped. Robot stopped.")

def main(args=None):
    rclpy.init(args=args)
    node = KeyboardController()

    try:
        node.run()
    except KeyboardInterrupt:
        node.get_logger().info("Keyboard interrupt detected in main. Exiting...")
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
