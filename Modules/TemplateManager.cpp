void TemplateManager::applyTemplate(QCustomPlot *plot, const QString &tplName) {
    QFile file(QString("templates/%1.json").arg(tplName));
    file.open(QIODevice::ReadOnly);
    QJsonObject config = QJsonDocument::fromJson(file.readAll()).object();
    
    // 应用轴样式
    QJsonObject axis = config["axis"].toObject();
    plot->xAxis->setLabelFont(QFont(axis["labelFont"].toString()));
    plot->yAxis->setNumberPrecision(axis["labelPrecision"].toInt());
}

void TemplateManager::validateTemplate(const QJsonObject &config) {
    if(!config.contains("axis")) {
        throw InvalidTemplateException("缺失axis配置项");
    }
    // 添加更多校验逻辑
}