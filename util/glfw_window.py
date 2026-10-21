"""
File: glfw_window.py
Author: Chuncheng Zhang
Date: 2025-10-09
Copyright & Email: chuncheng.zhang@ia.ac.cn

Purpose:
    GLFW window.

Functions:
    1. Requirements and constants
    2. Function and class
    3. Play ground
    4. Pending
    5. Pending
"""


# %% ---- 2025-10-09 ------------------------
# Requirements and constants
from .fps_ruler import FPSRuler
from .text_render import TextRenderer
from .color_transfer import ColorTransfer
from .logging import logger

import glfw
from enum import Enum
from OpenGL.GL import *

# %%

# %% ---- 2025-10-09 ------------------------
# Function and class


class TextAnchor(Enum):
    '''
    The text anchor setups.

    ----------- Top -----------
    ---------------------------
    Left ---- Center ---- Right
    ---------------------------
    ---------- Bottom ---------

    '''
    C = 0
    TL = 1
    TR = 2
    T = 3
    L = 4
    R = 5
    BL = 6
    BR = 7
    B = 8


class CursorPosition:
    _cursor_pos = (0, 0)

    @property
    def cursor_pos(self):
        return self._cursor_pos

    @cursor_pos.setter
    def cursor_pos(self, xy):
        self._cursor_pos = xy


