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

## Run the humanoid MID360 pipeline

This is the main launch path that mirrors the ROS1 `elevation_mapping_humanoid` workflow, but runs as ROS2 nodes.

Workspace location on this machine:

```bash
cd /home/ant/Robots/elevation_mapping
```

Prepare the ROS2 environment:

```bash
source /opt/ros/<ROS_DISTRO>/setup.bash
source install/setup.bash
```

For this machine with ROS2 Humble:

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
```

If `livox_ros_driver2` is built in a separate workspace, source it before this workspace:

```bash
source /opt/ros/<ROS_DISTRO>/setup.bash
source /path/to/livox_ros_driver2/install/setup.bash
source /home/ant/Robots/elevation_mapping/install/setup.bash
```

Start the full stack:

```bash
ros2 launch elevation_mapping livox_elevation_mapping.launch.py
```

Start without RViz:

```bash
ros2 launch elevation_mapping livox_elevation_mapping.launch.py rviz:=false
```

Start without FAST-LIO, for checking elevation mapping, pose publisher, pointcloud filter and visualization launch wiring:

```bash
ros2 launch elevation_mapping livox_elevation_mapping.launch.py \
  start_fast_lio:=false \
  rviz:=false
```

Start without grid map visualization nodes:

```bash
ros2 launch elevation_mapping livox_elevation_mapping.launch.py \
  start_visualization:=false \
  rviz:=false
```

Check launch arguments:

```bash
ros2 launch elevation_mapping livox_elevation_mapping.launch.py --show-args
```

Expected launch arguments:

```text
use_sim_time
start_fast_lio
start_filter
start_visualization
fast_lio_config
rviz
rviz_config
```

### What the launch starts

`livox_elevation_mapping.launch.py` starts:

```text
fast_lio / fastlio_mapping          # node name: /laserMapping
pc_filter.py                        # node name: /pointcloud_filter
pose_publisher                      # node name: /node_pose_publisher
elevation_mapping                   # node name: /elevation_mapping
grid_map_visualization raw/fused    # optional, controlled by start_visualization
rviz2                               # optional, controlled by rviz
```

### ROS1-equivalent data path

The ROS2 pipeline keeps the same humanoid logic and topic flow as the ROS1 workspace:

```text
/utlidar/cloud_livox_mid360 + /utlidar/imu_livox_mid360
  -> fast_lio
  -> /cloud_registered
  -> pc_filter
  -> /cloud_registered/filtered
  -> elevation_mapping
  -> /elevation_map, /elevation_map_raw_post, /visibility_cleanup_map

fast_lio TF odom_torso -> torso_link
  -> pose_publisher
  -> /pose
  -> elevation_mapping robot pose input
```

Important topics:

```text
Inputs:
/utlidar/cloud_livox_mid360
/utlidar/imu_livox_mid360

FAST-LIO outputs:
/cloud_registered
/cloud_registered_body
/fastlio_pc
/fastlio_odom
/Laser_map
/path
/tf

Pointcloud filter:
/cloud_registered -> /cloud_registered/filtered

Elevation mapping:
/pose
/elevation_map
/elevation_map_raw_post
/visibility_cleanup_map
```

Important frames:

```text
odom_torso -> torso_link
```

The main configs for this path are:

```text
fast_lio_mid360/config/mid360.yaml
elevation_mapping/elevation_mapping/config/robots/humanoid_fast_lio.yaml
elevation_mapping/elevation_mapping/config/postprocessing/postprocessor_pipeline.yaml
```

### Smoke test

Run the full ROS2 launch without RViz and without grid map visualization:

```bash
cd /home/ant/Robots/elevation_mapping
source /opt/ros/<ROS_DISTRO>/setup.bash
source install/setup.bash

ros2 launch elevation_mapping livox_elevation_mapping.launch.py \
  rviz:=false \
  start_visualization:=false
```

In another terminal:

```bash
source /opt/ros/<ROS_DISTRO>/setup.bash
source /home/ant/Robots/elevation_mapping/install/setup.bash

