/*
 * Copyright (c) 2014, Zhi Yan <zhi.yan@mines-douai.fr>
 * Ported to ROS 2.
 */

#include <chrono>
#include <memory>
#include <string>

#include <geometry_msgs/msg/pose_with_covariance_stamped.hpp>
#include <rclcpp/rclcpp.hpp>
#include <tf2/exceptions.h>
#include <tf2_ros/buffer.h>
#include <tf2_ros/transform_listener.h>

class PosePublisherNode : public rclcpp::Node {
public:
  PosePublisherNode()
      : Node("node_pose_publisher"),
        tf_buffer_(this->get_clock()),
        tf_listener_(tf_buffer_) {
    publish_frequency_ = declare_parameter<double>("publish_frequency", 10.0);
    map_frame_ = declare_parameter<std::string>("map_frame", "map");
    base_frame_ = declare_parameter<std::string>("base_frame", "base_link");
    topic_republish_ = declare_parameter<std::string>("topic_republish", "pose");

    pose_publisher_ = create_publisher<geometry_msgs::msg::PoseWithCovarianceStamped>(topic_republish_, 1);

    const auto period = std::chrono::duration<double>(1.0 / std::max(publish_frequency_, 1e-3));
    timer_ = create_wall_timer(std::chrono::duration_cast<std::chrono::nanoseconds>(period),
                               std::bind(&PosePublisherNode::timerCallback, this));
  }

private:
  void timerCallback() {
    geometry_msgs::msg::TransformStamped transform;
    try {
      transform = tf_buffer_.lookupTransform(map_frame_, base_frame_, tf2::TimePointZero);
    } catch (const tf2::TransformException &ex) {
      RCLCPP_DEBUG(get_logger(), "Could not transform %s to %s: %s",
                   base_frame_.c_str(), map_frame_.c_str(), ex.what());
      return;
    }

    geometry_msgs::msg::PoseWithCovarianceStamped pose_stamped;
    pose_stamped.header.stamp = now();
    pose_stamped.header.frame_id = map_frame_;
    pose_stamped.pose.pose.position.x = transform.transform.translation.x;
    pose_stamped.pose.pose.position.y = transform.transform.translation.y;
    pose_stamped.pose.pose.position.z = transform.transform.translation.z;
    pose_stamped.pose.pose.orientation = transform.transform.rotation;
    pose_publisher_->publish(pose_stamped);
  }

  double publish_frequency_{};
  std::string map_frame_;
  std::string base_frame_;
  std::string topic_republish_;
  rclcpp::Publisher<geometry_msgs::msg::PoseWithCovarianceStamped>::SharedPtr pose_publisher_;
  tf2_ros::Buffer tf_buffer_;
  tf2_ros::TransformListener tf_listener_;
  rclcpp::TimerBase::SharedPtr timer_;
};

int main(int argc, char **argv) {
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<PosePublisherNode>());
  rclcpp::shutdown();
  return 0;
}