class GLFWWindow(CursorPosition):
    # Monitor params (Read-only)
    width: int
    height: int
    refresh_rate: int

    # Window
    window = None

    # Options
    is_focused = True
    click_through = False

    # Addons
    text_renderer = TextRenderer()
    fps = FPSRuler()

    def __init__(self):
        super().__init__()
        pass

    def load_font(self, font_path: str, font_size: int = 48):
        self.text_renderer.load_font(font_path, font_size)
        self.font_path = font_path
        self.font_size = font_size
        return

    def on_focus_change(self, window, focused):
        self.is_focused = focused
        logger.info('Focus changed: {}'.format(
            'Got focus' if focused else 'Lost focus'))
        self.update_window_attributes()
        return

    def update_window_attributes(self):
        '''
        当窗口无焦点时自动启用点击穿透
        '''
        auto_click_through = not self.is_focused
        final_click_through = self.click_through or auto_click_through

        glfw.set_window_attrib(
            self.window,
            glfw.MOUSE_PASSTHROUGH,
            glfw.TRUE if final_click_through else glfw.FALSE
        )

        return

    def init_window(self):
        if not glfw.init():
            raise RuntimeError('Failed initialize GLFW')

        # 获取主显示器
        monitors = glfw.get_monitors()

        logger.info(f'Available monitors: {len(monitors)}, {monitors=}')

        primary_monitor = glfw.get_primary_monitor()

        # 获取视频模式(包含分辨率信息)
        vid_mode = glfw.get_video_mode(primary_monitor)

        # 提取分辨率
        width, height = vid_mode.size
        refresh_rate = vid_mode.refresh_rate
        self.width = width
        self.height = height
        self.refresh_rate = refresh_rate
        logger.info(
            f'Using primary monitor: {width} x {height} ({refresh_rate} Hz)')

        # 请求核心配置文件 for modern mode
        # glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        # glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        # glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

        # 配置窗口
        glfw.window_hint(glfw.TRANSPARENT_FRAMEBUFFER, glfw.TRUE)
        glfw.window_hint(glfw.DECORATED, glfw.FALSE)  # 无边框
        glfw.window_hint(glfw.SAMPLES, 4)  # 抗锯齿
        glfw.window_hint(glfw.FLOATING, glfw.TRUE)  # 置顶窗口

        # 设置点击穿透
        glfw.window_hint(glfw.MOUSE_PASSTHROUGH, glfw.TRUE)

        # Leave out 1 pixel to prevent from crashing. But don't know why.
        window = glfw.create_window(
            width-1, height-1, 'OpenGL Wnd.', None, None)

        if not window:
            glfw.terminate()
            raise RuntimeError(f'Can not create window: {glfw.get_error()}')

        # Make context
        glfw.make_context_current(window)

        self.window = window

        return window

    def render_top_bar(self):
        return
        scale = 0.5
        color = (1.0, 1.0, 1.0, 1.0)

        text = f"GLFW ({glfw.__version__}) is Rendering at {self.width} x {self.height} ({self.refresh_rate} Hz)"
        self.draw_text(text, 0, 1.0, scale, TextAnchor.TL, color)

        text = '窗口获得焦点' if self.is_focused else '窗口失去焦点'
        self.draw_text(text, 0.5, 1.0, scale, TextAnchor.T, color)

        text = ' | '.join([
            '-',
            f'FPS: {self.fps.get_fps():.2f}'
        ])
        self.draw_text(text, 1.0, 1.0, scale, TextAnchor.TR, color)
        return

    def render_loop(self, main_render: callable, *args, background_enabled=False, background_color=(0.85, 0.85, 0.85, 1.0), **kwargs):
        window = self.window

        # Bind focus callback
        # glfw.make_context_current(window)
        glfw.set_window_focus_callback(window, self.on_focus_change)
        self.update_window_attributes()

        # 设置混合模式以实现透明度
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glfw.swap_interval(1)

        # Main rendering loop
        while not glfw.window_should_close(window):
            t = glfw.get_time()
            # 设置背景
            if background_enabled:
                glClearColor(*background_color)
            else:
                glClearColor(0.0, 0.0, 0.0, 0.0)
            glClear(GL_COLOR_BUFFER_BIT)

            # Run the main_render() for custom rendering.
            main_render(*args, **kwargs)

            # Draw the top bar.
            # self.render_top_bar()

            # Just draw the buffer.
            glfw.swap_buffers(window)
            glfw.poll_events()

            # try:
            #     glfw.poll_events()
            #     self.fps.update()
            # except Exception as err:
            #     logger.exception(err)
            #     raise err

            # toc = glfw.get_time()
            # fps = int(1/(toc - t))
            # if fps >(144+10) or (fps < 144-10):
            #     print(fps)

        glfw.terminate()
        logger.info('Rendering stops')
        return

    def draw_rect(self, x, y, w, h, color=(1, 1, 1, 1)):
        '''
        Suppose the x, y is the SW corner of the rectangle.

        :param x, y, w, h: (0, 1) position and (0, 1) scale.
        '''
        color = ColorTransfer(color).rgba

        x = x * 2 - 1
        y = y * 2 - 1
        w *= 2
        h *= 2

        a = (x, y)
        b = (x, y+h)
        c = (x+w, y)
        d = (x+w, y+h)

        glBegin(GL_QUAD_STRIP)
        for e in [a, b, c, d]:
            glColor4f(*color)
            glVertex2f(*e)
        glEnd()
        return

    def draw_text(self, text, x, y, scale, anchor: TextAnchor = TextAnchor.BL, color=(1.0, 1.0, 1.0, 1.0)):
        '''
        The text is actually drawn by pixel units.

        :param x: (0, 1) position.
        :param y: (0, 1) position.
        '''
        color = ColorTransfer(color).rgba

        x = int(x * self.width)
        y = int(y * self.height)
        w, h, h2 = self.text_renderer.bounding_box(text, scale)

        if anchor == TextAnchor.BL:
            pass
        elif anchor == TextAnchor.BR:
            x -= w
        elif anchor == TextAnchor.B:
            x -= w // 2
        elif anchor == TextAnchor.TR:
            x -= w
            y -= h
        elif anchor == TextAnchor.TL:
            y -= h
        elif anchor == TextAnchor.T:
            x -= w // 2
            y -= h
        elif anchor == TextAnchor.C:
            x -= w // 2
            y -= h // 2
        elif anchor == TextAnchor.L:
            y -= h // 2
        elif anchor == TextAnchor.R:
            y -= h // 2
            x -= w

        self.text_renderer.render_text(text, x, y, scale, color)
        return w, h, h2

# %% ---- 2025-10-09 ------------------------
# Play ground


# %% ---- 2025-10-09 ------------------------
# Pending


# %% ---- 2025-10-09 ------------------------
# Pending
