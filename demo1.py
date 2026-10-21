"""
File: demo1.py
Author: Chuncheng Zhang
Date: 2026-04-10
Copyright & Email: chuncheng.zhang@ia.ac.cn

Purpose:
    The basic demo with cursor interaction.
    The rectangle under cursor is flipped at given frequency.

Functions:
    1. Requirements and constants
    2. Function and class
    3. Play ground
    4. Pending
    5. Pending
"""


# %% ---- 2026-04-10 ------------------------
# Requirements and constants
from omegaconf import OmegaConf
import argparse
import glfw
import math
import random
from util.glfw_window import GLFWWindow, TextAnchor
from util.logging import logger
from util.parallel_port import ParallelPortTrigger

FONT_SIZE = 48
APP_STATE = 'idle'
PHASE_START = None
CURRENT_BLOCK_INDEX = 0
FLICKER_TRIGGER_SENT = False


# %%
conf = OmegaConf.load('./conf/demo1.yaml')
logger.info(f'Using {conf=}')
# 读取目标文字块配置（12个）
TARGET_BLOCKS = {str(k): v for k, v in conf.design.target_blocks.items()}
# 读取闪烁块配置（11个）
FLICKER_BLOCKS = {str(k): v for k, v in conf.design.flicker_blocks.items()}
DISPLAY_TARGET_ITEMS = list(TARGET_BLOCKS.items())
DISPLAY_FLICKER_ITEMS = list(FLICKER_BLOCKS.items())
# 创建BLOCK_MAP，包含12个文字框（实验目标）
# 格式: [x, y, 宽, 高]
BLOCK_MAP = {}
for k, v in TARGET_BLOCKS.items():
    BLOCK_MAP[k] = [v[1], v[2], v[3], v[4]]
USE_SPECIFIED_ORDER = bool(conf.experiment.use_specified_order)
CONTINUOUS_MODE = bool(conf.experiment.continuous_mode)  # 演示模式：一直循环
CONFIGURED_BLOCK_ORDER = [str(item) for item in conf.experiment.block_order]
BLOCK_ITEMS = []
PROMPT_BOX = conf.design.prompt_box
PROMPT_TEXT_SCALE = conf.design.prompt_text_scale
COUNTDOWN_TEXT_SCALE = conf.design.countdown_text_scale
CUE_SECONDS = float(conf.experiment.cue_seconds)
FLICKER_SECONDS = float(conf.experiment.flicker_seconds)
RED_FRAME_THICKNESS = float(conf.design.red_frame_thickness)
SHOW_RED_FRAME = bool(conf.design.show_red_frame)  # 是否显示红色提示框
BACKGROUND_ENABLED = bool(conf.design.background_enabled)
BACKGROUND_COLOR = tuple(conf.design.background_color)
BLOCK_TRIGGER_CODES = {str(k): int(v)
                       for k, v in conf.experiment.block_trigger_codes.items()}

missing_trigger_codes = [
    key for key in BLOCK_MAP if key not in BLOCK_TRIGGER_CODES]
if missing_trigger_codes:
    raise ValueError(
        f'block_trigger_codes is missing keys from design.blocks: {missing_trigger_codes}')

PARALLEL_PORT = ParallelPortTrigger(
    enabled=bool(conf.parallel_port.enabled),
    address=int(str(conf.parallel_port.address), 0),
    dll_path=conf.parallel_port.dll_path,
    pulse_width_ms=float(conf.parallel_port.pulse_width_ms),
    reset_to_zero=bool(conf.parallel_port.reset_to_zero),
)
ROUND_START_CODE = int(conf.parallel_port.round_start_code)
ROUND_END_CODE = int(conf.parallel_port.round_end_code)

# %% ---- 2026-04-10 ------------------------
# Function and class


def build_block_items():
    if USE_SPECIFIED_ORDER:
        missing_blocks = [
            key for key in CONFIGURED_BLOCK_ORDER if key not in BLOCK_MAP]
        # 演示模式(continuous_mode)下允许重复和未定义的区块
        # 实验模式下保持严格检查
        if not CONTINUOUS_MODE:
            duplicate_blocks = [
                key for key in CONFIGURED_BLOCK_ORDER if CONFIGURED_BLOCK_ORDER.count(key) > 1]
            undefined_blocks = [
                key for key in BLOCK_MAP if key not in CONFIGURED_BLOCK_ORDER]

            if duplicate_blocks:
                raise ValueError(
                    f'Duplicate keys found in block_order: {sorted(set(duplicate_blocks))}')

            if undefined_blocks:
                raise ValueError(
                    f'block_order is missing keys from design.blocks: {undefined_blocks}')

        if missing_blocks:
            raise ValueError(
                f'Invalid block_order keys not found in design.blocks: {missing_blocks}')

        block_order = CONFIGURED_BLOCK_ORDER
    else:
        block_order = list(BLOCK_MAP.keys())
        random.shuffle(block_order)

    return [(key, BLOCK_MAP[key]) for key in block_order]


