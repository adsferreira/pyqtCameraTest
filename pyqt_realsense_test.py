import sys
from PyQt5.QtWidgets import QMainWindow , QApplication
from PyQt5.QtGui import QIcon
import pyrealsense2 as rs


class MainWidget(QMainWindow):
    def __init__(self, parent=None):
        super(MainWidget, self).__init__(parent)
        self.setWindowTitle("QMainWindow Example")
        self.resize(400, 200)
        self.status = self.statusBar()
        self.status.showMessage("Status", 5000)
        # Configure depth and color streams
        self.pipeline = rs.pipeline()
        self.config = rs.config()

    def enable_rs_cam(self):
        # Start streaming
        profile = self.pipeline.start()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("./images/cartoon1.ico"))
    main = MainWidget()
    print('Test...')
    main.show()
    main.enable_rs_cam()
    print('Enable RSCamera')
    sys.exit(app.exec_())
