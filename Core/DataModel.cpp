#include "DataModel.h"

DataModel::DataModel(QObject *parent) : QObject(parent) {}

void DataModel::loadExcel(const QString &path) {
    try {
        QXlsx::Document xlsx(path);
        if(!xlsx.load()) {
            throw std::runtime_error("Excel文件加载失败");
        }
        QVector<QVector<double>> matrix;
        for (int row=2; row<=xlsx.dimension().lastRow(); ++row) {
            QVector<double> cols;
            for (int col=1; col<=xlsx.dimension().lastColumn(); ++col) {
                cols << xlsx.read(row, col).toDouble();
            }
            matrix << cols;
        }
        emit dataParsed(matrix);
        emit dataLoaded(matrix);
    } catch (const std::exception &e) {
        qCritical() << "数据加载错误: " << e.what();
        // Ensure matrix is cleared or not used if loading failed partially before error
        // For simplicity, we assume matrix might be empty or partially filled, 
        // but dataLoaded/dataParsed won't be emitted on error path.
        emit errorOccurred(tr("文件加载失败: %1").arg(e.what()));
    }
}
