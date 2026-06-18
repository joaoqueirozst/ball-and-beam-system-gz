#!/usr/bin/env python3
import rclpy
import time

from rclpy.node import Node
from std_msgs.msg import Float64MultiArray
from sensor_msgs.msg import JointState
from tf2_msgs.msg import TFMessage

class BallStateNode(Node):

    def __init__(self):
        super().__init__("ball_state_node")

        self.publisher = self.create_publisher(
            Float64MultiArray,
            "/ball_state",
            10
        )

        self.pose_sub = self.create_subscription(
            TFMessage,
            "/world/ball_beam_world/dynamic_pose/info",
            self.pose_callback,
            10
        )

        self.joint_sub = self.create_subscription(
            JointState,
            "/joint_states",
            self.joint_callback,
            10
        )

        self.ball_position = 0.0
        self.ball_velocity = 0.0
        self.beam_angle = 0.0
        self.beam_velocity = 0.0
        self.last_ball_position = None
        self.last_time = time.time()

        self.timer = self.create_timer(0.02, self.publish_state)

        self.get_logger().info("Ball State Node iniciado")

    def pose_callback(self, msg):

        current_time = time.time()
        ball_x = msg.transforms[1].transform.translation.x
        self.ball_position = ball_x

        if self.last_ball_position is not None:

            dt = current_time - self.last_time
            if dt > 0:
                self.ball_velocity = (self.ball_position - self.last_ball_position)/dt

        self.last_ball_position = self.ball_position
        self.last_time = current_time

    def joint_callback(self, msg):

        if "beam_joint" not in msg.name:
            return

        idx = msg.name.index("beam_joint")

        self.beam_angle = msg.position[idx]
        self.beam_velocity = msg.velocity[idx]

    def publish_state(self):

        msg = Float64MultiArray()
        msg.data = [
            float(self.ball_position),
            float(self.ball_velocity),
            float(self.beam_angle),
            float(self.beam_velocity)
        ]

        self.publisher.publish(msg)

def main(args=None):

    rclpy.init(args=args)
    node = BallStateNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()