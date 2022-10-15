import pickle as cPickle

import time
import sys

from datetime import datetime

from socketserver import BaseRequestHandler, ThreadingTCPServer
import threading
import socket

import sqlite3 as SQL

import SocketForPics as SFP

global FLAG_online
FLAG_online = True

if FLAG_online != True:
    from PyQt5.QtWidgets import QWidget, QPushButton, QGridLayout
    from PyQt5.QtCore import QCoreApplication
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtWidgets import QGridLayout, QGroupBox
    from PyQt5.QtGui import QPixmap, QIcon
    from PyQt5.QtCore import QSize

    from work_with_icons import *


HOST = socket.gethostname()
PORT = 9191

data = " ".join(sys.argv[1:])
global FLAG_shutdown
FLAG_shutdown = False


'''
import os
ON_HEROKU = os.environ.get('ON_HEROKU')
if ON_HEROKU: # get the heroku port
    port = int(os.environ.get('PORT', 17995)) # as per OP comments default is 17995 else: port = 3000
'''
global window
global bnt3
global bnt4
btn3 = None
btn4 = None
window = None



dict_sql_query = {"add" : "SELECT {} "
            }


class HandleConn(BaseRequestHandler):
    name_db = "DataBaseServer\\picseditor.db"
    table_db = "fons"

    def close_server(self, sql_query, cur_thread):
        global FLAG_shutdown
        if sql_query == 'end' or sql_query == b'end' :
            print("Получили запрос на закрытие соединения!")
            self.request.send(b"end") # отправили кденту ответ, что поняли его и закрываем с ним связь
            return True
        if sql_query == 'quit' or sql_query == b'quit':
            print("Получили запрос на останов всего сервера со всеми потоками!")
            self.request.send(b'quit') # отправили кденту ответ, что поняли его и закрываем с ним связь
            FLAG_shutdown = True
            self.executeSQL(str(("Умирает сервер по команде от клиента: " +str(cur_thread.name)+"\nПолучено сообщение: " + str(sql_query))))
            self.server.shutdown()
            return True
        if FLAG_shutdown:
            self.executeSQL(str(("Умирает поток клиента: " +str(cur_thread.name)+"\nПолучено сообщение: " + str(sql_query))))
            self.server.shutdown()
            return True

        return False

    def_get_pics_list = 'def_get_pics_list' # #получить список картинок  def_get_pics_list
    def_get_weights_list = 'def_get_weights_list'# получить список весов     def_get_weights_list
    def_del_record_weight = 'def_del_record_weight'# удалить строку с определенным весом                       def_del_record_weight
    def_add_record_pic = 'def_add_record_pic'# добавить строку с картинкой - картинку передаем тдельно   def_add_record_pic

    def handle(self):
        global FLAG_shutdown
        global window
        global btn3
        global btn4
        global FLAG_online

        # получили информацию от клиента
        # sql_query = str(self.request.recv(1024), 'utf-8') #получили SQL запрос от клиента
        sql_query = str(self.request.recv(4096), 'utf-8') #получили SQL запрос от клиента

        # создали отдельный поток работы с клиентом
        cur_thread = threading.current_thread()
        response = bytes("{}: {}".format(cur_thread.name, sql_query), 'utf-8')
        print ("Инициализирован новый поток: {}".format(response))

        # создали наш собственный экземпляр класса обработки запросов и напарвления ответов
        my_pics_socket = SFP.Socket4Pics(self.request)

        if self.close_server(sql_query, cur_thread): # если закрываем сервер, то выходим
            return False

        # если же добавляем картинку, то следует добавить строку, а потом в нее вставить саму картинку pic
        # в первом сообщении от клиента получаем тип сообщения:
            # получить список картинок  def_get_pics_list
            # получить список весов     def_get_weights_list
            # удалить строку с определенным весом                       def_del_record_weight
            # добавить строку с картинкой - картинку передаем тдельно   def_add_record_pic

        # отправить клиенту сообщение, что сервер его понял и готов принимать следующие данные
        self.request.send(sql_query.encode()) # отправляем подтверждения получения запроса - тот же самый запрос

        # отправить клиенту список картинок  def_get_pics_list
        if sql_query == self.def_get_pics_list:
            print("получить список картинок  def_get_pics_list")
            # получаем список картинок
            sql_query = str(self.request.recv(4096), 'utf-8') #получили SQL запрос от клиента
            data_sql = self.executeSQL("", sql_query)
            if data_sql != []:
                # передаем все картинки клиенту, каждая кнопка в байтах с количеством байт в заголовке
                for d in data_sql:
                    data = d[0]
                    def_size_icon = 50
                    size_icon = 50
                    print(str(data[:20]))
                    if FLAG_online == False:
                        btn3 = set_icon_from_blob(btn3, data, def_size_icon)
                    my_pics_socket.send_msg(data)
        # отправить клиенту список весов     def_get_weights_list
        elif sql_query == self.def_get_weights_list:
            print("получить список весов     def_get_weights_list")
            sql_query = str(self.request.recv(4096), 'utf-8') #получили SQL запрос от клиента
            data_sql = self.executeSQL("", sql_query)
            data = cPickle.dumps(data_sql)
            self.request.send(data)
        elif sql_query == self.def_del_record_weight:# удалить строку с определенным весом                       def_del_record_weight
            print("удалить строку с определенным весом   def_del_record_weight")
            sql_query = str(self.request.recv(4096), 'utf-8') #получили SQL запрос от клиента
            data_sql = self.executeSQL("", sql_query)
            data = cPickle.dumps(data_sql) # если все ок, то возвращаем true
            self.request.send(data)
        elif sql_query == self.def_add_record_pic:# добавить строку с картинкой - картинку передаем тдельно   def_add_record_pic
            print("добавить строку с картинкой - картинку передаем тдельно   def_add_record_pic")
            # получаем SQL запрос
            sql_query_select = str(self.request.recv(4096), 'utf-8')
            data = cPickle.dumps(True) # если все ок, то возвращаем true
            self.request.send(data)
            # получаем тип записи
            # sql_query_type =  str(self.request.recv(4096), 'utf-8')
            sql_query_type =  self.request.recv(4096)
            sql_query_type = sql_query_type.decode()
            self.request.send(data)
            # получаем тип записи - имя картинки
            sql_query_name =  str(self.request.recv(4096), 'utf-8')
            self.request.send(data)
            # получаем картинку
            img_blob = my_pics_socket.recv_msg() # в виде строки байтов
            self.request.send(data)
            # получаем комментарии
            sql_query_comment =  str(self.request.recv(4096), 'utf-8')
            self.request.send(data)
            # получаем вес картинки
            sql_query_weight =  str(self.request.recv(4096), 'utf-8')
            # открываем БД
            db_cur = self.open_db_pics()
            # формируем запрос
            data_tuple = (sql_query_type, sql_query_name, img_blob, sql_query_comment, sql_query_weight)
            # исполняем запрос к БД
            db_cur[1].execute(sql_query_select, data_tuple)
            self.request.send(data)
            self.close_db_pics(db_cur[0])
        else:
            print("Передали незнакомую команду:\n" + str(sql_query)[:50])
            # self.executeSQL(str(("Поток клиента: " +str(cur_thread.name)+"\nПолучено сообщение: " + str(sql_query))))
            data_sql = self.executeSQL("", sql_query)

        # отправляем сигнал, что все картики передали, чтобы клиент разорвал сообщение с сервером
        # передали все картинки и отправили информацию об окончании пакета картинок и соединения с сервером- 0!
        my_pics_socket.send_msg_end()


    def executeSQL (self, sql_query_text, sql_query = ""):
        result = []
        if sql_query_text == "":
            print ("Исполняем Пустой SQL запрос: " + str(sql_query_text))
        else:
            print ("Исполняем SQL запрос: " + str(sql_query_text))

        if sql_query == "":
            return result

        db_cur = self.open_db_pics()
        # определям тип запроса - SELECT, INSERT, UPDATE или DELETE
        type_query = sql_query[:6]
            # при возврате: SELECT - возвращаем fetchall, INSERT - True/False, UPDATE - True/False или DELETE - True/False
        try:
            db_cur[1].execute(sql_query)
            if type_query == 'SELECT':
                result = db_cur[1].fetchall()
            else:
                result = True
        except SQL.Error as error:
            print("(executeSQL) ошибка при работе с SQL: " + str(type_query), error)
            result = False
        finally:
            if db_cur != None:
                self.close_db_pics(db_cur[0])
        return result

    # открываем/создаем базу данных
    def open_db_pics (self, name_db = name_db): # list[0] = имя базы данных, list[1] = список таблиц
        db = -1
        cur = -1
        try:
            db = SQL.connect(name_db)
            cur = db.cursor()
        except SQL.Error as error:
            print("(open_db_pics) ошибка при работе с SQL: ", error)
            return [db, cur]
        return [db, cur]          # возвращает ссылку на БД и на КУРСОР

    # закрываем базу данных
    def close_db_pics (self, db):
        try:
            if db and db != -1:
                db.commit()
                db.close()
        except SQL.Error as error:
            print("(close_db_pics) ошибка при работе с SQL: ", error)
            return False
        return True

    # создание БД и ТАБЛИЦЫ, если такой таблицы не существует еще
    def create_db_pics (self, name_db = name_db, name_table = table_db):
        db = None
        try:
            d = self.open_db_pics(name_db)
            if (d != -1):
                db = d[0]
                table_fields = "type TEXT, name TEXT, pic BLOB, comment TEXT, weight FLOAT"
                db.execute(f"""
                            CREATE TABLE IF NOT EXISTS {name_table} (
                                            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                                            {table_fields}
                                            );
                            """
                            )
        except SQL.Error as error:
            print("(create_db_pics) ошибка при работе с SQL: ", error)
        finally:
            if db != None:
                self.close_db_pics(db)
        return True

    def get_pics_from_db (self, name_db = name_db, table_db = table_db):
        return self.get_meanings_field_from_db (name_db, table_db, "pics")

        d = self.open_db_pics(name_db)
        db = d[0]
        cur = d[1]
        # получили все записи из поля pic из всей таблицы
        cur.execute(f'SELECT pic FROM {table_db}')
        pics = cur.fetchall()
        return pics

    def get_weight_from_db (self, name_db = name_db, table_db = table_db):
        return self.get_meanings_field_from_db (name_db, table_db, "weight")

        d = self.open_db_pics(name_db)
        db = d[0]
        cur = d[1]
        # получили все номера всех кнопок всей таблицы (как они стоят по порядку)
        cur.execute(f'SELECT weight FROM {table_db}')
        weights = cur.fetchall()
        return weights

    def get_meanings_field_from_db (self, name_db = name_db, table_db = table_db, field = ""):
        d = self.open_db_pics(name_db)
        db = d[0]
        cur = d[1]
        # получили все номера всех кнопок всей таблицы (как они стоят по порядку)
        cur.execute(f'SELECT {field} FROM {table_db}')
        meaning_fields = cur.fetchall()
        return meaning_fields

    # удаляем запись по wight
    def del_pic_in_db(self, name_db = name_db, table_db = table_db, weight = 0):
        f = False
        db_cur = None
        try:
            db_cur = self.open_db_pics(name_db)
            # получили все записи из поля pic из всей таблицы
            db_cur[1].execute(f'DELETE FROM {table_db} WHERE weight = {weight}')
            f = True
        except SQL.Error as error:
            print("(del_pic_in_db) ошибка при работе с SQL: ", error)
            f = False
        finally:
            if db_cur != None:
                self.close_db_pics(db_cur[0])
        return f

    # записать информацию в таблицу
    def put_record_db_pics (self, name_db = name_db, table_db = table_db, name = "", pic = b'', comment = "", weight = 0):
        f = True
        db_cur = None
        try:
            db_cur = self.open_db_pics(name_db)
            sqlite_insert_blob_query = f"""INSERT INTO {table_db} (type, name, pic, comment, weight) VALUES(?, ?, ?, ?, ?)"""
            data_tuple = ("", name, pic, comment, weight)
            db_cur[1].execute (sqlite_insert_blob_query, data_tuple)
            f = True
        except SQL.Error as error:
            print("(put_record_db_pics) ошибка при работе с SQL: ", error)
            f = False
        finally:
            if db_cur != None:
                self.close_db_pics(db_cur[0])
        return f

    # проверяем, есть ли такой бинарный файл с такой картинкой уже в БД
    # если есть то возвращаем его идентификатор
    # если нет, то возвращаем False
    def verify_pic (self, name_db = name_db, table_db = table_db, img_blob = b''):
        f = False
        db_cur = None
        try:
            db_cur = self.open_db_pics(name_db)
            # получили все записи из поля pic из всей таблицы
            db_cur[1].execute(f'SELECT pic FROM {table_db}')
            pics = db_cur[1].fetchall()
            for pic in pics:
                if pic[0] == img_blob:
                    f = True
                    break
            # закрываем БД
        except SQL.Error as error:
            print("(verify_pic) ошибка при работе с SQL: ", error)
            f = False
        finally:
            if db_cur != None:
                self.close_db_pics(db_cur[0])
        return f


