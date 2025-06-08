#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>
#include <QAction>

// Forward declaration for Ui::MainWindow if using .ui file
QT_BEGIN_NAMESPACE
namespace Ui { class MainWindow; }
QT_END_NAMESPACE

class UndoRedoManager; // Forward declaration
// class QCustomPlot; // No longer needed here, PlotView handles its QCustomPlot instance

class PlotView; // Forward declare PlotView if ui_mainwindow.h doesn't include PlotView.h early enough, or include PlotView.h
                // However, ui_mainwindow.h (generated from mainwindow.ui) should handle PlotView.

class MainWindow : public QMainWindow
{
    Q_OBJECT

public:
    explicit MainWindow(QWidget *parent = nullptr);
    ~MainWindow();

private slots:
    // Add slots for UI interactions here

private:
    void setupUiElements();      // Helper to set up UI elements not in .ui or needing code
    void setupConnections();     // Helper to connect signals and slots
    void setupUndoRedo();        // Declaration for the existing function

    Ui::MainWindow *ui;          // Pointer to the UI components defined in mainwindow.ui
    UndoRedoManager *undoManager; // Example member for undo/redo
    QAction *undoAction;
    QAction *redoAction;

    // QCustomPlot *customPlot; // This is now accessed via ui->plotView->getCustomPlot()
    // Add other members like data models, view models etc. later
};

#endif // MAINWINDOW_H
