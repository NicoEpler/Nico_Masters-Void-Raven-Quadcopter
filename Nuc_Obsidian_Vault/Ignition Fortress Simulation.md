
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

4. To visualize 3D pointcloud in rviz:
	1. Set "fixed frame" from "diff_drive/odom" to:
```
x500_depth/OakD-Lite/base_link/StereoOV7251
```
	2. Add "PointCloud2" and rename /depth_camera/ to /depth_camera/points






topics:
1. /depth_camera
2. /depth_camera/points
3. camera
4. camera/info



