"""
Aviator Oracle - Statistical Prediction Engine
A Kivy mobile app for tracking and analyzing Aviator crash points.
"""

import os
os.environ['KIVY_NO_ENV_CONFIG'] = '1'

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, SlideTransition
from kivy.core.window import Window
from kivy.utils import platform

# Set mobile-friendly window size on desktop
if platform not in ('android', 'ios'):
    Window.size = (400, 750)
    Window.clearcolor = (0.07, 0.07, 0.10, 1)

from screens.main_screen import MainScreen
from utils.data_store import DataStore


class AviatorOracleApp(App):
    title = 'Aviator Oracle'

    def build(self):
        self.data_store = DataStore()
        self.sm = ScreenManager(transition=SlideTransition())
        self.sm.add_widget(MainScreen(name='main', data_store=self.data_store))
        return self.sm

    def on_stop(self):
        self.data_store.save()


if __name__ == '__main__':
    AviatorOracleApp().run()
