"""Displays brancos de sete segmentos, sem arquivos de fonte externos."""
from io import BytesIO

from PIL import Image, ImageDraw, ImageFilter
from direct.gui.DirectGui import DirectFrame
from panda3d.core import PNMImage, StringStream, Texture, TransparencyAttrib

DIGIT_SEGMENTS = {
    '0': 'abcdef', '1': 'bc', '2': 'abdeg', '3': 'abcdg', '4': 'bcfg',
    '5': 'acdfg', '6': 'acdefg', '7': 'abc', '8': 'abcdefg', '9': 'abcdfg',
}


def display_image(value):
    """Desenha segmentos chanfrados e dois pontos com fundo transparente."""
    widths = [24 if char == ':' else 64 for char in value]
    image = Image.new('RGBA', (sum(widths), 104))
    draw = ImageDraw.Draw(image)
    offset = 0
    for char, width in zip(value, widths):
        if char == ':':
            for y in (32, 72):
                draw.rectangle((offset + 8, y - 4, offset + 15, y + 3), fill='white')
        else:
            segments = {}
            for name, y in [('a', 8), ('g', 52), ('d', 96)]:
                segments[name] = [(12, y), (17, y - 5), (47, y - 5),
                                  (52, y), (47, y + 5), (17, y + 5)]
            for name, x, y in [('f', 10, 30), ('b', 54, 30),
                               ('e', 10, 74), ('c', 54, 74)]:
                segments[name] = [(x, y - 19), (x + 5, y - 14), (x + 5, y + 14),
                                  (x, y + 19), (x - 5, y + 14), (x - 5, y - 14)]
            for name in DIGIT_SEGMENTS[char]:
                draw.polygon([(offset + x, y) for x, y in segments[name]], fill='white')
        offset += width
    outline = Image.new("RGBA", image.size, (3, 12, 20, 255))
    outline.putalpha(image.getchannel("A").filter(ImageFilter.MaxFilter(7)))
    outline.alpha_composite(image)
    return outline


class SevenSegmentDisplay(DirectFrame):
    def __init__(self, parent, position, height=0.14):
        super().__init__(parent=parent, pos=position, frameColor=(0, 0, 0, 0))
        self.setTransparency(TransparencyAttrib.MAlpha)
        self.height = height
        self.width = 0.0
        self.value = None

    def set_value(self, value):
        if value == self.value:
            return
        image = display_image(value)
        buffer = BytesIO()
        image.save(buffer, format='PNG')
        pnm = PNMImage()
        pnm.read(StringStream(buffer.getvalue()))
        texture = Texture('seven-segment-display')
        texture.load(pnm)
        texture.setMinfilter(Texture.FTLinear)
        texture.setMagfilter(Texture.FTLinear)
        self.width = self.height * image.width / image.height
        self['image'] = texture
        self['image_scale'] = (self.width / 2, 1, self.height / 2)
        self['image_pos'] = (self.width / 2, 0, 0)
        self.value = value
