cmake_minimum_required(VERSION 3.10)
project(Verify)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O3")

include_directories(
    ../lib/tdzdd/include
    ../lib/frontier_basic_tdzdd
    ../cpp/spanning_tree_zdd/src
)

add_executable(verify
    verify.cpp
    ../cpp/spanning_tree_zdd/src/SpanningTree.cpp
)
