from os import getcwd, path, remove

import numpy as np
import plotly.graph_objects as go
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QIcon, QCloseEvent
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableWidget
from plotly import io

import genetic


class DrawWindow(QWidget):
    def __init__(self, parent=None, table: QTableWidget = None):
        # Инициализация окна и необходимых параметров
        super(DrawWindow, self).__init__(parent)
        self.setWindowTitle("Interactive graph")
        self.resize(800, 800)
        self.setWindowIcon(QIcon('plot.png'))
        self.filename = 'graph.html'
        self.table = table

        # Инициализация интерфейса для открытия html
        self.web_view = QWebEngineView()
        layout = QVBoxLayout()
        layout.addWidget(self.web_view)
        self.setLayout(layout)

        self.draw_html()

    def add_points(self, fig: go.Figure):
        x = []
        y = []
        z = []
        for i in range(self.table.rowCount()):
            x.append(float(self.table.item(i, 1).text()))
            y.append(float(self.table.item(i, 2).text()))
            z.append(float(self.table.item(i, 0).text()))
        fig.add_trace(go.Scatter3d(x=x, y=y, z=z, mode='markers', marker=dict(size=5)))

    def draw_html(self):
        z = genetic.fitness_function
        _x, _y = np.mgrid[-4:4:300j, -4:4:300j]

        _z = np.zeros((300, 300), dtype=float)
        i = 0
        for x in _x:
            j = 0
            for y in _y:
                _z[i][j] = z(x[i], y[j])
                j += 1
            i += 1

        fig = go.Figure(go.Surface(
            x=_x,
            y=_y,
            z=_z,
        ))

        if self.table.rowCount() != 1:
            self.add_points(fig)

        # fig.update_layout(title_text="My func")
        with open(self.filename, 'w') as f:
            f.write(io.to_html(fig))
        self.web_view.load(QUrl.fromLocalFile(getcwd() + '\\' + self.filename))

    def closeEvent(self, a0: QCloseEvent) -> None:
        if path.isfile(self.filename):
            remove(self.filename)
        a0.accept()
