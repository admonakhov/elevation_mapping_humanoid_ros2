# Elevation Mapping Humanoid ROS2

English documentation. Russian documentation is available in [README.ru.md](README.ru.md).

This is a ROS2 workspace for humanoid elevation mapping from LiDAR, IMU and odometry data. The main `elevation_mapping` stack has been ported to ROS2 and builds with `colcon`.

The workspace is based on:

- Robot-Centric Elevation Mapping: https://github.com/ANYbotics/elevation_mapping
- FAST-LIO / FAST-LIO2 for LiDAR-inertial odometry
- Grid Map
- kindr / kindr_ros

## Workspace packages

Active ROS2 packages:

```text
elevation_mapping
elevation_mapping_demos
fast_lio
kindr
kindr_msgs
kindr_ros
message_logger
pose_publisher
```

Notes:

- `elevation_mapping` builds and runs on ROS2.
- `fast_lio` lives in `fast_lio_mid360` and requires `livox_ros_driver2`.
- ROS1/catkin-only packages and RViz1 plugins were removed from this workspace.
- The old duplicate `FAST_LIO_ROS2` directory was removed. The active FAST-LIO package is `fast_lio_mid360`.

## Requirements

Expected environment:

- Ubuntu with ROS2 installed under `/opt/ros/<ROS_DISTRO>`
- `colcon`
- system Python `/usr/bin/python3`

Install common dependencies, replacing `<ROS_DISTRO>` with your target ROS2 distribution name:

```bash
sudo apt update
sudo apt install -y \
  python3-colcon-common-extensions \
  python3-rosdep \
  ros-<ROS_DISTRO>-grid-map \
  ros-<ROS_DISTRO>-grid-map-ros \
  ros-<ROS_DISTRO>-grid-map-msgs \
  ros-<ROS_DISTRO>-grid-map-visualization \
  ros-<ROS_DISTRO>-pcl-ros \
  ros-<ROS_DISTRO>-pcl-conversions \
  ros-<ROS_DISTRO>-tf2 \
  ros-<ROS_DISTRO>-tf2-ros \
  ros-<ROS_DISTRO>-tf2-eigen \
  ros-<ROS_DISTRO>-tf2-geometry-msgs \
  ros-<ROS_DISTRO>-rviz2
```

`fast_lio` additionally requires the ROS2 Livox driver:

```text
livox_ros_driver2
```

If `livox_ros_driver2` is not installed or not sourced, build and test `elevation_mapping` without `fast_lio`.

## Conda warning

On conda-heavy machines, conda can break ROS2 builds:

- ament may pick conda Python instead of `/usr/bin/python3`;
- conda `curl-config` can cause linker errors with `libcurl`, `gdal` or `netcdf`;
- system Python and conda Python numpy modules may conflict.

Use a clean ROS/system environment before building:

```bash
source /opt/ros/<ROS_DISTRO>/setup.bash
export PATH=/opt/ros/<ROS_DISTRO>/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
export PYTHONPATH=/usr/lib/python3/dist-packages:${PYTHONPATH:-}
```

Pass system Python explicitly when needed:

```bash
-DPython3_EXECUTABLE=/usr/bin/python3
```

## Build

### Legacy tests

The upstream `kindr_ros` test files in this vendored tree are still ROS1-style (`geometry_msgs/Pose.h`, `geometry_msgs/Quaternion.h`, `tf::Transform`). They are disabled by default via:

```cmake
KINDR_ROS_BUILD_LEGACY_TESTS=OFF
```

Therefore plain `colcon build` should not fail with:

```text
fatal error: geometry_msgs/Pose.h: No such file or directory
fatal error: geometry_msgs/Quaternion.h: No such file or directory
```

For a runtime-only build, you can additionally disable all tests:

```bash
--cmake-args -DBUILD_TESTING=OFF
```

Go to the workspace:

```bash
cd /path/to/elevation_mapping_humanoid_ros2
```

Prepare the environment:

```bash
source /opt/ros/<ROS_DISTRO>/setup.bash
export PATH=/opt/ros/<ROS_DISTRO>/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
export PYTHONPATH=/usr/lib/python3/dist-packages:${PYTHONPATH:-}
```

### Build the elevation_mapping stack only

This is the main verified build path and does not require `livox_ros_driver2`:

```bash
colcon build \
  --packages-up-to elevation_mapping \
  --cmake-args \
    -DBUILD_TESTING=OFF \
    -DPython3_EXECUTABLE=/usr/bin/python3
```

After building:

```bash
source install/setup.bash
```

Check package discovery:

```bash
ros2 pkg prefix elevation_mapping
ros2 pkg executables elevation_mapping
```

Expected executables:

```text
elevation_mapping elevation_mapping
elevation_mapping get_grid_map_client
elevation_mapping listener
```

### Build all ROS2 packages except fast_lio

Use this when `livox_ros_driver2` is not installed yet:

```bash
colcon build \
  --packages-skip fast_lio \
  --cmake-args \
    -DBUILD_TESTING=OFF \
    -DPython3_EXECUTABLE=/usr/bin/python3
```

### Build with fast_lio

First build/source `livox_ros_driver2`, then build this workspace:

```bash
source /opt/ros/<ROS_DISTRO>/setup.bash
source /path/to/livox_ros_driver2/install/setup.bash
cd /path/to/elevation_mapping_humanoid_ros2

colcon build \
  --cmake-args \
    -DBUILD_TESTING=OFF \
    -DPython3_EXECUTABLE=/usr/bin/python3
```

