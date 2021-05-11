set(CMAKE_VERBOSE_MAKEFILE on)

add_executable(lcjoin lcjoin.cpp)
target_link_libraries(lcjoin PRIVATE cxxopts fmt::fmt)
target_include_directories(lcjoin PRIVATE ../include)

add_executable(treebased treebased.cpp)
target_link_libraries(treebased PRIVATE cxxopts fmt::fmt)
target_include_directories(treebased PRIVATE ../include)