cmake_minimum_required(VERSION 3.10)
project(SpanningTreeZdd)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O3")

# インクルードパス
include_directories(
    ../../lib/tdzdd/include
    ../../lib/frontier_basic_tdzdd
)

# 実行ファイル
add_executable(spanning_tree_zdd
    src/main.cpp
    src/SpanningTree.cpp
    src/UnfoldingFilter.cpp
)
