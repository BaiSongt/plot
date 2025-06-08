#include "UndoRedoManager.h"
#include "UndoRedoCommand.h" // For ICommand definition
#include <QDebug> // For potential debugging output

UndoRedoManager::UndoRedoManager(QObject *parent)
    : QObject(parent)
{
    // Initialization, if any
}

UndoRedoManager::~UndoRedoManager()
{
    clearStacks(); // Ensure all commands are deleted
}

// Adds a command, executes it, and pushes it onto the undo stack.
void UndoRedoManager::addCommand(ICommand *command)
{
    if (!command) {
        qWarning("UndoRedoManager::addCommand: Attempted to add a null command.");
        return;
    }

    command->execute(); // Execute the command first
    undoStack.push(command);
    
    // Clear the redo stack whenever a new command is executed
    qDeleteAll(redoStack);
    redoStack.clear();

    updateCanUndoRedo();
    emit commandExecuted();
}

void UndoRedoManager::undo()
{
    if (canUndo()) {
        ICommand *command = undoStack.pop();
        command->undo();
        redoStack.push(command);
        updateCanUndoRedo();
        emit commandExecuted();
    }
}

void UndoRedoManager::redo()
{
    if (canRedo()) {
        ICommand *command = redoStack.pop();
        command->execute(); // Re-execute the command
        undoStack.push(command);
        updateCanUndoRedo();
        emit commandExecuted();
    }
}

bool UndoRedoManager::canUndo() const
{
    return !undoStack.isEmpty();
}

bool UndoRedoManager::canRedo() const
{
    return !redoStack.isEmpty();
}

void UndoRedoManager::clearStacks()
{
    qDeleteAll(undoStack);
    undoStack.clear();

    qDeleteAll(redoStack);
    redoStack.clear();

    updateCanUndoRedo();
}

void UndoRedoManager::updateCanUndoRedo()
{
    emit canUndoChanged(!undoStack.isEmpty());
    emit canRedoChanged(!redoStack.isEmpty());
}