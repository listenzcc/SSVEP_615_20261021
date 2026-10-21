"""
File: color_manager.py
Author: Chuncheng Zhang
Date: 2025-10-10
Copyright & Email: chuncheng.zhang@ia.ac.cn

Purpose:
    Load pretty & styled color schemes.

Functions:
    1. Requirements and constants
    2. Function and class
    3. Play ground
    4. Pending
    5. Pending
"""


# %% ---- 2025-10-10 ------------------------
# Requirements and constants
import pandas as pd
from pathlib import Path


# %% ---- 2025-10-10 ------------------------
# Function and class
class WowColors:
    color_dir = Path('./resource/color')
    class_colors = pd.read_csv(color_dir / 'wow-class-colors.csv', sep='\t')
    power_colors = pd.read_csv(color_dir / 'wow-power-colors.csv', sep='\t')
    quality_colors = pd.read_csv(
        color_dir / 'wow-quality-colors.csv', sep='\t')

    def report(self):
        print(self.class_colors)
        print(self.power_colors)
        print(self.quality_colors)


class MyColors:
    color_dir = Path('./resource/color')
    damage_colors = pd.read_csv(color_dir / 'damage-colors.csv', sep='\t')

    def report(self):
        print(self.damage_colors)


# %% ---- 2025-10-10 ------------------------
# Play ground
if __name__ == '__main__':
    wc = WowColors()
    wc.report()

    mc = MyColors()
    mc.report()


# %% ---- 2025-10-10 ------------------------
# Pending


# %% ---- 2025-10-10 ------------------------
# Pending
