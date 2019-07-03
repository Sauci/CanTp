# the bellow targets might be replaced by a custom command (add_custom_command), but it will add
# extra dependencies (see https://cmake.org/cmake/help/v3.15/command/add_custom_command.html). thus
# a custom target is created instead.
add_custom_target(CanTp_Cfg.c
    DEPENDS ${can_tp_cfg_in}
    DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/script/config.c.jinja2
    COMMAND ${PYTHON_EXECUTABLE} can_tp.py ${can_tp_cfg_in}
    -source ${CMAKE_CURRENT_SOURCE_DIR}/CanTp_Cfg.c
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/script
    COMMENT "generating configuration source")

add_custom_target(CanTp_Cfg.h
    DEPENDS ${can_tp_cfg_in}
    DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/script/config.h.jinja2
    COMMAND ${PYTHON_EXECUTABLE} can_tp.py ${can_tp_cfg_in}
    -header ${CMAKE_CURRENT_SOURCE_DIR}/CanTp_Cfg.h
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/script
    COMMENT "generating configuration header")

add_library(CanTp_Cfg STATIC ${CMAKE_CURRENT_SOURCE_DIR}/CanTp_Cfg.c)
add_dependencies(CanTp_Cfg CanTp_Cfg.h)

target_include_directories(CanTp_Cfg
    INTERFACE ${CMAKE_CURRENT_SOURCE_DIR}
    PRIVATE ${CMAKE_SOURCE_DIR}/interface
    PRIVATE $<$<BOOL:${enable_test}>:${CMAKE_SOURCE_DIR}/stub>)

if (${enable_static_code_analysis})
    add_pc_lint_target(NAME CanTp_Cfg
        DEPENDS CanTp_Cfg.c CanTp_Cfg.h
        OUTPUT_LOG ${CMAKE_SOURCE_DIR}/${PROJECT_NAME}_Cfg.lnt.log
        EXCLUDE_DIRECTORIES
        ${CMAKE_SOURCE_DIR}/interface
        ${CMAKE_SOURCE_DIR}/stub
        OPTION_FILES
        ${CMAKE_SOURCE_DIR}/extern/lint/MISRA${can_tp_misra_c_version}.lnt
        ${CMAKE_SOURCE_DIR}/config/CanTp.lnt)
endif ()
