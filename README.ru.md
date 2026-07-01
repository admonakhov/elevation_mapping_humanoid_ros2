# Elevation Mapping Humanoid ROS2

Русская документация. Английская документация доступна в [README.md](README.md).

Это ROS2 workspace для построения elevation map гуманоидного робота по данным LiDAR, IMU и odometry. Основной стек `elevation_mapping` портирован на ROS2 и собирается через `colcon`.

Проект основан на:

- Robot-Centric Elevation Mapping: https://github.com/ANYbotics/elevation_mapping
- FAST-LIO / FAST-LIO2 для LiDAR-inertial odometry
- Grid Map
- kindr / kindr_ros

## Текущий состав workspace

Активные ROS2 пакеты:

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

Важно:

- `elevation_mapping` собирается и запускается под ROS2.
- `fast_lio` находится в директории `fast_lio_mid360` и требует `livox_ros_driver2`.
- Старые ROS1/catkin-only пакеты и RViz1 plugins удалены.
- Старый дубликат `FAST_LIO_ROS2` удалён. Активный FAST-LIO пакет теперь только `fast_lio_mid360`.

## Требования

Ожидаемое окружение:

- Ubuntu с ROS2, установленным в `/opt/ros/<ROS_DISTRO>`
- `colcon`
- системный Python `/usr/bin/python3`

Установить основные зависимости, заменив `<ROS_DISTRO>` на имя целевого ROS2 дистрибутива:

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

Для `fast_lio` дополнительно нужен ROS2 драйвер Livox:

```text
livox_ros_driver2
```

Если `livox_ros_driver2` не установлен/не собран, собирай и проверяй `elevation_mapping` отдельно, без `fast_lio`.

## Важное про conda

На машинах с активной conda conda может ломать ROS2-сборку:

- ament может подхватить conda Python вместо `/usr/bin/python3`;
- conda `curl-config` может привести к linker errors с `libcurl`, `gdal`, `netcdf`;
- numpy из системного Python и conda Python могут конфликтовать.

Перед сборкой используй чистое ROS/system окружение:

```bash
source /opt/ros/<ROS_DISTRO>/setup.bash
export PATH=/opt/ros/<ROS_DISTRO>/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
export PYTHONPATH=/usr/lib/python3/dist-packages:${PYTHONPATH:-}
```

При необходимости явно передавай системный Python:

```bash
-DPython3_EXECUTABLE=/usr/bin/python3
```

## Сборка

### Важно про tests

В `kindr_ros` upstream test-файлы в этом vendored tree всё ещё ROS1-style (`geometry_msgs/Pose.h`, `geometry_msgs/Quaternion.h`, `tf::Transform`). Они отключены по умолчанию через:

```cmake
KINDR_ROS_BUILD_LEGACY_TESTS=OFF
```

Поэтому обычный `colcon build` больше не должен падать на ошибках:

```text
fatal error: geometry_msgs/Pose.h: No such file or directory
fatal error: geometry_msgs/Quaternion.h: No such file or directory
```

Если нужна только runtime-сборка без любых tests, можно дополнительно использовать:

```bash
--cmake-args -DBUILD_TESTING=OFF
```

Перейти в workspace:

```bash
cd /path/to/elevation_mapping_humanoid_ros2
```

Подготовить окружение:

```bash
source /opt/ros/<ROS_DISTRO>/setup.bash
export PATH=/opt/ros/<ROS_DISTRO>/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
export PYTHONPATH=/usr/lib/python3/dist-packages:${PYTHONPATH:-}
```

### Сборка только elevation_mapping стека

Это основной проверенный вариант, не требующий `livox_ros_driver2`:

```bash
colcon build \
  --packages-up-to elevation_mapping \
  --cmake-args \
    -DBUILD_TESTING=OFF \
    -DPython3_EXECUTABLE=/usr/bin/python3
```

После сборки:

```bash
source install/setup.bash
```

Проверка, что пакет виден ROS2:

```bash
ros2 pkg prefix elevation_mapping
ros2 pkg executables elevation_mapping
```

Ожидаемые executables:

```text
elevation_mapping elevation_mapping
elevation_mapping get_grid_map_client
elevation_mapping listener
```

### Сборка всех ROS2 пакетов без fast_lio

Если `livox_ros_driver2` ещё не установлен:

```bash
colcon build \
  --packages-skip fast_lio \
  --cmake-args \
    -DBUILD_TESTING=OFF \
    -DPython3_EXECUTABLE=/usr/bin/python3
```

### Сборка с fast_lio

Сначала собери и source `livox_ros_driver2`, затем собери этот workspace:

```bash
source /opt/ros/<ROS_DISTRO>/setup.bash
source /path/to/livox_ros_driver2/install/setup.bash
cd /path/to/elevation_mapping_humanoid_ros2

colcon build \
  --cmake-args \
    -DBUILD_TESTING=OFF \
    -DPython3_EXECUTABLE=/usr/bin/python3
```

Если CMake выдаёт:

```text
Could not find livox_ros_driver2Config.cmake
```

значит `livox_ros_driver2` не установлен или не был `source`-нут.

## Запуск elevation_mapping

Подготовить окружение:

