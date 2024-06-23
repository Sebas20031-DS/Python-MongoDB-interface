### Instalación de paquetes
# %pip install pymongo
# %pip install Pillow
# %pip install PyQt5

import sys
import os
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, 
                             QLineEdit, QListWidget, QFileDialog, QInputDialog, QLabel)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from pymongo import MongoClient
from PIL import Image

class ImageManager(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.connectDB()

    def initUI(self):
        self.setWindowTitle('Image Manager')
        self.setGeometry(100, 100, 600, 500)

        layout = QVBoxLayout()

        # Add image button
        self.addButton = QPushButton('Add Image')
        self.addButton.clicked.connect(self.addImage)
        layout.addWidget(self.addButton)

        # Search bar
        searchLayout = QHBoxLayout()
        self.searchBar = QLineEdit()
        self.searchButton = QPushButton('Search')
        self.searchButton.clicked.connect(self.searchImages)
        searchLayout.addWidget(self.searchBar)
        searchLayout.addWidget(self.searchButton)
        layout.addLayout(searchLayout)

        # Results list
        self.resultsList = QListWidget()
        self.resultsList.itemClicked.connect(self.displayImage)
        layout.addWidget(self.resultsList)

        # Image display
        self.imageLabel = QLabel()
        self.imageLabel.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.imageLabel)

        # Exit button
        self.exitButton = QPushButton('Exit')
        self.exitButton.clicked.connect(self.close)
        layout.addWidget(self.exitButton)

        self.setLayout(layout)

    def connectDB(self):
        client = MongoClient('localhost', 27017)
        db = client['image_database']
        self.collection = db['images']

    def addImage(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Image Files (*.png *.jpg *.bmp)")
        if fileName:
            tags, ok = QInputDialog.getText(self, 'Image Tags', 'Enter tags (comma-separated):')
            if ok:
                image_info = {
                    'filename': os.path.basename(fileName),
                    'path': fileName,
                    'tags': [tag.strip() for tag in tags.split(',')]
                }
                self.collection.insert_one(image_info)
                print(f"Added image: {fileName}")

    def searchImages(self):
        query = self.searchBar.text()
        results = self.collection.find({'tags': {'$regex': query, '$options': 'i'}})
        
        self.resultsList.clear()
        for result in results:
            self.resultsList.addItem(f"{result['filename']} - Tags: {', '.join(result['tags'])}")

    def displayImage(self, item):
        filename = item.text().split(' - ')[0]
        image_info = self.collection.find_one({'filename': filename})
        if image_info:
            pixmap = QPixmap(image_info['path'])
            if not pixmap.isNull():
                pixmap = pixmap.scaled(300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.imageLabel.setPixmap(pixmap)
            else:
                self.imageLabel.setText("Unable to load image")
        else:
            self.imageLabel.setText("Image not found in database")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ImageManager()
    ex.show()
    app.exec_()