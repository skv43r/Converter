from PyQt5 import uic, QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QIcon, QPainter, QFont, QColor, QPen, QPixmap

from config import Config

MainWidget, _ = uic.loadUiType("ui.ui")

class Main(QtWidgets.QWidget, MainWidget):
    '''Класс Main наследуется от QtWidgets.QWidget и MainWidget. Он является основным классом приложения и отвечает за инициализацию и настройку графического интерфейса пользователя.'''

    def __init__(self):
        '''Инициализирует объект класса Main'''
        super(Main,self).__init__()
        self.setupUi(self)
        self.setWindowIcon(QIcon('icon.png'))
        self.set_ui_values()
        self.startButton.clicked.connect(self.start_work)
        self.addAccsPath.clicked.connect(self.set_path)
        self.addOutputPath.clicked.connect(self.set_path)
        self.addProxyPath.clicked.connect(self.set_path)


    def set_path(self):
        '''Устанавливает путь к файлу для элементов графического интерфейса пользователя.'''
        sender = QtWidgets.QPushButton = self.sender()

        path = QFileDialog.getOpenFileName(self,"Выбрать файл",".")[0]

        if sender == 'addAccsPath':
            self.accsPath.setText(path)
        if sender == 'addOutputPath':
            self.outputPath.setText(path)
        if sender == 'addProxyPath':
            self.proxyPath.setText(path)

    def start_work(self):
        '''Начинает выполнение задачи конвертации аккаунтов.'''
        self.startButton.setEnabled(False)
        self.startButton.setText('Конвертируем..')
        self.t = Worker(self)
        self.t.finished.connect(self.work_finished)
        self.t.start()

    def work_finished(self, value, result, errors):
        '''Обрабатывает результат выполнения задачи конвертации аккаунтов.'''
        self.startButton.setEnabled(True)
        self.startButton.setText('Конвертировать')
        self.show_message(value, result, errors)

    def show_message(self, value, result, errors):
        '''Показывает сообщение пользователю о результате выполнения задачи конвертации аккаунтов.'''
        msg = QMessageBox()
        msg.setWindowIcon(QIcon('icon.png'))
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        if value == True:
            msg.setWindowTitle("Выполнено успешно!")
            text = f"Конвертировано аккаунтов: {self.t.count} шт"
            if errors:
                text += f'\n Ошибки: {errors}'
            msg.setText(text)
            msg.setIconPixmap(QPixmap('icon_success.png'))
        else:
            msg.setWindowTitle("Ошибка!")
            text = "Не удалось загрузить аккаунты."
            if errors:
                text += f'\n Ошибки: {errors}'
            msg.setText(text)
            msg.setInformativeText(result)
            msg.setIconPixmap(QPixmap('icon_error.png'))

        msg.exec_()

    def set_ui_values(self):
        '''Устанавливает значения для элементов графического интерфейса пользователя на основе конфигурационных файлов.'''
        Config.load()

        items: list[QtWidgets.QWidget] = self.findChildren(QtWidgets.QWidget)

        for item in items:

            name = item.objectName()
            # ---------------------------------------------------------------
            if isinstance(item, QtWidgets.QLineEdit) and 'qt_spinbox_lineedit' not in name:

                if name in Config.configparser['Settings']:
                    value = Config.get('Settings', name)
                    item.setText(value)
                else:
                    value = item.text()
                    Config.set('Settings', name, value)
                item.textChanged.connect(self.save_to_config)
            # ---------------------------------------------------------------
            elif isinstance(item, (QtWidgets.QRadioButton, QtWidgets.QCheckBox)):

                if name in Config.configparser['Settings']:
                    value = Config.get('Settings', name)
                    if value == 'True':
                        item.setChecked(True)
                    elif value == 'False':
                        item.setChecked(False)
                else:
                    value = str(item.isChecked())
                    Config.set('Settings', name, value)
                item.toggled.connect(self.save_to_config)
            # ---------------------------------------------------------------
            elif isinstance(item, QtWidgets.QSpinBox):

                if name in Config.configparser['Settings']:
                    value = Config.get('Settings', name)
                    try:
                        int(value)
                    except:
                        value = 0
                    item.setValue(int(value))
                else:
                    value = str(item.value())
                    Config.set('Settings', name, value)
                item.valueChanged.connect(self.save_to_config)
            # ---------------------------------------------------------------
            elif isinstance(item, QtWidgets.QComboBox):

                if name in Config.configparser['Settings']:
                    value = Config.get('Settings', name)
                    try:
                        int(value)
                    except:
                        value = 0
                    item.setCurrentIndex(int(value))
                else:
                    value = str(item.currentIndex())
                    Config.set('Settings', name, value)
                item.currentIndexChanged.connect(self.save_to_config)

            elif isinstance(item, QtWidgets.QDateTimeEdit):

                if name in Config.configparser['Settings']:
                    value = Config.get('Settings', name)
                    if value is not False:
                        try:
                            time = QtCore.QDateTime.fromString(value)
                            item.setDateTime(time)
                        except Exception as e:
                            print(e)
                            pass
                else:
                    value = str(item.dateTime().toString("yyyy.MM.dd hh:mm:ss"))
                    Config.set('Settings', name, value)
                item.dateTimeChanged.connect(self.save_to_config)



    def save_to_config(self):
        '''Сохраняет изменения в конфигурационных файлах.'''
        sender = self.sender()
        if sender is None:
            return
        name : str = sender.objectName()

        if type(sender) == QLineEdit:
            value = sender.text()
            Config.set('Settings', name, value)

        elif type(sender) == QRadioButton or type(sender) == QCheckBox:
            value = str(sender.isChecked())
            Config.set('Settings', name, value)

        elif type(sender) == QSpinBox:
            value = str(sender.value())
            Config.set('Settings', name, value)
            if name == 'count_for_kpd':
                value = self.calculate_kpd()

        elif type(sender) == QComboBox:
            value = str(sender.currentIndex())
            Config.set('Settings', name, value)

        elif type(sender) == QDateTimeEdit:
            value = str(sender.dateTime().toString("yyyy.MM.dd hh:mm:ss"))
            Config.set('Settings', name, value)

