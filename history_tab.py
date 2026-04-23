"""
History tab - log and view crash points.
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.metrics import dp, sp

from utils.theme import *
from utils.widgets import FlatLabel, AccentButton, GhostButton, DividerLine


class HistoryRow(BoxLayout):
    def __init__(self, index, round_num, value, on_delete=None, **kwargs):
        super().__init__(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(44),
            padding=[dp(12), 0],
            **kwargs
        )
        self._on_delete = on_delete
        self._index = index

        round_lbl = Label(
            text=f'Round {round_num}', font_size=sp(12),
            color=TEXT_TERTIARY, halign='left', valign='middle',
            size_hint_x=0.35
        )
        round_lbl.bind(size=lambda *a: setattr(round_lbl, 'text_size', round_lbl.size))

        val_lbl = Label(
            text=f'{value:.2f}x', font_size=sp(16), bold=True,
            color=mult_color(value), halign='center', valign='middle',
            size_hint_x=0.45
        )
        val_lbl.bind(size=lambda *a: setattr(val_lbl, 'text_size', val_lbl.size))

        del_btn = Button(
            text='✕', font_size=sp(14), color=TEXT_TERTIARY,
            background_color=(0, 0, 0, 0),
            size_hint_x=0.20, size_hint_y=None, height=dp(44)
        )
        del_btn.bind(on_press=lambda *a: on_delete(index) if on_delete else None)

        self.add_widget(round_lbl)
        self.add_widget(val_lbl)
        self.add_widget(del_btn)

        with self.canvas.before:
            Color(0.18, 0.18, 0.24, 1)
            self._sep = Rectangle(pos=(self.x, self.y), size=(self.width, 1))
        self.bind(pos=lambda *a: setattr(self._sep, 'pos', (self.x, self.y)),
                  size=lambda *a: setattr(self._sep, 'size', (self.width, 1)))


class HistoryTab(BoxLayout):
    def __init__(self, data_store, **kwargs):
        super().__init__(orientation='vertical', spacing=dp(10), padding=dp(14), **kwargs)
        self.ds = data_store
        self._build()

    def _build(self):
        # Add result row
        add_title = FlatLabel(text='ADD CRASH POINT', font_size=sp(10),
                               color=TEXT_TERTIARY, size_hint_y=None, height=dp(18))
        self.add_widget(add_title)

        add_row = BoxLayout(orientation='horizontal', size_hint_y=None,
                             height=dp(48), spacing=dp(10))
        self._input = TextInput(
            hint_text='e.g. 2.34',
            font_size=sp(16),
            foreground_color=TEXT_PRIMARY,
            hint_text_color=TEXT_TERTIARY,
            background_color=BG_INPUT,
            cursor_color=ACCENT_AMBER,
            input_filter='float',
            multiline=False,
            size_hint_x=0.65,
        )
        add_btn = Button(
            text='+ ADD',
            font_size=sp(13), bold=True,
            background_color=(0, 0, 0, 0),
            color=TEXT_DARK,
            size_hint_x=0.35,
            size_hint_y=None, height=dp(48)
        )
        with add_btn.canvas.before:
            Color(*ACCENT_TEAL)
            self._add_rect = RoundedRectangle(pos=add_btn.pos, size=add_btn.size, radius=[dp(10)])
        add_btn.bind(
            pos=lambda *a: setattr(self._add_rect, 'pos', add_btn.pos),
            size=lambda *a: setattr(self._add_rect, 'size', add_btn.size),
        )
        add_btn.bind(on_press=self._add_result)
        add_row.add_widget(self._input)
        add_row.add_widget(add_btn)
        self.add_widget(add_row)

        self._count_lbl = FlatLabel(
            text=f'HISTORY — 0 ROUNDS', font_size=sp(10),
            color=TEXT_TERTIARY, size_hint_y=None, height=dp(18)
        )
        self.add_widget(self._count_lbl)

        sv = ScrollView(do_scroll_x=False)
        self._list = BoxLayout(orientation='vertical', size_hint_y=None, spacing=0)
        self._list.bind(minimum_height=self._list.setter('height'))
        sv.add_widget(self._list)
        self.add_widget(sv)

        self._render_history()

    def _add_result(self, *a):
        txt = self._input.text.strip()
        try:
            val = float(txt)
            if val < 1.0:
                raise ValueError
        except ValueError:
            self._input.background_color = (0.4, 0.1, 0.1, 1)
            return
        self._input.background_color = BG_INPUT
        self.ds.add_result(val)
        self._input.text = ''
        self._render_history()

    def _delete_result(self, index):
        self.ds.delete_result(index)
        self._render_history()

    def _render_history(self):
        self._list.clear_widgets()
        n = len(self.ds.history)
        self._count_lbl.text = f'HISTORY — {n} ROUNDS'

        if not self.ds.history:
            empty = Label(
                text='No rounds logged yet.\nAdd your first crash point above.',
                font_size=sp(13), color=TEXT_TERTIARY,
                halign='center', valign='middle',
                size_hint_y=None, height=dp(80)
            )
            empty.bind(size=lambda *a: setattr(empty, 'text_size', empty.size))
            self._list.add_widget(empty)
            return

        for i, val in enumerate(self.ds.history[:60]):
            row = HistoryRow(
                index=i,
                round_num=n - i,
                value=val,
                on_delete=self._delete_result
            )
            self._list.add_widget(row)

    def on_tab_shown(self):
        self._render_history()
