import sys 

from vispy import scene
from vispy.color import get_colormap, ColorArray
from vispy.visuals import transforms

from PyQt5 import QtCore, QtWidgets

from PyQt5.QtWidgets import QWidget, QPushButton, QTreeWidget, QTreeWidgetItem, QLabel, QRadioButton, QSpinBox
from PyQt5.QtWidgets import QBoxLayout, QHBoxLayout, QGridLayout

from PyQt5.QtCore import Qt

import numpy as np
import numpy.random as rd

# an observable
class TensorData(object):
    def __init__(self, tensor):
        self.tensor = tensor
        self.partitions = (1, 1, 1)
        self.ranks = []
        self.observers = []

    def register(self, a_observer):
        self.observers.append(a_observer)

    # ValueError only if program error
    def unregister(self, a_observer):
        self.observers.remove(a_observer)

    def update(self):
        for observer in self.observers:
            observer(self)

class CostumizedCanvas(scene.SceneCanvas):
    def __init__(self, *args, **kv):
        super().__init__(*args, **kv)
        self.unfreeze()

    def on_close(self, event):
        try:
            self.on_close_handler(self, event)
        except AttributeError:
            pass

    def set_on_close_handler(self, handler):
        self.on_close_handler = handler

class Context:
    def __init__(self):
        #self.canvas = scene.SceneCanvas(keys='interactive', size=(800, 600), show=True)
        #self.canvas = scene.SceneCanvas(keys='interactive', show=True)
        #self.canvas = scene.SceneCanvas(keys='interactive')
        self.canvas = CostumizedCanvas(keys='interactive')
        self.view = self.canvas.central_widget.add_view()
        self.view.camera = 'turntable'
        self.canvas.central_widget.remove_widget(self.view)
        self.canvas.central_widget.add_widget(self.view)
    
    def show(self):
        self.canvas.show()

_context = Context()

