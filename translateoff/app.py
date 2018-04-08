from java.util import Random
import android
from android.util import Log
from android.widget import LinearLayout
from android.widget import Button
from android.widget import TextView
from android.view import Gravity
import android.view

import translateoff.sentence


class ButtonClick(implements=android.view.View[OnClickListener]):
    def __init__(self, callback, *args, **kwargs):
        self.callback = callback
        self.args = args
        self.kwargs = kwargs

    def onClick(self, view: android.view.View) -> void:
        self.callback(*self.args, **self.kwargs)


class TranslateOffApp:
    def __init__(self):
        self._activity = android.PythonActivity.setListener(self)
        self.buttons = []
        self.top_label = self.solution_label = None
        self.message = None
        self.sentence = None
        self.shelf_layout = self.solution_layout = None

    def onCreate(self):
        r = Random()

        self.sentence = translateoff.sentence.Sentence('我想我可以。',
                                                       'I think I can.',
                                                       randrange=r.nextInt)

        vlayout = LinearLayout(self._activity)
        vlayout.setOrientation(LinearLayout.VERTICAL)

        self.top_label = TextView(self._activity)
        self.top_label.setText(self.sentence.translation)
        self.top_label.setTextSize(50)
        vlayout.addView(self.top_label)

        self.solution_layout = LinearLayout(self._activity)
        self.solution_layout.setOrientation(LinearLayout.HORIZONTAL)
        self.solution_layout.setGravity(Gravity.LEFT)
        self.solution_label = TextView(self._activity)
        self.solution_label.setText('')
        self.solution_label.setTextSize(50)
        self.solution_layout.addView(self.solution_label)
        vlayout.addView(self.solution_layout)

        self.shelf_layout = LinearLayout(self._activity)
        self.shelf_layout.setOrientation(LinearLayout.HORIZONTAL)
        self.shelf_layout.setGravity(Gravity.CENTER)
        for text in self.sentence.get_buttons():
            button = Button(self._activity)
            button.setText(text)
            button.setTextSize(50)
            self.shelf_layout.addView(button)
            button.setOnClickListener(ButtonClick(self.move_button, button))
        vlayout.addView(self.shelf_layout)

        # self.button.setOnClickListener(ButtonClick(self.play))
        # self.button.setText('Click Me')

        footer = TextView(self._activity)
        footer.setText('Powered by Python')
        footer.setGravity(Gravity.CENTER)
        vlayout.addView(footer)

        self.update_ui()

        self._activity.setContentView(vlayout)

    def update_ui(self):
        if self.message:
            self.top_label.setText(self.message)

    def move_button(self, button):
        parent = button.getParent()
        parent.removeView(button)
        self.solution_layout.addView(button)
        buttons = [self.solution_layout.getChildAt(i).getText()
                   for i in range(1, self.solution_layout.getChildCount())]
        if self.sentence.is_solved(buttons):
            self.solution_label.setText(self.sentence.text)
            while self.solution_layout.getChildCount() > 1:
                self.solution_layout.removeView(
                    self.solution_layout.getChildAt(1))
        self.update_ui()


def main():
    TranslateOffApp()
