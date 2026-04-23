"""
Bankroll tab - bet sizing calculator and session tracker.
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp, sp

from utils.theme import *
from utils.widgets import FlatLabel, AccentButton, StatBox, Card


RISK_OPTIONS = ['Very Low (1%)', 'Low (2%)', 'Medium (5%)', 'High (10%)']
RISK_VALUES  = {'Very Low (1%)': 0.01, 'Low (2%)': 0.02,
                'Medium (5%)': 0.05, 'High (10%)': 0.10}


class InputRow(BoxLayout):
    def __init__(self, label, hint='', input_filter='float', value='', **kwargs):
        super().__init__(orientation='horizontal', size_hint_y=None,
                          height=dp(48), spacing=dp(10), **kwargs)
        lbl = Label(text=label, font_size=sp(13), color=TEXT_SECONDARY,
                    size_hint_x=None, width=dp(110), halign='right', valign='middle')
        lbl.bind(size=lambda *a: setattr(lbl, 'text_size', lbl.size))
        self.text_input = TextInput(
            hint_text=hint, text=value,
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


class BankrollTab(BoxLayout):
    def __init__(self, data_store, **kwargs):
        super().__init__(orientation='vertical', spacing=dp(10), padding=dp(14), **kwargs)
        self.ds = data_store
        self._session_started = False
        self._build()

    def _build(self):
        sv = ScrollView(do_scroll_x=False)
        content = BoxLayout(orientation='vertical', spacing=dp(12),
                             size_hint_y=None, padding=[0, dp(4), 0, dp(20)])
        content.bind(minimum_height=content.setter('height'))

        # Settings section
        t1 = FlatLabel(text='BANKROLL SETTINGS', font_size=sp(10),
                        color=TEXT_TERTIARY, size_hint_y=None, height=dp(18))
        content.add_widget(t1)

        self._balance_row = InputRow('Balance (KSh)', hint='1000', value='1000')
        self._balance_row.text_input.bind(text=self._calc)
        content.add_widget(self._balance_row)

        # Risk spinner
        risk_row = BoxLayout(orientation='horizontal', size_hint_y=None,
                              height=dp(48), spacing=dp(10))
        risk_lbl = Label(text='Risk Level', font_size=sp(13), color=TEXT_SECONDARY,
                         size_hint_x=None, width=dp(110), halign='right', valign='middle')
        risk_lbl.bind(size=lambda *a: setattr(risk_lbl, 'text_size', risk_lbl.size))
        self._risk_spinner = Spinner(
            text='Low (2%)',
            values=RISK_OPTIONS,
            font_size=sp(13),
            background_color=BG_INPUT,
            color=TEXT_PRIMARY,
        )
        self._risk_spinner.bind(text=self._calc)
        risk_row.add_widget(risk_lbl)
        risk_row.add_widget(self._risk_spinner)
        content.add_widget(risk_row)

        self._target_row = InputRow('Target cashout', hint='2.0', value='2.0')
        self._target_row.text_input.bind(text=self._calc)
        content.add_widget(self._target_row)

        # Result card
        t2 = FlatLabel(text='RECOMMENDATION', font_size=sp(10),
                        color=TEXT_TERTIARY, size_hint_y=None, height=dp(18))
        content.add_widget(t2)

        self._result_card = Card(size_hint_y=None, height=dp(140))
        self._result_card.padding = [dp(14), dp(12)]
        self._result_card.spacing = dp(8)
        self._result_lbl = Label(
            font_size=sp(14), color=TEXT_SECONDARY,
            halign='left', valign='top', markup=True,
            text_size=(None, None), line_height=1.6
        )
        self._result_lbl.bind(
            size=lambda *a: setattr(self._result_lbl, 'text_size', (self._result_lbl.width, None))
        )
        self._result_card.add_widget(self._result_lbl)
        content.add_widget(self._result_card)

        # Session tracker
        t3 = FlatLabel(text='SESSION TRACKER', font_size=sp(10),
                        color=TEXT_TERTIARY, size_hint_y=None, height=dp(18))
        content.add_widget(t3)

        sess_grid = GridLayout(cols=2, spacing=dp(8), size_hint_y=None, height=dp(80))
        self._sb_start = StatBox('Starting', '—', ACCENT_BLUE)
        self._sb_cur   = StatBox('Current',  '—', ACCENT_TEAL)
        self._sb_pnl   = StatBox('P&L',      '—', ACCENT_AMBER)
        self._sb_rounds = StatBox('Rounds', '0', TEXT_SECONDARY)
        for sb in [self._sb_start, self._sb_cur, self._sb_pnl, self._sb_rounds]:
            sess_grid.add_widget(sb)
        content.add_widget(sess_grid)

        t4 = FlatLabel(text='LOG ROUND RESULT', font_size=sp(10),
                        color=TEXT_TERTIARY, size_hint_y=None, height=dp(18))
        content.add_widget(t4)

        log_row = BoxLayout(orientation='horizontal', size_hint_y=None,
                             height=dp(48), spacing=dp(10))
        self._log_input = TextInput(
            hint_text='Profit or loss (e.g. -50 or 120)',
            font_size=sp(14),
            foreground_color=TEXT_PRIMARY,
            hint_text_color=TEXT_TERTIARY,
            background_color=BG_INPUT,
            cursor_color=ACCENT_AMBER,
            input_filter='float',
            multiline=False,
            size_hint_x=0.65,
        )
        log_btn = Button(
            text='LOG',
            font_size=sp(13), bold=True,
            background_color=(0, 0, 0, 0),
            color=TEXT_DARK,
            size_hint_x=0.35,
            size_hint_y=None, height=dp(48)
        )
        with log_btn.canvas.before:
            Color(*ACCENT_AMBER)
            self._log_rect = RoundedRectangle(pos=log_btn.pos, size=log_btn.size, radius=[dp(10)])
        log_btn.bind(
            pos=lambda *a: setattr(self._log_rect, 'pos', log_btn.pos),
            size=lambda *a: setattr(self._log_rect, 'size', log_btn.size),
        )
        log_btn.bind(on_press=self._log_round)
        log_row.add_widget(self._log_input)
        log_row.add_widget(log_btn)
        content.add_widget(log_row)

        reset_btn = Button(
            text='Reset Session',
            font_size=sp(12),
            background_color=(0, 0, 0, 0),
            color=TEXT_TERTIARY,
            size_hint_y=None, height=dp(36)
        )
        reset_btn.bind(on_press=self._reset_session)
        content.add_widget(reset_btn)
        content.add_widget(Widget(size_hint_y=None, height=dp(20)))

        sv.add_widget(content)
        self.add_widget(sv)
        self._session_rounds = 0
        self._calc()

    def _calc(self, *a):
        try:
            bal = float(self._balance_row.text_input.text or '0')
        except ValueError:
            bal = 0
        risk = RISK_VALUES.get(self._risk_spinner.text, 0.02)
        try:
            target = float(self._target_row.text_input.text or '2.0')
            if target <= 1.0:
                target = 2.0
        except ValueError:
            target = 2.0

        bet = round(bal * risk)
        profit = round(bet * (target - 1))
        win_rate_needed = round((1 / target) * 100)

        self._result_lbl.text = (
            f'[color=#ccccdd]Recommended bet: [b][color=#F5C400]KSh {bet:,}[/color][/b]\n'
            f'Win at {target:.1f}x: [b][color=#1D9E75]+KSh {profit:,}[/color][/b]\n'
            f'Loss per round: [b][color=#E24B4A]-KSh {bet:,}[/color][/b]\n'
            f'Win rate to break even: [b]{win_rate_needed}%[/b][/color]'
        )

        if not self._session_started:
            self._sb_start.set_value(f'KSh {int(bal):,}')
            self._sb_cur.set_value(f'KSh {int(bal):,}')
            self._session_bal = bal

    def _log_round(self, *a):
        txt = self._log_input.text.strip()
        try:
            delta = float(txt)
        except ValueError:
            return

        if not self._session_started:
            try:
                start = float(self._balance_row.text_input.text or '1000')
            except ValueError:
                start = 1000
            self._session_bal = start
            self._sb_start.set_value(f'KSh {int(start):,}')
            self._session_started = True
            self._session_rounds = 0

        self._session_bal += delta
        self._session_rounds += 1
        self._log_input.text = ''

        self._sb_cur.set_value(f'KSh {int(self._session_bal):,}')

        try:
            start_val = float(self._balance_row.text_input.text or '1000')
        except ValueError:
            start_val = 1000
        pnl = self._session_bal - start_val
        sign = '+' if pnl >= 0 else ''
        pnl_color = ACCENT_TEAL if pnl >= 0 else ACCENT_RED
        self._sb_pnl.set_value(f'{sign}KSh {int(pnl):,}', pnl_color)
        self._sb_rounds.set_value(str(self._session_rounds))

    def _reset_session(self, *a):
        self._session_started = False
        self._session_rounds = 0
        self._sb_start.set_value('—')
        self._sb_cur.set_value('—')
        self._sb_pnl.set_value('—')
        self._sb_rounds.set_value('0')

    def on_tab_shown(self):
        pass
