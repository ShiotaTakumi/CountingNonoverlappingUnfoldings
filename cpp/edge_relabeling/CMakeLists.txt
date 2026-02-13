cmake_minimum_required(VERSION 3.10)
project(EdgeRelabeling)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O3")

# Executable / 実行ファイル
add_executable(edge_relabeling
    src/main.cpp
)

# Include path for lib/decompose is not needed (relative path in main.cpp)
# lib/decompose のインクルードパスは不要（main.cpp で相対パス指定）
