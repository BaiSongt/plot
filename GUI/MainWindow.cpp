#include "MainWindow.h"
#include "ui_mainwindow.h" // Generated from mainwindow.ui
#include "Core/UndoRedoManager.h"
#include "Core/DataModel.h"
#include "qcustomplot.h"
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QMenuBar>
#include <QMenu>
#include <QFileDialog>
#include <QMessageBox>
#include <QGroupBox>
#include <QLabel>

MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent)
    , ui(new Ui::MainWindow)
    , undoManager(new UndoRedoManager(this))
    , dataModel(new DataModel(this))
    , stateVariableComboBox(nullptr)
    , xAxisComboBox(nullptr)
    , yAxisComboBox(nullptr)
    , plotDataButton(nullptr)
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
    // Basic plot setup (axis labels)
    QCustomPlot *localCustomPlot = ui->plotView->getCustomPlot();
    if (localCustomPlot) {
        localCustomPlot->xAxis->setLabel("X Axis");
        localCustomPlot->yAxis->setLabel("Y Axis");
        localCustomPlot->replot();
    } else {
        qWarning("Failed to get QCustomPlot instance from ui->plotView in setupUiElements.");
    }

    // Create Data Selection Group Box (programmatically)
    dataSelectionGroup = new QGroupBox(tr("Data Selection"));
    QHBoxLayout *dataSelectionLayout = new QHBoxLayout();

    // State Variable ComboBox (placeholder for now)
    dataSelectionLayout->addWidget(new QLabel(tr("State:")));
    stateVariableComboBox = new QComboBox();
    stateVariableComboBox->setEnabled(false); // Disabled until multi-dataset/state var logic is added
    stateVariableComboBox->addItem(tr("Default State"));
    dataSelectionLayout->addWidget(stateVariableComboBox);

    // X-Axis ComboBox
    dataSelectionLayout->addWidget(new QLabel(tr("X-Axis:")));
    xAxisComboBox = new QComboBox();
    dataSelectionLayout->addWidget(xAxisComboBox);

    // Y-Axis ComboBox
    dataSelectionLayout->addWidget(new QLabel(tr("Y-Axis:")));
    yAxisComboBox = new QComboBox();
    dataSelectionLayout->addWidget(yAxisComboBox);

    // Plot Button
    plotDataButton = new QPushButton(tr("Plot Data"));
    dataSelectionLayout->addWidget(plotDataButton);

    dataSelectionGroup->setLayout(dataSelectionLayout);

    // Add the group box to the main layout
    // Assuming centralWidget has a QVBoxLayout as per the .ui file structure
    if (ui->centralWidget && ui->centralWidget->layout()) {
        // The .ui file has a QVBoxLayout directly on centralWidget.
        // We add our groupbox to this existing layout.
        ui->centralWidget->layout()->addWidget(dataSelectionGroup);
    } else {
        // Fallback if layout is not set as expected (should not happen with the provided .ui)
        QVBoxLayout *mainLayout = new QVBoxLayout(ui->centralWidget);
        mainLayout->addWidget(ui->plotView); // Ensure plotView is still there
        mainLayout->addWidget(dataSelectionGroup);
        // mainLayout->addWidget(ui->toolBar); // Toolbar is usually managed by QMainWindow itself
        ui->centralWidget->setLayout(mainLayout);
        qWarning("Central widget layout was not set as expected from .ui. Created new QVBoxLayout.");
    }

    setWindowTitle(tr("Data Visualizer Pro - V0.3"));
}

