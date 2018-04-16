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


sentence_text = """\
我想我可以。
I think I can.
他在學中文。
He's studying Chinese.
你不是學生。
You are not a student.
现在几点钟？
What time is it?
今天是几月几日？
What is the date today?
今天是星期日。
Today is Sunday.
今天是她的生日。
It's her birthday today.
我喜欢冰淇淋。
I like ice cream.
他喜欢玩游戏。
He likes to play games.
他几岁？
How old is he?
她有长头发吗？
Does she have long hair?
你喜欢小龙包吗？
Do you like soup dumplings?
"""


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
        self.solution_buttons.clear()
        while self.solution_layout.getChildCount() > 1:
            self.solution_layout.removeViewAt(1)
        while self.shelf_layout.getChildCount():
            self.shelf_layout.removeViewAt(0)
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
