"""Captura menus USB e partida local offscreen sem alterar saves do jogador."""
from pathlib import Path
from tempfile import TemporaryDirectory
from io import BytesIO
import sys
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from PIL import Image
from panda3d.core import ClockObject, PNMImage, StringStream, loadPrcFileData
loadPrcFileData('', 'audio-library-name null')
from game.app import Game


def main():
    destination = ROOT / 'docs/images'
    frames = []
    with TemporaryDirectory() as save:
        game = Game(offscreen=True, storage_directory=Path(save))
        try:
            clock = ClockObject.getGlobalClock()
            clock.setMode(ClockObject.MNonRealTime)
            clock.setDt(1 / 20)
            for screen, name in [(game.controller_options, 'controle-usb'),
                                 (game.two_player_menu, 'dois-jogadores-menu'),
                                 (lambda: game.local_controls_menu(1), 'dois-jogadores-controles')]:
                screen()
                for _ in range(3):
                    game.graphicsEngine.renderFrame()
                game.win.saveScreenshot(str(destination / (name + '.png')))
            game.new_capture()
            for _ in range(3):
                game.graphicsEngine.renderFrame()
            game.win.saveScreenshot(str(destination / 'dois-jogadores.png'))
            game.set_key('w', True)
            game.set_key('arrow_up', True)
            for _ in range(50):
                game.taskMgr.step()
                game.graphicsEngine.renderFrame()
                shot, stream = PNMImage(), StringStream()
                game.win.getScreenshot(shot)
                shot.write(stream, 'frame.png')
                with Image.open(BytesIO(stream.getData())) as image:
                    frames.append(image.convert('RGB').resize((640, 360)))
        finally:
            game.destroy()
    frames[0].save(destination / 'dois-jogadores.gif', save_all=True,
                   append_images=frames[1:], duration=50, loop=0)
    print(destination / 'dois-jogadores.gif')


if __name__ == '__main__':
    main()