```bash
cd /path/to/elevation_mapping_humanoid_ros2
source /opt/ros/<ROS_DISTRO>/setup.bash
source install/setup.bash
```

Запустить node напрямую:

```bash
ros2 run elevation_mapping elevation_mapping
```

Smoke-test без датчиков:

```bash
timeout 5s ros2 run elevation_mapping elevation_mapping \
  --ros-args \
  -p enable_visibility_cleanup:=false \
  -p fused_map_publishing_rate:=0.5
```

Ожидаемые сообщения:

```text
Elevation mapping node started.
Elevation map grid resized ...
Successfully launched node.
```

Предупреждение ниже нормально для запуска без входных point cloud источников:

```text
Not registering any callbacks, no input sources given. Did you configure the InputSourceManager?
```

Для реального робота нужно настроить `input_sources` и sensor processor YAML config под топики LiDAR/point cloud.

## Визуализация elevation map

Проверка launch-файла:

```bash
ros2 launch elevation_mapping visualization.launch.py --show-args
```

Запуск визуализации:

```bash
ros2 launch elevation_mapping visualization.launch.py
```

Этот launch стартует `grid_map_visualization` для raw/fused карт с конфигами:

```text
elevation_mapping/config/visualization/raw.yaml
elevation_mapping/config/visualization/fused.yaml
```

Проверить топики:

```bash
ros2 topic list | grep -E 'elevation|grid|map'
```

Основные ожидаемые топики:

```text
/elevation_map
/elevation_map_raw_post
/visibility_cleanup_map
```

Посмотреть один message:

```bash
ros2 topic echo /elevation_map --once
```

## Запуск fast_lio для MID360

Пакет `fast_lio` находится здесь:

```text
fast_lio_mid360
```

Launch-файл:

```text
fast_lio_mid360/launch/mapping.launch.py
```

Проверить аргументы:

```bash
ros2 launch fast_lio mapping.launch.py --show-args
```

Запуск MID360 config с RViz:

```bash
ros2 launch fast_lio mapping.launch.py \
  config_file:=mid360.yaml \
  rviz:=true
```

Без RViz:

```bash
ros2 launch fast_lio mapping.launch.py \
  config_file:=mid360.yaml \
  rviz:=false
```

Доступные configs:

```text
fast_lio_mid360/config/mid360.yaml
fast_lio_mid360/config/mid360_mr.yaml
fast_lio_mid360/config/avia.yaml
fast_lio_mid360/config/horizon.yaml
fast_lio_mid360/config/ouster64.yaml
fast_lio_mid360/config/velodyne.yaml
fast_lio_mid360/config/velodyne_mr.yaml
```

Важно: `fast_lio` не соберётся и не запустится для MID360 без `livox_ros_driver2`.

## Типовой порядок запуска на роботе

Используй разные терминалы.

### Терминал 1: Livox driver

```bash
source /opt/ros/<ROS_DISTRO>/setup.bash
source /path/to/livox_ros_driver2/install/setup.bash
ros2 launch livox_ros_driver2 rviz_MID360_launch.py
```

Проверить cloud topic:

```bash
ros2 topic list | grep -E 'livox|point|cloud'
ros2 topic hz /livox/lidar
```

### Терминал 2: FAST-LIO

```bash
cd /path/to/elevation_mapping_humanoid_ros2
source /opt/ros/<ROS_DISTRO>/setup.bash
source /path/to/livox_ros_driver2/install/setup.bash
source install/setup.bash

ros2 launch fast_lio mapping.launch.py config_file:=mid360.yaml rviz:=false
```

Проверить odometry/map topics:

```bash
ros2 topic list | grep -E 'odom|cloud|path|lio|map'
```

### Терминал 3: elevation_mapping

```bash
cd /path/to/elevation_mapping_humanoid_ros2
source /opt/ros/<ROS_DISTRO>/setup.bash
source install/setup.bash

ros2 run elevation_mapping elevation_mapping
```

### Терминал 4: визуализация

```bash
cd /path/to/elevation_mapping_humanoid_ros2
source /opt/ros/<ROS_DISTRO>/setup.bash
source install/setup.bash

ros2 launch elevation_mapping visualization.launch.py
```

## Настройка под своего робота

Минимально проверить и настроить:

1. TF tree:

```bash
ros2 run tf2_ros tf2_echo odom base_link
ros2 run tf2_ros tf2_echo base_link livox_frame
```

2. Frame IDs в configs:

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

4. Если `elevation_mapping` пишет, что input sources не настроены, нужно добавить/исправить `input_sources` в YAML config elevation_mapping под реальные топики point cloud.

## Проверенные команды

Сборка `elevation_mapping`:

```text
Summary: 3 packages finished
```

Проверка launch parse:

```bash
ros2 launch elevation_mapping visualization.launch.py --show-args
```

Ожидаемый результат:

```text
Arguments:
  No arguments.
```

Smoke run node:

```bash
timeout 5s ros2 run elevation_mapping elevation_mapping \
  --ros-args \
  -p enable_visibility_cleanup:=false \
  -p fused_map_publishing_rate:=0.5
```

Node стартует, публикует topics, затем останавливается по `timeout`.
