import eel
from database import m3_engine

eel.init('web')

if __name__ == '__main__':
    eel.start('index.html', size=(1100, 750))