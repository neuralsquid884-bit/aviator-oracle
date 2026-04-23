"""
Stats tab - statistical analysis and distribution view.
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.graphics import Color, RoundedRectangle, Rectangle, Line, Ellipse
from kivy.metrics import dp, sp

from utils.theme import *
from utils.widgets import FlatLabel, StatBox, Card


class DistBar(BoxLayout):
    """Single distribution bar row."""
    def __init__(self, label, count, max_count, **kwargs):
        super().__init__(orientation='horizontal', size_hint_y=None,
                          height=dp(26), spacing=dp(8), **kwargs)
        lbl = Label(text=label, font_size=sp(11), color=TEXT_SECONDARY,
                    halign='right', valign='middle', size_hint_x=None, width=dp(50))
        lbl.bind(size=lambda *a: setattr(lbl, 'text_size', lbl.size))
        self.add_widget(lbl)

        bar_wrap = BoxLayout(size_hint_x=1, padding=[0, dp(6)])
        bar_widget = Widget(size_hint_y=None, height=dp(14))
        pct = count / max_count if max_count > 0 else 0
        with bar_widget.canvas:
            Color(0.18, 0.18, 0.26, 1)
            bar_widget._bg = RoundedRectangle(pos=bar_widget.pos,
                                               size=bar_widget.size, radius=[dp(4)])
            Color(*ACCENT_BLUE)
            bar_widget._fill = RoundedRectangle(
                pos=bar_widget.pos,
                size=(bar_widget.width * pct, bar_widget.height),
                radius=[dp(4)]
            )

        def _update_bar(*a):
            bar_widget._bg.pos = bar_widget.pos
            bar_widget._bg.size = bar_widget.size
            bar_widget._fill.pos = bar_widget.pos
            bar_widget._fill.size = (bar_widget.width * pct, bar_widget.height)

        bar_widget.bind(pos=_update_bar, size=_update_bar)
        bar_wrap.add_widget(bar_widget)
        self.add_widget(bar_wrap)

        cnt_lbl = Label(text=str(count), font_size=sp(11), color=TEXT_TERTIARY,
                        halign='left', valign='middle', size_hint_x=None, width=dp(26))
        self.add_widget(cnt_lbl)


# Use ACCENT_BLUE as a theme color here
ACCENT_BLUE = (0.22, 0.54, 0.87, 1)


class MiniTrendChart(Widget):
    """Simple polyline sparkline chart."""
    def __init__(self, data, **kwargs):
        super().__init__(size_hint_y=None, height=dp(130), **kwargs)
        self._data = data
        self.bind(pos=self._draw, size=self._draw)

    def _draw(self, *a):
        self.canvas.clear()
        data = self._data[-20:] if len(self._data) > 20 else self._data
        if len(data) < 2:
            return
        w, h = self.width, self.height
        pad = dp(10)
        dw = w - pad * 2
        dh = h - pad * 2
        mn, mx = min(data), max(data)
        rng = mx - mn or 1

        def pt(i, v):
            x = pad + (i / (len(data) - 1)) * dw
            y = pad + ((v - mn) / rng) * dh
            return x + self.x, y + self.y

        points_list = []
        for i, v in enumerate(data):
            px, py = pt(i, v)
            points_list += [px, py]

        with self.canvas:
            # Grid lines
            Color(0.22, 0.22, 0.30, 1)
            for q in [0.25, 0.5, 0.75, 1.0]:
                y = self.y + pad + q * dh
                Line(points=[self.x + pad, y, self.x + w - pad, y], width=0.8)

            # Area fill (approximate — draw filled rectangles)
            for i in range(len(data) - 1):
                px1, py1 = pt(i, data[i])
                px2, py2 = pt(i + 1, data[i + 1])
                Color(0.22, 0.54, 0.87, 0.12)
                # thin fill strip between two points
                mid_x = (px1 + px2) / 2
                mid_y = (py1 + py2) / 2
                Rectangle(pos=(px1, self.y + pad), size=(px2 - px1, min(py1, py2) - self.y - pad))

            # Main line
            Color(0.22, 0.54, 0.87, 1)
            Line(points=points_list, width=1.8)

            # Dots colored by value
            for i, v in enumerate(data):
                px, py = pt(i, v)
                r = dp(4)
                c = mult_color(v)
                Color(*c)
                Ellipse(pos=(px - r, py - r), size=(r * 2, r * 2))


class StatsTab(BoxLayout):
    def __init__(self, data_store, **kwargs):
        super().__init__(orientation='vertical', spacing=dp(10), padding=dp(14), **kwargs)
        self.ds = data_store
        self._content = None
        self._build()

    def _build(self):
        self._sv = ScrollView(do_scroll_x=False)
        self._outer = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(12))
        self._outer.bind(minimum_height=self._outer.setter('height'))
        self._sv.add_widget(self._outer)
        self.add_widget(self._sv)
        self._render()

    def _render(self):
        self._outer.clear_widgets()
        h = self.ds.history
        if len(h) < 5:
            empty = Label(
                text='Add at least 5 rounds to see statistics.',
                font_size=sp(14), color=TEXT_TERTIARY,
                halign='center', valign='middle',
                size_hint_y=None, height=dp(120)
            )
            empty.bind(size=lambda *a: setattr(empty, 'text_size', empty.size))
            self._outer.add_widget(empty)
            return

        stats = self.ds.get_stats()

        # Stat boxes grid
        title1 = FlatLabel(text='SUMMARY', font_size=sp(10), color=TEXT_TERTIARY,
                            size_hint_y=None, height=dp(18))
        self._outer.add_widget(title1)

        grid = GridLayout(cols=2, spacing=dp(8), size_hint_y=None, height=dp(120))
        self._s_avg  = StatBox('Average',     f'{stats["avg"]:.2f}x', ACCENT_AMBER)
        self._s_med  = StatBox('Median',      f'{stats["median"]:.2f}x', ACCENT_TEAL)
        self._s_max  = StatBox('Highest',     f'{stats["max"]:.2f}x', ACCENT_BLUE)
        self._s_low  = StatBox('Below 2x',    f'{stats["below_2x"]}%', ACCENT_RED)
        for sb in [self._s_avg, self._s_med, self._s_max, self._s_low]:
            grid.add_widget(sb)
        self._outer.add_widget(grid)

        # Distribution
        title2 = FlatLabel(text='CRASH DISTRIBUTION', font_size=sp(10), color=TEXT_TERTIARY,
                            size_hint_y=None, height=dp(18))
        self._outer.add_widget(title2)

        dist = self.ds.get_distribution()
        max_count = max(c for _, c in dist) or 1
        dist_card = Card(size_hint_y=None)
        dist_card.padding = [dp(12), dp(10)]
        dist_card.spacing = dp(4)
        total_h = dp(10) + dp(10) + len(dist) * (dp(26) + dp(4))
        dist_card.height = total_h

        for label, count in dist:
            dist_card.add_widget(DistBar(label, count, max_count))
        self._outer.add_widget(dist_card)

        # Trend sparkline
        title3 = FlatLabel(text='TREND — LAST 20 ROUNDS', font_size=sp(10),
                            color=TEXT_TERTIARY, size_hint_y=None, height=dp(18))
        self._outer.add_widget(title3)

        trend_card = Card(size_hint_y=None, height=dp(160))
        trend_card.padding = [dp(8), dp(8)]
        chart = MiniTrendChart(list(reversed(self.ds.history[:20])))
        trend_card.add_widget(chart)
        self._outer.add_widget(trend_card)

        self._outer.add_widget(Widget(size_hint_y=None, height=dp(20)))

    def on_tab_shown(self):
        self._render()