class TensorRankViewSelector(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QHBoxLayout(self)
        #self.setLayout(layout)

        self.point_cloud = QRadioButton('point cloud')
        layout.addWidget(self.point_cloud)

        self.pure_heat = QRadioButton('pure heat')
        layout.addWidget(self.pure_heat)

        self.hybrid = QRadioButton('hybrid')
        self.hybrid.setChecked(True)
        layout.addWidget(self.hybrid)

class TensorRankShower(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        data_len_per_dim = 5
        layout = QBoxLayout(QBoxLayout.TopToBottom, self)

        label_container = QWidget(self)
        layout.addWidget(label_container)
        label_container_layout = QHBoxLayout(label_container)
        label = QLabel('Tensor Rank', self)
        label.setAlignment(Qt.AlignHCenter)
        label_container_layout.addWidget(label)
        show_all_button = QPushButton('Expand/Collapse', self)
        label_container_layout.addWidget(show_all_button)

        tw = QTreeWidget(self)
        layout.addWidget(tw)
        tw.setColumnCount(2)
        tw.setHeaderLabels(["where", "rank", "size"])

        for x in range(data_len_per_dim):
            x_child = QTreeWidgetItem(["x:{}".format(x)])
            for y in range(data_len_per_dim):
                y_child = QTreeWidgetItem(["y:{}".format(y)])
                for z in range(data_len_per_dim):
                    z_child = QTreeWidgetItem(["z:{}".format(z), "({},{},{})".format(1, 1, 1), "{}x{}x{}".format(10, 10, 10)])
                    y_child.addChild(z_child)
                x_child.addChild(y_child)
            tw.addTopLevelItem(x_child)

        self.is_expanded = False
        def toggle_expand():
            tw.collapseAll() if self.is_expanded else tw.expandAll()
            self.is_expanded = not self.is_expanded

        show_all_button.clicked.connect(toggle_expand)

class XYZRangeSelector(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QGridLayout(self)

        modes = ['X', 'Y', 'Z']
        for m in range(1, 4):
            mode = modes[m - 1]

            label = QLabel(mode, self)
            label.setAlignment(Qt.AlignHCenter)
            layout.addWidget(label, 1, m)

            how_many_partition_box = QSpinBox(self)
            how_many_partition_box.setToolTip("how many partition?")
            layout.addWidget(how_many_partition_box, 2, m)
        
            start_box = QSpinBox(self)
            start_box.setToolTip("start from")
            layout.addWidget(start_box, 3, m)

            end_box = QSpinBox(self)
            end_box.setToolTip("end at")
            layout.addWidget(end_box, 4, m)
            
class Window(QWidget):
    def __init__(self):
        super(Window, self).__init__()
        box = QBoxLayout(QBoxLayout.LeftToRight, self)
        self.resize(1200, 800)

        def canvas_on_close_handler(_1, _2):
            self.close()
        _context.canvas.set_on_close_handler(canvas_on_close_handler)
        box.addWidget(_context.canvas.native)
        
        rightBoxWidget = QWidget()
        rightBox = QBoxLayout(QBoxLayout.TopToBottom, rightBoxWidget)
        rightBox.setAlignment(Qt.AlignTop)
        box.addWidget(rightBoxWidget)

        tensor_view_selector = TensorRankViewSelector()
        rightBox.addWidget(tensor_view_selector)

        #button = QPushButton('Change View', self)
        #button.setToolTip('Change View Port')
        #rightBox.addWidget(button)

        xyzRangeSelector = XYZRangeSelector()
        rightBox.addWidget(xyzRangeSelector)

        tw_container = TensorRankShower()
        rightBox.addWidget(tw_container)

        self.show()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()

def add_scatter():
    how_many_seg = 5
    to_scale = 0.4
    poss = []
    for l in range(how_many_seg):
        for m in range(how_many_seg):
            for n in range(how_many_seg):
                if l == m and l == n:
                    for _ in range(10000):
                        poss.append((
                              (np.random.random() + l - how_many_seg/2) * to_scale
                            , (np.random.random() + m - how_many_seg/2) * to_scale
                            , (np.random.random() + n - how_many_seg/2) * to_scale
                        ))
                else:
                    for _ in range(10):
                        poss.append((
                              (np.random.random() + l - how_many_seg/2) * to_scale
                            , (np.random.random() + m - how_many_seg/2) * to_scale
                            , (np.random.random() + n - how_many_seg/2) * to_scale
                        ))

    poss = np.array(poss)
    scatter = scene.visuals.Markers()
    scatter.set_data(poss, edge_color=None, face_color=(1, 1, 1, 0.5), size=5)
    _context.view.add(scatter)

def add_scatter_one_by_one():
    how_many_seg = 5
    to_scale = 0.4
    for l in range(how_many_seg):
        for m in range(how_many_seg):
            for n in range(how_many_seg):
                scatter = scene.visuals.Markers()
                poss = np.random.random(size=(10000, 3)) if l == m and l == n else np.random.random(size=(10, 3))
                poss += (l, m, n)
                poss -= how_many_seg/2
                poss *= to_scale

                scatter.set_data(poss, face_color=(1, 0, 0, 0.5) if l == m and l == n else (1, 1, 1, 0.5), size=5)
                _context.view.add(scatter)


def add_cubes():
    cm = get_colormap('hot')
    how_many_seg = 5
    for l in range(how_many_seg):
        for m in range(how_many_seg):
            for n in range(how_many_seg):
                cube_size = 0.15
                how_much_red = np.random.random()
                cube = scene.visuals.Sphere(
                          radius=cube_size/2
                        , method='latitude'
                        , color=cm[np.random.random()]
                        )
                #cube = scene.visuals.Cube((cube_size, cube_size, cube_size),
                        #color=ColorArray((how_much_red, 0, 0, 0.8)))#,
                        #edge_color='k')
                cube.transform = transforms.MatrixTransform()
                to_translate = 0.4
                cube.transform.translate((to_translate*(l-how_many_seg//2), to_translate*(m-how_many_seg//2), to_translate*(n-how_many_seg//2)))
                _context.view.add(cube)


if __name__ == '__main__':
    #add_scatter()
    add_scatter_one_by_one()
    qt_app = QtWidgets.QApplication(sys.argv)
    ex = Window()
    qt_app.exec_()

    #add_cubes()
    #_context.canvas.app.run()