ros2 node list | sort
ros2 topic list | sort | grep -E '^/(cloud_registered|cloud_registered/filtered|fastlio_pc|fastlio_odom|elevation_map|pose|path|Laser_map|livox|tf|visibility_cleanup_map)'
```

Expected nodes:

```text
/elevation_mapping
/laserMapping
/node_pose_publisher
/pointcloud_filter
```

Expected topics include:

```text
/cloud_registered
/cloud_registered_body
/cloud_registered/filtered
/elevation_map
/elevation_map_raw_post
/fastlio_odom
/fastlio_pc
/Laser_map
/utlidar/imu_livox_mid360
/utlidar/cloud_livox_mid360
/path
/pose
/tf
/tf_static
/visibility_cleanup_map
```

If there is no live MID360 data, the nodes still start, but FAST-LIO and elevation mapping will not publish meaningful map updates until `/utlidar/cloud_livox_mid360`, `/utlidar/imu_livox_mid360` and the TF chain are available.

## Run individual components

### Run elevation_mapping directly

Direct node execution is useful only for low-level debugging because it does not load the humanoid YAML by itself:

```bash
ros2 run elevation_mapping elevation_mapping
```

For the humanoid setup, prefer:

```bash
ros2 launch elevation_mapping livox_elevation_mapping.launch.py
```

### Run visualization only

```bash
ros2 launch elevation_mapping visualization.launch.py
```

This starts `grid_map_visualization` for raw/fused maps with:

```text
elevation_mapping/config/visualization/raw.yaml
elevation_mapping/config/visualization/fused.yaml
```

It does not start RViz by itself. The full humanoid launch starts RViz when `rviz:=true`.

### Run FAST-LIO only

```bash
ros2 launch fast_lio mapping.launch.py \
  config_file:=mid360.yaml \
  rviz:=false
```

`mid360.yaml` is configured for the humanoid pipeline:

```text
lid_topic: /utlidar/cloud_livox_mid360
imu_topic: /utlidar/imu_livox_mid360
cloud_deskewed_topic: /fastlio_pc
odometry_topic: /fastlio_odom
odom_frame: odom_torso
body_frame: torso_link
```

## Typical robot startup order

Use the full launch when possible:

```bash
# Terminal 1: Livox driver, if it is not launched elsewhere.
source /opt/ros/<ROS_DISTRO>/setup.bash
source /path/to/livox_ros_driver2/install/setup.bash
ros2 launch livox_ros_driver2 rviz_MID360_launch.py
```

```bash
# Terminal 2: humanoid elevation mapping pipeline.
cd /home/ant/Robots/elevation_mapping
source /opt/ros/<ROS_DISTRO>/setup.bash
source /path/to/livox_ros_driver2/install/setup.bash
source install/setup.bash
ros2 launch elevation_mapping livox_elevation_mapping.launch.py
```

Check live inputs:

```bash
ros2 topic hz /utlidar/cloud_livox_mid360
ros2 topic hz /utlidar/imu_livox_mid360
ros2 run tf2_ros tf2_echo odom_torso torso_link
```

Check map outputs:

```bash
ros2 topic hz /cloud_registered
ros2 topic hz /cloud_registered/filtered
ros2 topic hz /pose
ros2 topic hz /elevation_map
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

The following commands were verified on this machine with ROS2 Humble.

Build the current ROS2 humanoid stack:

```bash
cd /home/ant/Robots/elevation_mapping
source /opt/ros/humble/setup.bash

colcon build \
  --packages-select fast_lio pose_publisher elevation_mapping_demos elevation_mapping \
  --cmake-args -DBUILD_TESTING=OFF
```

Expected result:

```text
Summary: 4 packages finished
```

Check the full launch arguments:

```bash
source /opt/ros/humble/setup.bash
source /home/ant/Robots/elevation_mapping/install/setup.bash
ros2 launch elevation_mapping livox_elevation_mapping.launch.py --show-args
```

Smoke launch without RViz and without visualization:

```bash
source /opt/ros/humble/setup.bash
source /home/ant/Robots/elevation_mapping/install/setup.bash

timeout 8s ros2 launch elevation_mapping livox_elevation_mapping.launch.py \
  rviz:=false \
  start_visualization:=false
```

Expected startup includes:

```text
process started: fastlio_mapping
process started: pc_filter.py
process started: pose_publisher
process started: elevation_mapping
Elevation mapping node started.
Configured pointcloud:front @ /cloud_registered/filtered
Filtering /cloud_registered -> /cloud_registered/filtered; target_frame=torso_link; z <= -0.5
Successfully launched node.
```

`timeout` exit code `124` is expected for smoke tests because the launch is intentionally stopped after a few seconds.

Verify discovered ROS2 executables:

```bash
ros2 pkg executables elevation_mapping_demos | sort
ros2 pkg executables fast_lio | sort
```

Expected relevant executables:

```text
elevation_mapping_demos pc_filter.py
fast_lio fastlio_mapping
```
