from minisom import MiniSom

import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler

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
        self.data = None

    def learning(self):
        """
        Функция обучения сети
        """
        self.data = self.data_preprocessing()
        self.som = MiniSom(self.grid_rows, self.grid_columns, self.data.shape[1],
                           sigma=self.sigma,
                           learning_rate=self.learning_rate,
                           activation_distance='euclidean',
                           topology='hexagonal',
                           neighborhood_function='gaussian')
        self.som.train(self.data, self.epochs, verbose=True)

    def data_preprocessing(self):
        """
        Функция, выполняющая чтение и обработку датесета

        :rtype: numpy.ndarray
        :return: массив данных
        """
        # Чтение данных из файла
        data = pd.read_excel(self.fname)
        data = data.rename(columns=data.iloc[0]).drop(data.index[0])

        # Извлечение меток данных
        self.target = data['Type'].values
        self.label_names = {1: 'Type 1', 2: 'Type 2', 3: 'Type 3'}
        data = data[data.columns[:-1]]

        # Нормализация данных
        data = self.__normalization__(data)

        # Задание карты оптимального размера
        size = np.math.ceil(np.sqrt(5 * np.sqrt(len(data))))
        self.grid_rows = size
        self.grid_columns = size
        return data

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

        w_x, w_y = zip(*[self.som.winner(d) for d in self.data])
        w_x = np.array(w_x)
        w_y = np.array(w_y)

        # Маркеры данных
        markers = ['p', 'X', '*']  # Форма меток
        colors = ['brown', 'darkgreen', 'navy']  # Цвета меток
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
        for cnt, x in enumerate(self.data):
            # Нейрон-победитель
            w = self.som.winner(x)
            # Размещение маркера на позицию победившего нейрона
            wx, wy = self.som.convert_map_to_euclidean(w)
            wy = wy * np.sqrt(3) / 2
            ax1.plot(wx, wy,
                     markers[self.target[cnt] - 1],
                     markerfacecolor=colors[self.target[cnt] - 1],
                     markeredgecolor=colors[self.target[cnt] - 1],
                     markersize=12,
                     markeredgewidth=2)
        # Настройка делений осей
        xrange = np.arange(weights.shape[0] + 1)
        yrange = np.arange(weights.shape[1] + 1)
        ax1.set_xticks(xrange - 0.5, xrange)
        ax1.set_yticks(yrange * np.sqrt(3) / 2, yrange)
        # Настройка легенды
        legend_elements = []
        for i in range(len(np.unique(self.target))):
            legend_elements.append(Line2D([0], [0], marker=markers[i], color=colors[i], label=self.label_names[i + 1],
                                          markerfacecolor=colors[i], markersize=14, linestyle='None',
                                          markeredgewidth=2))
        ax1.legend(handles=legend_elements, bbox_to_anchor=(0, 1.08), loc='upper left',
                   borderaxespad=0, ncol=3, fontsize=12)

        # Отрисовка датасета на карте
        ax2 = fig.add_subplot(122)
        ax2.set_aspect('equal')
        plt.pcolor(self.som.distance_map().T, cmap=map_style, alpha=alpha)
        # Распределение данных по карте
        for c in np.unique(self.target):
            idx_target = self.target == c
            ax2.scatter(w_x[idx_target] + .5 + (np.random.rand(np.sum(idx_target)) - .5) * .8,
                        w_y[idx_target] + .5 + (np.random.rand(np.sum(idx_target)) - .5) * .8,
                        s=40, c=colors[c - 1], label=self.label_names[c])
        # Настройка легенды
        ax2.legend(bbox_to_anchor=(0, 1.08), loc='upper left',
                   borderaxespad=0, ncol=3, fontsize=12)

        # Отрисовка цветовой шкалы
        plt.colorbar()
        # plt.grid()
        plt.show()


if __name__ == "__main__":
    som = SOM()
    som.learning()
    som.plot_som()
