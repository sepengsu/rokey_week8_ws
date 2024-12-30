from geometry_msgs.msg import PoseWithCovarianceStamped, Quaternion, PoseStamped

class CommandFunction:
    '''
    msg.data에 따라 명령을 수행하는 클래스
    '''
    def cmd_standby(self):
        '''
        Standby 명령 수행
        '''
        print('Standby')
        return 0, 0
    
    def cmd_start(self):
        '''
        Start 명령 수행
        '''
        print('Start')
        goal_pose = PoseWithCovarianceStamped()
        position = [1,1,0]
        orientation = [0,0,0,1]
        goal_pose.pose.pose.position.x = position[0]
        goal_pose.pose.pose.position.y = position[1]
        goal_pose.pose.pose.position.z = position[2]
        goal_pose.pose.pose.orientation = Quaternion(
            x=orientation[0], y=orientation[1], z=orientation[2], w=orientation[3]
        )

    def cmd_stop(self):
        '''
        Stop 명령 수행
        '''

class GoToGoalFunction:
    '''
    목표 지점으로 이동하는 클래스
    '''
    def send_goal(self):
        # 세 개의 웨이포인트 정의
        waypoints = []

        # 첫 번째 웨이포인트
        waypoint1 = PoseStamped()
        waypoint1.header.stamp.sec = 0
        waypoint1.header.stamp.nanosec = 0
        waypoint1.header.frame_id = "map"  # 프레임 ID를 설정 (예: "map")
        waypoint1.pose.position.x = 0.35624730587005615
        waypoint1.pose.position.y = -0.7531262636184692
        waypoint1.pose.position.z = 0.0

        waypoint1_yaw = 0.0  # Target orientation in radians
        waypoint1.pose.orientation = self.euler_to_quaternion(0, 0, waypoint1_yaw)

        # 서버 연결 대기
        self.action_client.wait_for_server()

        # 목표 전송 및 피드백 콜백 설정
        self._send_goal_future = self.action_client.send_goal_async(
            goal_msg,
            feedback_callback=self.feedback_callback
        )
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
        self.get_logger().info(f'Current Waypoint Index: {feedback.current_waypoint}')

    def cancel_goal(self):
        if self._goal_handle is not None:
            self.get_logger().info('Attempting to cancel the goal...')
            cancel_future = self._goal_handle.cancel_goal_async()
            cancel_future.add_done_callback(self.cancel_done_callback)
        else:
            self.get_logger().info('No active goal to cancel.')

    def cancel_done_callback(self, future):
        cancel_response = future.result()
        if len(cancel_response.goals_cancelled) > 0:
            self.get_logger().info('Goal cancellation accepted. Exiting program...')
            self.destroy_node()
            rclpy.shutdown()
            sys.exit(0)  # Exit the program after successful cancellation
        else:
            self.get_logger().info('Goal cancellation failed or no active goal to cancel.')

    def get_result_callback(self, future):
        result = future.result().result
        missed_waypoints = result.missed_waypoints
        if missed_waypoints:
            self.get_logger().info(f'Missed waypoints: {missed_waypoints}')
        else:
            self.get_logger().info('All waypoints completed successfully!')
