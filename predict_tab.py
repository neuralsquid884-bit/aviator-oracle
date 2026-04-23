"""
Predict tab - strategy selector + animated prediction display.
"""

import random
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.metrics import dp, sp

from utils.theme import *
from utils.widgets import Card, FlatLabel, AccentButton, ProgressBar, StatBox


STRATEGIES = [
    ('safe',       'SAFE',       '🛡'),
    ('balanced',   'BALANCED',   '⚖'),
    ('aggressive', 'AGGRESSIVE', '🔥'),
    ('moonshot',   'MOON',       '🚀'),
]


class StrategyCard(Button):
    def __init__(self, key, label, icon, **kwargs):
        super().__init__(
            background_color=(0, 0, 0, 0),
            size_hint_y=None,
            height=dp(72),
            **kwargs
        )
        self.key = key
        self.selected = False
        with self.canvas.before:
            self._bg_color = Color(*BG_CARD)
            self._bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(12)])
            self._border_color = Color(0.25, 0.25, 0.32, 1)
            self._border = Line(rounded_rectangle=(self.x, self.y, self.width, self.height, dp(12)), width=1)
        self.bind(pos=self._upd, size=self._upd)

        inner = BoxLayout(orientation='vertical', spacing=dp(2), padding=dp(8))
        self.icon_lbl = Label(text=icon, font_size=sp(20), size_hint_y=None, height=dp(26))
        self.name_lbl = Label(text=label, font_size=sp(10), bold=True,
                              color=TEXT_SECONDARY, size_hint_y=None, height=dp(14))
        self.val_lbl = Label(text='—', font_size=sp(16), bold=True,
                             color=ACCENT_AMBER, size_hint_y=None, height=dp(22))
        inner.add_widget(self.icon_lbl)
        inner.add_widget(self.name_lbl)
        inner.add_widget(self.val_lbl)
        self.add_widget(inner)

    def _upd(self, *a):
        self._bg.pos = self.pos
        self._bg.size = self.size
        self._border.rounded_rectangle = (self.x, self.y, self.width, self.height, dp(12))

    def set_selected(self, sel):
        self.selected = sel
        if sel:
            self._border_color.rgba = ACCENT_AMBER
            self._border.width = 2
        else:
            self._border_color.rgba = (0.25, 0.25, 0.32, 1)
            self._border.width = 1

    def set_value(self, v):
        self.val_lbl.text = f'{v:.2f}x'


