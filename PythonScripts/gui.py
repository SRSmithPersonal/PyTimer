import sys
from time import sleep
from Timer import sleep_killer, get_procs
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QListWidget, QLabel, QLineEdit, QPushButton, \
    QAbstractItemView, QHBoxLayout, QListWidgetItem
from PyQt6.QtCore import QObject, QThread, pyqtSignal, Qt


def delete_item(listwidg, itemname):
    items_list = listwidg.findItems(itemname, Qt.MatchFlag.MatchExactly)
    for item in items_list:
        r = listwidg.row(item)
        listwidg.takeItem(r)


def update_item(listwidg, ite):
    print("Here")
    items_list = listwidg.findItems(ite["title"], Qt.MatchFlag.MatchExactly)
    print(ite, items_list)
    for item in items_list:
        print("setting")
        # item.setToolTip(str(ite['value']))
        item.setToolTip(f"{int(ite['value'] / 60)} Hours {ite['value']%60} Minutes")
        print("set")


class Worker(QObject):
    finished = pyqtSignal()

    t = 0
    proc = ""
    parent = None

    to_stop = False

    def run(self):
        for i in range(self.t, 0, -1):
            if self.to_stop:
                break
            if i == 1:
                sleep_killer(60, self.proc+'.exe')
            else:
                self.parent.update.append({"title": self.proc, "value": i})
                sleep(60)

        self.finished.emit()
        self.parent.finished.append(self.proc)

    def stop(self):
        self.to_stop = True


class Cleaner(QObject):
    finished = pyqtSignal()
    parent = None

    def run(self):
        while True:
            while self.parent.finished:
                sleep(0.1)
                rem = self.parent.finished.pop()
                try:
                    delete_item(self.parent.list_box2, rem)
                    self.parent.activities.pop(rem)
                except:
                    print("item no longer available")
            sleep(0.1)
        self.finished.emit()


class Updater(QObject):
    finished = pyqtSignal()
    parent = None

    def run(self):
        while True:
            while self.parent.update:
                rem = self.parent.update.pop()
                try:
                    update_item(self.parent.list_box2, rem)
                except:
                    print("item no longer available")
            sleep(2)
        self.finished.emit()


class MyWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.finished = []
        self.list_box1 = QListWidget(self)
        self.list_box2 = QListWidget(self)
        self.integer_label = QLabel("Time amount:", self)
        self.integer_label2 = QLabel("H", self)
        self.integer_label3 = QLabel("min", self)
        self.ref_button = QPushButton("Refresh", self)
        # self.rem_button = QPushButton("Remove", self)
        self.integer_setting1 = QLineEdit(self)
        self.integer_setting1.setText('0')
        self.integer_setting2 = QLineEdit(self)
        self.integer_setting2.setText('0')
        self.activities = {}
        self.clean_thread = QThread()
        self.clean_worker = Cleaner()
        self.update_thread = QThread()
        self.update_worker = Updater()
        self.update = []
        # Initialize the UI components
        self.init_ui()

    def init_ui(self):
        # Create a layout
        layout = QHBoxLayout()
        box1 = QVBoxLayout()
        box2 = QVBoxLayout()
        box5 = QVBoxLayout()
        box3 = QHBoxLayout()
        box4 = QHBoxLayout()

        self.list_box1.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.list_box1.addItems(get_procs())
        box1.addWidget(self.list_box1)

        self.list_box2.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        # self.rem_button.clicked.connect(self.rem_values)
        box5.addWidget(self.list_box2)
        # box5.addWidget(self.rem_button)
        box2.addLayout(box5)

        # Create a label and line edit for the integer setting

        box4.addWidget(self.integer_label)

        self.ref_button.clicked.connect(self.refresh_list)
        box4.addWidget(self.ref_button)

        box1.addLayout(box4)

        box3.addWidget(self.integer_setting1)
        box3.addWidget(self.integer_label2)
        box3.addWidget(self.integer_setting2)
        box3.addWidget(self.integer_label3)

        # Create a set button
        set_button = QPushButton("Set", self)
        set_button.clicked.connect(self.set_values)
        box3.addWidget(set_button)

        box1.addLayout(box3)

        # Set the layout of the main widget
        layout.addLayout(box1)
        layout.addLayout(box2)
        self.setLayout(layout)

        self.clean_worker.parent = self

        self.clean_worker.moveToThread(self.clean_thread)
        self.clean_thread.started.connect(self.clean_worker.run)
        self.clean_worker.finished.connect(self.clean_thread.quit)
        self.clean_worker.finished.connect(self.clean_worker.deleteLater)
        self.clean_thread.finished.connect(self.clean_thread.deleteLater)
        self.clean_thread.start()

        self.update_worker.parent = self

        self.update_worker.moveToThread(self.update_thread)
        self.update_thread.started.connect(self.update_worker.run)
        self.update_worker.finished.connect(self.update_thread.quit)
        self.update_worker.finished.connect(self.update_worker.deleteLater)
        self.update_thread.finished.connect(self.update_thread.deleteLater)
        self.update_thread.start()

    def refresh_list(self):
        self.list_box1.clear()
        new_procs = [p for p in get_procs() if p not in self.activities.keys()]
        
        self.list_box1.addItems(new_procs)

    def set_values(self):
        # Get the selected item from the list box
        selected_items = self.list_box1.selectedItems()

        # Get the integer value from the line edit
        integer_value = str(int(self.integer_setting1.text()) * 60 + int(self.integer_setting2.text()))

        # Print the selected item and integer value (you can replace this with your desired functionality)
        for ite in selected_items:
            self.list_box1.takeItem(self.list_box1.row(ite))
            item = QListWidgetItem(f"{ite.text()}")
            item.setToolTip(f'{int(int(integer_value)/60)} Hours {int(integer_value)%60} Minutes')
            self.list_box2.addItem(item)
            v = ite.text()
            self.activities[v] = {'thread': QThread(), 'worker': Worker()}
            self.activities[v]['worker'].proc = v
            self.activities[v]['worker'].t = int(integer_value)
            self.activities[v]['worker'].parent = self
            self.activities[v]['worker'].moveToThread(self.activities[v]['thread'])
            self.activities[v]['thread'].started.connect(self.activities[v]['worker'].run)
            self.activities[v]['worker'].finished.connect(self.activities[v]['thread'].quit)
            self.activities[v]['worker'].finished.connect(self.activities[v]['worker'].deleteLater)
            self.activities[v]['thread'].finished.connect(self.activities[v]['thread'].deleteLater)
            # # Step 6: Start the thread
            self.activities[ite.text()]['thread'].start()
            # print(f"Selected Item: {ite.text()}, Integer Value: {integer_value}")

    def rem_values(self):
        # Get the selected item from the list box
        selected_items = self.list_box2.selectedItems()
        for ite in selected_items:
            v = ite.text()
            a = self.activities.pop(v)
            a["worker"].stop()
            a["thread"].quit()
            self.list_box2.takeItem(self.list_box2.row(ite))


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    widget = MyWidget()
    widget.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()