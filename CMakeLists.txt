cmake_minimum_required(VERSION 3.13.0)

project(CanTp VERSION 0.1.0 LANGUAGES C)


option(enable_test "enable/add test-related target(s) of CanTp module." ON)
option(enable_code_coverage "build unit test target(s) with code coverage options." ON)

find_package(PythonInterp 3 REQUIRED)

add_library(CanTp STATIC source/CanTp.c)

target_compile_definitions(CanTp
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

target_include_directories(CanTp PUBLIC interface)

add_custom_command(OUTPUT ${CMAKE_CURRENT_SOURCE_DIR}/interface/CanTp_Cfg.h
    DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/python/pycantp/template/config.c.mustache
    DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/python/pycantp/template/config.h.mustache
    DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/python/pycantp/template/config.schema.json
    DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/config/CanTp.json
    COMMAND ${PYTHON_EXECUTABLE} cli.py ${CMAKE_CURRENT_SOURCE_DIR}/config/CanTp.json
    -header ${CMAKE_CURRENT_SOURCE_DIR}/interface/CanTp_Cfg.h
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/python
    COMMENT "generating interface code")

add_custom_command(OUTPUT ${CMAKE_CURRENT_SOURCE_DIR}/source/CanTp_Cfg.c
    DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/python/pycantp/template/config.c.mustache
    DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/python/pycantp/template/config.h.mustache
    DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/python/pycantp/template/config.schema.json
    DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/config/CanTp.json
    COMMAND ${PYTHON_EXECUTABLE} cli.py ${CMAKE_CURRENT_SOURCE_DIR}/config/CanTp.json
    -source ${CMAKE_CURRENT_SOURCE_DIR}/source/CanTp_Cfg.c
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/python
    COMMENT "generating source code")

add_library(CanTp_Cfg STATIC source/CanTp_Cfg.c)

target_include_directories(CanTp_Cfg PUBLIC interface)

target_link_libraries(CanTp PRIVATE CanTp_Cfg)

if (${enable_test})
    enable_testing()

    include_directories(${CMAKE_CURRENT_SOURCE_DIR}/stub)

    add_library(CanIf INTERFACE)
    target_include_directories(CanIf INTERFACE stub)

    add_library(Det INTERFACE)
    target_include_directories(Det INTERFACE stub)

    add_library(PduR INTERFACE)
    target_include_directories(PduR INTERFACE stub)

    target_compile_definitions(CanTp PUBLIC $<$<BOOL:${enable_test}>:CANTP_CFFI_ENABLE>)

    target_link_libraries(CanTp INTERFACE CanIf Det PduR)

    add_custom_command(OUTPUT ${CMAKE_CURRENT_SOURCE_DIR}/python/pycantp/input/source.c
        DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/source/CanTp.c
        DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/interface/CanTp_Cfg.h
        COMMAND pcpp ${CMAKE_CURRENT_SOURCE_DIR}/source/CanTp.c
        "-D$<JOIN:$<TARGET_PROPERTY:CanTp,COMPILE_DEFINITIONS>,;-D>"
        -DCANTP_BUILD_CFFI_INTERFACE
        "-I$<JOIN:$<TARGET_PROPERTY:CanTp,INCLUDE_DIRECTORIES>,;-I>"
        --line-directive -o ${CMAKE_CURRENT_SOURCE_DIR}/python/pycantp/input/source.c
        COMMAND_EXPAND_LISTS
        COMMENT "preprocessing cffi source"
        VERBATIM)

    add_custom_command(OUTPUT ${CMAKE_CURRENT_SOURCE_DIR}/python/pycantp/input/config.c
        DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/source/CanTp_Cfg.c
        COMMAND pcpp ${CMAKE_CURRENT_SOURCE_DIR}/source/CanTp_Cfg.c
        "-D$<JOIN:$<TARGET_PROPERTY:CanTp,COMPILE_DEFINITIONS>,;-D>"
        -DCANTP_BUILD_CFFI_INTERFACE
        "-I$<JOIN:$<TARGET_PROPERTY:CanTp,INCLUDE_DIRECTORIES>,;-I>"
        --line-directive -o ${CMAKE_CURRENT_SOURCE_DIR}/python/pycantp/input/config.c
        COMMAND_EXPAND_LISTS
        COMMENT "preprocessing cffi config"
        VERBATIM)

    add_custom_command(OUTPUT ${CMAKE_CURRENT_SOURCE_DIR}/python/pycantp/input/header.h
        DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/interface/CanTp.h
        COMMAND pcpp ${CMAKE_CURRENT_SOURCE_DIR}/interface/CanTp.h
        "-D$<JOIN:$<TARGET_PROPERTY:CanTp,COMPILE_DEFINITIONS>,;-D>"
        -DCANTP_BUILD_CFFI_INTERFACE
        "-I$<JOIN:$<TARGET_PROPERTY:CanTp,INCLUDE_DIRECTORIES>,;-I>"
        --line-directive -o ${CMAKE_CURRENT_SOURCE_DIR}/python/pycantp/input/header.h
        COMMAND_EXPAND_LISTS
        COMMENT "preprocessing cffi header"
        VERBATIM)

    add_custom_target(sdist
        DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/python/pycantp/input/config.c
        DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/python/pycantp/input/source.c
        DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/python/pycantp/input/header.h
        COMMAND ${PYTHON_EXECUTABLE} setup.py sdist -d ${CMAKE_BINARY_DIR}
        COMMAND ${CMAKE_COMMAND} -E remove_directory build
        COMMAND ${CMAKE_COMMAND} -E remove_directory pycantp.egg-info
        COMMAND ${CMAKE_COMMAND} -E remove_directory pycantp/input/pycantp
        WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/python
        COMMENT "building python source distribution package")

    add_custom_target(sdist_install
        DEPENDS sdist
        COMMAND ${PYTHON_EXECUTABLE} -m pip install ./*.tar.gz --user
        COMMENT "installing python source distribution package"
        WORKING_DIRECTORY ${CMAKE_BINARY_DIR})

    add_test(NAME CanTp_UnitTest
        COMMAND ${PYTHON_EXECUTABLE} -m pytest test/unit_test --junitxml=./report/ut.xml
        WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR})

    add_test(NAME CanTp_FuncTest
        COMMAND ${PYTHON_EXECUTABLE} -m behave test/func_test --junit-directory=./report --junit
        WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR})

    set_tests_properties(CanTp_UnitTest PROPERTIES DEPENDS sdist_install)
    set_tests_properties(CanTp_FuncTest PROPERTIES DEPENDS sdist_install)
endif ()
