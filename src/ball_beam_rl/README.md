# Architecture

The file layout for this project is below.

```bash
src/
├── ball_beam_rl/
│   ├── ball_beam_rl/
│   │   ├── __init__.py
│   │   ├── ball_state_node.py
│   │   ├── gym_env.py
│   │   ├── simulation.py
│   │   └── train.py
│   │
│   ├── config/
│   │   └── controllers.yaml
│   │
│   └── launch/
│   │    └── ball_beam_launch.py
│   │
│   └── resource/
│   │    └── ball_beam_rl
│   │
│   └── urdf/
│   │   ├── ball.urdf
│   │   └── ball_beam.xacro
│   │
│   └── worlds/
│   │    └── empty.world
│   │
│   ├── package.xml
│   ├── setup.cfg
│   └── setup.py
│
├── ppo_ball_beam.zip
└── README.md
```

# Simulation

To run the simulation environment, simply run the commands in the terminals below.

In the **terminal 1**:

```bash
cd ~/{'your folder'}
colcon build --packages-select ball_beam_rl
source install/setup.bash
ros2 launch ball_beam_rl ball_beam.launch.py
```

In **terminal 2**, to manually start the node::

```bash
ros2 run ball_beam_rl ball_state_node
```

On **terminal 3**, listen for the position and velocity values ​​of the ball and the angle and velocity of the bar:

```bash
ros2 topic echo /ball_state
```

Finally, in **terminal 4**, to test with the trained control algorithm, run:

```bash
ros2 run ball_beam_rl simulation
```
