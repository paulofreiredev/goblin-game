"""Gera a fonte vetorial original do jogo; requer fontTools apenas para regenerar."""
import math
from pathlib import Path
import unicodedata

from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen

ROOT = Path(__file__).resolve().parent.parent
# Traços separados, com pontas chanfradas, inspirados em displays digitais.
SEGMENTS = {
    'a': (80, 700, 520, 700), 'b': (550, 670, 550, 380),
    'c': (550, 320, 550, 30), 'd': (80, 0, 520, 0),
    'e': (50, 30, 50, 320), 'f': (50, 380, 50, 670),
    'g': (80, 350, 520, 350), 'h': (80, 670, 270, 380),
    'i': (300, 670, 300, 380), 'j': (520, 670, 330, 380),
    'k': (80, 30, 270, 320), 'l': (300, 30, 300, 320),
    'm': (520, 30, 330, 320),
}
LETTERS = {
    'A': 'abcefg', 'B': 'abcdefg', 'C': 'adef', 'D': 'abcdil',
    'E': 'adefg', 'F': 'aefg', 'G': 'acdefg', 'H': 'bcefg',
    'I': 'adil', 'J': 'bcde', 'K': 'efjm', 'L': 'def',
    'M': 'bcefhj', 'N': 'bcefhm', 'O': 'abcdef', 'P': 'abefg',
    'Q': 'abcdefm', 'R': 'abefgm', 'S': 'acdfg', 'T': 'ail',
    'U': 'bcdef', 'V': 'efjk', 'W': 'bcefkm', 'X': 'hjkm',
    'Y': 'hjl', 'Z': 'adjk',
    '0': 'abcdef', '1': 'bc', '2': 'abdeg', '3': 'abcdg',
    '4': 'bcfg', '5': 'acdfg', '6': 'acdefg', '7': 'abc',
    '8': 'abcdefg', '9': 'abcdfg', '-': 'g', '+': 'gil',
    '/': 'jk', '\\': 'hm', '|': 'il', '=': '', '_': 'd',
    '[': 'adef', ']': 'abcd', '(': 'ef', ')': 'bc',
    '<': 'jm', '>': 'hk', '*': 'ghjkm',
}


def stroke(pen, x0, y0, x1, y1, thickness=48):
    length = math.hypot(x1 - x0, y1 - y0)
    ux, uy = (x1 - x0) / length, (y1 - y0) / length
    px, py = -uy * thickness / 2, ux * thickness / 2
    bevel = min(thickness / 2, length / 4)
    points = [(x0, y0), (x0 + ux * bevel + px, y0 + uy * bevel + py),
              (x1 - ux * bevel + px, y1 - uy * bevel + py), (x1, y1),
              (x1 - ux * bevel - px, y1 - uy * bevel - py),
              (x0 + ux * bevel - px, y0 + uy * bevel - py)]
    pen.moveTo(tuple(round(v) for v in points[0]))
    for point in points[1:]:
        pen.lineTo(tuple(round(v) for v in point))
    pen.closePath()


def glyph(char):
    pen = TTGlyphPen(None)
    decomposed = unicodedata.normalize('NFD', char)
    base = decomposed[0].upper()
    for segment in LETTERS.get(base, ''):
        stroke(pen, *SEGMENTS[segment])
    if base in '.:;!?' or base not in LETTERS and not char.isspace():
        stroke(pen, 285, 0, 315, 0, 60)
    if base in ':;':
        stroke(pen, 285, 450, 315, 450, 60)
    if base == '!':
        stroke(pen, 300, 170, 300, 700)
    if base == '?':
        for segment in 'abg':
            stroke(pen, *SEGMENTS[segment])
        stroke(pen, 300, 150, 300, 320)
    if base == ',':
        stroke(pen, 280, -100, 310, 0)
    if base in "'\"":
        stroke(pen, 240, 580, 270, 700)
        if base == '"':
            stroke(pen, 350, 580, 380, 700)
    if base == '=':
        stroke(pen, 80, 250, 520, 250)
        stroke(pen, 80, 450, 520, 450)
    for accent in decomposed[1:]:
        if accent == '\u0301':
            stroke(pen, 250, 800, 350, 880, 36)
        elif accent == '\u0300':
            stroke(pen, 250, 880, 350, 800, 36)
        elif accent == '\u0302':
            stroke(pen, 200, 800, 300, 880, 36)
            stroke(pen, 300, 880, 400, 800, 36)
        elif accent == '\u0303':
            for coords in [(170, 800, 250, 850), (250, 850, 350, 800), (350, 800, 430, 850)]:
                stroke(pen, *coords, 36)
        elif accent == '\u0327':
            stroke(pen, 300, -60, 340, -110, 36)
            stroke(pen, 340, -110, 270, -160, 36)
        elif accent == '\u0308':
            stroke(pen, 190, 830, 220, 830, 40)
            stroke(pen, 380, 830, 410, 830, 40)
    return pen.glyph()


def main():
    characters = [chr(code) for code in range(32, 256)]
    cmap = {ord(char): f'uni{ord(char):04X}' for char in characters}
    builder = FontBuilder(1000, isTTF=True)
    builder.setupGlyphOrder(['.notdef'] + list(cmap.values()))
    builder.setupCharacterMap(cmap)
    builder.setupGlyf({'.notdef': glyph('?'), **{cmap[ord(c)]: glyph(c) for c in characters}})
    builder.setupHorizontalMetrics({name: (680, 0) for name in builder.font.getGlyphOrder()})
    builder.setupHorizontalHeader(ascent=950, descent=-200)
    builder.setupNameTable({'familyName': 'Goblin Digital', 'styleName': 'Regular',
                           'uniqueFontIdentifier': 'GoblinDigital-Regular-1',
                           'fullName': 'Goblin Digital Regular', 'psName': 'GoblinDigital-Regular',
                           'version': 'Version 1.0',
                           'copyright': 'Fonte original criada para goblin-game.'})
    builder.setupOS2(sTypoAscender=950, sTypoDescender=-200, usWinAscent=950, usWinDescent=200)
    builder.setupPost()
    builder.setupMaxp()
    destination = ROOT / 'assets/fonts/goblin-digital.ttf'
    destination.parent.mkdir(parents=True, exist_ok=True)
    builder.save(destination)
    print(destination)


if __name__ == '__main__':
    main()
