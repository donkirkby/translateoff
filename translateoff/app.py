# noinspection PyPackageRequirements
from java.util import Random
# noinspection PyPackageRequirements
import android
# noinspection PyPackageRequirements
from android.widget import LinearLayout, Button, TextView
# noinspection PyPackageRequirements
from android.view import Gravity
# noinspection PyPackageRequirements
import android.view

from translateoff.sentence import Sentence
from translateoff.sentence_data import sentence_text


# noinspection PyUnresolvedReferences,PyPep8Naming
class ButtonClick(implements=android.view.View[OnClickListener]):
    def __init__(self, callback, *args, **kwargs):
        self.callback = callback
        self.args = args
        self.kwargs = kwargs

    def onClick(self, _view: android.view.View) -> void:
        self.callback(*self.args, **self.kwargs)


class Player:
    def __init__(self, activity, is_inverted, solved_callback):
        """ Initialize.

        :param activity: the main activity for the app
        :param is_inverted: True if this player should be displayed upside
            down
        :param solved_callback: to call when the sentence is solved -
            solved_callback(player)"""
        self.activity = activity
        self.is_inverted = is_inverted
        self.solved_callback = solved_callback
        self.solution_buttons = []
        self.shelf_buttons = []
        self.solution_sources = []
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
        self.solution_label.setText('')
        self.solution_sources.clear()
        button_count = len(self.sentence.get_buttons())
        while self.shelf_layout.getChildCount() > button_count:
            self.shelf_layout.removeViewAt(0)
            self.shelf_buttons.pop(0)
            self.solution_layout.removeViewAt(1)
            self.solution_buttons.pop(0)
        while self.shelf_layout.getChildCount() < button_count:
            self.add_button(self.shelf_layout, self.shelf_buttons)
            self.add_button(self.solution_layout, self.solution_buttons)
        for button in self.solution_buttons:
            button.setVisibility(button.INVISIBLE)
        for text, button in zip(self.sentence.get_buttons(), self.shelf_buttons):
            button.setText(text)
            button.setVisibility(button.VISIBLE)

    def add_button(self, layout, button_list):
        button = Button(self.activity)
        button.setTextSize(50)
        layout.addView(button)
        button_list.append(button)
        button.setOnClickListener(ButtonClick(self.move_button, button))

    def move_button(self, button):
        if button in self.solution_buttons:
            solution_index = self.solution_buttons.index(button)
            source = self.solution_sources[solution_index]
            self.solution_sources.pop(solution_index)
            last_button = self.solution_buttons[len(self.solution_sources)]
            last_button.setVisibility(last_button.INVISIBLE)
            source.setVisibility(source.VISIBLE)
            for target, source in zip(self.solution_buttons,
                                      self.solution_sources):
                target.setText(source.getText())
        else:
            button.setVisibility(button.INVISIBLE)
            last_button = self.solution_buttons[len(self.solution_sources)]
            last_button.setText(button.getText())
            last_button.setVisibility(last_button.VISIBLE)
            self.solution_sources.append(button)
        buttons = [button.getText() for button in self.solution_sources]
        if self.sentence.is_solved(buttons):
            for button in self.solution_buttons:
                button.setVisibility(button.INVISIBLE)
            self.solution_label.setText(self.sentence.text)
            self.solved_callback(self)


# noinspection PyPep8Naming
class TranslateOffApp:
    def __init__(self):
        self._activity = android.PythonActivity.setListener(self)
        self.players = []
        self.sentences = []
        self.next_button = None

    def onCreate(self):
        r = Random()

        sentence_lines = iter(sentence_text.splitlines())
        sentence_pairs = zip(sentence_lines, sentence_lines)
        self.sentences = [Sentence(text,
                                   translation,
                                   randrange=r.nextInt)
                          for text, translation in sentence_pairs]

        self.players = [Player(self._activity, is_inverted, self.on_solved)
                        for is_inverted in (True, False)]
        vlayout = LinearLayout(self._activity)
        vlayout.setOrientation(LinearLayout.VERTICAL)

        for i, player in enumerate(self.players):
            if i:
                self.next_button = Button(self._activity)
                self.next_button.setText('Start')
                # noinspection PyUnresolvedReferences
                self.next_button.setLayoutParams(LinearLayout.LayoutParams(
                    LinearLayout.LayoutParams.MATCH_PARENT,
                    LinearLayout.LayoutParams.MATCH_PARENT,
                    1))
                self.next_button.setOnClickListener(
                    ButtonClick(self.next_sentence))
                vlayout.addView(self.next_button)
            player.on_create(vlayout)

        self.next_sentence()
        self._activity.setContentView(vlayout)

    def on_solved(self, player):
        print('on_solved', self.next_button.getText())
        if self.next_button.getText():
            return
        if player.is_inverted:
            self.next_button.setRotation(180)
        else:
            self.next_button.setRotation(0)
        self.next_button.setText('Next')

    def next_sentence(self):
        print('next_sentence', self.next_button.getText(), len(self.sentences))
        if not self.next_button.getText():
            # Current sentence isn't solved.
            return
        self.next_button.setText('')
        if not self.sentences:
            # No more sentences.
            return
        sentence = self.sentences.pop()
        for player in self.players:
            player.set_sentence(sentence)


def main():
    TranslateOffApp()
