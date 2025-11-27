from otree.api import Bot
from . import PersonalInfoPage

class PlayerBot(Bot):
    def play_round(self):
        yield PersonalInfoPage, dict(
            age=25,
            gender="M",
            racial_identification="Pacific Islander",
            previous_experiment=2,
        )