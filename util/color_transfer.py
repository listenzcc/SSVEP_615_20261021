"""
File: color_transfer.py
Author: Chuncheng Zhang
Date: 2025-10-10
Copyright & Email: chuncheng.zhang@ia.ac.cn

Purpose:
    Color transfer.

Functions:
    1. Requirements and constants
    2. Function and class
    3. Play ground
    4. Pending
    5. Pending
"""


# %% ---- 2025-10-10 ------------------------
# Requirements and constants


# %% ---- 2025-10-10 ------------------------
# Function and class
class ColorTransfer:
    '''Translate everything into (0, 1) rgba tuple'''
    _rgba = (1, 1, 1, 1)

    def __init__(self, inp):
        self.rgba = inp

    @property
    def rgba(self):
        return self._rgba

    @rgba.setter
    def rgba(self, inp):
        if isinstance(inp, tuple) and len(inp) == 4:
            self._rgba = inp
            return

        if isinstance(inp, tuple) and len(inp) == 3:
            self._rgba = (inp[0], inp[1], inp[2], 1)
            return

        if isinstance(inp, tuple) and len(inp) == 2:
            self.rgba = inp[0]
            r, g, b, a = self.rgba
            self.rgba = (r, g, b, inp[1])
            return

        if isinstance(inp, float):
            self._rgba = (inp, inp, inp, inp)
            return

        if len(inp) == 7:
            inp += 'ff'

        r = int(inp[1:3], base=16) / 255
        g = int(inp[3:5], base=16) / 255
        b = int(inp[5:7], base=16) / 255
        a = int(inp[7:9], base=16) / 255
        self._rgba = (r, g, b, a)
        return


# %% ---- 2025-10-10 ------------------------
# Play ground
if __name__ == '__main__':
    test_cases = {
        'rgba': (0.1, 0.2, 0.3, 0.4),
        'rgb': (0.1, 0.2, 0.3),
        'float': 0.5,
        'hex+a': ('#abcdef', 0.5),
        'hex(6)': '#abcdef',
        'hex(8)': '#abcdefaa'
    }

    for k, v in test_cases.items():
        print(f'{k}:\t {v}, {ColorTransfer(v).rgba}')


# %% ---- 2025-10-10 ------------------------
# Pending


# %% ---- 2025-10-10 ------------------------
# Pending