class Worker(QThread):
    '''Класс Worker наследуется от QThread. Он является вспомогательным классом, который выполняет задачу конвертации аккаунтов в отдельном потоке.'''
    finished = QtCore.pyqtSignal(bool, str, str)

    def __init__(self, main):
        '''Инициализирует объект класса Worker.'''
        super().__init__()
        self.main = main
        self.count = 0
        self.errors_list = ''

    def run(self):
        '''Выполняет задачу конвертации аккаунтов'''
        try:
            with open(self.main.accsPath.text(), 'r', encoding = 'utf-8', errors = 'ignore') as file:
                accounts = file.read().split('\n')
                converted_accounts = ''
                current_str = 1
                proxy_index = 1
                for acc in accounts:
                    try:
                        token = 'EAAB' + acc.split('EAAB')[-1]
                        password = acc.split()[2]
                        proxy = ''
                        if self.main.setProxyTumbler.isChecked():
                            with open(self.main.proxyPath.text(), 'r', encoding = 'utf-8', errors = 'ignore') as file:
                                proxies = file.read().split('\n')
                                if proxy_index <= len(proxies):
                                    proxy = proxies[proxy_index-1]
                                else:
                                    proxy_index = 1
                                    proxy = proxies[proxy_index-1]
                                proxy_index += 1
                        cookies = '[{' + acc.split('[{')[-1].split('}]')[0] + '}]'
                        new_data = '::' + token + '::::' + proxy + '::' + cookies + '::' + password
                        if new_data:
                            self.count += 1
                            new_data = str(self.count) + new_data
                            converted_accounts += new_data + '\n'
                    except Exception as e:
                        print(e)
                        self.errors_list += f'Строка:{current_str} - ' + str(e) + '\n'
                    current_str += 1
                with open(self.main.outputPath.text(), 'w') as file:
                    file.write(converted_accounts)

            self.finished.emit(True, 'ok', self.errors_list)
        except Exception as e:
                return self.finished.emit(False, str(e), self.errors_list)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)

    main = Main()
    main.show()

    sys.exit(app.exec_())
