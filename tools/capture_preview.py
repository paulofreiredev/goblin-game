"""Capturas e GIF curto da execução offscreen real; não substitui teste interativo."""
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
    destination = ROOT / 'docs/images'
    destination.mkdir(parents=True, exist_ok=True)
    frames = []
    with TemporaryDirectory() as folder:
        game = Game(offscreen=True, storage_directory=Path(folder))
        try:
            clock = ClockObject.getGlobalClock()
            clock.setMode(ClockObject.MNonRealTime)
            clock.setDt(1 / 20)
            for phase, name in enumerate(['manha', 'tarde', 'noite']):
                game.new_game()
                game.player.phase = phase
                game.apply_phase()
                for _ in range(3):
                    game.graphicsEngine.renderFrame()
                game.win.saveScreenshot(str(destination / f'{name}.png'))
                game.set_key('d', True)
                for _ in range(30):
                    game.taskMgr.step()
                    game.graphicsEngine.renderFrame()
                    screenshot = PNMImage()
                    game.win.getScreenshot(screenshot)
                    stream = StringStream()
                    screenshot.write(stream, 'frame.png')
                    with Image.open(BytesIO(stream.getData())) as image:
                        frames.append(image.convert('RGB').resize((640, 360)))
                game.keys.clear()
            game.options()
            for _ in range(3):
                game.graphicsEngine.renderFrame()
            game.win.saveScreenshot(str(destination / 'dificuldade.png'))
        finally:
            game.destroy()
    frames[0].save(destination / 'jogo.gif', save_all=True, append_images=frames[1:],
                   duration=50, loop=0, optimize=True)
    print(destination / 'jogo.gif')


if __name__ == '__main__':
    main()