def client(ip, port, message):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((ip, port))
        sock.sendall(bytes(message, 'utf-8'))
        response = str(sock.recv(1024), 'utf-8')
        print("Получено: {}".format(response))

def run():
    # start a tcp server
    # создали экземпляр класса серверов и передали ему обработчик запросов, которые будут образаться к серверу
    server = ThreadingTCPServer((HOST, PORT), HandleConn)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    print("Запустили серверр, работающий в потоке: ", server_thread.name)
    global FLAG_shutdown
    while FLAG_shutdown != True:
        # запустили бесконечный цикл сервера
        pass

#    server.serve_forever()

    '''
    with server:
        ip, port = server.server_address
        # Начать поток с сервера, далее поток запустит еще один поток
        # для каждого запроса
        server_thread = threading.Thread(target=server.serve_forever)
        # Выйти из серверного потока, когда основной поток завершится
        server_thread.daemon = True
        server_thread.start()
        print("Цикл сервера, работающий в потоке:", server_thread.name)

        #client(ip, port, "Hello World 1")
        #client(ip, port, "Hello World 2")
        #client(ip, port, "Hello World 3")

        #server.shutdown()

    # вызвали серверный объект для обрабюотки запросов
    # serv.serve_forever()
    '''


def close_all():
    global FLAG_shutdown
    global window
    FLAG_shutdown = True
    window.close()
    window.destroy()
    QCoreApplication.instance().quit

