#include "MainWindow.h"
#include "ui_mainwindow.h" // Generated from mainwindow.ui
#include "Core/UndoRedoManager.h" // Assuming UndoRedoManager.h is in Core
#include "qcustomplot.h"      // For QCustomPlot
#include <QVBoxLayout>
#include <QMenuBar>
#include <QMenu>

MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent)
    , ui(new Ui::MainWindow)
    , undoManager(new UndoRedoManager(this))
    // , customPlot(nullptr) // MainWindow no longer owns QCustomPlot directly, it's in ui->plotView
{
    ui->setupUi(this);
    setupUiElements();
    setupConnections();
    setupUndoRedo(); // Call the existing setup function

    // Set a central widget if not already set in the .ui file
    // or if you want to replace it programmatically.
    // For now, we assume the .ui file has a central widget or layout.
}

MainWindow::~MainWindow()
{
    delete ui;
    // undoManager is a child of MainWindow, Qt will handle its deletion
}

void MainWindow::setupUiElements()
{
    // QCustomPlot is now managed by PlotView, which is accessible via ui->plotView.
    // We retrieve the QCustomPlot instance from ui->plotView.
    QCustomPlot *localCustomPlot = ui->plotView->getCustomPlot();

    if (!localCustomPlot) {
        qWarning("Failed to get QCustomPlot instance from ui->plotView.");
        return; // Cannot proceed with plot setup
    }

    // Basic plot setup example using the QCustomPlot instance from PlotView
    localCustomPlot->addGraph();
    localCustomPlot->graph(0)->setPen(QPen(Qt::blue)); // QPen requires <QPen> or qcustomplot.h
    localCustomPlot->xAxis->setLabel("x Axis");
    localCustomPlot->yAxis->setLabel("y Axis");

    // Generate some example data:
    QVector<double> xData(101), yData(101);
    for (int i = 0; i < 101; ++i)
    {
        xData[i] = i / 50.0 - 1; // x goes from -1 to 1
        yData[i] = xData[i] * xData[i]; // example: y = x^2
    }
    localCustomPlot->graph(0)->setData(xData, yData);
    localCustomPlot->rescaleAxes();
    localCustomPlot->replot();

    // Further UI element setup can go here (e.g., toolbars, status bars)
    setWindowTitle(tr("Data Visualizer Pro - V0.2")); // Updated version for clarity
}

void MainWindow::setupConnections()
{
    // Connect UI element signals to slots here
    // Example: connect(ui->actionOpen, &QAction::triggered, this, &MainWindow::openFile);
}

void MainWindow::setupUndoRedo() {
    // This function definition was already present.
    // Ensure undoAction and redoAction are members of MainWindow and initialized.
    // They are now declared in MainWindow.h and should be created here or in setupUiElements.

    // Create actions if not already created (e.g., by .ui file)
    // If they are part of a menu in .ui, this might not be needed or just connect them.
    if (!undoAction) {
        undoAction = new QAction(tr("撤销"), this);
        // Add to a menu, e.g., ui->menuEdit->addAction(undoAction);
    }
    if (!redoAction) {
        redoAction = new QAction(tr("重做"), this);
        // Add to a menu, e.g., ui->menuEdit->addAction(redoAction);
    }

    // Connect actions to the UndoRedoManager slots
    // Ensure undoManager is initialized (it is in the constructor now)
    connect(undoAction, &QAction::triggered, undoManager, &UndoRedoManager::undo);
    connect(redoAction, &QAction::triggered, undoManager, &UndoRedoManager::redo);

    // Example: Adding to an Edit menu (assuming ui->menuEdit exists)
    // This part depends on your .ui file structure.
    // If you don't have a menuEdit in your .ui, you'll need to create one programmatically.
    QMenu *editMenu = menuBar()->findChild<QMenu*>("menuEdit");
    if (!editMenu) { // If menuEdit doesn't exist, create it
        editMenu = menuBar()->addMenu(tr("编辑(&E)"));
    }
    editMenu->addAction(undoAction);
    editMenu->addAction(redoAction);
    
    // Update action states based on undo/redo stack availability
    connect(undoManager, &UndoRedoManager::canUndoChanged, undoAction, &QAction::setEnabled);
    connect(undoManager, &UndoRedoManager::canRedoChanged, redoAction, &QAction::setEnabled);
    undoAction->setEnabled(undoManager->canUndo());
    redoAction->setEnabled(undoManager->canRedo());
}