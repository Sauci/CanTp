cmake_minimum_required(VERSION 3.13.0)

project(CanTp VERSION 0.1.0 LANGUAGES C)

# general user options.
option(enable_test "enable/add test-related target(s) of CanTp module." ON)
option(enable_code_coverage "build unit test target(s) with code coverage options." ON)

set(can_tp_config ${CMAKE_CURRENT_SOURCE_DIR}/config/CanTp.json)
set(can_tp_source ${CMAKE_CURRENT_SOURCE_DIR}/source/CanTp.c)
set(can_tp_header ${CMAKE_CURRENT_SOURCE_DIR}/interface/CanTp.h)

find_package(PythonInterp 3 REQUIRED)

add_library(CanTp STATIC ${can_tp_source})

target_compile_definitions(CanTp
    PRIVATE CANTP_MAX_NUM_OF_CHANNEL=16
    PRIVATE CANTP_MAX_NUM_OF_N_SDU=16
    PRIVATE CANTP_DEV_ERROR_DETECT=STD_ON
    PRIVATE CANTP_SW_VERSION_MAJOR=${PROJECT_VERSION_MAJOR}
    PRIVATE CANTP_SW_VERSION_MINOR=${PROJECT_VERSION_MINOR}
    PRIVATE CANTP_SW_VERSION_PATCH=${PROJECT_VERSION_PATCH}
    PUBLIC CANTP_API=STD_ON
    PUBLIC CANTP_INIT_API=STD_ON
    PUBLIC CANTP_GET_VERSION_INFO_API=STD_ON
    PUBLIC CANTP_SHUTDOWN_API=STD_ON
    PUBLIC CANTP_TRANSMIT_API=STD_ON
    PUBLIC CANTP_CANCEL_TRANSMIT_API=STD_ON
    PUBLIC CANTP_CANCEL_RECEIVE_API=STD_ON
    PUBLIC CANTP_CHANGE_PARAMETER_API=STD_ON
    PUBLIC CANTP_READ_PARAMETER_API=STD_ON)

target_include_directories(CanTp
    PUBLIC interface
    PUBLIC $<$<BOOL:${enable_test}>:${CMAKE_BINARY_DIR}>
    INTERFACE stub)

add_custom_command(OUTPUT ${CMAKE_BINARY_DIR}/CanTp_Cfg.h
    DEPENDS ${can_tp_config}
    COMMAND ${PYTHON_EXECUTABLE} main.py ${can_tp_config}
    -header ${CMAKE_BINARY_DIR}/CanTp_Cfg.h
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/c_gen/can_tp
    COMMENT "generating interface code")

add_custom_command(OUTPUT ${CMAKE_BINARY_DIR}/CanTp_Cfg.c
    DEPENDS ${can_tp_config}
    COMMAND ${PYTHON_EXECUTABLE} main.py ${can_tp_config}
    -source ${CMAKE_BINARY_DIR}/CanTp_Cfg.c
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/c_gen/can_tp
    COMMENT "generating source code")

add_library(CanTp_Cfg STATIC ${CMAKE_BINARY_DIR}/CanTp_Cfg.c ${CMAKE_BINARY_DIR}/CanTp_Cfg.h)

target_include_directories(CanTp_Cfg
    PUBLIC interface
    PUBLIC stub)

if (${enable_test})
    target_compile_definitions(CanTp
        PUBLIC CANTP_BUILD_CFFI_INTERFACE=STD_ON)

    add_custom_target(can_tp_install
        COMMAND ${PYTHON_EXECUTABLE} setup.py install
        WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/c_gen)

    enable_testing()

    execute_process(COMMAND ${PYTHON_EXECUTABLE} setup.py install
        WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/c_gen)

    execute_process(COMMAND ${CMAKE_COMMAND} -E remove_directory build
        COMMAND ${CMAKE_COMMAND} -E remove_directory can_tp.egg-info
        COMMAND ${CMAKE_COMMAND} -E remove_directory dist
        WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/c_gen)

    add_library(Stub INTERFACE)
    target_include_directories(CanTp PRIVATE stub)

    target_link_libraries(CanTp INTERFACE Stub)

    add_test(NAME CanTp_UnitTest
        COMMAND ${CMAKE_COMMAND} -E env PYTHONPATH=${CMAKE_CURRENT_SOURCE_DIR}/c_gen
            ${PYTHON_EXECUTABLE} -m pytest ${CMAKE_CURRENT_SOURCE_DIR}/test/unit_test
        --junitxml=./report/ut.xml
        WORKING_DIRECTORY ${CMAKE_BINARY_DIR})

    add_test(NAME CanTp_FuncTest
        COMMAND ${PYTHON_EXECUTABLE} -m behave test/func_test --junit-directory=./report --junit
        WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR})

    set_tests_properties(CanTp_UnitTest PROPERTIES DEPENDS sdist_install)
    set_tests_properties(CanTp_FuncTest PROPERTIES DEPENDS sdist_install)

    get_target_property(can_tp_compile_definitions CanTp COMPILE_DEFINITIONS)
    get_target_property(can_tp_include_directories CanTp INCLUDE_DIRECTORIES)

    configure_file(config/cffi_config.py.in ${CMAKE_CURRENT_SOURCE_DIR}/test/ffi/cffi_config.py)
endif ()
