# One-joint robot: ROS 2, Gazebo and MoveIt 2

This package keeps the robot description, simulation configuration and MoveIt configuration in one ROS 2 package.

## Architecture

- Vaaman: MoveIt 2 `move_group` (motion planning).
- PC: Gazebo + `gz_ros2_control` + `arm_controller` (trajectory execution).
- PC: RViz 2 (visualization and planning UI).
- Both machines: same `ROS_DOMAIN_ID`, ROS 2 Humble, reachable over the same network.

## Build on both machines

```bash
source /opt/ros/humble/setup.bash
cd ~/one_joint_ws
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
source install/setup.bash
```

## PC: start Gazebo

```bash
export ROS_DOMAIN_ID=30
source /opt/ros/humble/setup.bash
source ~/one_joint_ws/install/setup.bash
ros2 launch one_joint_robot_description one_joint.launch.py
```

The existing simulation launch starts `joint_state_broadcaster` and `forward_position_controller`.

## PC: switch to the trajectory controller

In another PC terminal:

```bash
export ROS_DOMAIN_ID=30
source /opt/ros/humble/setup.bash
source ~/one_joint_ws/install/setup.bash
ros2 run controller_manager spawner arm_controller -c /controller_manager --inactive
ros2 control switch_controllers -c /controller_manager --deactivate forward_position_controller --activate arm_controller --strict
ros2 control list_controllers
```

Expected: `joint_state_broadcaster` active, `forward_position_controller` inactive, `arm_controller` active.

## Vaaman: start MoveIt

```bash
export ROS_DOMAIN_ID=30
source /opt/ros/humble/setup.bash
source ~/one_joint_ws/install/setup.bash
ros2 launch one_joint_robot_description moveit_move_group.launch.py
```

## PC: start RViz

```bash
export ROS_DOMAIN_ID=30
source /opt/ros/humble/setup.bash
source ~/one_joint_ws/install/setup.bash
ros2 launch one_joint_robot_description moveit_rviz.launch.py
```

## Important notes

- `joint1` is the only actuated joint. This example demonstrates joint-space planning, not arbitrary 3D end-effector pose planning.
- `forward_position_controller` and `arm_controller` must not be active at the same time because both claim `joint1`'s position command interface.
- `move_group` on Vaaman needs to discover `/joint_states`, TF, and the `arm_controller/follow_joint_trajectory` action from the PC.
- The RViz MotionPlanning panel on PC connects to the remote `move_group` over DDS. Ensure firewall/network settings permit ROS 2 DDS traffic.
- The robot's Gazebo model is spawned with a `world` frame; the SRDF virtual joint attaches `base_link` to `world`.
