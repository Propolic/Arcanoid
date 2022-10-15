from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import QSize


def convert_Blob_To_Icon (blob):
    pm = QPixmap()
#    pm.loadFromData(bytes(blob, encoding = "utf-8"))
    pm.loadFromData(bytes(blob))
    icon = QIcon(pm)
    return icon

def set_icon_from_blob(btn, img_blob, size_icon):
    icon = convert_Blob_To_Icon(img_blob)
    sizeIcon = QSize(size_icon, size_icon)
    btn.setIcon(icon)
    btn.setIconSize(sizeIcon)
    btn.setText("")
    return btn


def main():
    pass

if __name__ == '__main__':
    main()
