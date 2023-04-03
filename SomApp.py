import SOM

from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget, QSpinBox, \
    QGridLayout, QMenuBar, QMessageBox, QLabel, QDoubleSpinBox, QFileDialog


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QtGui.QIcon("Icon.jpg"))
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Анализ флокулянтов")
        self.setMinimumSize(500, 500)
        self.resize(650, 650)
        self.setMaximumSize(800, 800)
        # Генерация меню
        self.createMenu()
        # Установка центрального виджета
        self.central = CentralWidget(self)
        self.setCentralWidget(self.central)
        self.show()

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
               " процессом флокуляционной очистки сточных вод."
        QMessageBox.about(self, "Информация", text)


class CentralWidget(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.fname = None  # Имя файла
        self.initUI()

    def initUI(self):

        # Настройка виджета

        #   Лэйбл: параметры сети
        self.settings_label = QLabel(self)
        self.settings_label.setText("Параметры сети")

        #   Создание спин-боксов
        self.__configureSpins__()
        self.epochs_label = QLabel(self)
        self.epochs_label.setText("Укажите количество эпох обучения: ")
        self.lr_label = QLabel(self)
        self.lr_label.setText("Выберите коэффициент обучения: ")

        #   Кнопка выбора файла с данными
        self.browse_file = QPushButton("Выбрать файл", self)
        self.browse_file.clicked.connect(self.open_file_dialog)

        #   Кнопка начала обучения
        self.start_training = QPushButton("Начать обучение", self)
        self.start_training.clicked.connect(self.startTraining)

        #   Информативный лэйбл
        self.info_label = QLabel()
        self.info_label.setAlignment(Qt.AlignCenter)

        #   Кнопка сброса интерфейса
        self.reset_button = QPushButton("Сбросить", self)
        self.reset_button.setDisabled(True)
        self.reset_button.clicked.connect(self.reset)

        #  Расположение элементов в сетке
        self.grid = QGridLayout(self)
        self.grid.setContentsMargins(20, 20, 20, 20)
        self.grid.setSpacing(15)

        self.grid.addWidget(self.settings_label, 0, 0, 1, 3, alignment=Qt.AlignCenter)

        self.grid.addWidget(self.epochs_label, 1, 0, 1, 2, alignment=Qt.AlignLeft)
        self.grid.addWidget(self.epochs_spin, 1, 2)

        self.grid.addWidget(self.lr_label, 2, 0, 1, 2, alignment=Qt.AlignLeft)
        self.grid.addWidget(self.lr_spin, 2, 2)

        self.grid.addWidget(self.browse_file, 3, 1)

        self.grid.addWidget(self.start_training, 4, 1)

        self.grid.addWidget(self.info_label, 5, 1, alignment=Qt.AlignCenter)

        self.grid.addWidget(self.reset_button, 6, 1)

        self.setLayout(self.grid)

    def __configureSpins__(self):
        # Выбор количества эпох
        self.epochs_spin = QSpinBox(self)
        self.epochs_spin.setRange(100, 100000)
        self.epochs_spin.setValue(1000)
        self.epochs_spin.setSingleStep(100)
        # Выбор коэффициента обучения
        self.lr_spin = QDoubleSpinBox(self)
        self.lr_spin.setRange(0.05, 1)
        self.lr_spin.setValue(0.5)
        self.lr_spin.setSingleStep(0.05)

    def open_file_dialog(self):
        import os
        fname, _ = QFileDialog.getOpenFileName(self, "Выберите файл", '.', "Файлы Exсel (*.xlsx *.xls)")
        self.fname = os.path.basename(fname).split('/')[-1]
        print(f"fname = {self.fname}")

    def startTraining(self):
        self.epochs_spin.setDisabled(True)
        self.lr_spin.setDisabled(True)
        self.reset_button.setEnabled(True)

        if self.fname == None or self.fname == "":
            self.info_label.setText("Сначала выберите файл!")
            self.info_label.setStyleSheet("color: red")
        else:
            self.som = SOM.SOM(self.fname, self.epochs_spin.value(), self.lr_spin.value())
            self.som.learning()
            self.info_label.setText("Обучение завершено!")
            self.info_label.setStyleSheet("color: green")

    def reset(self):
        self.fname = None

        self.epochs_spin.setEnabled(True)
        self.epochs_spin.setValue(1000)

        self.lr_spin.setEnabled(True)
        self.lr_spin.setValue(0.5)

        self.info_label.clear()
        self.info_label.setStyleSheet("color: black")

        self.reset_button.setDisabled(True)


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
