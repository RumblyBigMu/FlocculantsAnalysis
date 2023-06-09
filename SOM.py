from minisom import MiniSom

import pandas as pd
import numpy as np

from sklearn.preprocessing import MinMaxScaler
from sklearn.linear_model import LinearRegression

import matplotlib.pyplot as plt
from matplotlib.patches import RegularPolygon
from matplotlib import cm, colorbar
from matplotlib.lines import Line2D


class SOM():
    def __init__(self, fname="FlocculantsData.xlsx", epochs=1000, learning_rate=0.5):
        """
        Конструктор класса SOM
        :param fname: имя файла
        :type fname: str
        :param epochs: количество эпох обучения
        :type epochs: int
        :param learning_rate: коэффициент обучения
        :type learning_rate: float
        """
        self.fname = fname
        # Гиперпараметры сети
        self.learning_rate = learning_rate
        self.epochs = epochs
        self.sigma = 1.5
        self.grid_rows = 10
        self.grid_columns = 10
        # Датасет
        self.target = None
        self.label_names = None
        self.data = None  # Ненормированные данные
        self.y = None  # Целевая переменная
        self.norm_data = None  # Нормированные данные

    def learning(self):
        """
        Функция обучения сети
        """
        self.data_preprocessing()
        self.som = MiniSom(self.grid_rows, self.grid_columns, self.norm_data.shape[1],
                           sigma=self.sigma,
                           learning_rate=self.learning_rate,
                           activation_distance='euclidean',
                           topology='hexagonal',
                           neighborhood_function='gaussian')
        self.som.train(self.norm_data, self.epochs, verbose=True)

    def data_preprocessing(self):
        """
        Функция, выполняющая чтение и обработку датесета

        :rtype: numpy.ndarray
        :return: массив данных
        """
        # Чтение данных из файла
        self.data = pd.read_excel(self.fname)
        self.data = self.data.rename(columns=self.data.iloc[0]).drop(self.data.index[0])

        # Извлечение меток данных
        self.target = self.data['Type'].values
        self.label_names = {'неудовл': 'Неудовлетворительно', 'удовл': 'Удовлетворительно', 'хор': 'Хорошо',
                            'отл': 'Отлично'}
        # Извлечение целевой переменной
        self.y = self.data[self.data.columns[-2:-1]]

        # Выбор данных для построения карты
        self.data = self.data[self.data.columns[:-1]]
        self.norm_data = self.__normalization__(self.data)  # Нормализация данных
        self.data = self.data[self.data.columns[:-1]]

        # Задание карты оптимального размера
        size = np.math.ceil(np.sqrt(5 * np.sqrt(len(self.data))))
        self.grid_rows = size
        self.grid_columns = size

    def __normalization__(self, data):
        """
        Функция, выполняющая нормализацию данных

        :param data: исходные данные

        :rtype: numpy.ndarray
        :return: нормализованные данные
        """
        sc = MinMaxScaler(feature_range=(0, 1))
        sc.fit(data)
        data = sc.fit_transform(data)
        return data

    def plot_som(self):
        """
        Функция отрисовки карты
        """
        xx, yy = self.som.get_euclidean_coordinates()
        umatrix = self.som.distance_map()
        weights = self.som.get_weights()

        w_x, w_y = zip(*[self.som.winner(d) for d in self.norm_data])
        w_x = np.array(w_x)
        w_y = np.array(w_y)

        # Маркеры данных
        self.markers = {'неудовл': 'p', 'удовл': 'X', 'хор': 'D', 'отл': 'H'}  # Форма меток
        self.colors = {'неудовл': 'darkgreen', 'удовл': 'olive', 'хор': 'yellowgreen',
                       'отл': 'lightgreen'}  # Цвета меток
        map_style = cm.Wistia  # Цветовая карта
        alpha = 1  # Прозрачность

        # Создание фигуры
        fig = plt.figure(figsize=(16, 8))
        fig.suptitle("Самоорганизующаяся карта Кохонена", fontsize=20)

        # Самоорганизующаяся карта Кохонена
        ax1 = fig.add_subplot(121)
        ax1.set_aspect('equal')
        # Создание поля
        for i in range(weights.shape[0]):
            for j in range(weights.shape[1]):
                wy = yy[(i, j)] * np.sqrt(3) / 2
                hex = RegularPolygon((xx[(i, j)], wy),
                                     numVertices=6,
                                     radius=0.9 / np.sqrt(3),
                                     facecolor=map_style(umatrix[i, j]),
                                     alpha=alpha,
                                     edgecolor='gray')
                ax1.add_patch(hex)
        for cnt, x in enumerate(self.norm_data):
            # Нейрон-победитель
            w = self.som.winner(x)
            # Размещение маркера на позицию победившего нейрона
            wx, wy = self.som.convert_map_to_euclidean(w)
            wy = wy * np.sqrt(3) / 2
            ax1.plot(wx, wy,
                     self.markers[self.target[cnt]],
                     markerfacecolor=self.colors[self.target[cnt]],
                     markeredgecolor=self.colors[self.target[cnt]],
                     markersize=12,
                     markeredgewidth=2)
        # Настройка делений осей
        xrange = np.arange(weights.shape[0] + 1)
        yrange = np.arange(weights.shape[1] + 1)
        ax1.set_xticks(xrange - 0.5, xrange)
        ax1.set_yticks(yrange * np.sqrt(3) / 2, yrange)
        # Настройка легенды
        legend_elements = []
        target_names = ['неудовл', 'удовл', 'хор', 'отл']
        for i in target_names:
            legend_elements.append(
                Line2D([0], [0], marker=self.markers[i], color=self.colors[i], label=self.label_names[i],
                       markerfacecolor=self.colors[i], markersize=5, linestyle='None',
                       markeredgewidth=2))
        ax1.legend(handles=legend_elements, loc='upper left', ncol=1, fontsize=8)

        # Отрисовка датасета на карте
        ax2 = fig.add_subplot(122)
        ax2.set_aspect('equal')
        plt.pcolor(self.som.distance_map().T, cmap=map_style, alpha=alpha)
        # Распределение данных по карте
        for c in target_names:
            idx_target = self.target == c
            ax2.scatter(w_x[idx_target] + .5 + (np.random.rand(np.sum(idx_target)) - .5) * .8,
                        w_y[idx_target] + .5 + (np.random.rand(np.sum(idx_target)) - .5) * .8,
                        s=40, c=self.colors[c], label=self.label_names[c])
        # Настройка легенды
        ax2.legend(loc='upper left', ncol=1, fontsize=8)

        # Отрисовка цветовой шкалы
        plt.colorbar()
        # plt.grid()
        plt.show()

    def plot_sample(self):
        xx, yy = self.som.get_euclidean_coordinates()
        umatrix = self.som.distance_map()
        weights = self.som.get_weights()

        w_test = self.som.winner(self.x_sample)
        x_test, y_test = self.som.convert_map_to_euclidean(w_test)
        y_test = y_test * np.sqrt(3) / 2

        # Маркеры данных
        self.markers = {'неудовл': 'p', 'удовл': 'X', 'хор': 'D', 'отл': 'H'}  # Форма меток
        self.colors = {'неудовл': 'darkgreen', 'удовл': 'olive', 'хор': 'yellowgreen',
                       'отл': 'lightgreen'}  # Цвета меток
        map_style = cm.Wistia  # Цветовая карта
        alpha = 1  # Прозрачность

        # Создание фигуры
        fig = plt.figure(figsize=(8, 8))

        # Самоорганизующаяся карта Кохонена
        ax = fig.add_subplot(111)
        ax.set_aspect('equal')
        # Создание поля
        for i in range(weights.shape[0]):
            for j in range(weights.shape[1]):
                wy = yy[(i, j)] * np.sqrt(3) / 2
                hex = RegularPolygon((xx[(i, j)], wy),
                                     numVertices=6,
                                     radius=0.9 / np.sqrt(3),
                                     facecolor=map_style(umatrix[i, j]),
                                     alpha=alpha,
                                     edgecolor='gray')
                ax.add_patch(hex)
        for cnt, x in enumerate(self.norm_data):
            # Нейрон-победитель
            w = self.som.winner(x)
            # Размещение маркера на позицию победившего нейрона
            wx, wy = self.som.convert_map_to_euclidean(w)
            wy = wy * np.sqrt(3) / 2
            ax.plot(wx, wy,
                    self.markers[self.target[cnt]],
                    markerfacecolor=self.colors[self.target[cnt]],
                    markeredgecolor=self.colors[self.target[cnt]],
                    markersize=12,
                    markeredgewidth=2)

        # Эксперимент
        ax.plot(x_test, y_test,
                marker='o',
                markerfacecolor='black',
                markeredgecolor='black',
                markersize=12)
        # Настройка делений осей
        xrange = np.arange(weights.shape[0] + 1)
        yrange = np.arange(weights.shape[1] + 1)
        ax.set_xticks(xrange - 0.5, xrange)
        ax.set_yticks(yrange * np.sqrt(3) / 2, yrange)
        # Настройка легенды
        legend_elements = []
        target_names = ['неудовл', 'удовл', 'хор', 'отл']
        for i in target_names:
            legend_elements.append(
                Line2D([0], [0], marker=self.markers[i], color=self.colors[i], label=self.label_names[i],
                       markerfacecolor=self.colors[i], markersize=8, linestyle='None',
                       markeredgewidth=2))
        ax.legend(handles=legend_elements, loc='upper left', ncol=1, fontsize=10)
        plt.show()

    def regression(self, x_sample):
        if not type(x_sample) == np.ndarray:
            self.x_sample = np.array(x_sample).reshape(1, -1)
        else:
            self.x_sample = x_sample
        model = LinearRegression()
        model.fit(self.data.to_numpy(), self.y)
        print(f"Regression score = {model.score(self.data.to_numpy(), self.y)}")
        self.y_pred = model.predict(self.x_sample)
        self.x_sample = np.append(self.x_sample, self.y_pred)


if __name__ == "__main__":
    som = SOM()
    som.learning()
    x = [5.2, 0.00075, 0.021, 9, 120, 21, 85, 92]
    som.regression(x)
    # print(f"Prediction = {float(som.y_pred)}")
    som.plot_sample()
    # som.plot_som()
