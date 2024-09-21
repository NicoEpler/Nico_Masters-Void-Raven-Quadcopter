
1. Install Fortress according to [this link](https://gazebosim.org/docs/fortress/install_ubuntu) and test installation using:
```Shell
ign gazebo
```

2. Create Workspace according to [this website](https://gazebosim.org/docs/fortress/ros_gz_project_template_guide)

3. To launch use:
```Shell
cd
cd DroneSim_ws/
colcon build --cmake-args -DBUILD_TESTING=ON
source install/setup.bash
ros2 launch ros_gz_example_bringup diff_drive.launch.py
```

4. Start the simulation
5. To visualize 3D pointcloud in rviz:
	1. Set "fixed frame" from "diff_drive/odom" to:
```
x500_depth/OakD-Lite/base_link/StereoOV7251
```
	2. Add "PointCloud2" and rename /depth_camera/ to /depth_camera/points

5. Change Directories in model and world files to appropriate directories on current device.

6. To make Drone Fly:
	1. Launch the simulation
	2. Start the simulation (Play in bottom left gazebo corner)
	3. Add following command in separate terminal to control rotation speed of motors
```Shell
ign topic -t /X500/gazebo/command/motor_speed --msgtype ignition.msgs.Actuators -p 'velocity:[700, 700, 700, 700]'
```


```Shell
gz topic -t /x500_0/command/motor_speed --msgtype gz.msgs.Actuators -p 'velocity:[700, 700, 700, 700]'
```













From Command Line Flying UAV:

In terminal 1:
```Shell
ign gazebo quadcopter.sdf
```

In terminal 2:
```Shell
ign topic -t /X3/gazebo/command/motor_speed --msgtype ignition.msgs.Actuators -p 'velocity:[700, 700, 700, 700]'
```

Location of quadcopter.sdf:
	/usr/share/ignition/ignition-gazebo6/worlds


try
```Shell
ign topic -t /X500/gazebo/command/motor_speed --msgtype ignition.msgs.Actuators -p 'velocity:[700, 700, 700, 700]'
```

For new Workspace:

```Shell
cd
cd Desktop/GazeboIgnitionFortressSim/DroneSim_ws/
colcon build --cmake-args -DBUILD_TESTING=ON
source install/setup.bash
ros2 launch ros_gz_example_bringup diff_drive.launch.py
```


