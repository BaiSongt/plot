cmake_minimum_required(VERSION 3.20)
project(DataVisualizer LANGUAGES CXX)

# Set modern policy for FetchContent timestamp behavior
cmake_policy(SET CMP0135 NEW)

# 自动下载第三方库
include(FetchContent)
FetchContent_Declare(
    QXlsx
    URL https://github.com/QtExcel/QXlsx/archive/refs/tags/v1.4.6.zip
)
FetchContent_Declare(
    QCustomPlot
    URL https://www.qcustomplot.com/release/2.1.1/QCustomPlot-sharedlib.tar.gz
)

# 配置Qt6
find_package(Qt6 COMPONENTS Core Gui Widgets REQUIRED)

# 创建模块化结构
add_subdirectory(Core)
add_subdirectory(GUI)
add_subdirectory(Modules)

# 包含下载的库
FetchContent_MakeAvailable(QXlsx QCustomPlot)

# --- Create Executable ---
# Automatically find Qt UI compiler, moc, and rcc
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTOUIC ON)
set(CMAKE_AUTORCC ON)

# Define the executable
add_executable(DataVisualizerApp main.cpp)

# Link libraries to the executable
target_link_libraries(DataVisualizerApp
    PRIVATE
    Qt6::Widgets
    GUI             # Link our GUI library
    # QCustomPlot and Core are linked transitively through GUI
)

# Set include directories for the executable to find headers from subdirectories
# This helps main.cpp find "GUI/MainWindow.h"
target_include_directories(DataVisualizerApp
    PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR} # Allows #include "GUI/MainWindow.h"
)

# macOS specific bundling (optional, but good practice)
if(APPLE)
    set(MACOSX_BUNDLE_GUI_IDENTIFIER com.yourcompany.datavisualizer)
    set(MACOSX_BUNDLE_BUNDLE_NAME DataVisualizerApp)
    # Add more macOS specific settings if needed
    set_target_properties(DataVisualizerApp PROPERTIES
        MACOSX_BUNDLE TRUE
        # MACOSX_BUNDLE_INFO_PLIST "${CMAKE_CURRENT_SOURCE_DIR}/Info.plist" # If you have a custom Info.plist
    )
endif()

# Windows specific settings (optional)
if(WIN32)
    # For a console application, remove WIN32_EXECUTABLE
    # For a GUI application without a console window, use WIN32_EXECUTABLE
    # add_executable(DataVisualizerApp WIN32 main.cpp) # If you re-declare, ensure it's consistent
    # If you want to set an icon for the executable on Windows:
    # target_sources(DataVisualizerApp PRIVATE "path/to/your/icon.rc") # Add a resource file
endif()