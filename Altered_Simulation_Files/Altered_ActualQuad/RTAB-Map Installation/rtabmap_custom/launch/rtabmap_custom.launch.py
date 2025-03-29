import os

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    # Locate the DepthAI camera launch file
    depthai_ros_driver_share = get_package_share_directory('depthai_ros_driver')
    depthai_launch_path = os.path.join(depthai_ros_driver_share, 'launch', 'camera.launch.py')

    # Locate the RTAB-Map launch file
    rtabmap_launch_share = get_package_share_directory('rtabmap_launch')
    rtabmap_launch_path = os.path.join(rtabmap_launch_share, 'launch', 'rtabmap.launch.py')

    # Include the DepthAI camera launch file
    depthai_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(depthai_launch_path)
    )

    # Include the RTAB-Map launch file with the desired parameters
    rtabmap_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(rtabmap_launch_path),
        launch_arguments={
            'args': '--delete_db_on_start',
            'depth_topic': '/oak/stereo/image_raw',
            'rgb_topic': '/oak/rgb/image_raw',
            'camera_info_topic': '/oak/rgb/camera_info',
            'frame_id': 'oak-d-base-frame',
            'use_sim_time': 'true',
            'approx_sync': 'true',
            'qos': '2',
            'queue_size': '30',
            'Rtabmap/MaxFeatures': '200',
            'Rtabmap/Resolution': '2',
            'Rtabmap/Decimation': '2',
            'Rtabmap/TimeTHrLoopClosure': '5',
            'RGBD/MaxDepth': '10',
            'Rtabmap/DetectionRate': '2',
            'Vis/MaxFeatures': '300',
            'Vis/FeatureType': '2',
            'Vis/Iterations': '100',
            'Odom/KeyFrameThr': '0.3',
            'OdomF2M/MaxNewFeatures': '300',
            
        }.items()
    )

    return LaunchDescription([
        depthai_launch,
        rtabmap_launch
    ])
