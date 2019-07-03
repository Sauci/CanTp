add_custom_command(OUTPUT ${CMAKE_CURRENT_SOURCE_DIR}/CanTp_Cfg.h
    DEPENDS ${can_tp_cfg_in}
    DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/script/config.h.jinja2
    COMMAND ${PYTHON_EXECUTABLE} can_tp.py ${can_tp_cfg_in}
    -header ${CMAKE_CURRENT_SOURCE_DIR}/CanTp_Cfg.h
    #-schema ${CMAKE_SOURCE_DIR}/config/can_tp.schema.json
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/script
    COMMENT "generating configuration header")

add_custom_command(OUTPUT ${CMAKE_CURRENT_SOURCE_DIR}/CanTp_Cfg.c
    DEPENDS ${can_tp_cfg_in}
    DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/script/config.c.jinja2
    DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/CanTp_Cfg.h
    COMMAND ${PYTHON_EXECUTABLE} can_tp.py ${can_tp_cfg_in}
    -source ${CMAKE_CURRENT_SOURCE_DIR}/CanTp_Cfg.c
    #-schema ${CMAKE_SOURCE_DIR}/config/can_tp.schema.json
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/script
    COMMENT "generating configuration source")

add_library(CanTp_Cfg STATIC ${CMAKE_CURRENT_SOURCE_DIR}/CanTp_Cfg.c)

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