def start_experiment_round(start_time):
    global APP_STATE, PHASE_START, CURRENT_BLOCK_INDEX, BLOCK_ITEMS, FLICKER_TRIGGER_SENT

    BLOCK_ITEMS = build_block_items()
    APP_STATE = 'cue'
    PHASE_START = start_time
    CURRENT_BLOCK_INDEX = 0
    FLICKER_TRIGGER_SENT = False

    order = [key for key, _ in BLOCK_ITEMS]
    order_mode = 'specified' if USE_SPECIFIED_ORDER else 'random'
    logger.info(f'Start experiment round: mode={order_mode}, order={order}')
    logger.info(
        f'Cue started: index=1/{len(BLOCK_ITEMS)}, block={BLOCK_ITEMS[0][0]}, t={start_time:0.3f}')
    PARALLEL_PORT.send(ROUND_START_CODE)


def draw_frame(x, y, w, h, color='#ff0000', thickness=0.004):
    wnd.draw_rect(x, y, w, thickness, color)
    wnd.draw_rect(x, y+h-thickness, w, thickness, color)
    wnd.draw_rect(x, y, thickness, h, color)
    wnd.draw_rect(x+w-thickness, y, thickness, h, color)


def advance_experiment_phase(t):
    global APP_STATE, PHASE_START, CURRENT_BLOCK_INDEX, BLOCK_ITEMS, FLICKER_TRIGGER_SENT

    if APP_STATE == 'cue' and t - PHASE_START >= CUE_SECONDS:
        APP_STATE = 'flicker'
        PHASE_START = t
        FLICKER_TRIGGER_SENT = False
        block_key = BLOCK_ITEMS[CURRENT_BLOCK_INDEX][0]
        logger.info(
            f'Flicker started: index={CURRENT_BLOCK_INDEX + 1}/{len(BLOCK_ITEMS)}, block={block_key}, t={t:0.3f}')
        return

    if APP_STATE == 'flicker' and t - PHASE_START >= FLICKER_SECONDS:
        CURRENT_BLOCK_INDEX += 1
        if CURRENT_BLOCK_INDEX >= len(BLOCK_ITEMS):
            if CONTINUOUS_MODE:
                # 演示模式：循环回到第一个区块
                CURRENT_BLOCK_INDEX = 0
                APP_STATE = 'cue'
                PHASE_START = t
                FLICKER_TRIGGER_SENT = False
                block_key = BLOCK_ITEMS[CURRENT_BLOCK_INDEX][0]
                logger.info(
                    f'Cue started (looping): index=1/{len(BLOCK_ITEMS)}, block={block_key}, t={t:0.3f}')
                return
            else:
                # 实验模式：结束
                APP_STATE = 'finished'
                PHASE_START = None
                logger.info('Experiment round completed')
                PARALLEL_PORT.send(ROUND_END_CODE)
                return
        APP_STATE = 'cue'
        PHASE_START = t
        FLICKER_TRIGGER_SENT = False
        block_key = BLOCK_ITEMS[CURRENT_BLOCK_INDEX][0]
        logger.info(
            f'Cue started: index={CURRENT_BLOCK_INDEX + 1}/{len(BLOCK_ITEMS)}, block={block_key}, t={t:0.3f}')
        return


def get_prompt_message_and_scale(t):
    if APP_STATE == 'idle':
        return 'S=开始 R=重开 Esc=退出', PROMPT_TEXT_SCALE

    if APP_STATE == 'cue':
        remaining = max(0, math.ceil(CUE_SECONDS - (t - PHASE_START)))
        return f'提示 {CURRENT_BLOCK_INDEX + 1}/{len(BLOCK_ITEMS)}: {remaining}', PROMPT_TEXT_SCALE

    if APP_STATE == 'flicker':
        remaining = max(0, math.ceil(FLICKER_SECONDS - (t - PHASE_START)))
        return f'闪烁 {CURRENT_BLOCK_INDEX + 1}/{len(BLOCK_ITEMS)}: {remaining}', PROMPT_TEXT_SCALE

    if APP_STATE == 'finished':
        return '完成 R=重开 Esc=退出', PROMPT_TEXT_SCALE

    return '', PROMPT_TEXT_SCALE


def key_callback(window, key, scancode, action, mods):
    '''
    Key press callback.
    '''

    # Only be interested in PRESS event.
    if not action == glfw.PRESS:
        return

    global APP_STATE

    key_name = glfw.get_key_name(key, scancode)
    print(key, key_name, scancode, action, mods)

    # 如果按下ESC键则关闭窗口
    if key == glfw.KEY_ESCAPE:
        print("已按下ESC键，程序退出。")
        glfw.set_window_should_close(window, True)
        return

    if key == glfw.KEY_R:
        start_experiment_round(glfw.get_time())
        return

    if key == glfw.KEY_S and APP_STATE in ['idle', 'finished']:
        start_experiment_round(glfw.get_time())
        return

    return


t0 = 0


