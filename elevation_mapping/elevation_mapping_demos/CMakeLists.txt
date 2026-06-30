cmake_minimum_required(VERSION 3.8)
project(elevation_mapping_demos)

find_package(ament_cmake REQUIRED)

install(DIRECTORY config doc launch rviz sample_data
  DESTINATION share/${PROJECT_NAME}
)

install(PROGRAMS
  scripts/tf_to_pose_publisher.py
  scripts/gravity_correction_publisher.py
  scripts/pc_filter.py
  scripts/publish_corrected_frame.py
  scripts/publish_map_frame.py
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
