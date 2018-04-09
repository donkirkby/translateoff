# noinspection PyPackageRequirements
from java.util import Random
# noinspection PyPackageRequirements
import android
# noinspection PyPackageRequirements
from android.widget import LinearLayout, Button, TextView
# noinspection PyPackageRequirements
from android.view import Gravity, View
# noinspection PyPackageRequirements
import android.view

import translateoff.sentence


# noinspection PyUnresolvedReferences,PyPep8Naming
class ButtonClick(implements=android.view.View[OnClickListener]):
    def __init__(self, callback, *args, **kwargs):
        self.callback = callback
        self.args = args
        self.kwargs = kwargs

    def onClick(self, _view: android.view.View) -> void:
        self.callback(*self.args, **self.kwargs)


class Player:
    def __init__(self, activity, is_inverted):
        self.activity = activity
        self.is_inverted = is_inverted
        self.solution_buttons = []
        self.top_label = None
        self.solution_label = None
        self.sentence = None
        self.shelf_layout = self.solution_layout = None

    def on_create(self, parent_layout):
        vlayout = LinearLayout(self.activity)
        vlayout.setOrientation(LinearLayout.VERTICAL)
        vlayout.setGravity(Gravity.BOTTOM)
        if self.is_inverted:
            vlayout.setRotation(180)
        parent_layout.addView(vlayout)

        self.top_label = TextView(self.activity)
        self.top_label.setTextSize(50)
        vlayout.addView(self.top_label)

        self.solution_layout = LinearLayout(self.activity)
        self.solution_layout.setOrientation(LinearLayout.HORIZONTAL)
        self.solution_layout.setGravity(Gravity.LEFT)
        self.solution_label = TextView(self.activity)
        self.solution_label.setText('')
        self.solution_label.setTextSize(50)
        self.solution_layout.addView(self.solution_label)
        vlayout.addView(self.solution_layout)

        self.shelf_layout = LinearLayout(self.activity)
        self.shelf_layout.setOrientation(LinearLayout.HORIZONTAL)
        self.shelf_layout.setGravity(Gravity.CENTER)
        vlayout.addView(self.shelf_layout)

    def set_sentence(self, sentence):
        self.sentence = sentence
        self.top_label.setText(self.sentence.translation)
        for text in self.sentence.get_buttons():
            button = Button(self.activity)
            button.setText(text)
            button.setTextSize(50)
            self.shelf_layout.addView(button)
            button.setOnClickListener(ButtonClick(self.move_button, button))

    def move_button(self, button):
        if button in self.solution_buttons:
            source = self.solution_layout
            target = self.shelf_layout
            self.solution_buttons.remove(button)
        else:
            source = self.shelf_layout
            target = self.solution_layout
            self.solution_buttons.append(button)
        source.removeView(button)
        target.addView(button)
        buttons = [button.getText() for button in self.solution_buttons]
        if self.sentence.is_solved(buttons):
            self.solution_label.setText(self.sentence.text)
            while self.solution_layout.getChildCount() > 1:
                self.solution_layout.removeView(
                    self.solution_layout.getChildAt(1))


# noinspection PyPep8Naming
class TranslateOffApp:
    def __init__(self):
        self._activity = android.PythonActivity.setListener(self)
        self.players = []

    def onCreate(self):
        r = Random()

        sentence = translateoff.sentence.Sentence('我想我可以。',
                                                  'I think I can.',
                                                  randrange=r.nextInt)

        self.players = [Player(self._activity, is_inverted)
                        for is_inverted in (True, False)]
        vlayout = LinearLayout(self._activity)
        vlayout.setOrientation(LinearLayout.VERTICAL)

        for i, player in enumerate(self.players):
            if i:
                spacer = View(self._activity)
                # noinspection PyUnresolvedReferences
                spacer.setLayoutParams(LinearLayout.LayoutParams(
                    LinearLayout.LayoutParams.MATCH_PARENT,
                    LinearLayout.LayoutParams.MATCH_PARENT,
                    1))
                vlayout.addView(spacer)
            player.on_create(vlayout)
            player.set_sentence(sentence)

        self._activity.setContentView(vlayout)


def main():
    TranslateOffApp()
