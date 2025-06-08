#include "PlotView.h"
#include <qcustomplot.h>

PlotView::PlotView(QWidget *parent) : QWidget(parent) {
    customPlot = new QCustomPlot(this);
    // 初始化绘图区域

    // It's good practice to set a layout for PlotView itself if QCustomPlot is its only child,
    // or if there might be other widgets later. This ensures QCustomPlot resizes with PlotView.
    QVBoxLayout *layout = new QVBoxLayout(this);
    layout->addWidget(customPlot);
    layout->setContentsMargins(0, 0, 0, 0); // Optional: remove margins
    this->setLayout(layout); 
}

QCustomPlot* PlotView::getCustomPlot() const
{
    return customPlot;
}

void PlotView::exportPlot(const QString &path) {
    if(path.endsWith(".png"))
        customPlot->savePng(path, width(), height());
    else if(path.endsWith(".svg"))
        customPlot->saveSvg(path);
}

void PlotView::batchExport(const QStringList &paths) {
    QMutexLocker locker(&exportMutex);
    QThreadPool::globalInstance()->start([=]{
        emit exportProgress(0, paths.count());
        int progress = 0;
        for(const auto &path : paths) {
            QMetaObject::invokeMethod(this, [this, path]{
                exportPlot(path);
            }, Qt::BlockingQueuedConnection);
            emit exportProgress(++progress, paths.count());
        }
    });
}