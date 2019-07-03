cmake_minimum_required(VERSION 3.8.0)

project(CanTp VERSION 0.1.0 LANGUAGES C)

option(ENABLE_DET "enable/disable developement error detection feature." ON)
option(ENABLE_TEST "enable/disable tests." ON)
option(ENABLE_SCA "enable/disable static code analysis." OFF)
set(MISRA_C_VERSION 2012 CACHE STRING "MISRA standard.")
set(CANTP_CONFIG_FILEPATH ${CMAKE_CURRENT_SOURCE_DIR}/config/can_tp.json CACHE FILEPATH "")

# find a distribution of Python 3. Python is used for:
# - generation of the static configuration sources (CanTp_Cfg.c and CanTp_Cfg.h)
# - running the tests
find_package(PythonInterp 3.6 REQUIRED)

if (${ENABLE_SCA})
    add_subdirectory(extern)
endif ()

add_subdirectory(generated)

add_library(${PROJECT_NAME} STATIC source/CanTp.c)

target_compile_definitions(${PROJECT_NAME}
    PRIVATE CANTP_MAX_NUM_OF_CHANNEL=16
    PRIVATE CANTP_MAX_NUM_OF_N_SDU=16
    PRIVATE CANTP_DEV_ERROR_DETECT=$<IF:$<BOOL:${ENABLE_DET}>,STD_ON,STD_OFF>
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
    PUBLIC CANTP_BUILD_CFFI_INTERFACE=$<IF:$<BOOL:${ENABLE_TEST}>,STD_ON,STD_OFF>)

target_include_directories(${PROJECT_NAME}
    PUBLIC interface
    PUBLIC $<$<BOOL:${ENABLE_TEST}>:${CMAKE_CURRENT_SOURCE_DIR}/generated>
    PUBLIC $<$<BOOL:${ENABLE_TEST}>:${CMAKE_CURRENT_SOURCE_DIR}/stub>)

if (${ENABLE_TEST})
    ENABLE_TESTing()

    target_link_libraries(${PROJECT_NAME}
        PUBLIC CanTp_Cfg)

    add_test(NAME CanTp_UnitTest
        COMMAND ${PYTHON_EXECUTABLE} -m pytest ${CMAKE_CURRENT_SOURCE_DIR}/test
        --junitxml=./report/ut.xml
        WORKING_DIRECTORY ${CMAKE_BINARY_DIR})

    configure_file(config/cffi_config.py.in ${CMAKE_BINARY_DIR}/cffi_config.tmp.py)

    file(GENERATE
        OUTPUT ${CMAKE_CURRENT_SOURCE_DIR}/test/ffi/cffi_config.py
        INPUT ${CMAKE_BINARY_DIR}/cffi_config.tmp.py)
endif ()

if (${ENABLE_SCA})
    add_pc_lint_target(NAME CanTp
        DEPENDENCIES ${CMAKE_CURRENT_SOURCE_DIR}/generated/CanTp_Cfg.h
        OUTPUT_LOG ${CMAKE_CURRENT_SOURCE_DIR}/${PROJECT_NAME}.lnt.log
        EXCLUDE_DIRECTORIES
        ${CMAKE_CURRENT_SOURCE_DIR}/stub
        OPTION_FILES
        ${CMAKE_CURRENT_SOURCE_DIR}/extern/lint/MISRA${MISRA_C_VERSION}.lnt
        ${CMAKE_CURRENT_SOURCE_DIR}/config/CanTp.lnt)
endif ()
