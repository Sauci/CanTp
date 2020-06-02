add_custom_command(OUTPUT
    ${CMAKE_CURRENT_SOURCE_DIR}/CanTp_PBcfg.c
    ${CMAKE_CURRENT_SOURCE_DIR}/CanTp_PBcfg.h
    DEPENDS ${CANTP_CONFIG_FILEPATH}
    DEPENDS ${PROJECT_SOURCE_DIR}/script/header.h.jinja2
    DEPENDS ${PROJECT_SOURCE_DIR}/script/source.c.jinja2
    COMMAND ${PYTHON_EXECUTABLE} -m bsw_code_gen
    -template_directory ${PROJECT_SOURCE_DIR}/script
    ${CANTP_CONFIG_FILEPATH}
    ${CMAKE_CURRENT_SOURCE_DIR}/CanTp_PBcfg.c
    ${CMAKE_CURRENT_SOURCE_DIR}/CanTp_PBcfg.h
    COMMENT "generating post-build configuration header")

add_library(CanTp_PBcfg STATIC ${CMAKE_CURRENT_SOURCE_DIR}/CanTp_PBcfg.c)

target_include_directories(CanTp_PBcfg
    INTERFACE ${CMAKE_CURRENT_SOURCE_DIR}
    PRIVATE ${PROJECT_SOURCE_DIR}/interface
    PRIVATE ${AUTOSAR_STD_HEADER_PATH}
    PRIVATE $<$<BOOL:${CANTP_ENABLE_TEST}>:${PROJECT_SOURCE_DIR}/test/stub>)

if (${ENABLE_PC_LINT})
    add_pc_lint_target(NAME CanTp_PBcfg
        DEPENDS CanTp_PBcfg.c CanTp_PBcfg.h
        OUTPUT_LOG ${PROJECT_SOURCE_DIR}/${PROJECT_NAME}_PBcfg.lnt.log
        EXCLUDE_DIRECTORIES
        ${PROJECT_SOURCE_DIR}/interface
        ${AUTOSAR_STD_HEADER_PATH}
        OPTION_FILES
        ${PROJECT_SOURCE_DIR}/extern/lint/MISRA${MISRA_C_VERSION}.lnt
        ${PROJECT_SOURCE_DIR}/config/CanTp.lnt)
endif ()
