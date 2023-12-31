import sys
from PyQt5 import uic
from PyQt5.QtWidgets import (
    QApplication, 
    QMainWindow, 
    QTableWidgetItem, 
    QWidget, 
    QMessageBox
)
import sqlite3


class AddCoffeeForm(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('addEditCoffeeForm.ui', self)
        self.main_window = False
        self.coffeeID = False
        self.initUI()
        self.show()
    
    def initUI(self):
        pass
    
    def setID(self, ID):
        self.coffeeID = ID

    def set_main(self, window):
        self.main_window = window   

    # Метод проверяющий на изменение кофе
    def get_editing_verdict(self):
        if self.name.toPlainText() and \
           self.status.toPlainText() and \
           self.moloti.toPlainText() and \
           self.description.toPlainText() and \
           self.price.toPlainText() and \
           self.volume.toPlainText():
            return True
        else:
            return False
    
    def update_values(self):
        query = """SELECT * from coffee WHERE id == """ + self.coffeeID
        data = self.main_window.do_query(query)[0]
        self.name.setPlainText(data[1])
        self.status.setPlainText(str(data[2]))
        self.moloti.setPlainText(data[3])
        self.description.setPlainText(data[4])
        self.price.setPlainText(str(data[5]))
        self.volume.setPlainText(str(data[6]))

    def create_coffee(self):
        if self.get_editing_verdict():
            name = self.name.toPlainText()
            status = self.status.toPlainText()
            moloti = self.moloti.toPlainText()
            description = self.description.toPlainText()
            price = self.price.toPlainText()
            volume = self.volume.toPlainText()
            # Делаем запрос к бд и вносим изменения
            query = f"""
            INSERT into coffee
            ('название сорта', 'степень обжарки', 'молотый/в зернах', 'описание вкуса', 'цена', 'объем упаковки')
            VALUES ('{name}', {status}, '{moloti}', '{description}', {price}, {volume})
            """
            self.main_window.do_query(query)
            self.main_window.update_table(self.main_window.do_query())
            self.close()
        
    def edit_coffee(self):
        if self.get_editing_verdict():
            name = self.name.toPlainText()
            status = self.status.toPlainText()
            moloti = self.moloti.toPlainText()
            description = self.description.toPlainText()
            price = self.price.toPlainText()
            volume = self.volume.toPlainText()
            # Формируем запрос
            query = f"""
            UPDATE coffee
            SET 'название сорта' = '{name}', 
            'степень обжарки' = {status}, 
            'молотый/в зернах' = '{moloti}', 
            'описание вкуса' = '{description}',
            'цена' = {price},
            'объем упаковки' = {volume}
            WHERE ID = {self.coffeeID}
            """
            # Изменяем в бд фильм
            self.main_window.do_query(query)
            # Обновляем таблицу после применения изменений в бд с помощью метода главног класса
            self.main_window.update_table(self.main_window.do_query())
            self.close()
            

class Espresso(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main.ui', self)
        self.InitUI()
    
    def InitUI(self):
        self.update_table(self.do_query())
        self.addbtn.clicked.connect(self.addCoffee)
        self.editBtn.clicked.connect(self.editCoffee)
        self.deleteBtn.clicked.connect(self.deleteCoffee)
    
    def do_query(self, query="SELECT * from coffee"):
        res = ''
        con = sqlite3.connect('coffee.sqlite')
        cur = con.cursor()
        if 'SELECT' in query:
            res = cur.execute(query).fetchall()
        else:
            cur.execute(query)
            con.commit()
        con.close()
        if res:
            return res

    def update_table(self, data):
        self.tableWidget.setRowCount(len(data))
        self.tableWidget.setColumnCount(len(data[0]))
        labels = ['ID', 'название сорта', 'степень обжарки', 'молотый/в зернах', 'описание вкуса',
                  'цена', 'объем упаковки']
        self.tableWidget.setHorizontalHeaderLabels(labels)
        for row in range(len(data)):
            for column in range(len(data[0])):
                self.tableWidget.setItem(row, column, QTableWidgetItem(str(data[row][column])))

    def addCoffee(self):
        # При нажатии на кнопку инициализируем обьект клааса создания кофе
        self.add_coffee_widget = AddCoffeeForm()
        # Устанавливаем объект основного класса
        self.add_coffee_widget.set_main(self)
        # Добавляем название нашему окну
        self.add_coffee_widget.setWindowTitle("Добавить кофе")
        # Задаем название кнопке в окне
        self.add_coffee_widget.button.setText("Добавить")
        # Подключаем функцию добавления кофе
        self.add_coffee_widget.button.clicked.connect(self.add_coffee_widget.create_coffee)

    def editCoffee(self):
        row = self.tableWidget.currentRow()
        ID = self.tableWidget.item(row, 0)
        if ID is not None:
            Id = ID.text()
            # Инициализимруем объект класса окна изменения кофе
            self.edit_coffee_widget = AddCoffeeForm()
            # Задаем название нашему окну
            self.edit_coffee_widget.setWindowTitle("Редактировать кофе")
            # Изменяем значение надписи кнопки
            self.edit_coffee_widget.button.setText("Редактировать")
            # Устанавливаем объект основного класса
            self.edit_coffee_widget.set_main(self)
            # устанавливаем id того кофе который редактируем
            self.edit_coffee_widget.setID(Id)
            # Обновляем значения окна так как мы редактируем существующий кофе
            self.edit_coffee_widget.update_values()
            # Подключаем функцию редактирования кофе
            self.edit_coffee_widget.button.clicked.connect(self.edit_coffee_widget.edit_coffee)
    
    def deleteCoffee(self):
        if self.tableWidget.selectedIndexes():
            # ID выбранных ячеек
            rows = [i.row() for i in self.tableWidget.selectedIndexes()]
            selected_id = list(set(map(int, [self.tableWidget.item(index, 0).text() for index in rows])))
            ids = ", ".join(map(str, sorted(selected_id)))
            question = QMessageBox.question(
                self, 
                "Удалить выбранные сорта кофе?", 
                "Действительно удалить элементы с id " + ids, 
                QMessageBox.Yes | QMessageBox.No
            )
            # Если выбрали действительно удалить кофе делаем запрос к бд
            if question == QMessageBox.Yes:
                query = f"""
                DELETE from coffee
                WHERE ID in ({ids})
                """
                self.do_query(query)
                # Обновляем таблицу кофе
                self.update_table(self.do_query())
            else:
                return


if __name__ == "__main__":
    app = QApplication(sys.argv)
    espresso = Espresso()
    espresso.show()
    sys.exit(app.exec())