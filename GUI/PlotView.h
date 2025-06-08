#ifndef PLOTVIEW_H
#define PLOTVIEW_H

#include <QWidget>
#include <QDebug> 
#include "qcustomplot.h" 

class PlotView : public QWidget
{
    Q_OBJECT

public:
    explicit PlotView(QWidget *parent = nullptr);
    ~PlotView() {
        delete customPlot;  
        qDebug() << "PlotView资源已释放";
    }

    QCustomPlot* getCustomPlot() const; 

signals:
    void exportProgress(int current, int total);

public slots:
    void exportPlot(const QString &path);
    void batchExport(const QStringList &paths);

private:
    QCustomPlot *customPlot; 
    QMutex exportMutex;     

    // Add any other necessary private members or helper functions
};

#endif // PLOTVIEW_H