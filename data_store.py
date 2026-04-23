"""
DataStore - handles saving/loading round history and session data.
"""

import json
import os
from kivy.app import App


class DataStore:
    def __init__(self):
        self.history = []
        self.session = {'start': None, 'current': None}
        self._load()

    def _get_path(self):
        try:
            app = App.get_running_app()
            data_dir = app.user_data_dir
        except Exception:
            data_dir = os.path.expanduser('~')
        return os.path.join(data_dir, 'aviator_data.json')

    def _load(self):
        path = self._get_path()
        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    data = json.load(f)
                    self.history = data.get('history', [])
                    self.session = data.get('session', {'start': None, 'current': None})
            except Exception:
                self.history = []
        if not self.history:
            # Demo seed data
            self.history = [
                1.23, 4.56, 1.02, 2.34, 1.78, 8.90, 1.45, 3.21,
                1.67, 2.89, 1.11, 5.67, 1.34, 2.01, 1.89, 12.5,
                1.56, 2.78, 1.22, 3.44
            ]

    def save(self):
        path = self._get_path()
        try:
            with open(path, 'w') as f:
                json.dump({'history': self.history, 'session': self.session}, f)
        except Exception:
            pass

    def add_result(self, value):
        self.history.insert(0, round(value, 2))
        self.save()

    def delete_result(self, index):
        if 0 <= index < len(self.history):
            self.history.pop(index)
            self.save()

    def get_stats(self):
        if not self.history:
            return {}
        h = self.history
        sorted_h = sorted(h)
        n = len(sorted_h)
        avg = sum(h) / n
        median = sorted_h[n // 2]
        max_val = max(h)
        below_2x = round(len([v for v in h if v < 2.0]) / n * 100)
        return {
            'avg': avg, 'median': median,
            'max': max_val, 'below_2x': below_2x,
            'count': n
        }

    def get_distribution(self):
        bins = [
            ('1–1.5x', 1.0, 1.5),
            ('1.5–2x', 1.5, 2.0),
            ('2–3x',   2.0, 3.0),
            ('3–5x',   3.0, 5.0),
            ('5–10x',  5.0, 10.0),
            ('10x+',   10.0, float('inf')),
        ]
        result = []
        for label, lo, hi in bins:
            count = len([v for v in self.history if lo <= v < hi])
            result.append((label, count))
        return result

    def get_strategy_targets(self):
        h = sorted(self.history)
        n = len(h)
        if n == 0:
            return {'safe': 1.5, 'balanced': 2.0, 'aggressive': 3.5, 'moonshot': 10.0}
        def percentile(p):
            idx = min(int(n * p), n - 1)
            return h[idx]
        return {
            'safe':       round(percentile(0.25), 2),
            'balanced':   round(percentile(0.50), 2),
            'aggressive': round(percentile(0.75), 2),
            'moonshot':   round(percentile(0.90), 2),
        }

    def get_confidence(self):
        n = len(self.history)
        import random
        if n < 5:
            return int(35 + random.random() * 10)
        if n < 20:
            return int(45 + (n / 20) * 20 + random.random() * 8)
        return int(min(82, 62 + n / 10 + random.random() * 5))
