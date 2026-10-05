"""Registra primeira/terceira pessoa em execução offscreen com save temporário."""
from io import BytesIO
from pathlib import Path
import sys
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from PIL import Image
from panda3d.core import ClockObject, PNMImage, StringStream, loadPrcFileData
loadPrcFileData('', 'audio-library-name null')
from game.app import Game


def main():
    frames = []
    folder = ROOT / 'docs/images'
    with TemporaryDirectory() as save:
        game = Game(offscreen=True, storage_directory=Path(save))
        try:
            game.new_game()
            clock = ClockObject.getGlobalClock()
            clock.setMode(ClockObject.MNonRealTime)
            clock.setDt(1 / 20)
            for mode, name in enumerate(['camera-terceira', 'camera-fps']):
                if mode:
                    game.toggle_camera()
                for _ in range(3):
                    game.graphicsEngine.renderFrame()
                game.win.saveScreenshot(str(folder / f'{name}.png'))
                game.set_key('w', True)
                for _ in range(25):
                    game.taskMgr.step()
                    game.graphicsEngine.renderFrame()
                    shot, stream = PNMImage(), StringStream()
                    game.win.getScreenshot(shot)
                    shot.write(stream, 'frame.png')
                    with Image.open(BytesIO(stream.getData())) as image:
                        frames.append(image.convert('RGB').resize((640, 360)))
                game.keys.clear()
        finally:
            game.destroy()
    frames[0].save(folder / 'camera-modos.gif', save_all=True, append_images=frames[1:], duration=50, loop=0)
    print(folder / 'camera-modos.gif')


if __name__ == '__main__':
    main()
