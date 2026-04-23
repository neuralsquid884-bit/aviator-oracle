"""
MainScreen - root screen containing header, tab bar, and all tab panels.
"""

from kivy.uix.screen import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.metrics import dp, sp

from utils.theme import *
from utils.widgets import TabBar, FlatLabel
from screens.predict_tab  import PredictTab
from screens.history_tab  import HistoryTab
from screens.stats_tab    import StatsTab
from screens.bankroll_tab import BankrollTab


class Header(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', size_hint_y=None, height=dp(80),
                          padding=[dp(14), dp(10)], spacing=dp(2), **kwargs)
        with self.canvas.before:
            Color(0.09, 0.09, 0.13, 1)
            self._bg = Rectangle(pos=self.pos, size=self.size)
            Color(0.22, 0.22, 0.30, 1)
            self._border = Rectangle(pos=(self.x, self.y), size=(self.width, 1))
        self.bind(pos=self._upd, size=self._upd)

        title_row = BoxLayout(orientation='horizontal')
        plane = Label(text='✈', font_size=sp(22), size_hint_x=None, width=dp(36),
                      color=ACCENT_AMBER, halign='center', valign='middle')
        name_col = BoxLayout(orientation='vertical', spacing=dp(1))
        title = Label(text='AVIATOR ORACLE', font_size=sp(16), bold=True,
                       color=TEXT_PRIMARY, halign='left', valign='middle')
        title.bind(size=lambda *a: setattr(title, 'text_size', title.size))
        sub = Label(text='Statistical Prediction Engine', font_size=sp(10),
                     color=TEXT_TERTIARY, halign='left', valign='middle')
        sub.bind(size=lambda *a: setattr(sub, 'text_size', sub.size))
        name_col.add_widget(title)
        name_col.add_widget(sub)
        title_row.add_widget(plane)
        title_row.add_widget(name_col)
        self.add_widget(title_row)

        disclaimer = Label(
            text='⚠  For entertainment only. Aviator uses provably fair RNG.',
            font_size=sp(9), color=(0.80, 0.60, 0.10, 1),
            halign='center', valign='middle', size_hint_y=None, height=dp(16)
        )
        disclaimer.bind(size=lambda *a: setattr(disclaimer, 'text_size', disclaimer.size))
        self.add_widget(disclaimer)

    def _upd(self, *a):
        self._bg.pos = self.pos
        self._bg.size = self.size
        self._border.pos = (self.x, self.y)
        self._border.size = (self.width, 1)


class MainScreen(Screen):
    def __init__(self, data_store, **kwargs):
        super().__init__(**kwargs)
        self.ds = data_store

        root = BoxLayout(orientation='vertical')

        with root.canvas.before:
            Color(*BG_DARK)
            self._bg = Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=lambda *a: setattr(self._bg, 'pos', root.pos),
                  size=lambda *a: setattr(self._bg, 'size', root.size))

        self.header = Header()
        root.add_widget(self.header)

        # Tab content area
        self._tabs = [
            PredictTab(data_store=self.ds),
            HistoryTab(data_store=self.ds),
            StatsTab(data_store=self.ds),
            BankrollTab(data_store=self.ds),
        ]
        self._current_tab = 0

        self._tab_container = BoxLayout(orientation='vertical')
        for i, tab in enumerate(self._tabs):
            if i != 0:
                tab.opacity = 0
                tab.disabled = True
                tab.size_hint_y = 0
            self._tab_container.add_widget(tab)

        root.add_widget(self._tab_container)

        tab_bar = TabBar(
            tabs=['PREDICT', 'HISTORY', 'STATS', 'BANKROLL'],
            on_tab=self._switch_tab
        )
        root.add_widget(tab_bar)

        self.add_widget(root)
        self._tabs[0].on_tab_shown()

    def _switch_tab(self, idx):
        if idx == self._current_tab:
            return
        old = self._tabs[self._current_tab]
        new = self._tabs[idx]

        old.opacity = 0
        old.disabled = True
        old.size_hint_y = 0

        new.opacity = 1
        new.disabled = False
        new.size_hint_y = 1

        self._current_tab = idx
        new.on_tab_shown()
