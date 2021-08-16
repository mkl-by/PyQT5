from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QWidget, QPushButton, QLabel, QVBoxLayout, QFileDialog, QMainWindow
# from createdb import Openfile
import os, pathlib, connection, sys, pickle
from parsing_docx import Pars_doc

class MyWindow(QMainWindow):
    """размер этого окна делаем равным (0.0), смотри main
    тут собираем все окна воедино"""
    def __init__(self):
        super().__init__()

    def win1(self):
        self.w1 = Windowmy()
        self.w1.but3.clicked.connect(self.win2)
        self.w1.show()

    def win2(self):

        self.w2 = connection.Sqlmodelout()
        self.w2.resize(1160,700)
        self.w2.show()


class Windowmy(QWidget):
    """СЧИТАЕМ ЭТО ОКНО ГЛАВНЫМ"""
    def __init__(self):
        QWidget.__init__(self)
        self.dirtabl = None
        self.path = os.path.abspath(os.curdir)  # директория к базе (коду)
        self.path_file_doc = []
        self.basa_on = self.basa_search()
        self.initUI()

    def closeEvent(self, e):
        """если закрыть окно закрываем и главное окно"""
        sys.exit()


    def initUI(self):
        self.label = QLabel('Выберите необходимое действие')
        self.but1 = QPushButton('Выбрать папку с файлами')
        self.but2 = QPushButton('Добавить данные в базу')
        self.but3 = QPushButton('Открыть базу')
        self.but4 = QPushButton('Открыть файл для добавления данных в базу')

        self.vbox = QVBoxLayout()
        self.vbox.addWidget(self.label)
        self.vbox.addWidget(self.but1)
        self.vbox.addWidget(self.but2)
        self.vbox.addWidget(self.but3)
        self.vbox.addWidget(self.but4)

        self.setLayout(self.vbox)

        #если база есть отключаем кнопку поиска файлов для базы
        if self.basa_on:
            self.but1.setEnabled(False)

        self.but1.clicked.connect(self.dirdbtabl)

        #добавляем данные в базу
        self.but2.clicked.connect(self.adddatadb)

        #добавляем данные из одного файла в базу
        self.but4.clicked.connect(self.add_one_file_db)


    def basa_search(self):
        """определяем наличие файла базы, если нет создали """
        p = pathlib.Path(self.path)
        dier = [i.name for i in p.iterdir() if i.name == 'basa.sqlite']

        if dier:
            return True
        else:
            #тут создали файл базы данных, sqlite для этих целей вполне достаточно
            connection.createcon()

            return False

    def dirdbtabl(self):
        '''выбираем директорию для поиска описей'''

        self.dirtabl = QFileDialog.getExistingDirectoryUrl(caption='Выберите директорию с файлами',
                                                           directory=QtCore.QUrl.fromLocalFile(QtCore.QDir.currentPath()))
        # из папки которую выбрали отбираем файлы с расширением
        p = pathlib.Path(self.dirtabl.path())
        #отбираем пути док файлов
        for i in p.glob('*.docx'):
            self.path_file_doc.append(i)
            print(i)
        #пишем в файл пути к выбранной папке
        with open('data.pickle', 'wb') as f:
            pickle.dump(self.path_file_doc, f)


    def pars_and_adddatadb(self, data):
        """читаем пути к файлам, отдаем для парсинга, пишем в базу"""

        for path in data:
            #парсим таблицу
            data_pars = Pars_doc(path)

            #пишем в базу
            connection.createconnection(data_pars.tabl)

    def read_path_file(self):
        """читаем файл"""
        try:
            with open('data.pickle', 'rb') as f:
                data = pickle.load(f)
        except FileNotFoundError:
            return (os.getcwd(), False) #возвращаем текущий каталог, если нет данных или файла
        print(data)
        return (data, True)


    def adddatadb(self):
        """читаем пути к файлам, отдаем для парсинга, пишем в базу, для всех файлов doc"""
        data, flag = self.read_path_file()
        if flag:
            self.pars_and_adddatadb(data)
        else:
            self.dirdbtabl()


    def add_one_file_db(self):
        """выбираем один файл из которого необходимо добавить данные в базу"""
        path = []
        path_file, flag = self.read_path_file()
        path_dir = os.path.dirname(path_file[0])


        file = QFileDialog.getOpenFileUrl(caption='Выберите файл для добавления в базу',
                                          directory=QtCore.QUrl.fromLocalFile(path_dir),
                                          filter="Docx (*.docx)", initialFilter="Docx (*.docx)",
                                          )


        path.append(file[0].toLocalFile())

        if path[0] != '':
            self.pars_and_adddatadb(path)






