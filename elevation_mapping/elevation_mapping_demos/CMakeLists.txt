cmake_minimum_required(VERSION 3.8)
project(elevation_mapping_demos)

find_package(ament_cmake REQUIRED)

# Install only directories that exist in the ROS2 workspace.  The old ROS1 XML
# launch directory was removed during the ROS2 cleanup, so installing a hardcoded
# `launch` directory makes plain `colcon build` fail at install time.
foreach(dir config doc rviz sample_data)
  if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/${dir}")
    install(DIRECTORY ${dir}
      DESTINATION share/${PROJECT_NAME}
    )
  endif()
endforeach()

install(PROGRAMS
  scripts/tf_to_pose_publisher.py
  scripts/gravity_correction_publisher.py
  scripts/pc_filter.py
  scripts/publish_corrected_frame.py
  scripts/publish_map_frame.py
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
