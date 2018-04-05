import android
from android.util import Log
from android.widget import LinearLayout
from android.widget import Button
from android.widget import TextView
from android.view import Gravity
import android.view



class ButtonClick(implements=android.view.View[OnClickListener]):
    def __init__(self, callback, *args, **kwargs):
        self.callback = callback
        self.args = args
        self.kwargs = kwargs

    def onClick(self, view: android.view.View) -> void:
        self.callback(*self.args, **self.kwargs)


class MyApp:
    def __init__(self):
        self._activity = android.PythonActivity.setListener(self)
        self.button = None
        self.top_label = None
        self.message = None

    def onCreate(self):
        self.button = Button(self._activity)

        vlayout = LinearLayout(self._activity)
        vlayout.setOrientation(LinearLayout.VERTICAL)

        self.top_label = TextView(self._activity)
        self.top_label.setTextSize(50)
        vlayout.addView(self.top_label)

        hlayout = LinearLayout(self._activity)
        hlayout.setOrientation(LinearLayout.HORIZONTAL)
        hlayout.setGravity(Gravity.CENTER)
        self.button.setTextSize(50)
        hlayout.addView(self.button)
        vlayout.addView(hlayout)

        self.button.setOnClickListener(ButtonClick(self.play))
        self.button.setText('Click Me')

        footer = TextView(self._activity)
        footer.setText('Powered by Python')
        footer.setGravity(Gravity.CENTER)
        vlayout.addView(footer)

        self.updateUI()

        self._activity.setContentView(vlayout)

    def updateUI(self):
        if self.message:
            self.top_label.setText(self.message)

    def play(self):
        self.message = 'Clicked 1!'
        self.updateUI()


def main():
    MyApp()
