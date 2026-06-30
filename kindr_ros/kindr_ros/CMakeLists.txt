cmake_minimum_required(VERSION 3.8)
project(kindr_ros)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
add_compile_options(-Wall -Wextra -Wpedantic)

find_package(ament_cmake REQUIRED)
find_package(Eigen3 REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(kindr REQUIRED)
find_package(tf2 REQUIRED)

add_library(${PROJECT_NAME} INTERFACE)
target_include_directories(${PROJECT_NAME} INTERFACE
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include>
  ${EIGEN3_INCLUDE_DIR}
)
target_link_libraries(${PROJECT_NAME} INTERFACE Eigen3::Eigen)
ament_target_dependencies(${PROJECT_NAME} INTERFACE geometry_msgs kindr tf2)

install(DIRECTORY include/
  DESTINATION include
)

install(TARGETS ${PROJECT_NAME}
  EXPORT export_${PROJECT_NAME}
)

ament_export_targets(export_${PROJECT_NAME} HAS_LIBRARY_TARGET)
ament_export_include_directories(include)
ament_export_dependencies(Eigen3 geometry_msgs kindr tf2)

if(BUILD_TESTING)
  find_package(ament_cmake_gtest REQUIRED)
  ament_add_gtest(test_${PROJECT_NAME}
    test/test_main.cpp
    test/RosGeometryMsgPhysicalQuantitiesTest.cpp
    test/RosGeometryMsgRotationTest.cpp
    test/RosGeometryMsgPoseTest.cpp
    test/RosTfPoseTest.cpp
    test/TfConventionTest.cpp
    WORKING_DIRECTORY ${PROJECT_SOURCE_DIR}/test
  )
  if(TARGET test_${PROJECT_NAME})
    target_include_directories(test_${PROJECT_NAME} PRIVATE include ${EIGEN3_INCLUDE_DIR})
    target_link_libraries(test_${PROJECT_NAME} ${PROJECT_NAME})
    ament_target_dependencies(test_${PROJECT_NAME} geometry_msgs kindr tf2)
  endif()
endif()

ament_package()
