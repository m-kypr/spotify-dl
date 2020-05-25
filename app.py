import os
import sys
import json
import spotipy
import youtube_dl

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

WIDTH = 500
HEIGHT = 150

YDL_OPTS = {
    'default_search': 'ytsearch',
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}


class ProcessRunnable(QRunnable):
    def __init__(self, target, args):
        QRunnable.__init__(self)
        self.t = target
        self.args = args

    def run(self):
        self.t(*self.args)

    def start(self):
        QThreadPool.globalInstance().start(self)


class GUI(QWidget):
    def __init__(self):
        global WIDTH, HEIGHT

        super().__init__()
        self.setWindowTitle('Spotify Downloader')
        self.setGeometry(0, 0, WIDTH, HEIGHT)
        self.setFixedSize(WIDTH, HEIGHT)

        self.create_grid()

        windowLayout = QVBoxLayout()
        windowLayout.addWidget(self.horizontalGroupBox)
        self.setLayout(windowLayout)

        self.center()
        self.show()

    def center(self):
        frameGm = self.frameGeometry()
        screen = QApplication.desktop().screenNumber(
            QApplication.desktop().cursor().pos())
        centerPoint = QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())

    def create_grid(self):
        self.horizontalGroupBox = QGroupBox()
        layout = QGridLayout()
        self.link = QLineEdit('', self)
        self.link.setMaximumHeight(int(HEIGHT/3))
        self.btn = QPushButton('Download', self)
        self.btn.resize(self.btn.sizeHint())
        self.btn.clicked.connect(self.download)
        self._dir = QPushButton('Select Directory', self)
        self._dir.clicked.connect(self.directory)
        self.info = QLabel('-----')
        self.credentials = QPushButton('credentials.json', self)
        self.credentials.clicked.connect(self.creds)
        layout.addWidget(self.link, 0, 0)
        layout.addWidget(self.btn, 0, 1)
        layout.addWidget(self._dir, 1, 1)
        layout.addWidget(self.info, 1, 0)
        layout.addWidget(self.credentials, 2, 1)
        self.horizontalGroupBox.setLayout(layout)

    def creds(self):
        self.creds, _ = QFileDialog.getOpenFileName(
            filter='credentials.json', initialFilter='credentials.json')
        self.creds = json.loads(open(self.creds, 'r').read())
        print('credentials: ' + str(self.creds))
        self.creds = spotipy.SpotifyClientCredentials(
            client_id=self.creds['client_id'], client_secret=self.creds['client_secret'])

    def directory(self):
        self.dir = str(QFileDialog.getExistingDirectory(
            self, 'Select Directory'))
        print('directory: ' + self.dir)

    def download(self):
        ProcessRunnable(target=self._download, args=()).start()

    def _download(self):
        os.chdir(self.dir)
        try:
            playlist_id = self.link.text().split(
                '/')[-1].split('?')[0]
            spotify = spotipy.Spotify(client_credentials_manager=self.creds)
            for track in spotify.playlist(playlist_id)['tracks']['items']:
                query = track['track']['name'] + ' by ' + \
                    ', '.join([x['name']
                               for x in track['track']['artists']])
                print(query)
                self.info.setText(query)
                with youtube_dl.YoutubeDL(YDL_OPTS) as dl:
                    dl.download([query])
        except Exception as e:
            print(e)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = GUI()
    sys.exit(app.exec_())
