project (CanTp_UnitTest VERSION 0.1.0 LANGUAGES C CXX)

include(GoogleTest)

find_package(Threads REQUIRED)

enable_testing()

set(CMAKE_CXX_STANDARD 11)

add_library(CanIf_Mock mock/CanIf_Mock.cpp)
target_include_directories(CanIf_Mock PUBLIC mock)
target_link_libraries(CanIf_Mock PRIVATE ${GMOCK_LIBRARIES})

add_library(Det_Mock mock/Det_Mock.cpp)
target_include_directories(Det_Mock PUBLIC mock)
target_link_libraries(Det_Mock PRIVATE ${GMOCK_LIBRARIES})

add_library(PduR_Mock mock/PduR_Mock.cpp)
target_include_directories(PduR_Mock PUBLIC mock)
target_link_libraries(PduR_Mock PRIVATE ${GMOCK_LIBRARIES})

add_executable(${PROJECT_NAME} CanTp_UnitTest.cpp)

target_link_libraries(${PROJECT_NAME}
    PUBLIC CanTp
    PRIVATE CanIf_Mock
    PRIVATE Det_Mock
    PRIVATE PduR_Mock
    PRIVATE Threads::Threads
    PRIVATE ${GTEST_LIBRARIES})

gtest_discover_tests(${PROJECT_NAME})
add_test(NAME ${PROJECT_NAME}
    COMMAND ${PROJECT_NAME} --gtest_output=xml:${PROJECT_NAME}.xml
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
