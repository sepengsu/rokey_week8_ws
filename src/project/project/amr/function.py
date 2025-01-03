from geometry_msgs.msg import PoseWithCovarianceStamped, Quaternion, PoseStamped
from nav2_msgs.action import NavigateToPose
from geometry_msgs.msg import Twist

def add_methods_from(source_class):
    """
    source_class의 메서드를 대상 클래스에 추가하는 데코레이터
    """
    def decorator(target_class):
        for attr_name in dir(source_class):
            if callable(getattr(source_class, attr_name)) and not attr_name.startswith("__"):
                # source_class의 메서드를 target_class에 추가
                setattr(target_class, attr_name, getattr(source_class, attr_name))
        return target_class
    return decorator

class InitPoseFunction:
    '''
    초기 위치를 설정하는 클래스
    initialpose 메시지를 발행하여 초기 위치 설정
    '''
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

class GoToGoalFunction:
    '''
    목표 지점으로 이동하는 클래스
    action client를 사용하여 목표 지점으로 이동
    action client: /navigate_to_pose 노드의 action server에 목표 지점을 전송
    self.navi_action_clients = self.create_client(NavigateToPose, 'navigate_to_pose')
    '''
    def send_goal(self, goal_msg):
        # 서버 연결 대기
        self.navi_action_client.wait_for_server()
        # 목표 전송 및 피드백 콜백 설정
        self._send_goal_future = self.navi_action_client.send_goal_async(
            goal_msg,
            feedback_callback=self.feedback_callback)
        self._send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().info('Goal rejected :(')
            return

        self.get_logger().info('Goal accepted :)')
        self._get_result_future = goal_handle.get_result_async()
        self._get_result_future.add_done_callback(self.get_result_callback)

    def feedback_callback(self, feedback_msg):
        feedback = feedback_msg.feedback
        self.get_logger().info(f'Feedback received: {feedback}') # 피드백 출력

    def cancel_goal(self):
        if self._goal_handle is not None:
            self.get_logger().info('수배차량을 찾았습니다. 목표를 취소합니다.')
            cancel_future = self._goal_handle.cancel_goal_async() # 목표 취소
            cancel_future.add_done_callback(self.cancel_done_callback) # 취소 결과 콜백
        else:
            self.get_logger().info('No active goal to cancel.')

    def cancel_done_callback(self, future):
        cancel_response = future.result()
        if len(cancel_response.goals_cancelled) > 0: # 목표 취소 성공
            self.get_logger().info('Goal successfully cancelled.')
        else:
            self.get_logger().info('Goal cancellation failed or no active goal to cancel.')

    def get_result_callback(self, future):
        result = future.result().result # 도착 결과
        if result.arrived:
            # 목표에 도착했지만 수배차량을 찾지 못한 경우
            self.get_logger().info('목표에 도착했으나 수배차량을 찾지 못했습니다.')
            self.not_found() # 수배차량을 찾지 못한 경우


@add_methods_from(InitPoseFunction) # InitPoseFunction의 메서드를 CommandFunction에 추가
@add_methods_from(GoToGoalFunction) # GoToGoalFunction의 메서드를 CommandFunction에 추가
class CommandFunction:
    '''
    msg.data에 따라 명령을 수행하는 클래스
    '''

    def cmd_callback(self, msg):
        '''
        /control/commands 메시지 콜백
        '''
        cmd = msg.data
        if cmd == 'Standby':
            self.cmd_standby()
        elif cmd == 'Start':
            self.cmd_start()
        elif cmd == 'Emergency stop':
            self.cmd_emergency_stop()
        elif cmd == 'Found':
            self.cmd_found()
        elif cmd.startswith('Velocity'):
            self.cmd_vel(cmd)
        else:
            print('Invalid command')
            
    def cmd_standby(self):
        '''
        Standby 명령 수행
        '''
        print('Standby')
        return 0, 0
    
    def cmd_start(self):
        '''
        Start 명령 수행
        1. 목표 지점 설정
        2. 목표 지점으로 이동 (send_goal)
        '''
        print('Start')
        goal_pose = NavigateToPose.Goal() # 목표 지점 설정
        position = [1,1,0]
        orientation = [0,0,0,1]
        goal_pose.pose.pose.position.x = position[0]
        goal_pose.pose.pose.position.y = position[1]
        goal_pose.pose.pose.position.z = position[2]
        goal_pose.pose.pose.orientation.x = orientation[0]
        goal_pose.pose.pose.orientation.y = orientation[1]
        goal_pose.pose.pose.orientation.z = orientation[2]
        goal_pose.pose.pose.orientation.w = orientation[3]
        goal_pose.pose.header.frame_id = 'map'
        self.send_goal(goal_pose) # 목표 지점으로 이동

    def cmd_emergency_stop(self):
        '''
        Stop 명령 수행 (수배차량을 찾지 못하고 급하게 정지)
        1. 이동 중인 목표 지점 취소 (cancel_goal)
        2. 로봇 정지
        '''
        print('Emergency stop')
        self.cancel_goal()

    def cmd_found(self):
        '''
        수배차량을 찾은 경우 수행
        1. 이동 중인 목표 지점 취소 (cancel_goal)
        2. 로봇 정지
        3. 수배차량을 찾았다는 메시지 출력
        4. tracking 시작
        '''
        print('Found')
        self.cancel_goal()

    def cmd_vel(self, msg):
        '''
        로봇 속도 제어
        [x, y, z] 속도와 w 각속도를 받아 로봇 제어
        for example, msg.data = [0.1, 0, 0, 0]
        '''
        print('Velocity')
        data = eval(msg.data)
        if len(data) != 4:
            print('Invalid data')
            return
        x, y, z, w = data # x, y, z, w

        # 로봇 제어 코드
        twist = Twist()
        twist.linear.x = x
        twist.linear.y = y
        twist.linear.z = z
        twist.angular.x = 0
        twist.angular.y = 0
        twist.angular.z = w
        self.cmd_vel_pub.publish(twist)





        



        
