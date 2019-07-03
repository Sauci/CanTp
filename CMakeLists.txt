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

# if set, an additional target will be available to perform static code analysis with PC-Lint.
# by default, static code analysis is disabled.
option(enable_static_code_analysis "enable/disable static code analysis." OFF)

# can_tp_misra_c_version specifies which MISRA C version should be used when performing static code
# analysis with PC-Lint.
# the possible values are 1998, 2004 and 2012
# by default, the MISRA C version 2012 is used.
set(can_tp_misra_c_version 2012 CACHE STRING "MISRA standard.")

# can_tp_cfg_in defines the default configuration file used to generate the auto-generated code of
# the module (CanTp_Cfg.c and CanTp_Cfg.h).
# by default, it uses the file located at ./config/CanTp.json.
set(can_tp_cfg_in ${CMAKE_CURRENT_SOURCE_DIR}/config/CanTp.json CACHE FILEPATH "")

# find a distribution of Python 3. Python is used for:
# - generation of the static configuration sources (CanTp_Cfg.c and CanTp_Cfg.h)
# - running the tests
find_package(PythonInterp 3.6 REQUIRED)

add_subdirectory(generated)

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
    PUBLIC $<$<BOOL:${enable_test}>:${CMAKE_CURRENT_SOURCE_DIR}/generated>
    PUBLIC $<$<BOOL:${enable_test}>:${CMAKE_CURRENT_SOURCE_DIR}/stub>)

if (${enable_test})
    enable_testing()

    target_link_libraries(${PROJECT_NAME}
        PUBLIC CanTp_Cfg)

    add_test(NAME CanTp_UnitTest
        COMMAND ${CMAKE_COMMAND} -E env PYTHONPATH=${CMAKE_CURRENT_SOURCE_DIR}/generated/script
        ${PYTHON_EXECUTABLE} -m pytest ${CMAKE_CURRENT_SOURCE_DIR}/test
        --junitxml=./report/ut.xml --maxfail=1
        WORKING_DIRECTORY ${CMAKE_BINARY_DIR})

    configure_file(config/cffi_config.py.in ${CMAKE_BINARY_DIR}/cffi_config.tmp.py)

    file(GENERATE
        OUTPUT ${CMAKE_CURRENT_SOURCE_DIR}/test/ffi/cffi_config.py
        INPUT ${CMAKE_BINARY_DIR}/cffi_config.tmp.py)
endif ()

if (${enable_static_code_analysis})
    add_subdirectory(extern)
    add_pc_lint_target(NAME CanTp
        DEPENDENCIES ${CMAKE_CURRENT_SOURCE_DIR}/generated/CanTp_Cfg.h
        OUTPUT_LOG ${CMAKE_CURRENT_SOURCE_DIR}/${PROJECT_NAME}.lnt.log
        EXCLUDE_DIRECTORIES
        ${CMAKE_CURRENT_SOURCE_DIR}/stub
        OPTION_FILES
        ${CMAKE_CURRENT_SOURCE_DIR}/extern/lint/MISRA${can_tp_misra_c_version}.lnt
        ${CMAKE_CURRENT_SOURCE_DIR}/config/CanTp.lnt)
endif ()