def main_render(freq=0.2):
    global FLICKER_TRIGGER_SENT
    global t0

    # Get time
    t = glfw.get_time()
    advance_experiment_phase(t)
    blocks_are_active = APP_STATE == 'flicker'
    highlighted_block_key = None
    current_block_key = None
    trigger_code = None

    if APP_STATE == 'cue' and BLOCK_ITEMS:
        highlighted_block_key = BLOCK_ITEMS[CURRENT_BLOCK_INDEX][0]

    # The 13rd always need this.
    try:
        current_block_key = BLOCK_ITEMS[CURRENT_BLOCK_INDEX][0]
        trigger_code = BLOCK_TRIGGER_CODES[current_block_key]
    except Exception:
        pass

    if APP_STATE == 'flicker' and BLOCK_ITEMS and not FLICKER_TRIGGER_SENT:
        current_block_key = BLOCK_ITEMS[CURRENT_BLOCK_INDEX][0]
        trigger_code = BLOCK_TRIGGER_CODES[current_block_key]
        logger.info(
            f'Flicker first frame trigger: index={CURRENT_BLOCK_INDEX + 1}/{len(BLOCK_ITEMS)}, '
            f'block={current_block_key}, code=0x{trigger_code:02X}, t={t:0.3f}'
        )
        PARALLEL_PORT.send(trigger_code)
        FLICKER_TRIGGER_SENT = True
        t0 = glfw.get_time()

    # Display the 13rd when necessary.
    if trigger_code == 13 and current_block_key == '13':
        for target_key, target_data in DISPLAY_TARGET_ITEMS[12:]:
            label_text, x, y, w, h = target_data

            # 绘制标签（黑色背景，白色文字）
            wnd.draw_rect(x, y-h, w, h, (0.0, 0.0, 0.0, 1.0))
            wnd.draw_text(label_text, x + w/2, y-h + h/2,
                          scale=0.8, anchor=TextAnchor.C, color='#ffffff')

            # 高亮显示当前目标
            if SHOW_RED_FRAME and highlighted_block_key == target_key:
                draw_frame(x, y-h, w, h,
                           color='#ff0000', thickness=RED_FRAME_THICKNESS)

    # 绘制目标文字块（12个）
    for target_key, target_data in DISPLAY_TARGET_ITEMS[:12]:
        label_text, x, y, w, h = target_data

        # 绘制标签（黑色背景，白色文字）
        wnd.draw_rect(x, y-h, w, h, (0.0, 0.0, 0.0, 1.0))
        wnd.draw_text(label_text, x + w/2, y-h + h/2,
                      scale=0.8, anchor=TextAnchor.C, color='#ffffff')

        # 高亮显示当前目标
        if SHOW_RED_FRAME and highlighted_block_key == target_key:
            draw_frame(x, y-h, w, h,
                       color='#ff0000', thickness=RED_FRAME_THICKNESS)

    # 绘制闪烁块（11个）
    for flicker_key, flicker_data in DISPLAY_FLICKER_ITEMS:
        freq, x, y, w, h = flicker_data

        # 计算闪烁块亮度
        if blocks_are_active:
            brightness = (math.sin((t-t0)*2*math.pi*freq) + 1.0) * 0.5
        else:
            brightness = 1.0  # 纯白色背景

        # 绘制闪烁块
        wnd.draw_rect(x, y-h, w, h, (brightness, brightness, brightness, 1.0))

        # 绘制频率标签
        # freq_text = f'{freq}Hz'
        # wnd.draw_text(freq_text, x + w/2, y - h + h/2,
        #               scale=0.5, anchor=TextAnchor.C, color='#000000')

    # Draw prompt box
    # box_x, box_y, box_w, box_h = PROMPT_BOX
    # prompt_text, prompt_scale = get_prompt_message_and_scale(t)
    # wnd.draw_rect(box_x, box_y, box_w, box_h, (0, 0, 0, 1))
    # wnd.draw_text(prompt_text, box_x + box_w/2, box_y + box_h/2,
    #               scale=prompt_scale, anchor=TextAnchor.C, color='#ffffff')

    # toc = glfw.get_time()
    # print(int(1/(toc-t)))

    return


# %% ---- 2026-04-10 ------------------------
# Play ground


argparse = argparse.ArgumentParser()
argparse.add_argument('--freq', type=float, default=0.2,
                      help='The blinking frequency of the square.')

opt = argparse.parse_args()

print(f'{opt=}')

# %%
wnd = GLFWWindow()
# wnd.load_font('c:\\windows\\fonts\\stliti.ttf', FONT_SIZE)
wnd.load_font('./resource/font/SIMSUNB.TTF', FONT_SIZE)
wnd.init_window()

glfw.set_key_callback(wnd.window, key_callback)

# Run FOREVER
wnd.render_loop(main_render, background_enabled=BACKGROUND_ENABLED,
                background_color=BACKGROUND_COLOR, freq=opt.freq)

# %% ---- 2026-04-10 ------------------------
# Pending


# %% ---- 2026-04-10 ------------------------
# Pending
