import os

from launch import LaunchDescription
from launch.actions import ExecuteProcess, TimerAction, RegisterEventHandler
from launch.event_handlers import OnProcessStart
from launch_ros.actions import Node
from launch.substitutions import Command
from launch_ros.parameter_descriptions import ParameterValue
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():

    pkg_path = get_package_share_directory('ball_beam_rl')

    xacro_file = os.path.join(pkg_path, 'urdf', 'ball_beam.xacro')
    ball_file = os.path.join(pkg_path, 'urdf', 'ball.urdf')
    world_file = os.path.join(pkg_path, 'worlds', 'empty.world')
    config_file = os.path.join(pkg_path, 'config', 'controllers.yaml')

    # 1. Descrição do robô (xacro -> string URDF)
    robot_description = ParameterValue(
        Command(['xacro ', xacro_file]),
        value_type=str
    )

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': robot_description,
                     'use_sim_time': True}],
        output='screen'
    )

    # 2. Gazebo Sim (Harmonic/gz sim)
    gazebo = ExecuteProcess(
        cmd=['gz', 'sim', '-r', world_file],
        output='screen'
    )

    # 3. Bridge ROS 2 <-> Gazebo
    #    Publica /clock e permite controle da junta via ros2_control
    ros_gz_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
            '/world/ball_beam_world/dynamic_pose/info@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V',
        ],
        parameters=[{'use_sim_time': True}],
        output='screen'
    )

    # 4. Spawn da barra (ball_beam): aguarda 3s para o Gazebo subir
    spawn_beam = TimerAction(
        period=3.0,
        actions=[
            Node(
                package='ros_gz_sim',
                executable='create',
                arguments=[
                    '-topic', 'robot_description',
                    '-name',  'ball_beam',
                    '-x', '0.0',
                    '-y', '0.0',
                    '-z', '0.0',
                ],
                output='screen'
            )
        ]
    )

    # 5. Spawn da bola: aguarda mais 2s (após beam estar no mundo)
    #    z = 0.32 = suporte(0.25) + eixo(0.015) + metade_calha(0.005) + raio_bola(0.03) + folga(0.02) ≈ 0.32
    spawn_ball = TimerAction(
        period=5.0,
        actions=[
            Node(
                package='ros_gz_sim',
                executable='create',
                arguments=[
                    '-file', ball_file,
                    '-name', 'ball',
                    '-x', '0.0',
                    '-y', '0.0',
                    '-z', '0.32',
                ],
                output='screen'
            )
        ]
    )

    # 6. Controller Manager (ros2_control) e carrega os controladores após o spawn
    joint_state_broadcaster = TimerAction(
        period=8.0,
        actions=[
            Node(
                package="controller_manager",
                executable="spawner",
                arguments=["joint_state_broadcaster"],
                output="screen"
            )
        ]
    )

    # Ativa os controladores após o controller_manager subir
    beam_controller = TimerAction(
        period=10.0,
        actions=[
            Node(
                package="controller_manager",
                executable="spawner",
                arguments=["beam_position_controller"],
                output="screen"
            )
        ]
    )

    # activate_beam_controller = TimerAction(
    #     period=9.0,
    #     actions=[
    #         ExecuteProcess(
    #             cmd=['ros2', 'control', 'load_controller', '--set-state', 'active',
    #                  'beam_position_controller'],
    #             output='screen'
    #         )
    #     ]
    # )

    # Launch Description
    return LaunchDescription([
        gazebo,
        ros_gz_bridge,
        robot_state_publisher,
        spawn_beam,
        spawn_ball,
        joint_state_broadcaster,
        beam_controller
    ])