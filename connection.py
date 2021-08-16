from PyQt5 import QtSql, QtWidgets, QtCore, QtGui


def condb():
    db = QtSql.QSqlDatabase.addDatabase('QSQLITE')
    db.setDatabaseName('basa.sqlite')
    db.open()
    return db


def createcon():
    """в случае отсутствия базы создаем ee и таблицу"""
    db = condb()
    if 'datas' not in db.tables():
        query = QtSql.QSqlQuery()
        query.exec("""create table datas (id integer primary key autoincrement, 
                                                               point integer,
                                                               numberin text (20),                                                         
                                                               numberout text (20),
                                                               datadoc   date,
                                                               instanse  text (6),
                                                               namedoc   text (80),
                                                               numberpage varchar (12),
                                                               casenum integer,
                                                               tome integer, 
                                                               datadatetime integer
                                                               
                                                               )""")
    db.close()


def createconnection(dat):
    """пишем данные в таблицу"""
    val_case_tom = dat.pop(0)
    db = condb()
    query = QtSql.QSqlQuery()

    for rec in dat:
        # проверяем наличие в базе записываемых данных
        try:
            s = rec['входящий номер'][0][0]
        except (IndexError, KeyError):
            s = rec['входящий номер']

        try:
            ss = rec['исходящий номер'][0]
        except IndexError:
            ss = rec['исходящий номер']

        sel = f"select * from datas where numberin='{s}' and numberout='{ss}' and datadoc='{rec['дата документа']}'"
        query.exec(sel)
        query.first()
        # если в базе есть записываемые данные, пропускаем запись
        if query.isValid():
            continue
        query.clear()

        # пишем в базу данные прошедшие проверку на наличие в базе
        query.prepare("insert into datas values (null, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)")
        query.addBindValue(rec['порядковый номер'])
        # организуем проверку наличия данных в базе

        query.addBindValue(s)
        query.addBindValue(ss)

        query.addBindValue(rec['дата документа'])
        query.addBindValue(rec['экземпляр'])
        query.addBindValue(rec['документ'])

        if len(rec['страницы']) == 1:
            query.addBindValue(rec['страницы'][0])
        else:
            recc = f'{rec["страницы"][0]}-{rec["страницы"][1]}'
            query.addBindValue(recc)

        query.addBindValue(val_case_tom['дело'])
        query.addBindValue(val_case_tom['том'])

        query.addBindValue(rec['дата дока'])
        query.exec_()

    db.close()


def searchData():
    pass


def searchdb():
    """поиск по базе, создаем новую таблицу в оперативной памяти
    и отображаем ее в той же таблице"""
    db = QtSql.QSqlDatabase.addDatabase('QSQLITE')
    db.setDatabaseName()
    db.open()


class sqlmodeldataout():
    def __init__(self, tabl='datas'):
        self.db = condb()
        self.model1 = QtSql.QSqlTableModel()
        self.model1.setTable(tabl)
        # self.model1.select()
        # self.db.close()


