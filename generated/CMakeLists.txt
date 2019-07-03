add_custom_command(OUTPUT ${CMAKE_CURRENT_SOURCE_DIR}/CanTp_Cfg.h
    DEPENDS ${can_tp_cfg_in}
    COMMAND ${PYTHON_EXECUTABLE} can_tp.py ${can_tp_cfg_in} -header ${CMAKE_CURRENT_SOURCE_DIR}/CanTp_Cfg.h
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/script
    COMMENT "generating configuration header")

add_custom_command(OUTPUT ${CMAKE_CURRENT_SOURCE_DIR}/CanTp_Cfg.c
    DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/CanTp_Cfg.h
    DEPENDS ${can_tp_cfg_in}
    COMMAND ${PYTHON_EXECUTABLE} can_tp.py ${can_tp_cfg_in} -source ${CMAKE_CURRENT_SOURCE_DIR}/CanTp_Cfg.c
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/script
    COMMENT "generating configuration source")

add_library(CanTp_Cfg STATIC ${CMAKE_CURRENT_SOURCE_DIR}/CanTp_Cfg.c)

target_include_directories(CanTp_Cfg
    INTERFACE ${CMAKE_CURRENT_SOURCE_DIR}
    PRIVATE ${CMAKE_SOURCE_DIR}/interface
    PRIVATE $<$<BOOL:${enable_test}>:${CMAKE_SOURCE_DIR}/stub>)

add_custom_target(generate
    DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/CanTp_Cfg.h
    DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/CanTp_Cfg.c
    COMMENT "generating generated files")
