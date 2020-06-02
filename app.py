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


class ProcessRunnable(QRunnable):
    def __init__(self, target, args):
        QRunnable.__init__(self)
        self.t = target
        self.args = args

    def run(self):
        self.t(*self.args)

    def start(self):
        QThreadPool.globalInstance().start(self)


class API():

    def initSpotify(self, creds):
        self.spotify = spotipy.Spotify(client_credentials_manager=creds)

    def _download(self, dir, link, extract, info):
        os.chdir(dir)
        s_buf = link.split('/')
        if len(s_buf) > 2:
            if "youtube" in s_buf[2]:
                self._download_youtube_link_extract(link, extract)
            elif "spotify" in s_buf[2]:
                self._download_spotify(s_buf[-1].split('?')[0])
        else:
            self._download_youtube_query(link, info)

    def _download_nogui(self, dir, link, extract):
        os.chdir(dir)
        s_buf = link.split('/')
        if len(s_buf) > 2:
            if "youtube" in s_buf[2]:
                self._download_youtube_link_extract_nogui(link, extract)
            elif "spotify" in s_buf[2]:
                self._download_spotify_nogui(s_buf[-1].split('?')[0])
        else:
            self._download_youtube_query_nogui(link)

    def _download_youtube_query(self, query, info):
        info.setText('querying: ' + query)
        self._download_youtube_query_nogui(query)

    def _download_youtube_query_nogui(self, query):
        print('querying: '+query)
        with youtube_dl.YoutubeDL({
            'default_search': 'ytsearch',
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }) as dl:
            dl.download([query])

    def _download_spotify(self, playlist_id, info):
        try:
            for track in self.spotify.playlist(playlist_id)['tracks']['items']:
                query = track['track']['name'] + ' by ' + \
                    ', '.join([x['name']
                               for x in track['track']['artists']])
                self._download_youtube_query(query, info)
        except Exception as e:
            print(e)

    def _download_spotify_nogui(self, playlist_id):
        try:
            for track in self.spotify.playlist(playlist_id)['tracks']['items']:
                query = track['track']['name'] + ' by ' + \
                    ', '.join([x['name']
                               for x in track['track']['artists']])
                self._download_youtube_query_nogui(query)
        except Exception as e:
            print(e)

    def _download_youtube_link_extract(self, link, extract):
        if extract.isChecked():
            print('extract audio: true')
            YDL_OPTS = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            }
        else:
            print('extract audio: false')
            YDL_OPTS = {}
        with youtube_dl.YoutubeDL(YDL_OPTS) as dl:
            try:
                print(link)
                dl.download([link])
            except Exception as e:
                print(e)

    def _download_youtube_link_extract_nogui(self, link, extract):
        if extract:
            print('extract audio: true')
            YDL_OPTS = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            }
        else:
            print('extract audio: false')
            YDL_OPTS = {}
        with youtube_dl.YoutubeDL(YDL_OPTS) as dl:
            try:
                print(link)
                dl.download([link])
            except Exception as e:
                print(e)


class GUI(QWidget):

    def __init__(self):
        global WIDTH, HEIGHT

        super().__init__()
        self.api = API()

        self.setWindowTitle('Spotify / Youtube Downloader')
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
        self.link.setPlaceholderText(
            'https://www.youtube.com/... https://open.spotify.com/...')
        self.btn = QPushButton('Download', self)
        self.btn.resize(self.btn.sizeHint())
        self.btn.clicked.connect(self.download)
        self._dir = QPushButton('Select Directory', self)
        self._dir.clicked.connect(self.directory)
        self.info = QLabel('-----')
        self.credentials = QPushButton('credentials.json (only Spotify)', self)
        self.credentials.clicked.connect(self.creds)
        self.extract = QCheckBox('Extract Audio (only YouTube)')
        layout.addWidget(self.link, 0, 0)
        layout.addWidget(self.btn, 0, 1)
        layout.addWidget(self._dir, 1, 1)
        layout.addWidget(self.info, 1, 0)
        layout.addWidget(self.credentials, 2, 1)
        layout.addWidget(self.extract, 3, 1)
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
        self.api.initSpotify(self.creds)
        ProcessRunnable(target=self.api._download, args=(
            self.dir, self.link.text(), self.extract, self.info)).start()


if __name__ == "__main__":
    usage = __file__ + ' <dir> <link or query> <extract: true or false>'
    if len(sys.argv) == 1:
        app = QApplication([])
        gui = GUI()
        sys.exit(app.exec_())
    elif len(sys.argv) > 3:
        API()._download_nogui(sys.argv[1], sys.argv[2], bool(sys.argv[3]))
    else:
        print(usage)
