cmake_minimum_required(VERSION 3.8.0)

project(CanTp VERSION 0.1.0 LANGUAGES C)

set(AUTOSAR_STD_HEADER_PATH ${CMAKE_CURRENT_SOURCE_DIR}/test/stub/common CACHE FILEPATH
    "path to directory containing Std_Types.h and ComStack_Types.h.")
set(CANTP_CONFIG_FILEPATH ${CMAKE_CURRENT_SOURCE_DIR}/config/can_tp.json CACHE FILEPATH
    "path to configuration file used to generate post-build configuration.")
option(CANTP_ENABLE_TEST "enables/disables tests." OFF)
option(ENABLE_DET "enables/disables development error detection." ON)
option(ENABLE_DOC_GEN "enables/disables documentation generation." OFF)
option(ENABLE_PC_LINT "enables/disables static code analysis." OFF)
set(MISRA_C_VERSION 2012 CACHE STRING "MISRA standard.")
option(OS_GET_TIME_API "indicates whether the OSEK API GetTime is available or not." OFF)

find_package(PythonInterp 3.6 REQUIRED)

if (${ENABLE_DOC_GEN})
    find_package(Doxygen REQUIRED dot)

    set(DOXYGEN_OUTPUT_DIRECTORY ${PROJECT_SOURCE_DIR}/doc)

    doxygen_add_docs(${PROJECT_NAME}.doc source interface COMMENT "generating CanTp documentation")
endif ()

add_subdirectory(extern)
add_subdirectory(generated)

add_library(CanTp STATIC source/CanTp.c)

target_compile_definitions(CanTp
    PRIVATE CANTP_DEV_ERROR_DETECT=$<IF:$<BOOL:${ENABLE_DET}>,STD_ON,STD_OFF>
    PRIVATE CANTP_SW_VERSION_MAJOR=${PROJECT_VERSION_MAJOR}
    PRIVATE CANTP_SW_VERSION_MINOR=${PROJECT_VERSION_MINOR}
    PRIVATE CANTP_SW_VERSION_PATCH=${PROJECT_VERSION_PATCH}
    PUBLIC CANTP_AR_RELEASE_MAJOR_VERSION=4 # SWS_BSW_00059
    PUBLIC CANTP_AR_RELEASE_MINOR_VERSION=4
    PUBLIC CANTP_API=STD_ON
    PUBLIC CANTP_GET_VERSION_INFO_API=STD_ON # ECUC_CanTp_00283
    PUBLIC CANTP_CHANGE_PARAMETER_API=STD_ON # ECUC_CanTp_00299
    PUBLIC CANTP_READ_PARAMETER_API=STD_ON # ECUC_CanTp_00300
    PUBLIC OS_GET_TIME_API=$<IF:$<BOOL:${OS_GET_TIME_API}>,STD_ON,STD_OFF>)

target_include_directories(CanTp
    PUBLIC interface
    PUBLIC ${AUTOSAR_STD_HEADER_PATH}
    PUBLIC $<$<BOOL:${CANTP_ENABLE_TEST}>:${CMAKE_CURRENT_SOURCE_DIR}/test/stub>)

if (${CANTP_ENABLE_TEST})
    enable_testing()

    add_test(NAME CanTp_UnitTest
        COMMAND ${PYTHON_EXECUTABLE} -W ignore::DeprecationWarning
        -m pytest ${CMAKE_CURRENT_SOURCE_DIR}/test
        --build_directory ${CMAKE_BINARY_DIR}
        --script_directory ${PROJECT_SOURCE_DIR}/script
        --header ${PROJECT_SOURCE_DIR}/interface/CanTp.h
        --source ${PROJECT_SOURCE_DIR}/source/CanTp.c
        --compile_definitions $<JOIN:$<TARGET_PROPERTY:CanTp,COMPILE_DEFINITIONS>,$<SEMICOLON>>
        --include_directories $<JOIN:$<TARGET_PROPERTY:CanTp,INCLUDE_DIRECTORIES>,$<SEMICOLON>>
        --junitxml=./report/${PROJECT_NAME}.xml
        WORKING_DIRECTORY ${CMAKE_BINARY_DIR})
endif ()

if (${ENABLE_PC_LINT})
    add_pc_lint_target(NAME CanTp
        DEPENDENCIES ${CMAKE_CURRENT_SOURCE_DIR}/generated/CanTp_PBcfg.h
        OUTPUT_LOG ${CMAKE_CURRENT_SOURCE_DIR}/${PROJECT_NAME}.lnt.log
        EXCLUDE_DIRECTORIES
        ${AUTOSAR_STD_HEADER_PATH}
        OPTION_FILES
        ${CMAKE_CURRENT_SOURCE_DIR}/extern/lint/MISRA${MISRA_C_VERSION}.lnt
        ${CMAKE_CURRENT_SOURCE_DIR}/config/CanTp.lnt)
endif ()
