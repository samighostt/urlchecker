import threading
import requests
from kivy.app import App
from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView

PATHS = ["admi", "login", ".env", "config"]

class Card(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.padding = dp(16)
        self.spacing = dp(10)
        with self.canvas.before:
            Color(0.08, 0.09, 0.12, 1)
            self.bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(18)])
            Color(0.18, 0.20, 0.25, 1)
            self.border = Line(rounded_rectangle=(self.x, self.y, self.width, self.height, dp(18)), width=1)
        self.bind(pos=self.update_canvas, size=self.update_canvas)

    def update_canvas(self, *_):
        self.bg.pos, self.bg.size = self.pos, self.size
        self.border.rounded_rectangle = (self.x, self.y, self.width, self.height, dp(18))

class LuxuryButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ""
        self.background_down = ""
        self.background_color = (0, 0, 0, 0)
        self.color = (0.96, 0.97, 1, 1)
        self.bold = True
        with self.canvas.before:
            Color(0.18, 0.35, 0.75, 1)
            self.bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(14)])
        self.bind(pos=self.update_canvas, size=self.update_canvas)

    def update_canvas(self, *_):
        self.bg.pos, self.bg.size = self.pos, self.size

class URLCheckerApp(App):
    def build(self):
        self.title = "URL Checker"
        self.scanning = False

        root = BoxLayout(orientation="vertical",
                         padding=[dp(18), dp(18), dp(18), dp(12)],
                         spacing=dp(12))
        with root.canvas.before:
            Color(0.025, 0.03, 0.045, 1)
            self.bg = RoundedRectangle(pos=root.pos, size=root.size)
        root.bind(pos=self.update_root, size=self.update_root)

        header = BoxLayout(orientation="vertical", size_hint_y=None, height=dp(72))
        header.add_widget(Label(text="[b]URL CHECKER[/b]", markup=True, font_size=dp(27),
                                color=(0.90,0.94,1,1), halign="left"))
        header.add_widget(Label(text="Professional HTTP status checker", font_size=dp(13),
                                color=(0.55,0.62,0.72,1), halign="left"))
        root.add_widget(header)

        card = Card(orientation="vertical", size_hint_y=None, height=dp(116))
        card.add_widget(Label(text="TARGET URL", size_hint_y=None, height=dp(24),
                              font_size=dp(12), color=(0.48,0.68,1,1), halign="left"))
        self.url_input = TextInput(hint_text="https://example.com", multiline=False,
                                   font_size=dp(16), foreground_color=(0.93,0.95,1,1),
                                   hint_text_color=(0.38,0.42,0.50,1),
                                   background_color=(0.12,0.13,0.17,1),
                                   padding=[dp(14),dp(12)])
        card.add_widget(self.url_input)
        root.add_widget(card)

        self.scan_btn = LuxuryButton(text="START SCAN", size_hint_y=None,
                                     height=dp(52), font_size=dp(16))
        self.scan_btn.bind(on_release=self.start_scan)
        root.add_widget(self.scan_btn)

        self.status = Label(text="Ready — use only on systems you own or are authorized to test.",
                            size_hint_y=None, height=dp(30), font_size=dp(11),
                            color=(0.50,0.56,0.66,1), halign="left")
        root.add_widget(self.status)

        results_card = Card(orientation="vertical")
        results_card.add_widget(Label(text="[b]SCAN RESULTS[/b]", markup=True,
                                      size_hint_y=None, height=dp(30), font_size=dp(13),
                                      color=(0.80,0.86,0.95,1), halign="left"))
        scroll = ScrollView(do_scroll_x=False)
        self.results = Label(text="No results yet.", markup=True, size_hint_y=None,
                             font_size=dp(13), color=(0.82,0.85,0.90,1),
                             halign="left", valign="top", padding=[dp(6),dp(8)])
        self.results.bind(texture_size=lambda obj, size: setattr(obj, "height", max(dp(100), size[1])))
        scroll.add_widget(self.results)
        results_card.add_widget(scroll)
        root.add_widget(results_card)

        root.add_widget(Label(text="HTTP • Requests • Android", size_hint_y=None,
                              height=dp(22), font_size=dp(10),
                              color=(0.32,0.37,0.45,1)))
        return root

    def update_root(self, instance, *_):
        self.bg.pos, self.bg.size = instance.pos, instance.size

    def add_result(self, text):
        def update(_):
            self.results.text = text if not self.results.text or self.results.text == "No results yet." else self.results.text + "\n" + text
        Clock.schedule_once(update)

    def start_scan(self, *_):
        if self.scanning:
            return
        url = self.url_input.text.strip()
        if not url:
            self.status.text = "Enter a URL first."
            return
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        self.scanning = True
        self.scan_btn.text = "SCANNING..."
        self.status.text = "Checking authorized target..."
        self.results.text = ""
        threading.Thread(target=self.scan_worker, args=(url,), daemon=True).start()

    def scan_worker(self, base_url):
        headers = {"User-Agent": "Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 Chrome/151.0.0.0 Mobile Safari/537.36"}
        for path in PATHS:
            target = f"{base_url.rstrip('/')}/{path}"
            try:
                r = requests.get(target, headers=headers, timeout=10, allow_redirects=False)
                code = r.status_code
                if code == 200:
                    tag = "[color=7CFF9B][b]200 OK[/b][/color]"
                elif code in (301,302,307,308):
                    tag = f"[color=FFD166][b]{code} REDIRECT[/b][/color]"
                elif code == 403:
                    tag = "[color=FFB86B][b]403 FORBIDDEN[/b][/color]"
                elif code == 404:
                    tag = "[color=8A93A6][b]404 NOT FOUND[/b][/color]"
                elif code >= 500:
                    tag = f"[color=FF6B7A][b]{code} SERVER ERROR[/b][/color]"
                else:
                    tag = f"[b]{code}[/b]"
                self.add_result(f"{tag}  {target}")
            except requests.RequestException as e:
                self.add_result(f"[color=FF6B7A]ERROR[/color]  {target}  [color=8A93A6]{type(e).__name__}[/color]")
        Clock.schedule_once(self.finish)

    def finish(self, _):
        self.scanning = False
        self.scan_btn.text = "START SCAN"
        self.status.text = "Scan finished."

if __name__ == "__main__":
    URLCheckerApp().run()
