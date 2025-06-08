add_library(GUI
    PlotView.cpp
    PlotView.h
    MainWindow.cpp
)

target_link_libraries(GUI
    PRIVATE Qt6::Widgets
    QCustomPlot
    Core
)

# 包含UI资源
qt_add_resources(GUI_RESOURCES
    mainwindow.qrc
)

target_sources(GUI PRIVATE ${GUI_RESOURCES})