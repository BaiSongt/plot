#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>
#include <QAction>
#include <QComboBox>
#include <QPushButton>
#include <QVector>
#include <QLabel> // Added for labels in programmatic UI

// Forward declaration for Ui::MainWindow if using .ui file
QT_BEGIN_NAMESPACE
namespace Ui { class MainWindow; }
QT_END_NAMESPACE

class UndoRedoManager; // Forward declaration
class PlotView;
class DataModel; // Forward declaration for DataModel
class QGroupBox; // Forward declaration for QGroupBox
                // However, ui_mainwindow.h (generated from mainwindow.ui) should handle PlotView.

class MainWindow : public QMainWindow
{
    Q_OBJECT

public:
    explicit MainWindow(QWidget *parent = nullptr);
    ~MainWindow();

private slots:
    void openFile();
    void onDataLoaded(const QVector<QVector<double>> &data);
    void onDataError(const QString &errorMessage);
    void plotSelectedData();
    // Add other slots for UI interactions here

private:
    void setupUiElements();      // Helper to set up UI elements not in .ui or needing code
    void setupConnections();     // Helper to connect signals and slots
    void setupUndoRedo();        // Declaration for the existing function

    Ui::MainWindow *ui;          // Pointer to the UI components defined in mainwindow.ui
    UndoRedoManager *undoManager; 
    QAction *undoAction;
    QAction *redoAction;

    DataModel *dataModel;
    QVector<QVector<double>> currentDataMatrix; // To store the loaded data

    // UI Elements for data selection (will be created programmatically for now)
    QGroupBox *dataSelectionGroup;
    QComboBox *stateVariableComboBox;
    QComboBox *xAxisComboBox;
    QComboBox *yAxisComboBox;
    QPushButton *plotDataButton;

    // QCustomPlot *customPlot; // This is now accessed via ui->plotView->getCustomPlot()
    // Add other members like data models, view models etc. later
};

#endif // MAINWINDOW_H
