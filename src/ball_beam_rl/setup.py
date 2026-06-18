import os
from setuptools import setup
from setuptools import find_packages
from glob import glob

package_name = 'ball_beam_rl'

setup(
    name=package_name,
    version='0.0.0',

    packages=find_packages(exclude=['test']),

    data_files=[('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'urdf'), glob('urdf/*')),
        (os.path.join('share', package_name, 'launch'), glob('launch/*')),
        (os.path.join('share', package_name, 'config'), glob('config/*')),
        (os.path.join('share', package_name, 'worlds'), glob('worlds/*')),
    ],

    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='joao',
    maintainer_email='joao@email.com',
    description='Ball and Beam RL',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'ball_state_node = ball_beam_rl.ball_state_node:main',
            # 'test = ball_beam_rl.test:main',
            'train = ball_beam_rl.train:main',
            'simulation = ball_beam_rl.simulation:main',
        ],
    },
)