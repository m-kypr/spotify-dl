# ALL CREDITS TO https://github.com/ritiek/spotify-downloader

import os
import sys
import spotipy
import youtube_dl

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

CLIENT_ID = '11aff9c705c3475283a84868a9bda0e5'
CLIENT_SECRET = '8027e1d8f33d4a2b9c4079d9467d4cea'

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

spotify = spotipy.Spotify(client_credentials_manager=spotipy.SpotifyClientCredentials(
    client_id=CLIENT_ID, client_secret=CLIENT_SECRET))


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
        self.link = QPlainTextEdit('', self)
        self.link.setMaximumHeight(int(HEIGHT/3))
        self.btn = QPushButton('Download', self)
        self.btn.resize(self.btn.sizeHint())
        self.btn.clicked.connect(self.download)
        # self.extract = QCheckBox('Extract Audio')
        # self.extract.setChecked(True)
        self._dir = QPushButton('Select Directory', self)
        self._dir.clicked.connect(self.directory)
        self.info = QLabel('-----')
        layout.addWidget(self.link, 0, 0)
        layout.addWidget(self.btn, 0, 1)
        # layout.addWidget(self.extract, 0, 2)
        layout.addWidget(self._dir, 1, 1)
        layout.addWidget(self.info, 1, 0)
        self.horizontalGroupBox.setLayout(layout)

    def directory(self):
        self.dir = str(QFileDialog.getExistingDirectory(
            self, 'Select Directory'))
        print(self.dir)

    def download(self):
        ProcessRunnable(target=self._download, args=()).start()

    def _download(self):
        with youtube_dl.YoutubeDL(YDL_OPTS) as dl:
            os.chdir(self.dir)
            try:
                playlist_id = self.link.toPlainText().split(
                    '/')[-1].split('?')[0]
                p = spotify.playlist(playlist_id)
                # queries = []
                for track in p['tracks']['items']:
                    query = track['track']['name'] + ' by ' + \
                        ', '.join([x['name']
                                   for x in track['track']['artists']])
                    self.info.setText(query)
                    dl.download([query])
                    # queries.append(query)
                # dl.download(queries)
            except Exception as e:
                print(e)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = GUI()
    sys.exit(app.exec_())
