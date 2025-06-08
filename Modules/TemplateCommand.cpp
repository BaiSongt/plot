class ApplyTemplateCommand : public ICommand {
    QCustomPlot *plot;
    Template oldState;
    Template newState;
public:
    void execute() override { /* 应用新模板 */ }
    void undo() override { plot->restoreState(oldState); }
};