If CMake reports:

```text
Could not find livox_ros_driver2Config.cmake
```

then `livox_ros_driver2` is not installed or has not been sourced.

## Run elevation_mapping

Prepare the environment:

```bash
cd /path/to/elevation_mapping_humanoid_ros2
source /opt/ros/<ROS_DISTRO>/setup.bash
source install/setup.bash
```

Run the node directly:

```bash
ros2 run elevation_mapping elevation_mapping
```

Smoke-test without sensors:

```bash
timeout 5s ros2 run elevation_mapping elevation_mapping \
  --ros-args \
  -p enable_visibility_cleanup:=false \
  -p fused_map_publishing_rate:=0.5
```

Expected startup messages:

```text
Elevation mapping node started.
Elevation map grid resized ...
Successfully launched node.
```

This warning is normal when no point cloud input sources are configured:

```text
Not registering any callbacks, no input sources given. Did you configure the InputSourceManager?
```

For a real robot, configure `input_sources` and sensor processor YAML files for your LiDAR/point cloud topics.

## Visualize the elevation map

Check launch arguments:

```bash
ros2 launch elevation_mapping visualization.launch.py --show-args
```

Start visualization:

```bash
ros2 launch elevation_mapping visualization.launch.py
```

This launch starts `grid_map_visualization` for raw/fused maps with:

```text
elevation_mapping/config/visualization/raw.yaml
elevation_mapping/config/visualization/fused.yaml
```

Check topics:

```bash
ros2 topic list | grep -E 'elevation|grid|map'
```

Expected topics include:

```text
/elevation_map
/elevation_map_raw_post
/visibility_cleanup_map
```

Inspect one message:

```bash
ros2 topic echo /elevation_map --once
```

## Run fast_lio for MID360

The `fast_lio` package is located in:

```text
fast_lio_mid360
```

Launch file:

```text
fast_lio_mid360/launch/mapping.launch.py
```

Check launch arguments:

```bash
ros2 launch fast_lio mapping.launch.py --show-args
```

Run MID360 config with RViz:

```bash
ros2 launch fast_lio mapping.launch.py \
  config_file:=mid360.yaml \
  rviz:=true
```

Run without RViz:

```bash
ros2 launch fast_lio mapping.launch.py \
  config_file:=mid360.yaml \
  rviz:=false
```

Available configs:

```text
fast_lio_mid360/config/mid360.yaml
fast_lio_mid360/config/mid360_mr.yaml
fast_lio_mid360/config/avia.yaml
fast_lio_mid360/config/horizon.yaml
fast_lio_mid360/config/ouster64.yaml
fast_lio_mid360/config/velodyne.yaml
fast_lio_mid360/config/velodyne_mr.yaml
```

Important: `fast_lio` will not build or run for MID360 without `livox_ros_driver2`.

## Typical robot startup order

Use separate terminals.

### Terminal 1: Livox driver

```bash
source /opt/ros/<ROS_DISTRO>/setup.bash
source /path/to/livox_ros_driver2/install/setup.bash
ros2 launch livox_ros_driver2 msg_MID360_launch.py
```

Check the cloud topic:

```bash
ros2 topic list | grep -E 'livox|point|cloud'
ros2 topic hz /livox/lidar
```

### Terminal 2: FAST-LIO

```bash
cd /path/to/elevation_mapping_humanoid_ros2
source /opt/ros/<ROS_DISTRO>/setup.bash
source /path/to/livox_ros_driver2/install/setup.bash
source install/setup.bash

ros2 launch fast_lio mapping.launch.py config_file:=mid360.yaml rviz:=false
```

Check odometry/map topics:

```bash
ros2 topic list | grep -E 'odom|cloud|path|lio|map'
```

### Terminal 3: elevation_mapping

```bash
cd /path/to/elevation_mapping_humanoid_ros2
source /opt/ros/<ROS_DISTRO>/setup.bash
source install/setup.bash

ros2 run elevation_mapping elevation_mapping
```

### Terminal 4: visualization

```bash
cd /path/to/elevation_mapping_humanoid_ros2
source /opt/ros/<ROS_DISTRO>/setup.bash
source install/setup.bash

ros2 launch elevation_mapping visualization.launch.py
```

## Adapt to your robot

Check and configure at least:

1. TF tree:

```bash
ros2 run tf2_ros tf2_echo odom base_link
ros2 run tf2_ros tf2_echo base_link livox_frame
```

2. Frame IDs in configs:

```text
elevation_mapping/config/robots/*.yaml
elevation_mapping/config/elevation_maps/*.yaml
elevation_mapping/config/sensor_processors/*.yaml
fast_lio_mid360/config/*.yaml
```

3. Point cloud topics:

```bash
ros2 topic list | grep -E 'cloud|points|livox|lidar'
```

4. If `elevation_mapping` reports that input sources are not configured, add or fix `input_sources` in the elevation_mapping YAML config for the real point cloud topics.

## Verified commands

Build `elevation_mapping`:

```text
Summary: 3 packages finished
```

Launch parse check:

```bash
ros2 launch elevation_mapping visualization.launch.py --show-args
```

Expected result:

```text
Arguments:
  No arguments.
```

Smoke run:

```bash
timeout 5s ros2 run elevation_mapping elevation_mapping \
  --ros-args \
  -p enable_visibility_cleanup:=false \
  -p fused_map_publishing_rate:=0.5
```

The node starts, publishes topics, and then exits due to `timeout`.
