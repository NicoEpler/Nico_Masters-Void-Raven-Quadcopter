"""
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Spectacular AI ROS2 node that manages the OAK-D device through DepthAI Python API
"""

import spectacularAI
import depthai
import numpy as np
import open3d as o3d #Nico: I added this line

from geometry_msgs.msg import PoseStamped, TransformStamped
from tf2_msgs.msg import TFMessage
from cv_bridge import CvBridge
from sensor_msgs.msg import Image, CameraInfo, PointCloud2, PointField
from builtin_interfaces.msg import Time

import rclpy
from rclpy.node import Node

PUBLISHER_QUEUE_SIZE = 10

def toRosTime(timeInSeconds):
    t = Time()
    t.sec = int(timeInSeconds)
    t.nanosec = int((timeInSeconds % 1) * 1e9)
    return t


def toPoseMessage(cameraPose, ts):
    msg = PoseStamped()
    msg.header.stamp = ts
    msg.header.frame_id = "world"
    msg.pose.position.x = cameraPose.position.x
    msg.pose.position.y = cameraPose.position.y
    msg.pose.position.z = cameraPose.position.z
    msg.pose.orientation.x = cameraPose.orientation.x
    msg.pose.orientation.y = cameraPose.orientation.y
    msg.pose.orientation.z = cameraPose.orientation.z
    msg.pose.orientation.w = cameraPose.orientation.w
    return msg


def toTfMessage(cameraPose, ts, frame_id):
    msg = TFMessage()
    msg.transforms = []
    transform = TransformStamped()
    transform.header.stamp = ts
    transform.header.frame_id = "world"
    transform.child_frame_id = frame_id
    transform.transform.translation.x = cameraPose.position.x
    transform.transform.translation.y = cameraPose.position.y
    transform.transform.translation.z = cameraPose.position.z
    transform.transform.rotation.x = cameraPose.orientation.x
    transform.transform.rotation.y = cameraPose.orientation.y
    transform.transform.rotation.z = cameraPose.orientation.z
    transform.transform.rotation.w = cameraPose.orientation.w
    msg.transforms.append(transform)
    return msg


def toCameraInfoMessage(camera, frame, ts):
    intrinsic = camera.getIntrinsicMatrix()
    msg = CameraInfo()
    msg.header.stamp = ts
    msg.header.frame_id = "left_camera"
    msg.height = frame.shape[0]
    msg.width = frame.shape[1]
    msg.distortion_model = "none"
    msg.d = []
    msg.k = intrinsic.ravel().tolist()
    return msg


