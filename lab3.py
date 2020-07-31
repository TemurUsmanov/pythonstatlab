import sys
import matplotlib.pyplot as plt

from PyQt5 import QtCore, QtGui
from numpy import linspace
from PyQt5.QtWidgets import QWidget, QApplication, QFileDialog, QLabel, QSlider, QComboBox, QLineEdit
from PyQt5.QtWidgets import QPushButton, QVBoxLayout, QHBoxLayout

from scipy.stats import shapiro
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from statsmodels.distributions.empirical_distribution import ECDF


class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.vector = list()
        self.initUI()

    def initUI(self):
        self.w,self.b,self.ce,self.ch=1,5,'blue','blue' 
        self.alpha=0.005
        self.hist = plt.figure()
        self.ecdf = plt.figure()

        self.canvas_hist = FigureCanvas(self.hist)
        self.canvas_hist.setFixedSize(400,300)
        self.canvas_ecdf = FigureCanvas(self.ecdf)
        self.canvas_ecdf.setFixedSize(400,300)

        self.btn_file = QPushButton('Выбрать файл')
        self.btn_file.clicked.connect(self.file_selection)

        self.btn_check_normality = QPushButton("Проверка на нормальность")
        self.btn_check_normality.clicked.connect(self.check_for_normality)

        self.check_result = QLabel()
        self.check_result.setAlignment(QtCore.Qt.AlignCenter)

        layout = QVBoxLayout()
        graphics1 = QHBoxLayout()
        graphics2 = QHBoxLayout()
        layout_ecdf = QVBoxLayout()
        layout_hist = QVBoxLayout()
        layout_hist1 = QHBoxLayout()
        layout_check = QHBoxLayout()

#ECDF
        graphics1.addWidget(self.canvas_ecdf)
        
        self.scroll=QSlider(QtCore.Qt.Horizontal)
        self.scroll.valueChanged[int].connect(self.changeValue)
        graphics1.addLayout(layout_ecdf)
        self.label_ecdf = QLabel()
        self.label_ecdf.setAlignment(QtCore.Qt.AlignCenter)
        self.label_ecdf.setText("Толщина линии")
        layout_ecdf.addWidget(self.label_ecdf)
        layout_ecdf.addWidget(self.scroll)
        
        self.combo=QComboBox(self)
        self.combo.addItems(["blue","red","green"])
        self.combo.activated[str].connect(self.onCombo)
        self.label_ecdf1 = QLabel()
        self.label_ecdf1.setAlignment(QtCore.Qt.AlignCenter)
        self.label_ecdf1.setText("Цвет линии")
        layout_ecdf.addWidget(self.label_ecdf1)
        layout_ecdf.addWidget(self.combo)


#HIST
        graphics2.addWidget(self.canvas_hist)
        graphics2.addLayout(layout_hist)
        layout_hist.addLayout(layout_hist1)
        self.label_hist = QLabel()
        self.label_hist.setAlignment(QtCore.Qt.AlignCenter)
        self.label_hist.setText("Bins =")
        layout_hist1.addWidget(self.label_hist)
        self.line=QLineEdit(self)
        self.line.setValidator(QtGui.QIntValidator(1, 10000))
        self.line.textChanged[str].connect(self.onLine)
        layout_hist1.addWidget(self.line)
        
        self.combo1=QComboBox(self)
        self.combo1.addItems(["blue","red","green"])
        self.combo1.activated[str].connect(self.onCombo1)
        self.label_hist1 = QLabel()
        self.label_hist1.setAlignment(QtCore.Qt.AlignCenter)
        self.label_hist1.setText("Цвет линии")
        layout_hist.addWidget(self.label_hist1)
        layout_hist.addWidget(self.combo1)
    
#Check
        self.label_c = QLabel()
        self.label_c.setAlignment(QtCore.Qt.AlignCenter)
        self.label_c.setText("Уровень значимости =")
        layout_check.addWidget(self.label_c)
        self.lineC=QLineEdit(self)
        self.lineC.setValidator(QtGui.QDoubleValidator(bottom=0,top=1,decimals=4,notation=QtGui.QDoubleValidator.StandardNotation))
        self.lineC.setValidator(QtGui.QDoubleValidator(1,0,4))
        self.lineC.textChanged[str].connect(self.onC)
        layout_check.addWidget(self.lineC)


        layout.addWidget(self.btn_file)
        layout.addLayout(graphics1)
        layout.addLayout(graphics2)
        layout.addLayout(layout_check)
        layout.addWidget(self.check_result)

        self.setLayout(layout)
        self.setWindowTitle("Лабораторная работа №3")

    def file_selection(self):

        file = QFileDialog.getOpenFileName(
            parent=self, caption="Выберите файл",)
        file_name = file[0]
        self.vector = list()
        with open(file_name, 'r') as data:
            for sample in data.read().split():
                self.vector.append(float(sample))
        #self.vector = sorted(self.vector)
        self.plot()

    def plot(self):
        ax_hist = self.hist.add_subplot(111)
        ax_hist.clear()
        ax_hist.hist(self.vector, bins=self.b, color=self.ch, normed=True)

        ax_ecdf = self.ecdf.add_subplot(111)
        ax_ecdf.clear()

        x = linspace(0, max(self.vector))
        ecdf = ECDF(self.vector)
        ax_ecdf.axis([0,x[-1],0,1])
        ax_ecdf.step(x, ecdf(x),color=self.ce,linewidth=self.w)

        self.canvas_hist.draw()
        self.canvas_ecdf.draw()

    def check_for_normality(self):
        if not self.vector:
            self.check_result.setText("Выберите файл с данными")
            return
        p_value = shapiro(self.vector)[1]
        if p_value > self.alpha:
            self.check_result.setText(
                "Гипотезу о нормальности распределения отвергать не стоит!")
        else:
            self.check_result.setText(
                "Гипотизу о нормальности распределения стоит отвергнуть!")

    def changeValue(self, value):
        self.w=value/20+1
        self.plot()

    def onCombo(self, text):
        self.ce=text
        self.plot()

    def onCombo1(self, text):
        self.ch=text
        self.plot()

    def onLine(self, text):
        if len(text) != 0:
            self.b=int(text)
            self.plot()

    def onC(self, text):
        if len(text) != 0:
            if text[-1]!=',':
                a=text.split(',')
                if len(a)!=1:
                    self.alpha=float(a[0])+float(a[-1])/(10**len(a[-1]))
                else:
                     self.alpha=float(a[0])   
                if self.alpha != 0:
                    print(self.alpha)
                    self.check_for_normality()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    main = Window()
    main.show()

    sys.exit(app.exec_())
