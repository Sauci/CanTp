set(MISRA_CONFIG_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/lint)

execute_process(COMMAND ${CMAKE_COMMAND} -E make_directory ${MISRA_CONFIG_DIRECTORY})

file(DOWNLOAD https://gist.githubusercontent.com/Sauci/39b03e60642a910e358d4dd0871a0b05/raw/d2ac6c04adf2ab823bc9bf18a5d8346516d5f9ca/add_pc_lint_target.cmake
    ${CMAKE_CURRENT_SOURCE_DIR}/add_pc_lint_target.cmake)

file(DOWNLOAD https://gimpel.com/html/pub90/au-misra1.lnt ${MISRA_CONFIG_DIRECTORY}/MISRA1998.lnt)
file(DOWNLOAD https://gimpel.com/html/pub90/au-misra2.lnt ${MISRA_CONFIG_DIRECTORY}/MISRA2004.lnt)
file(DOWNLOAD https://gimpel.com/html/pub90/au-misra3.lnt ${MISRA_CONFIG_DIRECTORY}/MISRA2012.lnt)

include(add_pc_lint_target.cmake)
