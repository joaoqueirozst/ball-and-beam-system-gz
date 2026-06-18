#!/usr/bin/env python3
import rclpy
import threading
import sys
import select
import termios
import tty
import time
from datetime import datetime

from stable_baselines3 import PPO
from ball_beam_rl.gym_env import BallBeamEnv

stop_flag = False
reset_flag = False

def keyboard_listener():
    global stop_flag, reset_flag

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)

    try:
        tty.setcbreak(fd)

        while not stop_flag:
            if select.select([sys.stdin], [], [], 0.1)[0]:
                key = sys.stdin.read(1).lower()

                if key == 'q':
                    print("\n[INFO] Encerrando execução...")
                    stop_flag = True

                elif key == 'r':
                    print("\n[INFO] Reset manual.")
                    reset_flag = True

    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

def main():

    global stop_flag, reset_flag

    rclpy.init()

    env = BallBeamEnv()
    model = PPO.load("ppo_ball_beam")

    threading.Thread(target=keyboard_listener, daemon=True).start()

    episode = 0
    obs, _ = env.reset()
    episode_start_time = time.time()

    print("[INFO] Sistema iniciado.")

    while not stop_flag and rclpy.ok():

        action, _ = model.predict(obs, deterministic=True)
        obs, reward, done, _, info = env.step(action)

        # RESET MANUAL
        if reset_flag:
            obs, _ = env.reset()
            episode += 1
            episode_start_time = time.time()

            print(f"\n[MANUAL RESET] Episódio {episode} iniciado em {datetime.now().strftime('%H:%M:%S')}\n")

            reset_flag = False
            continue

        # RESET AUTOMÁTICO DO AMBIENTE
        if done:
            duration = time.time() - episode_start_time
            episode += 1

            print(f"[EPISÓDIO FINALIZADO]")
            print(f"Episode: {episode}")
            print(f"Duração: {duration:.2f} segundos")
            print(f"Reward final: {reward:.3f}")
            print(f"Hora: {datetime.now().strftime('%H:%M:%S')}")

            obs, _ = env.reset()
            episode_start_time = time.time()

        time.sleep(0.02)

    env.close()
    rclpy.shutdown()
    print("[INFO] Execução encerrada.")

if __name__ == "__main__":
    main()