class SpectacularAINode(Node):
    def __init__(self):
        super().__init__("spectacular_ai_node")
        self.declare_parameter('recordingFolder', rclpy.Parameter.Type.STRING)

        self.odometry_publisher = self.create_publisher(PoseStamped, "/slam/odometry", PUBLISHER_QUEUE_SIZE)
        self.keyframe_publisher = self.create_publisher(PoseStamped, "/slam/keyframe", PUBLISHER_QUEUE_SIZE)
        self.left_publisher = self.create_publisher(Image, "/slam/left", PUBLISHER_QUEUE_SIZE)
        self.tf_publisher = self.create_publisher(TFMessage, "/tf", PUBLISHER_QUEUE_SIZE)
        self.point_publisher = self.create_publisher(PointCloud2, "/slam/pointcloud", PUBLISHER_QUEUE_SIZE)
        self.camera_info_publisher = self.create_publisher(CameraInfo, "/slam/camera_info", PUBLISHER_QUEUE_SIZE)
        self.bridge = CvBridge()
        self.keyframes = {}
        self.latestOutputTimestamp = None

        self.pipeline = depthai.Pipeline()
        config = spectacularAI.depthai.Configuration()

        recordingFolder = str(self.get_parameter('recordingFolder').value)
        if recordingFolder:
            self.get_logger().info("Recording: " + recordingFolder)
            config.recordingFolder = recordingFolder
            config.recordingOnly = True

        config.internalParameters = {
            "ffmpegVideoCodec": "libx264 -crf 15 -preset ultrafast",
            "computeStereoPointCloud": "true",
            "computeDenseStereoDepthKeyFramesOnly": "true"
        }
        config.useSlam = True #False Disables loop closures and other related processing. Can make the relative pose changes more predictable. Disables reduced FPS image data input.
        # config.useVioAutoExposure = True #Enable custom auto-exposure to improve low-light scenarios and reduce motion blur (BETA).
        # config.inputResolution = [400p]

        self.get_logger().info("Starting VIO") # Example of logging.
        self.vio_pipeline = spectacularAI.depthai.Pipeline(self.pipeline, config, self.onMappingOutput)
        changed_fps = 20 # Nico: I added this line Changes VIO framerate (Default=30)
        self.vio_pipeline.monoLeft.setFps(changed_fps) # Nico: I added this line
        self.vio_pipeline.monoRight.setFps(changed_fps) # Nico: I added this line
        self.device = depthai.Device(self.pipeline)
        self.vio_session = self.vio_pipeline.startSession(self.device)
        self.timer = self.create_timer(0, self.processOutput)


    def processOutput(self):
        while self.vio_session.hasOutput():
            self.onVioOutput(self.vio_session.getOutput())


    def onVioOutput(self, vioOutput):
        timestamp = toRosTime(vioOutput.getCameraPose(0).pose.time)
        self.latestOutputTimestamp = timestamp
        cameraPose = vioOutput.getCameraPose(0).pose
        self.odometry_publisher.publish(toPoseMessage(cameraPose, timestamp))
        self.tf_publisher.publish(toTfMessage(cameraPose, timestamp, "left_camera"))


    def onMappingOutput(self, output):
        for frame_id in output.updatedKeyFrames:
            keyFrame = output.map.keyFrames.get(frame_id)
            if not keyFrame: continue # Deleted keyframe
            if not keyFrame.pointCloud: continue
            if not self.hasKeyframe(frame_id):
                self.newKeyFrame(frame_id, keyFrame)


    def hasKeyframe(self, frame_id):
        return frame_id in self.keyframes


    def newKeyFrame(self, frame_id, keyframe):
        if not self.latestOutputTimestamp: return
        timestamp = toRosTime(keyframe.frameSet.primaryFrame.cameraPose.pose.time)
        self.keyframes[frame_id] = True
        msg = toPoseMessage(keyframe.frameSet.primaryFrame.cameraPose.pose, timestamp)
        msg.header.stamp = timestamp
        self.keyframe_publisher.publish(msg)

        left_frame_bitmap = keyframe.frameSet.primaryFrame.image.toArray()
        left_msg = self.bridge.cv2_to_imgmsg(left_frame_bitmap, encoding="mono8")
        left_msg.header.stamp = timestamp
        left_msg.header.frame_id = "left_camera"
        self.left_publisher.publish(left_msg)

        camera = keyframe.frameSet.primaryFrame.cameraPose.camera
        info_msg = toCameraInfoMessage(camera, left_frame_bitmap, timestamp)
        self.camera_info_publisher.publish(info_msg)

        self.publishPointCloud(keyframe, timestamp)


    # # NOTE This seems a bit slow.
    # def publishPointCloud(self, keyframe, timestamp):
    #     camToWorld = keyframe.frameSet.rgbFrame.cameraPose.getCameraToWorldMatrix()
    #     positions = keyframe.pointCloud.getPositionData()
    #     pc = np.zeros((positions.shape[0], 6), dtype=np.float32)
    #     p_C = np.vstack((positions.T, np.ones((1, positions.shape[0])))).T
    #     pc[:, :3] = (camToWorld @ p_C[:, :, None])[:, :3, 0]

    #     msg = PointCloud2()
    #     msg.header.stamp = timestamp
    #     msg.header.frame_id = "world"
    #     if keyframe.pointCloud.hasColors():
    #         pc[:, 3:] = keyframe.pointCloud.getRGB24Data() * (1. / 255.)
    #     msg.point_step = 4 * 6
    #     msg.height = 1
    #     msg.width = pc.shape[0]
    #     msg.row_step = msg.point_step * pc.shape[0]
    #     msg.data = pc.tobytes()
    #     msg.is_bigendian = False
    #     msg.is_dense = False
    #     ros_dtype = PointField.FLOAT32
    #     itemsize = np.dtype(np.float32).itemsize
    #     msg.fields = [PointField(name=n, offset=i*itemsize, datatype=ros_dtype, count=1) for i, n in enumerate('xyzrgb')]
    #     self.point_publisher.publish(msg)


    # Nico: I replaced the above function with the following one
    def publishPointCloud(self, keyframe, timestamp):
        
        #Parameters to edit:
        voxel_size = 0.03 #0.03
        nb_points = 10 #10 minimum number of points required to be within radius of each point to consider it an “inlier”
        radius = 0.15 #0.15 The distance within which nb_points must lie for the point to be kept
        
        
        # 1. Get the camera-to-world transform
        camToWorld = keyframe.frameSet.rgbFrame.cameraPose.getCameraToWorldMatrix()

        # 2. Get positions (N x 3) in camera frame
        positions = keyframe.pointCloud.getPositionData()

        # 3. Prepare Nx6 float array [X_w, Y_w, Z_w, R, G, B]
        pc = np.zeros((positions.shape[0], 6), dtype=np.float32)

        # Convert to homogeneous coords for matrix multiplication
        p_C = np.vstack((positions.T, np.ones((1, positions.shape[0])))).T

        # Multiply by camToWorld -> world coordinates
        pc[:, :3] = (camToWorld @ p_C[:, :, None])[:, :3, 0]

        # 4. If the point cloud has color data, fill columns 3..5
        if keyframe.pointCloud.hasColors():
            # Typically Nx3 uint8 => convert to float [0..1]
            pc[:, 3:] = keyframe.pointCloud.getRGB24Data() * (1.0 / 255.0)

        # ---------------------- OPEN3D PROCESSING ----------------------
        # 5. Convert Nx6 NumPy array into Open3D point cloud
        o3d_pc = o3d.geometry.PointCloud()
        o3d_pc.points = o3d.utility.Vector3dVector(pc[:, :3].astype(np.float64))
        if keyframe.pointCloud.hasColors():
            o3d_pc.colors = o3d.utility.Vector3dVector(pc[:, 3:].astype(np.float64))

        # 6. Voxel downsampling (adjust voxel_size to your needs)
        # voxel_size = 0.01  # e.g., 1 cm
        o3d_pc = o3d_pc.voxel_down_sample(voxel_size=voxel_size)

        # 7. Radius outlier removal
        #    E.g., remove points that have fewer than 5 neighbors in a 2cm radius
        # nb_points = 5
        # radius = 0.02
        o3d_pc, inlier_indices = o3d_pc.remove_radius_outlier(
            nb_points=nb_points, radius=radius
        )

        # 8. Convert back to Nx6 array (world coords + color)
        new_positions = np.asarray(o3d_pc.points)  # Nx3 float64
        new_colors = np.asarray(o3d_pc.colors) if keyframe.pointCloud.hasColors() else None

        # Rebuild the Nx6 array as float32
        filtered_pc = np.zeros((new_positions.shape[0], 6), dtype=np.float32)
        filtered_pc[:, :3] = new_positions.astype(np.float32)
        if new_colors is not None:
            filtered_pc[:, 3:] = new_colors.astype(np.float32)

        # ---------------------- ROS POINTCLOUD2 MESSAGE ----------------------
        # 9. Build the PointCloud2 message
        msg = PointCloud2()
        msg.header.stamp = timestamp
        msg.header.frame_id = "world"  # or whatever frame you using

        # Each point: 6 floats (x, y, z, r, g, b) => 24 bytes total
        ros_dtype = PointField.FLOAT32
        itemsize = np.dtype(np.float32).itemsize  # 4 bytes
        msg.point_step = itemsize * 6
        msg.height = 1
        msg.width = filtered_pc.shape[0]
        msg.row_step = msg.point_step * filtered_pc.shape[0]
        msg.is_bigendian = False
        msg.is_dense = False

        # The actual binary data
        msg.data = filtered_pc.tobytes()

        # Define the fields in the PointCloud2
        msg.fields = [
            PointField(name=n, offset=i*itemsize, datatype=ros_dtype, count=1)
            for i, n in enumerate(['x', 'y', 'z', 'r', 'g', 'b'])
        ]

        # 10. Finally, publish
        self.point_publisher.publish(msg)



def main(args=None):
    rclpy.init(args=args)
    sai_node = SpectacularAINode()
    rclpy.spin(sai_node)
    sai_node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
  main()