def create_test_window():
    # запустили клиента для контакта с сервером, которы йобрабатываетзапросы к своим Базам Данных
    global window
    global btn3
    global btn4

    app = QApplication(sys.argv)
    window = QWidget()
    window.setWindowTitle("Сервер")
    window.setFixedWidth(200)
    window.setFixedHeight(200)
    window.move(100,100)

    btn = QPushButton("Выход", window)
    btn2 = QPushButton("Запрос клиенту", window)

    btn3 = QPushButton("", window)
    sizeBtn = QSize(50, 50)
    btn3.setFixedSize(sizeBtn)

    btn4 = QPushButton("", window)
    sizeBtn = QSize(50, 50)
    btn4.setFixedSize(sizeBtn)


    #btn.clicked.connect(QCoreApplication.instance().quit)
    btn.clicked.connect(close_all)

    horizontalGroupBox2 = QGroupBox(window)
    grid_layout_dop_btn = QGridLayout(window)
    grid_layout_dop_btn.addWidget(btn, 0, 1)
    grid_layout_dop_btn.addWidget(btn2, 1, 1)
    grid_layout_dop_btn.addWidget(btn3, 2, 1)
    grid_layout_dop_btn.addWidget(btn4, 3, 1)

    horizontalGroupBox2.setLayout(grid_layout_dop_btn)

    window.show()

    sys.exit(app.exec_())

def main():
    run()
    # create_test_window()

    pass

if __name__ == '__main__':
    main()
