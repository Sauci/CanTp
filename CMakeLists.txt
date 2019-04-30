cmake_minimum_required(VERSION 3.13.0)

project(CanTp VERSION 0.1.0 LANGUAGES C CXX)


option(enable_test "enable/add test-related target(s) of CanTp module." ON)
option(enable_code_coverage "build unit test target(s) with code coverage options." ON)
option(enable_python_wrapper "generates code to wrap library into python module." ON)

file(MAKE_DIRECTORY ${CMAKE_BINARY_DIR}/python)

set(CMAKE_MACOSX_RPATH ON)
set(CMAKE_INSTALL_RPATH ${CMAKE_LIBRARY_OUTPUT_DIRECTORY})

add_library(CanTp STATIC source/CanTp.c source/CanTp_PBcfg.c)

target_compile_definitions(CanTp
    PUBLIC CANTP_API=STD_ON
    PUBLIC CANTP_INIT_API=STD_ON
    PUBLIC CANTP_GET_VERSION_INFO_API=STD_ON
    PUBLIC CANTP_SHUTDOWN_API=STD_ON
    PUBLIC CANTP_TRANSMIT_API=STD_ON
    PUBLIC CANTP_CANCEL_TRANSMIT_API=STD_ON
    PUBLIC CANTP_CANCEL_RECEIVE_API=STD_ON
    PUBLIC CANTP_CHANGE_PARAMETER_API=STD_ON
    PUBLIC CANTP_READ_PARAMETER_API=STD_ON)

target_include_directories(CanTp PUBLIC interface)

if (${enable_test})
    enable_testing()
    find_package(PythonInterp 3 REQUIRED)

    include_directories(${CMAKE_CURRENT_SOURCE_DIR}/stub)

    add_library(CanIf INTERFACE)
    target_include_directories(CanIf INTERFACE stub)

    add_library(Det INTERFACE)
    target_include_directories(Det INTERFACE stub)

    add_library(PduR INTERFACE)
    target_include_directories(PduR INTERFACE stub)

    target_compile_definitions(CanTp PUBLIC $<$<BOOL:${enable_python_wrapper}>:CANTP_CFFI_ENABLE>)

    target_link_libraries(CanTp INTERFACE CanIf Det PduR)

    add_custom_command(OUTPUT ${CMAKE_CURRENT_SOURCE_DIR}/python/pycantp/input/source.c
        COMMAND pcpp ${CMAKE_CURRENT_SOURCE_DIR}/source/CanTp.c
        "-D$<JOIN:$<TARGET_PROPERTY:CanTp,COMPILE_DEFINITIONS>,;-D>"
        -DCANTP_BUILD_CFFI_INTERFACE
        "-I$<JOIN:$<TARGET_PROPERTY:CanTp,INCLUDE_DIRECTORIES>,;-I>"
        --line-directive -o ${CMAKE_CURRENT_SOURCE_DIR}/python/pycantp/input/source.c
        COMMAND_EXPAND_LISTS
        COMMENT "preprocessing cffi source"
        VERBATIM)

    add_custom_command(OUTPUT ${CMAKE_CURRENT_SOURCE_DIR}/python/pycantp/input/header.h
        COMMAND pcpp ${CMAKE_CURRENT_SOURCE_DIR}/interface/CanTp.h
        "-D$<JOIN:$<TARGET_PROPERTY:CanTp,COMPILE_DEFINITIONS>,;-D>"
        -DCANTP_BUILD_CFFI_INTERFACE
        "-I$<JOIN:$<TARGET_PROPERTY:CanTp,INCLUDE_DIRECTORIES>,;-I>"
        --line-directive -o ${CMAKE_CURRENT_SOURCE_DIR}/python/pycantp/input/header.h
        COMMAND_EXPAND_LISTS
        COMMENT "preprocessing cffi header"
        VERBATIM)

    add_custom_target(sdist
        DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/python/pycantp/input/source.c
        DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/python/pycantp/input/header.h
        COMMAND ${CMAKE_COMMAND} -E copy_directory ${CMAKE_CURRENT_SOURCE_DIR}/python
        ${CMAKE_BINARY_DIR}/python
        COMMAND ${PYTHON_EXECUTABLE} setup.py sdist -d ${CMAKE_BINARY_DIR}
        WORKING_DIRECTORY ${CMAKE_BINARY_DIR}/python
        COMMENT "building python source distribution package")

    add_custom_target(sdist_install
        DEPENDS sdist
        COMMAND ${PYTHON_EXECUTABLE} -m pip install ./*.tar.gz
        COMMENT "installing python source distribution package"
        WORKING_DIRECTORY ${CMAKE_BINARY_DIR})

    add_test(NAME CanTp_UnitTest
        COMMAND ${PYTHON_EXECUTABLE} -m pytest test/unit_test --junitxml=./report/ut.xml
        WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR})

    set_tests_properties(CanTp_UnitTest PROPERTIES DEPENDS sdist_install)
endif ()
