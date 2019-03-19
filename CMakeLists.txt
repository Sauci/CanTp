cmake_minimum_required(VERSION 3.13.0)

project(CanTp VERSION 0.1.0 LANGUAGES C CXX)

option(cantp_standalone "build module in a standalone fashion." ON)
option(enable_unit_test "build unit test target(s) of CanTp module." OFF)
option(enable_code_coverage "build unit test target(s) with code coverage options." OFF)
option(enable_python_wrapper "generates code to wrap library into python module." ON)

set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)

include_directories($<$<BOOL:${cantp_standalone}>:${CMAKE_CURRENT_SOURCE_DIR}/stub>)

add_library(CanTp STATIC source/CanTp.c source/CanTp_PBcfg.c)

target_compile_definitions(CanTp
    PUBLIC $<$<BOOL:${enable_python_wrapper}>:CANTP_SWIG_ENABLE>
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

if (${enable_python_wrapper})

    find_package(SWIG 3 REQUIRED)
    find_package(PythonInterp 3 REQUIRED)
    find_package(PythonLibs REQUIRED)

    include(${SWIG_USE_FILE})

    add_library(CanIf SHARED stub/CanIf.c)
    target_include_directories(CanIf PUBLIC stub)
    set_property(TARGET CanIf PROPERTY POSITION_INDEPENDENT_CODE ON)

    swig_add_library(pycantp
        TYPE SHARED
        LANGUAGE python
        OUTPUT_DIR ${CMAKE_BINARY_DIR}/swig/pycantp
        OUTFILE_DIR ${CMAKE_BINARY_DIR}/swig/pycantp
        SOURCES ${CMAKE_SOURCE_DIR}/swig/CanTp.i
        source/CanTp.c source/CanTp_PBcfg.c)
    target_include_directories(pycantp
        PUBLIC ${CMAKE_SOURCE_DIR}/interface
        PUBLIC ${CMAKE_SOURCE_DIR}/stub
        PUBLIC ${PYTHON_INCLUDE_DIRS})
    target_link_libraries(pycantp
        PUBLIC ${PYTHON_LIBRARIES})
    set_property(TARGET pycantp PROPERTY POSITION_INDEPENDENT_CODE ON)

    target_sources(pycantp
        PUBLIC stub/CanIf.c
        PUBLIC stub/Det.c
        PUBLIC stub/PduR.c)

    add_custom_command(TARGET pycantp POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy
        ${CMAKE_LIBRARY_OUTPUT_DIRECTORY}/$<TARGET_FILE_NAME:pycantp>
        ${CMAKE_BINARY_DIR}/swig/pycantp/_pycantp.so)

    configure_file(${CMAKE_SOURCE_DIR}/swig/__init__.py.in ${CMAKE_BINARY_DIR}/swig/pycantp/__init__.py)
    configure_file(${CMAKE_SOURCE_DIR}/swig/setup.py.in ${CMAKE_BINARY_DIR}/swig/setup.py)

    add_custom_target(build
        DEPENDS pycantp
        COMMAND ${PYTHON_EXECUTABLE} setup.py build
        COMMAND ${PYTHON_EXECUTABLE} setup.py sdist
        COMMAND ${PYTHON_EXECUTABLE} setup.py install
        WORKING_DIRECTORY ${CMAKE_BINARY_DIR}/swig)

endif ()

if (${enable_unit_test})
    include(FetchContent)
    fetchcontent_declare(googletest
        GIT_REPOSITORY https://github.com/google/googletest.git
        GIT_TAG release-1.8.1)
    fetchcontent_makeavailable(googletest)
    include_directories(${googletest_SOURCE_DIR}/googletest/include)
    include_directories(${googletest_SOURCE_DIR}/googlemock/include)
    set(GTEST_LIBRARIES gtest_main)
    set(GMOCK_LIBRARIES gmock_main)

    if (${enable_code_coverage})
        include(CodeCoverage.cmake)
        setup_target_for_coverage_gcovr_html(NAME coverage EXECUTABLE CanTp_UnitTest)
        #set(COVERAGE_GCOVR_EXCLUDES ${googletest_SOURCE_DIR})
        add_compile_options($<$<C_COMPILER_ID:AppleClang>:-fprofile-arcs>
            $<$<C_COMPILER_ID:AppleClang>:-ftest-coverage>
            $<$<C_COMPILER_ID:Clang>:-fprofile-instr-generate>
            $<$<C_COMPILER_ID:Clang>:-fcoverage-mapping>
            $<$<C_COMPILER_ID:GNU>:--coverage>
            $<$<C_COMPILER_ID:GNU>:-fprofile-arcs>
            $<$<C_COMPILER_ID:GNU>:-ftest-coverage>)
    endif ()

    add_subdirectory(unit_test)
endif ()
