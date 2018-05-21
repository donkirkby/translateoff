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
        self.opponent = None
        self.unlimited_hints = False
        self.top_label = None
        self.next_button = None
        self.solution_label = None
        self.sentence = None
        self.shelf_layout = self.solution_layout = self.top_layout = None

    def on_create(self, parent_layout):
        vlayout = LinearLayout(self.activity)
        vlayout.setOrientation(LinearLayout.VERTICAL)
        vlayout.setGravity(Gravity.BOTTOM)
        if self.is_inverted:
            vlayout.setRotation(180)
        parent_layout.addView(vlayout)

        self.top_layout = LinearLayout(self.activity)
        self.top_layout.setOrientation(LinearLayout.HORIZONTAL)
        self.top_label = TextView(self.activity)
        self.top_label.setTextSize(50)
        self.top_layout.addView(self.top_label)
        self.next_button = Button(self.activity)
        self.next_button.setText('Hint')
        self.next_button.setOnClickListener(
            ButtonClick(self.next))
        self.top_layout.addView(self.next_button)
        vlayout.addView(self.top_layout)

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
        button_count = len(self.sentence.source)
        while self.shelf_layout.getChildCount() > button_count:
            self.shelf_layout.removeViewAt(0)
            self.shelf_buttons.pop(0)
            self.solution_layout.removeViewAt(1)
            self.solution_buttons.pop(0)
        while self.shelf_layout.getChildCount() < button_count:
            self.add_button(self.shelf_layout, self.shelf_buttons)
            self.add_button(self.solution_layout, self.solution_buttons)
        self.update_display()

    def update_display(self):
        self.update_buttons(self.solution_buttons,
                            self.sentence.selected,
                            self.sentence.hint_size)
        self.update_buttons(self.shelf_buttons, self.sentence.source)
        if self.sentence.is_solved:
            self.next_button.setText('Next')
            self.next_button.setEnabled(True)

    # noinspection PyMethodMayBeStatic
    def update_buttons(self, buttons, characters, disabled_count=0):
        for i, (button, text) in enumerate(zip(buttons, characters)):
            button.setEnabled(i >= disabled_count)
            button.setText(text)
            button.setVisibility(button.INVISIBLE
                                 if text == ' '
                                 else button.VISIBLE)

    def add_button(self, layout, button_list):
        button = Button(self.activity)
        button.setTextSize(50)
        layout.addView(button)
        button_list.append(button)
        button.setOnClickListener(ButtonClick(self.move_button, button))

    def move_button(self, button):
        if button in self.solution_buttons:
            solution_index = self.solution_buttons.index(button)
            self.sentence.replace(solution_index)
        else:
            source_index = self.shelf_buttons.index(button)
            self.sentence.select(source_index)
        self.update_display()
        if self.sentence.is_solved:
            self.solution_label.setText(self.sentence.text)
            for b in self.solution_buttons:
                b.setVisibility(b.INVISIBLE)

    def get_buttons(self):
        buttons = [button.getText() for button in self.solution_sources]
        return buttons

    def enable_hint(self):
        self.next_button.setEnabled(True)

    def next(self):
        self.next_button.setEnabled(self.unlimited_hints)
        self.opponent.enable_hint()
        if self.sentence.is_solved:
            self.next_button.setText('Hint')
            self.solved_callback(self)
        else:
            self.sentence.get_hint()
            self.update_display()


# noinspection PyPep8Naming
class TranslateOffApp:
    def __init__(self):
        self._activity = android.PythonActivity.setListener(self)
        self.players = []
        self.player_progress = None
        self.sentence_pairs = None
        self.winner_label = None
        self.next_button = None
        self.random = Random()

    def onCreate(self):
        sentence_lines = iter(sentence_text.splitlines())
        self.sentence_pairs = list(zip(sentence_lines, sentence_lines))[10:20]

        self.players = [Player(self._activity, is_inverted, self.on_solved)
                        for is_inverted in (True, False)]
        self.player_progress = {player: 0 for player in self.players}
        vlayout = LinearLayout(self._activity)
        vlayout.setOrientation(LinearLayout.VERTICAL)

        for i, player in enumerate(self.players):
            if i:
                self.winner_label = TextView(self._activity)
                self.winner_label.setTextSize(50)
                # noinspection PyUnresolvedReferences
                self.winner_label.setLayoutParams(LinearLayout.LayoutParams(
                    LinearLayout.LayoutParams.MATCH_PARENT,
                    LinearLayout.LayoutParams.MATCH_PARENT,
                    1))
                vlayout.addView(self.winner_label)
            player.opponent = self.players[(i+1) % 2]
            player.on_create(vlayout)
            self.set_sentence(player)

        self._activity.setContentView(vlayout)

    def set_sentence(self, player):
        i = self.player_progress[player]
        text, translation = self.sentence_pairs[i]
        player.set_sentence(
            Sentence(text, translation, randrange=self.random.nextInt))

    def on_solved(self, player):
        i = self.player_progress[player] + 1
        if i < len(self.sentence_pairs):
            self.player_progress[player] = i
            self.set_sentence(player)
        else:
            if self.winner_label.getText():
                return
            if player.is_inverted:
                self.winner_label.setRotation(180)
            else:
                self.winner_label.setRotation(0)
            self.winner_label.setText('You Win!')
            player.opponent.unlimited_hints = True


def main():
    TranslateOffApp()
