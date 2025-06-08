#include <QObject>
#include <QXlsx/xlsxdocument.h>

class DataModel : public QObject {
    Q_OBJECT
public:
    explicit DataModel(QObject *parent = nullptr);
    void loadExcel(const QString &path);
    
signals:
    void dataParsed(const QVector<QVector<double>>& matrix);
    void dataLoaded(const QVector<QVector<double>>& matrix);
    void errorOccurred(const QString &message);
};