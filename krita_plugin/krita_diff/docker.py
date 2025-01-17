from functools import partial

from krita import DockWidget, QScrollArea, QTabWidget, QTimer, QVBoxLayout, QWidget

from .defaults import REFRESH_INTERVAL, STATE_INIT, STATE_READY, STATE_URLERROR
from .pages import (
    ConfigTabWidget,
    Img2ImgTabWidget,
    InpaintTabWidget,
    SDCommonWidget,
    Txt2ImgTabWidget,
    UpscaleTabWidget,
)
from .script import script
from .widgets import QLabel

# TODO:
# - Consider making QuickConfig a dropdown to save vertical space
# - Come up with more ways to save vertical space for inpaint
# - Save horizontal space too


class SDPluginDocker(DockWidget):
    def __init__(self, *args, **kwargs):
        super(SDPluginDocker, self).__init__(*args, **kwargs)
        self.setWindowTitle("SD Plugin")
        self.create_interfaces()
        self.update_remote_config()
        self.update_interfaces()
        self.connect_interfaces()
        self.setWidget(self.widget)

    def create_interfaces(self):
        self.quick_widget = SDCommonWidget()
        self.txt2img_widget = Txt2ImgTabWidget()
        self.img2img_widget = Img2ImgTabWidget()
        self.inpaint_widget = InpaintTabWidget()
        self.upscale_widget = UpscaleTabWidget()
        self.config_widget = ConfigTabWidget(self.update_interfaces)

        self.tabs = tabs = QTabWidget()
        tabs.addTab(self.txt2img_widget, "Txt2Img")
        tabs.addTab(self.img2img_widget, "Img2Img")
        tabs.addTab(self.inpaint_widget, "Inpaint")
        tabs.addTab(self.upscale_widget, "Upscale")
        tabs.addTab(self.config_widget, "Config")

        self.status_bar = QLabel()
        self.update_status_bar(STATE_INIT)

        layout = QVBoxLayout()
        layout.addWidget(self.quick_widget)
        layout.addWidget(self.status_bar)
        layout.addWidget(tabs)
        layout.addStretch()

        self.widget = QScrollArea()
        widget = QWidget(self)
        widget.setLayout(layout)
        self.widget.setWidget(widget)
        self.widget.setWidgetResizable(True)

        self.update_timer = QTimer()

    def update_interfaces(self):
        self.quick_widget.cfg_init()
        self.txt2img_widget.cfg_init()
        self.img2img_widget.cfg_init()
        self.inpaint_widget.cfg_init()
        self.upscale_widget.cfg_init()
        self.config_widget.cfg_init()

        self.tabs.setCurrentIndex(script.cfg("tab_index", int))

    def connect_interfaces(self):
        self.quick_widget.cfg_connect()
        self.txt2img_widget.cfg_connect()
        self.img2img_widget.cfg_connect()
        self.inpaint_widget.cfg_connect()
        self.upscale_widget.cfg_connect()
        self.config_widget.cfg_connect()

        self.update_timer.timeout.connect(self.update_remote_config)
        self.update_timer.start(REFRESH_INTERVAL)
        script.status_changed.connect(self.update_status_bar)
        self.tabs.currentChanged.connect(partial(script.cfg.set, "tab_index"))

    def update_status_bar(self, s):
        if s == STATE_READY and STATE_URLERROR not in self.status_bar.text():
            return
        self.status_bar.setText(f"<b>Status:</b> {s}")

    def update_remote_config(self):
        script.update_config()
        self.update_interfaces()

    def canvasChanged(self, canvas):
        pass
