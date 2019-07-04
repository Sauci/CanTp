add_custom_command(OUTPUT ${CMAKE_CURRENT_SOURCE_DIR}/CanTp_PBcfg.h
    DEPENDS ${CANTP_CONFIG_FILEPATH}
    DEPENDS ${PROJECT_SOURCE_DIR}/script/config.h.jinja2
    COMMAND ${PYTHON_EXECUTABLE} can_tp.py ${CANTP_CONFIG_FILEPATH}
    -header ${CMAKE_CURRENT_SOURCE_DIR}/CanTp_PBcfg.h
    #-schema ${CMAKE_SOURCE_DIR}/config/can_tp.schema.json
    WORKING_DIRECTORY ${PROJECT_SOURCE_DIR}/script
    COMMENT "generating post-build configuration header")

add_custom_command(OUTPUT ${CMAKE_CURRENT_SOURCE_DIR}/CanTp_PBcfg.c
    DEPENDS ${CANTP_CONFIG_FILEPATH}
    DEPENDS ${PROJECT_SOURCE_DIR}/script/config.c.jinja2
    DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/CanTp_PBcfg.h
    COMMAND ${PYTHON_EXECUTABLE} can_tp.py ${CANTP_CONFIG_FILEPATH}
    -source ${CMAKE_CURRENT_SOURCE_DIR}/CanTp_PBcfg.c
    #-schema ${CMAKE_SOURCE_DIR}/config/can_tp.schema.json
    WORKING_DIRECTORY ${PROJECT_SOURCE_DIR}/script
    COMMENT "generating post-build configuration source")

add_library(CanTp_PBcfg STATIC ${CMAKE_CURRENT_SOURCE_DIR}/CanTp_PBcfg.c)

target_include_directories(CanTp_PBcfg
    INTERFACE ${CMAKE_CURRENT_SOURCE_DIR}
    PRIVATE ${PROJECT_SOURCE_DIR}/interface
    PRIVATE $<$<BOOL:${ENABLE_TEST}>:${PROJECT_SOURCE_DIR}/test/stub>)

if (${ENABLE_SCA})
    add_pc_lint_target(NAME CanTp_PBcfg
        DEPENDS CanTp_PBcfg.c CanTp_PBcfg.h
        OUTPUT_LOG ${PROJECT_SOURCE_DIR}/${PROJECT_NAME}_PBcfg.lnt.log
        EXCLUDE_DIRECTORIES
        ${PROJECT_SOURCE_DIR}/interface
        ${PROJECT_SOURCE_DIR}/test/stub
        OPTION_FILES
        ${PROJECT_SOURCE_DIR}/extern/lint/MISRA${MISRA_C_VERSION}.lnt
        ${PROJECT_SOURCE_DIR}/config/CanTp.lnt)
endif ()
