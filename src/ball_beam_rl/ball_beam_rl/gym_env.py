#!/usr/bin/env python3
import time
import numpy as np
import gymnasium as gym
import rclpy
import subprocess
import os
import random

from rclpy.node import Node
from std_msgs.msg import Float64MultiArray
from gymnasium import spaces

class BallBeamEnv(Node, gym.Env):
    def __init__(self):

        Node.__init__(self, "ball_beam_env")
        gym.Env.__init__(self)

        # Observação:
        #   [ball_pos,
        #   ball_vel,
        #   beam_angle,
        #   beam_vel]

        self.observation_space = spaces.Box(low=np.array([-1.0, -10.0, -0.4, -5.0], dtype=np.float32), high=np.array([1.0, 10.0, 0.4, 5.0], dtype=np.float32), dtype=np.float32)

        # ação = ângulo desejado
        self.action_space = spaces.Box(low=np.array([-0.20], dtype=np.float32), high=np.array([0.20], dtype=np.float32), )
        self.state = np.zeros(4, dtype=np.float32)

        self.subscription = self.create_subscription(
            Float64MultiArray,
            "/ball_state",
            self.ball_state_callback,
            10
        )

        self.publisher = self.create_publisher(
            Float64MultiArray,
            "/beam_position_controller/commands",
            10
        )

        self.max_steps = 500
        self.current_step = 0

        self.get_logger().info("Gym Environment iniciado")

    def ball_state_callback(self, msg):

        print("RECEBIDO:", msg.data)

        self.state = np.array(
            msg.data,
            dtype=np.float32
        )

    def pause_simulation(self):

        subprocess.run(
            [
                "gz", "service",
                "--service", "/world/ball_beam_world/control",
                "--reqtype", "gz.msgs.WorldControl",
                "--reptype", "gz.msgs.Boolean",
                "--timeout", "3000",
                "--req", "pause: true"
            ],
            capture_output=True,
            text=True
        )

    def resume_simulation(self):

        subprocess.run(
            [
                "gz", "service",
                "--service", "/world/ball_beam_world/control",
                "--reqtype", "gz.msgs.WorldControl",
                "--reptype", "gz.msgs.Boolean",
                "--timeout", "3000",
                "--req", "pause: false"
            ],
            capture_output=True,
            text=True
        )

    def reset_ball_position(self):

        x = random.uniform(-0.15, 0.15)

        cmd = f"""
                gz service \
                --service /world/ball_beam_world/set_pose \
                --reqtype gz.msgs.Pose \
                --reptype gz.msgs.Boolean \
                --timeout 3000 \
                --req '
                name: "ball"
                position {{
                x: {x}
                y: 0.0
                z: 0.325
                }}
                '
                """

        os.system(cmd)

        self.get_logger().info(
            f"Bola reposicionada para x={x:.3f}"
        )

    def step(self, action):
        target_angle = float(action[0])

        cmd = Float64MultiArray()
        cmd.data = [target_angle]

        self.publisher.publish(cmd)

        # espera simulador atualizar
        rclpy.spin_once(self, timeout_sec=0.02)

        observation = self.state.copy()
        ball_position = observation[0]

        reward = (
            1.0
            -3.0*abs(ball_position)
            -0.2*abs(observation[1])
            -0.05*abs(target_angle)
        )

        terminated = False

        if abs(ball_position) > 0.45:
            terminated = True
            reward -= 100.0

        self.current_step += 1

        truncated = self.current_step >= self.max_steps

        info = {}

        print(
            f"pos={ball_position:.3f}"
            f"vel={observation[1]:.3f}"
            f"action={target_angle:.3f}"
            f"reward={reward:.3f}"
        )

        return (observation, reward, terminated, truncated, info)

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)

        self.current_step = 0

        # Centraliza a barra
        cmd = Float64MultiArray()
        cmd.data = [0.0]
        self.publisher.publish(cmd)

        # Aguarda a barra estabilizar
        time.sleep(1.0)

        # Reposiciona a bola em posição aleatória
        self.reset_ball_position()

        # Aguarda a física estabilizar
        time.sleep(1.0)

        # Atualiza estado várias vezes
        for _ in range(20):
            rclpy.spin_once(self, timeout_sec=0.05)

        print("RESET STATE =", self.state)

        return self.state.copy(), {}

    def close(self):
        self.destroy_node()