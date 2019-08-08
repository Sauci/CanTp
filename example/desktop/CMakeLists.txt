include(ExternalProject)

ExternalProject_Add(can_tp
    GIT_REPOSITORY "https://github.com/Sauci/CanTp.git"
    GIT_TAG "develop"
    UPDATE_COMMAND ""
    PATCH_COMMAND ""
    TEST_COMMAND ""
    INSTALL_COMMAND ""
    SOURCE_DIR "${CMAKE_BINARY_DIR}/can_tp"
    BINARY_DIR "${CMAKE_BINARY_DIR}/iso_tp"
    CMAKE_ARGS -DENABLE_DET=0 -DENABLE_TEST=1)

add_library(iso_tp source/iso_tp.cpp)
target_include_directories(iso_tp PUBLIC interface)
target_link_libraries(iso_tp PUBLIC CanTp)

add_executable(iso_tp_c source/main.cpp)
target_link_libraries(iso_tp_c iso_tp)
