"""Программа создана в учебных целях,
приемы используемые в программе могут быть не очень логичны - 
но в учебных целях очень помогают понять некоторые вещи,
используемые модули и библиотеки взяты для обучения,
базу данных в реальном проекте заменить"""
from PyQt5.QtWidgets import QApplication
from docdb import MyWindow

if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    window = MyWindow()
    window.setWindowTitle('Поиск документа по базе')
    window.resize(0, 0)  # убиваем QMainWidget
    # window.move(10, 10)
    # window.show()
    window.win1()
    sys.exit(app.exec_())
