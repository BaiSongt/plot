add_library(Core
    DataModel.cpp
    DataModel.h
    # PlotTemplate.cpp # Assuming PlotTemplate.cpp and .h exist, otherwise remove or add them
    UndoRedoManager.cpp
    # UndoRedoCommand.h is a header, usually not listed here unless it's a source for specific Qt processing (like moc)
    # It will be found via include directories.
)

# Export include directories for other targets (like GUI) to find Core's headers
# This allows #include "Core/UndoRedoManager.h" or #include "UndoRedoCommand.h" from GUI module
# if GUI's include path is set to ${CMAKE_SOURCE_DIR} (as it is for DataVisualizerApp)
# or if GUI links Core publicly.
# A more robust way for modular projects is to make Core export its include directory.
target_include_directories(Core
    PUBLIC 
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}> 
        $<INSTALL_INTERFACE:include> # For when/if you install the library
    PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR} # For Core's own cpp files to find its headers
)


target_link_libraries(Core
    PRIVATE Qt6::Core
    Qt6::Gui
    QXlsx
)

# 包含模板配置文件
file(COPY templates DESTINATION ${CMAKE_CURRENT_BINARY_DIR})