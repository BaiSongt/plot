#ifndef UNDOREDOMANAGER_H
#define UNDOREDOMANAGER_H

#include <QObject>
#include <QStack>

// Forward declaration for the command base class
class ICommand; 

class UndoRedoManager : public QObject
{
    Q_OBJECT

public:
    explicit UndoRedoManager(QObject *parent = nullptr);
    ~UndoRedoManager();

    void addCommand(ICommand *command);

    bool canUndo() const;
    bool canRedo() const;

public slots:
    void undo();
    void redo();
    void clearStacks();

signals:
    void canUndoChanged(bool canUndo);
    void canRedoChanged(bool canRedo);
    void commandExecuted(); // Optional: if UI needs to know when any command is done/redone

private:
    QStack<ICommand*> undoStack;
    QStack<ICommand*> redoStack;

    void updateCanUndoRedo();
};

#endif // UNDOREDOMANAGER_H
