import random
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIntValidator, QDoubleValidator, QFont, QIcon
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QMessageBox, QDesktopWidget, \
    QCheckBox, QTableWidget, QTableWidgetItem, QAbstractItemView, QHeaderView

import genetic
import guigraph
# noinspection PyUnresolvedReferences
from math import *


def input_error(text):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Warning)
    msg.setText('Неверно введены данные')
    msg.setInformativeText(text)
    msg.setWindowTitle('Ошибка')
    msg.setWindowIcon(QIcon('warning.png'))
    msg.exec()


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        f = QFont("Times", 10)
        self.setWindowIcon(QIcon('dna.png'))

        # Валидаторы проверяющие тип ввода
        only_int = QIntValidator()
        only_float = QDoubleValidator()
        only_float.setNotation(QDoubleValidator.StandardNotation)
        only_float.setRange(float(0), float(1), 6)

        # Текстовые поля
        self.params = QLabel('Parameters', self)
        self.params.setFont(QFont("Times", 10, QFont.Bold, QFont.StyleItalic))
        self.params.move(10, 10)

        self.table_label = QLabel('Output table', self)
        self.table_label.setFont(QFont("Times", 10, QFont.Bold, QFont.StyleItalic))
        self.table_label.move(450, 10)

        self.control = QLabel('Control', self)
        self.control.setFont(QFont("Times", 10, QFont.Bold, QFont.StyleItalic))
        self.control.move(10, 270)

        self.output = QLabel('Output', self)
        self.output.setFont(QFont("Times", 10, QFont.Bold, QFont.StyleItalic))
        self.output.move(10, 350)

        # Ввод функции
        self.fitness_label = QLabel('Input function:', self)
        self.fitness_label.move(10, 40)
        self.fitness_input = QLineEdit(self)
        self.fitness_input.setText('x**2+3*y**2+2*x*y')
        self.fitness_input.setPlaceholderText('Input your f(x, y)')
        self.fitness_input.setReadOnly(True)
        self.fitness_input.move(160, 40)
        self.fitness_input.setMinimumWidth(250)

        # Создание меток и полей ввода для параметров
        self.population_size_label = QLabel('Population size:', self)
        self.population_size_input = QLineEdit(self)
        self.population_size_input.setText('100')
        self.population_size_input.setPlaceholderText('int, >=2')
        self.population_size_input.setValidator(only_int)

        self.generations_label = QLabel('Generations:', self)
        self.generations_input = QLineEdit(self)
        self.generations_input.setPlaceholderText('int, >=0')
        self.generations_input.setText('10')
        self.generations_input.setValidator(only_int)

        self.crossover_rate_label = QLabel('Crossover rate:', self)
        self.crossover_rate_input = QLineEdit(self)
        self.crossover_rate_input.setText('0.5')
        self.crossover_rate_input.setToolTip('Note: 2 parents -> 2 children')
        self.crossover_rate_input.setPlaceholderText('float, [0, 1]')
        self.crossover_rate_input.setValidator(only_float)

        self.mutation_rate_label = QLabel('Mutation rate:', self)
        self.mutation_rate_input = QLineEdit(self)
        self.mutation_rate_input.setText('0.2')
        self.mutation_rate_input.setPlaceholderText('float, [0, 1]')
        self.mutation_rate_input.setValidator(only_float)

        self.edit_checkbox = QCheckBox('I want custom function (test, slower)', self)
        self.edit_checkbox.setFont(f)
        self.edit_checkbox.toggled.connect(self.edit_on_clicked)
        self.stabilize_checkbox = QCheckBox('Stabilize population size', self)
        self.stabilize_checkbox.setFont(f)
        self.stabilize_checkbox.toggled.connect(self.stabilization_clicked)

        # Создание кнопок
        self.start_button = QPushButton('Start', self)
        self.start_button.clicked.connect(self.run_algorithm)

        self.reset_button = QPushButton('Reset parameters', self)
        self.reset_button.clicked.connect(self.reset_params)
        self.reset_button.setMinimumWidth(200)

        self.draw_button = QPushButton('Draw', self)
        self.draw_button.setToolTip('Note: slow for complicated functions')
        self.draw_button.clicked.connect(self.draw)
        self.draw_window = None

        # Расположение элементов ввода на окне
        self.population_size_label.move(10, 80)
        self.population_size_input.move(160, 80)

        self.generations_label.move(10, 110)
        self.generations_input.move(160, 110)

        self.crossover_rate_label.move(10, 140)
        self.crossover_rate_input.move(160, 140)

        self.mutation_rate_label.move(10, 170)
        self.mutation_rate_input.move(160, 170)

        self.edit_checkbox.move(10, 200)
        self.stabilize_checkbox.move(10, 230)

        self.start_button.move(10, 300)
        self.reset_button.move(126, 300)
        self.draw_button.move(330, 300)

        # Вывод результатов 290
        self.best_sol_label = QLabel('Best solution:', self)
        self.best_sol = QLabel('f(x, y):', self)
        self.best_sol.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.best_sol_coord = QLabel('x:\ny:', self)
        self.best_sol_coord.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.iters = QLabel('Iterations finished: 0', self)
        self.best_sol.setMinimumWidth(350)
        self.best_sol_coord.setMinimumWidth(350)
        self.iters.setMinimumWidth(300)

        self.best_sol_label.setFont(f)
        self.best_sol.setFont(f)
        self.best_sol_coord.setFont(f)
        self.iters.setFont(f)

        self.best_sol_label.move(10, 380)
        self.best_sol.move(10, 410)
        self.best_sol_coord.move(10, 440)
        self.iters.move(10, 500)

        # Шрифты
        self.fitness_input.setFont(f)
        self.fitness_label.setFont(f)
        self.population_size_input.setFont(f)
        self.population_size_label.setFont(f)
        self.generations_label.setFont(f)
        self.generations_input.setFont(f)
        self.crossover_rate_input.setFont(f)
        self.crossover_rate_label.setFont(f)
        self.mutation_rate_input.setFont(f)
        self.mutation_rate_label.setFont(f)
        self.start_button.setFont(f)
        self.reset_button.setFont(f)
        self.draw_button.setFont(f)

        # Создание таблицы вывода
        self.table = QTableWidget(self)
        self.table.setColumnCount(3)
        self.table.setFixedWidth(500)
        self.table.setFixedHeight(500)
        self.table.move(450, 40)
        self.table.setHorizontalHeaderItem(0, QTableWidgetItem('Result'))
        self.table.setHorizontalHeaderItem(1, QTableWidgetItem('Gene 1'))
        self.table.setHorizontalHeaderItem(2, QTableWidgetItem('Gene 2'))
        self.table.setColumnWidth(0, 150)
        self.table.setColumnWidth(1, 150)
        self.table.setColumnWidth(2, 150)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setRowCount(1)

        # Установка размеров окна и заголовка
        self.resize(1000, 550)
        self.setWindowTitle('Genetic Algorithm')

        # Окно в центр экрана
        qt_rectangle = self.frameGeometry()
        center_point = QDesktopWidget().availableGeometry().center()
        qt_rectangle.moveCenter(center_point)
        self.move(qt_rectangle.topLeft())

    def draw(self):
        if self.edit_checkbox.isChecked() and self.table.rowCount() == 1:
            input_error('Рассчитайте минимум перед построением графика')
            return
        self.draw_window = guigraph.DrawWindow(table=self.table)
        self.draw_window.show()

    def refresh_table(self, values):
        self.table.clearContents()
        self.table.setRowCount(len(values))
        for i in range(len(values)):
            self.table.setItem(i, 0, QTableWidgetItem(str(round(genetic.ff(values[i]), 3))))
            self.table.setItem(i, 1, QTableWidgetItem(str(round(values[i][0], 3))))
            self.table.setItem(i, 2, QTableWidgetItem(str(round(values[i][1], 2))))

    def reset_params(self):
        self.population_size_input.setText('100')
        self.generations_input.setText('10')
        self.crossover_rate_input.setText('0.5')
        self.mutation_rate_input.setText('0.2')

    def stabilization_clicked(self):
        genetic.toggle_stabilization()
        if self.stabilize_checkbox.isChecked():
            self.crossover_rate_input.setText('0.5')
            self.crossover_rate_input.setReadOnly(True)
        else:
            self.crossover_rate_input.setReadOnly(False)

    def edit_on_clicked(self):
        if self.edit_checkbox.isChecked():
            self.fitness_input.setReadOnly(False)
            self.fitness_input.clear()
        if not self.edit_checkbox.isChecked():
            self.fitness_input.setReadOnly(True)
            self.fitness_input.setText('x**2+3*y**2+2*x*y')
            genetic.reset_ff()

    def set_res(self, ff, sol, i):
        print(str(ff), str(sol[0]), str(sol[1]), str(i))
        self.best_sol.setText('f(x,y): ' + str(ff))
        self.best_sol_coord.setText('x:       ' + str(sol[0]) + '\ny:       ' + str(sol[1]))
        self.iters.setText('Iterations finished: ' + str(i))

    def run_algorithm(self):
        # Получение параметров из полей ввода
        if self.edit_checkbox.isChecked():
            try:
                expr = str(self.fitness_input.text())
                test_func = lambda x, y: eval(expr)
                for i in range(10):
                    a = random.randint(-10, 10)
                    b = random.randint(-10, 10)
                    if isinstance(test_func(a, b), complex):
                        input_error('Введена комплексная функция')
                        return
                genetic.fitness_function = lambda x, y: eval(expr)
            except SyntaxError:
                input_error('Некорректная функция')
                return
            except NameError:
                input_error('Использована недоступная функция')
                return
        try:
            population_size = int(self.population_size_input.text())
            generations = int(self.generations_input.text())
            crossover_rate = float(self.crossover_rate_input.text())
            mutation_rate = float(self.mutation_rate_input.text())
        except ValueError:
            input_error('Проверьте правильность введенных параметров')
            return

        try:
            genetic.set_args(population_size, generations, crossover_rate, mutation_rate)
        except ValueError as e:
            input_error(str(e))
            return
        # Запуск генетического алгоритма с полученными параметрами
        i = -1
        best_res = 0
        best_solution = 0
        res = 0
        for generation in genetic.next_gen():
            i += 1
            if not generation:
                print('Population is extinct')
                i -= 1
                break
            generation.sort(key=genetic.ff)
            best_solution = generation[0]
            best_res = genetic.ff(best_solution)
            print("Generation:", i, "Optimal solution:", best_solution,
                  "Fitness:", genetic.fitness_function(*best_solution), "Population size:", len(generation))
            res = generation
        self.set_res(best_res, best_solution, i)
        self.refresh_table(res)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
