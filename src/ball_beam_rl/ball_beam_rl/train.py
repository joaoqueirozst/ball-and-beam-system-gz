#!/usr/bin/env python3
import rclpy
import matplotlib.pyplot as plt

from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import BaseCallback
from ball_beam_rl.gym_env import BallBeamEnv

class RewardCallback(BaseCallback):

    def __init__(self):
        super().__init__()

        self.episode_rewards = []
        self.current_reward = 0.0

    def _on_step(self):

        reward = self.locals["rewards"][0]
        self.current_reward += reward
        done = (self.locals["dones"][0])

        if done:
            self.episode_rewards.append(self.current_reward)

            print(
                f"Episode {len(self.episode_rewards)} "
                f"Reward = {self.current_reward:.2f}"
            )

            self.current_reward = 0.0

        return True

def main():

    rclpy.init()

    env = BallBeamEnv()
    callback = RewardCallback()

    model = PPO(
        policy="MlpPolicy",
        env=env,
        verbose=1,
        learning_rate=3e-4,
        n_steps=2048,
        batch_size=64,
        gamma=0.99,
    )

    model.learn(total_timesteps=400_000, callback=callback)

    model.save("ppo_ball_beam")

    plt.figure(figsize=(10,5))
    plt.plot(callback.episode_rewards)
    plt.xlabel("Episode")
    plt.ylabel("Reward")

    plt.title("Treinamento PPO Ball Beam")
    plt.grid(True)
    plt.savefig("training_rewards.png",dpi=300)

    plt.show()

    env.close()
    rclpy.shutdown()

if __name__ == "__main__":
    main()