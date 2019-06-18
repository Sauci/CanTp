cmake_minimum_required(VERSION 3.8.0)

project(CanTp VERSION 0.1.0 LANGUAGES C)

# if set, the module will be compiled with developement error detection (AUTOSAR's Det module)
# enabled.
# by default, developement error detection is enabled.
option(enable_det "enable/disable developement error detection feature." ON)

# if set, the module is built for testing purposes, which means:
# - the compiler definition CANTP_BUILD_CFFI_INTERFACE is set
# - the stubbed headers are used instead of user-provided headers
# if not set, the user is responsible of providing the required headers (CanIf.h, ComStack_Types.h,
# Det.h, PduR.h and Std_Types.h, see AUTOSAR's CanTp software specification).
# by default, tests are enabled.
option(enable_test "enable/disable tests." ON)

# can_tp_cfg_in defines the default configuration file used to generate the auto-generated code of
# the module (CanTp_Cfg.c and CanTp_Cfg.h).
# by default, it uses the file located at ./config/CanTp.json.
set(can_tp_cfg_in ${CMAKE_CURRENT_SOURCE_DIR}/config/CanTp.json)

# can_tp_cfg_out defines the output folder of all auto-generated files.
# by default, it is located in the 'generated' folder, in the default CMake's binary directory.
set(can_tp_cfg_out ${CMAKE_BINARY_DIR}/generated)



execute_process(COMMAND ${CMAKE_COMMAND} -E make_directory ${can_tp_cfg_out})

# find a distribution of Python 3. Python is used for:
# - generation of the static configuration sources (CanTp_Cfg.c and CanTp_Cfg.h)
# - running the tests
find_package(PythonInterp 3 REQUIRED)

add_custom_target(can_tp_gen_install
    COMMAND ${PYTHON_EXECUTABLE} setup.py install
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/c_gen
    COMMENT "installing CanTp code generator for python located at ${PYTHON_EXECUTABLE}")

add_custom_command(OUTPUT ${can_tp_cfg_out}/CanTp_Cfg.h
    DEPENDS can_tp_gen_install
    DEPENDS ${can_tp_cfg_in}
    COMMAND ${PYTHON_EXECUTABLE} -m can_tp ${can_tp_cfg_in} -header ${can_tp_cfg_out}/CanTp_Cfg.h
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/c_gen/can_tp
    COMMENT "generating configuration header")

add_custom_command(OUTPUT ${can_tp_cfg_out}/CanTp_Cfg.c
    DEPENDS can_tp_gen_install
    DEPENDS ${can_tp_cfg_out}/CanTp_Cfg.h
    DEPENDS ${can_tp_cfg_in}
    COMMAND ${PYTHON_EXECUTABLE} -m can_tp ${can_tp_cfg_in} -source ${can_tp_cfg_out}/CanTp_Cfg.c
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/c_gen/can_tp
    COMMENT "generating configuration source")

add_library(CanTp_Cfg STATIC ${can_tp_cfg_out}/CanTp_Cfg.c)

target_include_directories(CanTp_Cfg
    PUBLIC interface
    PUBLIC $<$<BOOL:${enable_test}>:${CMAKE_CURRENT_SOURCE_DIR}/stub>)

add_library(${PROJECT_NAME} STATIC source/CanTp.c)

target_compile_definitions(${PROJECT_NAME}
    PRIVATE CANTP_MAX_NUM_OF_CHANNEL=16
    PRIVATE CANTP_MAX_NUM_OF_N_SDU=16
    PRIVATE CANTP_DEV_ERROR_DETECT=$<IF:$<BOOL:${enable_det}>,STD_ON,STD_OFF>
    PRIVATE CANTP_SW_VERSION_MAJOR=${PROJECT_VERSION_MAJOR}
    PRIVATE CANTP_SW_VERSION_MINOR=${PROJECT_VERSION_MINOR}
    PRIVATE CANTP_SW_VERSION_PATCH=${PROJECT_VERSION_PATCH}
    PUBLIC CANTP_API=STD_ON
    # ECUC_CanTp_00283
    PUBLIC CANTP_GET_VERSION_INFO_API=STD_ON
    # ECUC_CanTp_00299
    PUBLIC CANTP_CHANGE_PARAMETER_API=STD_ON
    # ECUC_CanTp_00300
    PUBLIC CANTP_READ_PARAMETER_API=STD_ON
    PUBLIC CANTP_BUILD_CFFI_INTERFACE=$<IF:$<BOOL:${enable_test}>,STD_ON,STD_OFF>)

target_include_directories(${PROJECT_NAME}
    PUBLIC interface
    PUBLIC $<$<BOOL:${enable_test}>:${can_tp_cfg_out}>
    PUBLIC $<$<BOOL:${enable_test}>:${CMAKE_CURRENT_SOURCE_DIR}/stub>)

if (${enable_test})
    enable_testing()

    target_link_libraries(${PROJECT_NAME}
        PUBLIC CanTp_Cfg)

    add_test(NAME CanTp_UnitTest
        COMMAND ${PYTHON_EXECUTABLE} -m pytest ${CMAKE_CURRENT_SOURCE_DIR}/test
        --junitxml=./report/ut.xml
        WORKING_DIRECTORY ${CMAKE_BINARY_DIR})

    set_tests_properties(CanTp_UnitTest PROPERTIES DEPENDS can_tp_gen_install)

    configure_file(config/cffi_config.py.in ${CMAKE_BINARY_DIR}/cffi_config.tmp.py)

    file(GENERATE
        OUTPUT ${CMAKE_CURRENT_SOURCE_DIR}/test/ffi/cffi_config.py
        INPUT ${CMAKE_BINARY_DIR}/cffi_config.tmp.py)
endif ()
