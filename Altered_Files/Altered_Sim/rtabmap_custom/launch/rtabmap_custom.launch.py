import os

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    
    # Locate the DepthAI camera launch file             ##Disable for simulation
    # depthai_ros_driver_share = get_package_share_directory('depthai_ros_driver')
    # depthai_launch_path = os.path.join(depthai_ros_driver_share, 'launch', 'camera.launch.py')

    # Locate the RTAB-Map launch file
    rtabmap_launch_share = get_package_share_directory('rtabmap_launch')
    rtabmap_launch_path = os.path.join(rtabmap_launch_share, 'launch', 'rtabmap.launch.py')

    # Include the DepthAI camera launch file            ##Disable for simulation
    # depthai_launch = IncludeLaunchDescription(
    #     PythonLaunchDescriptionSource(depthai_launch_path)
    # )

    # Include the RTAB-Map launch file with the desired parameters
    rtabmap_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(rtabmap_launch_path),
        launch_arguments={
            ## NOTE: once RTABMap is installed, parameters can be found in /opt/ros/humble/share/rtabmap_launch/launch/rtabmap.launch.py
            ## NOTE: Additional parameters can also be found on https://github.com/introlab/rtabmap/blob/master/corelib/include/rtabmap/core/Parameters.h 
            
            #Parameters changed in launch file
            'args': '--delete_db_on_start',       # Delete the previous database on start-up for a fresh SLAM session(start new map)
            'depth_topic': '/depth_camera',         # ROS2 topic for depth images
            'rgb_topic': '/camera',                 # ROS2 topic for RGB images
            'camera_info_topic': '/camera_info',      # ROS2 topic for camera calibration info
            'frame_id': 'x500_depth_0/OakD-Lite/base_link/IMX214',  # Coordinate frame ID for the camera
            'use_sim_time': 'true',                 # Use simulation time (useful in simulation environments)
            'approx_sync': 'true',                  # Enable approximate synchronization of image topics
            'qos': '2',                           # Quality of Service level for topic communication (2=Best Effort)
            'queue_size': '30',                   # Message queue size for subscriptions

            # RTAB-Map specific parameters:
            'Rtabmap/MaxFeatures': '200',         # Maximum number of features to extract for loop closure detection
            'Rtabmap/Resolution': '2',            # Map/occupancy grid resolution (e.g., voxel size)
            'Rtabmap/Decimation': '2',            # Downsampling factor for input images to speed up processing
            'Rtabmap/TimeTHrLoopClosure': '5',    # Minimum time (seconds) between loop closure detections
            'RGBD/MaxDepth': '10',                # Maximum depth (in meters) to consider for RGB-D image processing
            'Rtabmap/DetectionRate': '2',         # Frequency (Hz) at which loop closure detection is attempted
            'Vis/MaxFeatures': '300',             # Maximum number of visual features for visual odometry
            'Vis/FeatureType': '2',               # Visual feature extraction algorithm (2=ORB)
            'Vis/Iterations': '100',              # Maximum iterations for feature matching optimization
            'Odom/KeyFrameThr': '0.3',            # Threshold for creating a new keyframe during odometry
            'OdomF2M/MaxNewFeatures': '300',      # Maximum new features added during frame-to-model odometry
            
        }.items()
    )

    return LaunchDescription([
        # depthai_launch,                               ##Disable for simulation
        rtabmap_launch
    ])