class PredictTab(BoxLayout):
    def __init__(self, data_store, **kwargs):
        super().__init__(orientation='vertical', spacing=dp(10), padding=dp(14), **kwargs)
        self.ds = data_store
        self.current_strat = 'safe'
        self._anim_event = None
        self._strat_cards = {}
        self._build()

    def _build(self):
        sv = ScrollView(do_scroll_x=False)
        content = BoxLayout(orientation='vertical', spacing=dp(12),
                            size_hint_y=None, padding=[0, dp(4), 0, dp(10)])
        content.bind(minimum_height=content.setter('height'))

        # --- Main prediction display card ---
        pred_card = Card(size_hint_y=None, height=dp(170))
        pred_card.padding = [dp(14), dp(16)]

        top_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(20))
        top_row.add_widget(Label(text='SUGGESTED CASHOUT', font_size=sp(10),
                                  color=TEXT_TERTIARY, halign='left', valign='middle',
                                  size_hint_x=0.6, text_size=(None, None)))
        self._signal_lbl = Label(text='● READY', font_size=sp(10),
                                  color=ACCENT_TEAL, halign='right', valign='middle',
                                  size_hint_x=0.4)
        top_row.add_widget(self._signal_lbl)
        pred_card.add_widget(top_row)

        self._pred_value = Label(
            text='—', font_size=sp(52), bold=True, color=ACCENT_AMBER,
            size_hint_y=None, height=dp(70), halign='center', valign='middle'
        )
        self._pred_value.bind(size=lambda *a: setattr(self._pred_value, 'text_size', self._pred_value.size))
        pred_card.add_widget(self._pred_value)

        conf_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(16))
        conf_row.add_widget(Label(text='CONFIDENCE', font_size=sp(9), color=TEXT_TERTIARY,
                                   halign='left', valign='middle'))
        self._conf_pct_lbl = Label(text='—', font_size=sp(9), color=TEXT_SECONDARY,
                                    halign='right', valign='middle')
        conf_row.add_widget(self._conf_pct_lbl)
        pred_card.add_widget(conf_row)

        self._conf_bar = ProgressBar(progress=0)
        pred_card.add_widget(self._conf_bar)
        content.add_widget(pred_card)

        # --- Strategy grid ---
        strat_title = FlatLabel(text='STRATEGY MODE', font_size=sp(10),
                                 color=TEXT_TERTIARY, halign='left',
                                 size_hint_y=None, height=dp(18))
        content.add_widget(strat_title)

        grid = GridLayout(cols=4, spacing=dp(8), size_hint_y=None, height=dp(80))
        for key, label, icon in STRATEGIES:
            card = StrategyCard(key, label, icon)
            card.bind(on_press=lambda btn, k=key: self._select_strat(k))
            self._strat_cards[key] = card
            grid.add_widget(card)
        content.add_widget(grid)
        self._strat_cards['safe'].set_selected(True)

        # --- Predict button ---
        self._predict_btn = AccentButton(text='▶  GENERATE PREDICTION',
                                          size_hint_y=None, height=dp(54))
        self._predict_btn.bind(on_press=self._run_prediction)
        content.add_widget(self._predict_btn)

        # --- Insight card ---
        insight_title = FlatLabel(text='ANALYSIS INSIGHT', font_size=sp(10),
                                   color=TEXT_TERTIARY, halign='left',
                                   size_hint_y=None, height=dp(18))
        content.add_widget(insight_title)

        self._insight_card = Card(size_hint_y=None)
        self._insight_lbl = Label(
            font_size=sp(13), color=TEXT_SECONDARY, halign='left', valign='top',
            text_size=(None, None), markup=True
        )
        self._insight_lbl.bind(
            size=lambda *a: setattr(self._insight_lbl, 'text_size', (self._insight_lbl.width, None)),
            texture_size=lambda *a: setattr(self._insight_lbl, 'height', self._insight_lbl.texture_size[1] + dp(8))
        )
        self._insight_lbl.bind(
            height=lambda *a: setattr(self._insight_card, 'height', self._insight_lbl.height + dp(28))
        )
        self._insight_lbl.text = (
            '[color=#9999aa]Add at least 10 rounds in History for smarter predictions. '
            'Demo data active.[/color]'
        )
        self._insight_card.add_widget(self._insight_lbl)
        content.add_widget(self._insight_card)

        sv.add_widget(content)
        self.add_widget(sv)
        self._update_strat_values()

    def _select_strat(self, key):
        for k, card in self._strat_cards.items():
            card.set_selected(k == key)
        self.current_strat = key

    def _update_strat_values(self):
        targets = self.ds.get_strategy_targets()
        for key, card in self._strat_cards.items():
            card.set_value(targets.get(key, 2.0))

    def _run_prediction(self, *a):
        if self._anim_event:
            return
        self._predict_btn.disabled = True
        self._signal_lbl.text = '● CALCULATING'
        self._signal_lbl.color = ACCENT_AMBER
        self._anim_steps = 0
        self._anim_event = Clock.schedule_interval(self._anim_tick, 0.06)

    def _anim_tick(self, dt):
        self._anim_steps += 1
        fake = 1.0 + random.random() * 15
        self._pred_value.text = f'{fake:.2f}x'
        if self._anim_steps >= 20:
            Clock.unschedule(self._anim_event)
            self._anim_event = None
            self._finish_prediction()

    def _finish_prediction(self):
        targets = self.ds.get_strategy_targets()
        target = targets.get(self.current_strat, 2.0)
        jitter = (random.random() - 0.5) * 0.3
        target = max(1.1, target + jitter)
        conf = self.ds.get_confidence()

        self._pred_value.text = f'{target:.2f}x'
        self._pred_value.color = mult_color(target)
        self._conf_pct_lbl.text = f'{conf}%'
        self._conf_bar.progress = conf

        if conf > 60:
            self._conf_bar.bar_color = ACCENT_TEAL
        elif conf > 45:
            self._conf_bar.bar_color = ACCENT_AMBER
        else:
            self._conf_bar.bar_color = ACCENT_RED

        h = self.ds.history
        n = len(h)
        below = len([v for v in h if v < target])
        pct = round((below / n) * 100) if n else 50
        note = 'Add more rounds to improve accuracy.' if conf < 50 else 'Moderate confidence from your data.'
        self._insight_lbl.text = (
            f'[color=#ccccdd]Based on [b]{n}[/b] rounds, [b]{pct}%[/b] of rounds '
            f'crashed below [b]{target:.2f}x[/b]. {note}[/color]'
        )

        self._signal_lbl.text = '● SIGNAL READY'
        self._signal_lbl.color = ACCENT_TEAL
        self._predict_btn.disabled = False

    def on_tab_shown(self):
        self._update_strat_values()
