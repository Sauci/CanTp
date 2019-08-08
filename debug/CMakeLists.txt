add_executable(main main.c)

add_library(CanTp_PBcfg_ ${CMAKE_BINARY_DIR}/CanTp_PBcfg.c)
target_include_directories(CanTp_PBcfg_
    PUBLIC ${CMAKE_BINARY_DIR}
    PUBLIC ${CMAKE_SOURCE_DIR}/interface
    PUBLIC ${CMAKE_SOURCE_DIR}/test/stub)

target_link_libraries(main
    PUBLIC CanTp
    PUBLIC CanTp_PBcfg_)
