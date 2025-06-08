#include <QApplication>
#include "GUI/MainWindow.h" // Assuming MainWindow.h is in the GUI subdirectory

int main(int argc, char *argv[]) {
    QApplication a(argc, argv);

    MainWindow w;
    w.setWindowTitle("Data Visualizer Pro"); // Set a nice window title
    w.show();

    return a.exec();
}
