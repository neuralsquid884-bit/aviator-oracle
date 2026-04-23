"""
Custom reusable Kivy widgets for Aviator Oracle.
"""

from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.graphics import Color, RoundedRectangle, Rectangle, Line
from kivy.properties import StringProperty, ColorProperty, NumericProperty
from kivy.metrics import dp, sp

from utils.theme import *


class Card(BoxLayout):
    """Dark card container with rounded corners."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = [dp(14), dp(12)]
        self.spacing = dp(6)
        with self.canvas.before:
            Color(*BG_CARD)
            self._rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(14)])
        self.bind(pos=self._update, size=self._update)

    def _update(self, *a):
        self._rect.pos = self.pos
        self._rect.size = self.size


class FlatLabel(Label):
    """Label with sensible defaults."""
    def __init__(self, text='', font_size=sp(14), color=TEXT_PRIMARY,
                 bold=False, halign='left', **kwargs):
        super().__init__(
            text=text,
            font_size=font_size,
            color=color,
            bold=bold,
            halign=halign,
            valign='middle',
            size_hint_y=None,
            **kwargs
        )
        self.bind(size=lambda *a: setattr(self, 'text_size', (self.width, None)))
        self.texture_update()
        self.height = max(self.texture_size[1] + dp(4), dp(20))
        self.bind(texture_size=lambda *a: setattr(
            self, 'height', max(self.texture_size[1] + dp(4), dp(20))
        ))


class AccentButton(Button):
    """Primary action button with amber accent."""
    def __init__(self, text='', accent=None, **kwargs):
        super().__init__(
            text=text,
            font_size=sp(14),
            bold=True,
            background_color=(0, 0, 0, 0),
            color=TEXT_DARK,
            size_hint_y=None,
            height=dp(52),
            **kwargs
        )
        self._accent = accent or ACCENT_AMBER
        with self.canvas.before:
            self._btn_color = Color(*self._accent)
            self._btn_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(12)])
        self.bind(pos=self._upd, size=self._upd)

    def _upd(self, *a):
        self._btn_rect.pos = self.pos
        self._btn_rect.size = self.size


class GhostButton(Button):
    """Outlined ghost button."""
    def __init__(self, text='', accent=None, **kwargs):
        ac = accent or ACCENT_TEAL
        super().__init__(
            text=text,
            font_size=sp(13),
            background_color=(0, 0, 0, 0),
            color=ac,
            size_hint_y=None,
            height=dp(40),
            **kwargs
        )
        self._accent = ac
        with self.canvas.before:
            Color(*BG_CARD)
            self._bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(10)])
            self._border_color = Color(*ac)
            self._border = Line(rounded_rectangle=(self.x, self.y, self.width, self.height, dp(10)), width=1.2)
        self.bind(pos=self._upd, size=self._upd)

    def _upd(self, *a):
        self._bg.pos = self.pos
        self._bg.size = self.size
        self._border.rounded_rectangle = (self.x, self.y, self.width, self.height, dp(10))


class StatBox(BoxLayout):
    """Small stat card: label + big number."""
    def __init__(self, label='', value='—', value_color=None, **kwargs):
        super().__init__(orientation='vertical', padding=dp(10), spacing=dp(4), **kwargs)
        self._vc = value_color or ACCENT_AMBER
        with self.canvas.before:
            Color(*BG_CARD)
            self._rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(10)])
        self.bind(pos=self._upd, size=self._upd)
        self._lbl = FlatLabel(text=label.upper(), font_size=sp(10), color=TEXT_TERTIARY, halign='center')
        self._val = FlatLabel(text=value, font_size=sp(22), color=self._vc, bold=True, halign='center')
        self.add_widget(self._lbl)
        self.add_widget(self._val)

    def _upd(self, *a):
        self._rect.pos = self.pos
        self._rect.size = self.size

    def set_value(self, v, color=None):
        self._val.text = str(v)
        if color:
            self._val.color = color


class ProgressBar(Widget):
    """Simple horizontal progress bar."""
    progress = NumericProperty(0)
    bar_color = ColorProperty(ACCENT_TEAL)

    def __init__(self, **kwargs):
        super().__init__(size_hint_y=None, height=dp(8), **kwargs)
        with self.canvas:
            Color(0.2, 0.2, 0.27, 1)
            self._bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(4)])
            self._fc = Color(*self.bar_color)
            self._fill = RoundedRectangle(pos=self.pos, size=(0, self.height), radius=[dp(4)])
        self.bind(pos=self._upd, size=self._upd, progress=self._upd, bar_color=self._color_upd)

    def _color_upd(self, *a):
        self._fc.rgba = self.bar_color

    def _upd(self, *a):
        self._bg.pos = self.pos
        self._bg.size = self.size
        w = self.width * max(0, min(1, self.progress / 100))
        self._fill.pos = self.pos
        self._fill.size = (w, self.height)


class TabBar(BoxLayout):
    """Custom bottom tab bar."""
    def __init__(self, tabs, on_tab=None, **kwargs):
        super().__init__(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(52),
            **kwargs
        )
        self._on_tab = on_tab
        self._btns = []
        with self.canvas.before:
            Color(0.09, 0.09, 0.13, 1)
            self._bg = Rectangle(pos=self.pos, size=self.size)
            Color(0.22, 0.22, 0.30, 1)
            self._top = Line(points=[], width=1)
        self.bind(pos=self._upd, size=self._upd)

        for i, label in enumerate(tabs):
            btn = Button(
                text=label,
                font_size=sp(10),
                bold=True,
                background_color=(0, 0, 0, 0),
                color=TEXT_TERTIARY,
            )
            btn._tab_index = i
            btn.bind(on_press=self._tab_pressed)
            self._btns.append(btn)
            self.add_widget(btn)
        self._select(0)

    def _upd(self, *a):
        self._bg.pos = self.pos
        self._bg.size = self.size
        self._top.points = [self.x, self.top, self.right, self.top]

    def _tab_pressed(self, btn):
        self._select(btn._tab_index)
        if self._on_tab:
            self._on_tab(btn._tab_index)

    def _select(self, idx):
        for i, btn in enumerate(self._btns):
            if i == idx:
                btn.color = ACCENT_AMBER
            else:
                btn.color = TEXT_TERTIARY


class DividerLine(Widget):
    def __init__(self, **kwargs):
        super().__init__(size_hint_y=None, height=dp(1), **kwargs)
        with self.canvas:
            Color(0.22, 0.22, 0.30, 1)
            self._line = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=lambda *a: setattr(self._line, 'pos', self.pos),
                  size=lambda *a: setattr(self._line, 'size', self.size))


class StyledInput(BoxLayout):
    """Labelled text input row."""
    def __init__(self, label='', hint='', input_filter=None, **kwargs):
        from kivy.uix.textinput import TextInput
        super().__init__(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(48),
            spacing=dp(10),
            **kwargs
        )
        lbl = Label(text=label, font_size=sp(13), color=TEXT_SECONDARY,
                    size_hint_x=None, width=dp(100), halign='right', valign='middle')
        lbl.bind(size=lambda *a: setattr(lbl, 'text_size', lbl.size))
        self.text_input = TextInput(
            hint_text=hint,
            font_size=sp(15),
            foreground_color=TEXT_PRIMARY,
            hint_text_color=TEXT_TERTIARY,
            background_color=BG_INPUT,
            cursor_color=ACCENT_AMBER,
            input_filter=input_filter,
            multiline=False,
        )
        self.add_widget(lbl)
        self.add_widget(self.text_input)
