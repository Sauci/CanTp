set(MISRA_CONFIG_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/lint)

execute_process(COMMAND ${CMAKE_COMMAND} -E make_directory ${MISRA_CONFIG_DIRECTORY})

file(DOWNLOAD
    https://gist.githubusercontent.com/Sauci/39b03e60642a910e358d4dd0871a0b05/raw/b4830fba6d48517950866c14e811000b0ae08020/add_pc_lint_target.cmake
    ${CMAKE_CURRENT_SOURCE_DIR}/add_pc_lint_target.cmake)

file(DOWNLOAD https://gimpel.com/html/pub90/au-misra1.lnt ${MISRA_CONFIG_DIRECTORY}/MISRA1998.lnt)
file(DOWNLOAD https://gimpel.com/html/pub90/au-misra2.lnt ${MISRA_CONFIG_DIRECTORY}/MISRA2004.lnt)
file(DOWNLOAD https://gimpel.com/html/pub90/au-misra3.lnt ${MISRA_CONFIG_DIRECTORY}/MISRA2012.lnt)

if (${ENABLE_PC_LINT})
    include(add_pc_lint_target.cmake)
endif ()