class Sqlmodelout(QtWidgets.QWidget):
    """отображаем модель"""

    def __init__(self, tabl='datas', parent=None):
        super().__init__(parent)
        self.db = condb()  # без этого не работает
        layout = QtWidgets.QVBoxLayout(self)
        layout_h = QtWidgets.QHBoxLayout(self)
        self.line = QtWidgets.QLineEdit()
        self.linenumber = QtWidgets.QLineEdit()
        self.label = QtWidgets.QLabel('Поиск по всем ячейкам')
        self.labelnumber = QtWidgets.QLabel('Поиск по входящему номеру')
        self.labelout = QtWidgets.QLabel('Поиск по исходящему номеру')
        self.dataname = QtWidgets.QLabel(' ')
        self.button = QtWidgets.QPushButton('Поиск')

        self.datanamein = QtWidgets.QLabel('Поиск в диапазоне дат                         C ')
        self.datanamein.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.datanameout = QtWidgets.QLabel('По ')
        self.datanameout.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.lineout = QtWidgets.QLineEdit()
        self.datain = QtWidgets.QDateEdit()
        self.datain.setCalendarPopup(True)
        self.dataout = QtWidgets.QDateEdit()
        self.dataout.setCalendarPopup(True)

        # делаем валидацию на linenumber входящие документы
        reg = QtCore.QRegExp(r'(\d?\d?\d?\d(kkk|k|kk|оk)?-kk)')  # можно взять из класса Pars_doc
        numberin = QtGui.QRegExpValidator(reg, self.linenumber)
        self.linenumber.setValidator(numberin)

        # делаем валидацию на lineout на исходящие документы
        reg1 = QtCore.QRegExp(r'(((0|1)/0/)\d?\d?\d(kkk|k|kk|оk)?-kk)')
        numberout = QtGui.QRegExpValidator(reg1, self.lineout)
        self.lineout.setValidator(numberout)

        self.view = QtWidgets.QTableView()  # представление
        self.proxymodel = QtCore.QSortFilterProxyModel()  # промежуточная модель

        layout.addWidget(self.view)
        layout.addWidget(self.label)
        layout.addWidget(self.line)
        layout.addWidget(self.labelnumber)
        layout.addWidget(self.linenumber)
        layout.addWidget(self.labelout)
        layout.addWidget(self.lineout)
        layout.addWidget(self.dataname)

        layout_h.addWidget(self.datanamein)
        layout_h.addWidget(self.datain)
        layout_h.addWidget(self.datanameout)
        layout_h.addWidget(self.dataout)
        layout_h.addWidget(self.button)

        layout.addLayout(layout_h)

        # создаем модель связанную с таблицей tabl
        self.model = QtSql.QSqlTableModel()
        self.model.setTable(tabl)

        self.headerinstall(self.model)
        # меняем заголовки в таблице на те, что в списке

    def headerinstall(self, modelka):
        header = ['Номер в описи', 'Входящий номер', 'Исходящий номер', 'Дата документа',
                  'Экземпляр', 'Наименование',
                  'Страницы', 'Номер дела', 'Номер тома']
        for i, head in enumerate(header, start=1):
            modelka.setHeaderData(i, QtCore.Qt.Horizontal, head)

        # создаем промежуточную модель для организации фильтрации и поиска
        self.prox()

        self.proxymodel.setFilterFixedString('')

        self.view.setModel(self.proxymodel)  # добавляем модель

        self.view.hideColumn(0)  # делаем невидимыми колонки
        self.view.hideColumn(10)
        self.view.resizeColumnsToContents()  # подгоняем по ширине строк
        self.view.setSortingEnabled(True)
        # при вводе текста осуществляем поиск
        self.line.textChanged[str].connect(self.onChanged)
        self.linenumber.textChanged[str].connect(self.onChangedNumber)
        self.lineout.textChanged[str].connect(self.onChangedNumberOut)
        # self.dataout.dateChanged.connect(self.onChangeddata)
        self.button.clicked.connect(self.onChangeddata)
        self.model.select()
        self.db.close()

    def prox(self):
        """создание промежуточной модели"""
        self.proxymodel.setSourceModel(self.model)  # создаем промежуточную модель
        self.proxymodel.setFilterKeyColumn(-1)  # ищем во всех ячейках
        self.proxymodel.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)  # не учитываем регистр

    def onChanged(self):
        """Осуществляет поиск по всем ячейкам"""
        # поиск по таблице по каждой ячейке
        self.proxymodel.setFilterFixedString(self.line.text())
        self.view.setModel(self.proxymodel)  # добавляем модель

    def onChangedNumber(self):
        """Осуществляет поиск по номеру документа, входящего"""
        self.proxymodel.setFilterKeyColumn(2)
        self.proxymodel.setFilterFixedString(self.linenumber.text())
        self.view.setModel(self.proxymodel)  # добавляем модель

    def onChangedNumberOut(self):
        """Осуществляет поиск по номеру документа, входящего"""
        self.proxymodel.setFilterKeyColumn(3)
        self.proxymodel.setFilterFixedString(self.lineout.text())
        self.view.setModel(self.proxymodel)  # добавляем модель

    def onChangeddata(self):
        # создаем модельку
        m = sqlmodeldataout()
        # изменяем заголовки
        self.headerinstall(m.model1)
        # берем дату начала и конца поиска datetime.date в pyqt5
        din = self.datain.date().toPyDate().toordinal()
        dout = self.dataout.date().toPyDate().toordinal()

        if din > dout:
            self.dataname.setFont(QtGui.QFont("Sanserif", 18))
            self.dataname.setStyleSheet('color:red')
            self.dataname.setAlignment(QtCore.Qt.AlignHCenter)
            self.dataname.setText('Дата начала поиска не должна быть больше даты окончания поиска, повторите ввод')
        elif din == dout:
            self.dataname.setText(' ')
            # ПОСЛЕДНЕЕ ЗНАЧЕНИЕ делаем выборку из данных диапазон дат
            m.model1.setFilter('datadatetime = {0}'.format(dout))
        else:
            self.dataname.setText(' ')
            # ПОСЛЕДНЕЕ ЗНАЧЕНИЕ делаем выборку из данных диапазон дат
            m.model1.setFilter('datadatetime <= {0} and datadatetime >= {1}'.format(dout, din))

        m.model1.select()

        # отображаем
        self.view.setModel(m.model1)


if __name__ == "__main__":
    datas = [{'дело': 3, 'том': 3},
             {'порядковый номер': '1', 'входящий номер': [('3k-kk', 'k')], 'дата документа': '30.12.2019',
              'исходящий номер': '', 'экземпляр': '7', 'документ': 'Мама мыла раму', 'страницы': ('7',)},
             {'порядковый номер': '2', 'входящий номер': [('304kkk-kk', 'kkk')], 'дата документа': '12.12.2017',
              'исходящий номер': '', 'экземпляр': '2', 'документ': 'Папа не мыл раму', 'страницы': ('1', '2')},
             {'порядковый номер': '3', 'входящий номер': '', 'исходящий номер': ('0/1/0kkk-kk', 'kkk'),
              'дата документа': '10.11.2013', 'экземпляр': '2', 'документ': 'Саша читал книгу', 'страницы': ('3', '4')},
             {'порядковый номер': '4', 'входящий номер': [('555kk-kk', 'kk')], 'дата документа': '12.12.2019',
              'исходящий номер': '', 'экземпляр': '3', 'документ': 'Кролик ел марковку ', 'страницы': ('5', '7')}]
    # createcon()

    createconnection(datas)
    # for i in x.tabl:
    #     print(i)
    # import sys
    # app = QtWidgets.QApplication(sys.argv)
    # windo = Sqlmodelout()
    # windo.setWindowTitle('Поиск документа по базе')
    # windo.resize(300, 300)
    # # window.move(10, 10)
    # # print(QtCore.QPoint().x(), QtCore.QPoint().x())
    # windo.show()
    # sys.exit(app.exec_())
