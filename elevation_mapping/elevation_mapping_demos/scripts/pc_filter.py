#!/usr/bin/python3

import numpy as np

import rclpy
from rclpy.duration import Duration
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data

from sensor_msgs.msg import PointCloud2, PointField
from sensor_msgs_py import point_cloud2 as pc2
from tf2_ros import Buffer, TransformException, TransformListener
from tf2_sensor_msgs.tf2_sensor_msgs import do_transform_cloud


class PointCloudFilter(Node):
    """ROS2 port of the ROS1 humanoid pointcloud filter.

    Subscribes to /cloud_registered, transforms points into torso_link, keeps points
    below distance_threshold on local Z, and publishes /cloud_registered/filtered.
    """

    def __init__(self):
        super().__init__('pointcloud_filter')
        self.declare_parameter('distance_threshold', -0.5)
        self.declare_parameter('input_topic', '/cloud_registered')
        self.declare_parameter('output_topic', '/cloud_registered/filtered')
        self.declare_parameter('target_frame', 'torso_link')
        self.declare_parameter('lookup_timeout_sec', 0.1)

        self.distance_threshold = float(self.get_parameter('distance_threshold').value)
        input_topic = str(self.get_parameter('input_topic').value)
        output_topic = str(self.get_parameter('output_topic').value)
        self.target_frame = str(self.get_parameter('target_frame').value)
        self.lookup_timeout = Duration(seconds=float(self.get_parameter('lookup_timeout_sec').value))

        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        self.publisher = self.create_publisher(PointCloud2, output_topic, 10)
        self.subscription = self.create_subscription(
            PointCloud2, input_topic, self.pointcloud_callback, qos_profile_sensor_data)

        self.get_logger().info(
            f'Filtering {input_topic} -> {output_topic}; target_frame={self.target_frame}; '
            f'z <= {self.distance_threshold}')

    def pointcloud_callback(self, msg: PointCloud2):
        source_frame = msg.header.frame_id.lstrip('/')
        target_frame = self.target_frame.lstrip('/')
        if source_frame == target_frame:
            transformed_msg = msg
        else:
            try:
                transform = self.tf_buffer.lookup_transform(
                    self.target_frame,
                    msg.header.frame_id,
                    rclpy.time.Time.from_msg(msg.header.stamp),
                    timeout=self.lookup_timeout)
            except TransformException as exc:
                self.get_logger().warn(
                    f'TF lookup failed for {msg.header.frame_id} -> {self.target_frame}: {exc}',
                    throttle_duration_sec=2.0)
                return

            transformed_msg = do_transform_cloud(msg, transform)

        points = self.pointcloud2_to_numpy(transformed_msg)
        filtered_points = points[points[:, 2] <= self.distance_threshold]
        if points.size and filtered_points.size == 0:
            self.get_logger().warn(
                f'Filtered cloud is empty: input_points={len(points)}, '
                f'z_range=[{points[:, 2].min():.3f}, {points[:, 2].max():.3f}], '
                f'threshold={self.distance_threshold}',
                throttle_duration_sec=2.0)
        filtered_msg = self.numpy_to_pointcloud2(filtered_points, transformed_msg.header)
        self.publisher.publish(filtered_msg)

    @staticmethod
    def pointcloud2_to_numpy(msg: PointCloud2) -> np.ndarray:
        points = pc2.read_points(msg, field_names=('x', 'y', 'z'), skip_nans=True)
        if isinstance(points, np.ndarray):
            if points.size == 0:
                return np.empty((0, 3), dtype=np.float32)
            if points.dtype.names:
                return np.column_stack((points['x'], points['y'], points['z'])).astype(np.float32)
            return np.asarray(points, dtype=np.float32).reshape((-1, 3))

        points = list(points)
        if not points:
            return np.empty((0, 3), dtype=np.float32)
        return np.asarray(points, dtype=np.float32).reshape((-1, 3))

    @staticmethod
    def numpy_to_pointcloud2(points: np.ndarray, header) -> PointCloud2:
        fields = [
            PointField(name='x', offset=0, datatype=PointField.FLOAT32, count=1),
            PointField(name='y', offset=4, datatype=PointField.FLOAT32, count=1),
            PointField(name='z', offset=8, datatype=PointField.FLOAT32, count=1),
        ]
        return pc2.create_cloud(header, fields, points.astype(np.float32).tolist())


def main(args=None):
    rclpy.init(args=args)
    node = PointCloudFilter()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