void MainWindow::setupConnections()
{
    // File operations
    // Assuming actionOpen is defined in the .ui file and accessible via ui->actionOpen
    if (ui->actionOpen) {
         connect(ui->actionOpen, &QAction::triggered, this, &MainWindow::openFile);
    } else {
        qWarning("ui->actionOpen is null. Ensure it's defined in mainwindow.ui and setupUi is called.");
        // As a fallback, or if you prefer programmatic menu creation:
        // QMenu *fileMenu = menuBar()->addMenu(tr("&File"));
        // QAction *openAction = fileMenu->addAction(tr("&Open..."));
        // connect(openAction, &QAction::triggered, this, &MainWindow::openFile);
    }

    // Data model connections
    connect(dataModel, &DataModel::dataLoaded, this, &MainWindow::onDataLoaded);
    connect(dataModel, &DataModel::errorOccurred, this, &MainWindow::onDataError);

    // Plotting connection
    if (plotDataButton) {
        connect(plotDataButton, &QPushButton::clicked, this, &MainWindow::plotSelectedData);
    } else {
        qWarning("plotDataButton is null. Check setupUiElements.");
    }
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

void MainWindow::openFile()
{
    QString filePath = QFileDialog::getOpenFileName(
        this,
        tr("Open Data File"),
        QString(), // Default directory
        tr("Excel Files (*.xlsx *.xls);;CSV Files (*.csv);;All Files (*)")
    );

    if (!filePath.isEmpty()) {
        currentDataMatrix.clear(); // Clear previous data
        xAxisComboBox->clear();
        yAxisComboBox->clear();
        // Potentially clear the plot or show a loading state
        QCustomPlot *plot = ui->plotView->getCustomPlot();
        if(plot) {
            plot->clearGraphs();
            plot->replot();
        }
        dataModel->loadExcel(filePath); // For now, only Excel is implemented in DataModel
    }
}

void MainWindow::onDataLoaded(const QVector<QVector<double>> &data)
{
    currentDataMatrix = data;
    if (data.isEmpty() || data.first().isEmpty()) {
        QMessageBox::information(this, tr("Data Loaded"), tr("The file was loaded, but no data was found or data is empty."));
        return;
    }

    int numColumns = data.first().size();
    xAxisComboBox->clear();
    yAxisComboBox->clear();

    for (int i = 0; i < numColumns; ++i) {
        QString columnName = tr("Column %1").arg(i + 1);
        xAxisComboBox->addItem(columnName, i); // Store column index as item data
        yAxisComboBox->addItem(columnName, i);
    }

    QMessageBox::information(this, tr("Data Loaded"), tr("Data loaded successfully. Please select X and Y axes to plot."));
}

void MainWindow::onDataError(const QString &errorMessage)
{
    QMessageBox::critical(this, tr("Error Loading Data"), errorMessage);
    currentDataMatrix.clear();
    xAxisComboBox->clear();
    yAxisComboBox->clear();
}

void MainWindow::plotSelectedData()
{
    if (currentDataMatrix.isEmpty()) {
        QMessageBox::warning(this, tr("No Data"), tr("Please load a data file first."));
        return;
    }

    int xCol = xAxisComboBox->currentData().toInt();
    int yCol = yAxisComboBox->currentData().toInt();

    if (xAxisComboBox->currentIndex() < 0 || yAxisComboBox->currentIndex() < 0) {
        QMessageBox::warning(this, tr("Selection Error"), tr("Please select valid X and Y axes."));
        return;
    }

    QVector<double> xData, yData;
    if (currentDataMatrix.first().size() <= qMax(xCol, yCol)) {
         QMessageBox::critical(this, tr("Data Error"), tr("Selected column index out of bounds."));
         return;
    }

    for (const auto &row : currentDataMatrix) {
        if (row.size() > xCol) xData.append(row[xCol]);
        else { /* Handle potential ragged data or error */ }
        if (row.size() > yCol) yData.append(row[yCol]);
        else { /* Handle potential ragged data or error */ }
    }

    if (xData.size() != yData.size() || xData.isEmpty()) {
        QMessageBox::warning(this, tr("Plotting Error"), tr("Selected data columns are invalid or empty."));
        return;
    }

    QCustomPlot *plot = ui->plotView->getCustomPlot();
    if (!plot) {
        qWarning("QCustomPlot instance is null in plotSelectedData.");
        return;
    }

    plot->clearGraphs(); // Clear previous plots
    plot->addGraph();
    plot->graph(0)->setData(xData, yData);
    plot->graph(0)->setPen(QPen(Qt::blue)); // Example pen
    // plot->graph(0)->setLineStyle(QCPGraph::lsNone); // Example: scatter plot
    // plot->graph(0)->setScatterStyle(QCPScatterStyle(QCPScatterStyle::ssCircle, Qt::blue, Qt::white, 5));

    // Set labels based on selected columns (optional)
    plot->xAxis->setLabel(xAxisComboBox->currentText());
    plot->yAxis->setLabel(yAxisComboBox->currentText());

    plot->rescaleAxes();
    plot->replot();
}