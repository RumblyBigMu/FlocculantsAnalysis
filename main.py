from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenuBar, QMessageBox


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QtGui.QIcon('Icon.jpg'))
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Анализ флокулянтов")
        self.setMinimumSize(500, 500)
        self.resize(650, 650)
        self.setMaximumSize(800, 800)
        # Генерация меню
        self.createMenu()

    def createMenu(self):
        # Настройка меню
        self.menuBar = QMenuBar(self)
        self.setMenuBar(self.menuBar)
        # Меню "О программе"
        menu_about = self.menuBar.addMenu("О программе")
        menu_about.addAction("Информация", self.about, shortcut='F1')

    def about(self):
        text = "    Авторы: Мусина С.А., Миянов М.Р.\n" \
               "    Программа создана в рамках работы по созданию алгоритмов" \
               " по интеллектуальной поддержке принятия решений при управлении" \
               " процессом флокуляционной очистки сточных вод"
        QMessageBox.about(self, "Информация", text)


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
