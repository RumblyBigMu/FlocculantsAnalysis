import SOM

from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget, QSpinBox, \
    QGridLayout, QMenuBar, QMessageBox, QLabel, QDoubleSpinBox, QFileDialog, QCheckBox, QGroupBox, QVBoxLayout


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QtGui.QIcon("Icon.jpg"))
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Анализ флокулянтов")
        self.setMinimumSize(500, 500)
        self.resize(650, 500)
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
               " интеллектуальной поддержки принятия решений при управлении" \
               " процессом флокуляционной очистки сточных вод."
        QMessageBox.about(self, "Информация", text)


class CentralWidget(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.fname = None  # Имя файла
        self.initUI()

    def initUI(self):

        # Настройка виджета

        #   Создание спин-боксов
        self.__configureSpins__()
        self.epochs_label = QLabel("Укажите количество эпох обучения: ", self)
        self.lr_label = QLabel("Выберите коэффициент обучения: ", self)
        #   Лэйбл: выбор файла
        self.file_label = QLabel(self)
        self.file_label.setText("Выберите файл с данными: ")
        #   Кнопка выбора файла с данными
        self.browse_file_button = QPushButton("Выбрать файл", self)
        self.browse_file_button.clicked.connect(self.open_file_dialog)
        #   Кнопка начала обучения
        self.start_training_button = QPushButton("Начать обучение", self)
        self.start_training_button.clicked.connect(self.startTraining)
        #   Чекбокс отрисовки карты
        self.check_plot = QCheckBox("Нарисовать карту", self)
        #   Кнопка отрисовки карты
        self.plot_button = QPushButton("Нарисовать карту", self)
        self.plot_button.setDisabled(True)
        self.plot_button.clicked.connect(self.plot_map)
        #   Лэйбл: статус обучения
        self.status_label = QLabel(self)
        #   Кнопка сброса интерфейса
        self.reset_button = QPushButton("Сбросить", self)
        self.reset_button.setDisabled(True)
        self.reset_button.clicked.connect(self.reset)

        #  Группировка элементов окна, отвечающих за настройки работы сети
        self.settings_groupbox = QGroupBox("Параметры сети", self)
        settings_grid = QGridLayout(self)

        settings_grid.addWidget(self.file_label, 0, 0, 1, 2, alignment=Qt.AlignLeft)
        settings_grid.addWidget(self.browse_file_button, 0, 2)
        settings_grid.addWidget(self.epochs_label, 1, 0, 1, 2, alignment=Qt.AlignLeft)
        settings_grid.addWidget(self.epochs_spin, 1, 2)
        settings_grid.addWidget(self.lr_label, 2, 0, 1, 2, alignment=Qt.AlignLeft)
        settings_grid.addWidget(self.lr_spin, 2, 2)
        settings_grid.addWidget(self.start_training_button, 3, 2)
        settings_grid.addWidget(self.check_plot, 3, 0, 1, 2)
        settings_grid.addWidget(self.status_label, 4, 1, alignment=Qt.AlignCenter)
        settings_grid.addWidget(self.plot_button, 5, 1)

        self.settings_groupbox.setLayout(settings_grid)

        #   Создание спин-боксов
        self.__configureSampleSpins__()
        self.__configureSampleLabels__()
        #   Кнопка прогноза
        self.predict_button = QPushButton("Получить скорость осаждения", self)
        self.predict_button.clicked.connect(self.predict)
        #   Лэйбл: прогноз
        self.predict_label = QLabel(self)
        #   Кнопка отрисовки карты эксперимента
        self.plot_sample_button = QPushButton("Отрисовать эксперимент на карте", self)
        self.plot_sample_button.clicked.connect(self.plot_prediction)

        labels = [self.dose_spin_label, self.mass_spin_label, self.l_expenses_label, self.m_expenses_label,
                  self.v_mixing_label, self.t_mixing_label, self.h_layer_label, self.t_layer_label]
        self.spins = [self.dose_spin, self.mass_spin, self.l_expenses_spin, self.m_expenses_spin, self.v_mixing_spin,
                      self.t_mixing_spin, self.h_layer_spin, self.t_layer_spin]

        #  Группировка элементов окна, отвечающих за результаты отдельного эксперимента
        self.sample_groupbox = QGroupBox("Информация об эксперименте", self)
        self.sample_groupbox.setDisabled(True)
        sample_grid = QGridLayout(self)
        self.grid_cols = len(labels)

        for i in range(self.grid_cols):
            sample_grid.addWidget(labels[i], 0, i, 1, 1, alignment=Qt.AlignCenter)
            sample_grid.addWidget(self.spins[i], 1, i, 1, 1)
        sample_grid.addWidget(self.predict_label, 2, 0, 1, self.grid_cols, alignment=Qt.AlignCenter)
        sample_grid.addWidget(self.predict_button, 3, 0, 1, self.grid_cols, alignment=Qt.AlignCenter)
        sample_grid.addWidget(self.plot_sample_button, 4, 0, 1, self.grid_cols, alignment=Qt.AlignCenter)
        self.sample_groupbox.setLayout(sample_grid)

        #  Расположение элементов в сетке
        self.vbox = QVBoxLayout()
        self.vbox.addWidget(self.settings_groupbox)
        self.vbox.addWidget(self.sample_groupbox)
        self.vbox.addWidget(self.reset_button)
        self.setLayout(self.vbox)

    def __configureSampleLabels__(self):
        self.dose_spin_label = QLabel("Д, мл", self)
        self.mass_spin_label = QLabel("P, г", self)
        self.l_expenses_label = QLabel("c, г/л", self)
        self.m_expenses_label = QLabel("c, г/м^3", self)
        self.v_mixing_label = QLabel("n, об/мин", self)
        self.t_mixing_label = QLabel("t_пер, с", self)
        self.h_layer_label = QLabel("h, мм", self)
        self.t_layer_label = QLabel("t, с", self)

    def __configureSampleSpins__(self):
        # Выбор дозы раствора
        self.dose_spin = QDoubleSpinBox(self)
        self.dose_spin.setRange(0, 10)
        self.dose_spin.setValue(0.5)
        self.dose_spin.setSingleStep(0.5)
        # Выбор массы флокулянта в дозе раствора
        self.mass_spin = QDoubleSpinBox(self)
        self.mass_spin.setDecimals(5)
        self.mass_spin.setRange(0, 0.001)
        self.mass_spin.setValue(0.00005)
        self.mass_spin.setSingleStep(0.00005)
        # Выбор расхода флокулянта на литр
        self.l_expenses_spin = QDoubleSpinBox(self)
        self.l_expenses_spin.setDecimals(3)
        self.l_expenses_spin.setRange(0.001, 0.015)
        self.l_expenses_spin.setValue(0.001)
        self.l_expenses_spin.setSingleStep(0.001)
        # Выбор расхода флокулянта на м^3
        self.m_expenses_spin = QSpinBox(self)
        self.m_expenses_spin.setRange(1, 15)
        self.m_expenses_spin.setValue(1)
        self.m_expenses_spin.setSingleStep(1)
        # Выбор скорости перемешивания
        self.v_mixing_spin = QSpinBox(self)
        self.v_mixing_spin.setRange(30, 240)
        self.v_mixing_spin.setValue(30)
        self.v_mixing_spin.setSingleStep(30)
        # Выбор времени перемешивания
        self.t_mixing_spin = QSpinBox(self)
        self.t_mixing_spin.setRange(0, 200)
        self.t_mixing_spin.setValue(5)
        self.t_mixing_spin.setSingleStep(5)
        # Выбор высоты осветленного слоя
        self.h_layer_spin = QSpinBox(self)
        self.h_layer_spin.setRange(0, 200)
        self.h_layer_spin.setValue(60)
        self.h_layer_spin.setSingleStep(1)
        # Выбор времени осветления слоя
        self.t_layer_spin = QSpinBox(self)
        self.t_layer_spin.setRange(0, 300)
        self.t_layer_spin.setValue(50)
        self.t_layer_spin.setSingleStep(1)

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
        # self.fname = os.path.basename(fname).split('/')[-1]
        self.fname = fname
        print(f"fname = {self.fname}")

    def startTraining(self):
        if self.fname == None or self.fname == "":
            self.status_label.setText("Сначала выберите файл!")
            self.status_label.setStyleSheet("color: red")
            self.plot_button.setDisabled(True)
            self.reset_button.setEnabled(True)
        else:
            self.browse_file_button.setDisabled(True)
            self.epochs_spin.setDisabled(True)
            self.lr_spin.setDisabled(True)
            self.som = SOM.SOM(self.fname, self.epochs_spin.value(), self.lr_spin.value())
            self.som.learning()
            if self.check_plot.isChecked():
                self.plot_map()
            self.plot_button.setEnabled(True)
            self.reset_button.setEnabled(True)
            self.sample_groupbox.setEnabled(True)
            self.status_label.setText("Обучение завершено!")
            self.status_label.setStyleSheet("color: green")

    def reset(self):
        self.fname = None
        self.browse_file_button.setEnabled(True)

        self.epochs_spin.setEnabled(True)
        self.epochs_spin.setValue(1000)

        self.lr_spin.setEnabled(True)
        self.lr_spin.setValue(0.5)

        self.status_label.clear()
        self.status_label.setStyleSheet("color: black")
        self.predict_label.clear()

        self.plot_button.setDisabled(True)
        self.reset_button.setDisabled(True)
        self.reset_button.setDisabled(True)

        self.sample_groupbox.setDisabled(True)

    def plot_map(self):
        if not self.som == None:
            self.som.plot_som()

    def __generateSample__(self):
        sample = []
        for spin in self.spins:
            sample.append(spin.value())
        return sample

    def predict(self):
        sample = self.__generateSample__()
        if not self.som == None:
            self.som.regression(sample)
            self.predict_label.setText(f"Ожидаемая скорость осаждения: {round(float(self.som.y_pred), 2)} мм/с")

    def plot_prediction(self):
        sample = self.__generateSample__()
        if not self.som == None:
            self.som.regression(sample)
            self.som.plot_sample()


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
