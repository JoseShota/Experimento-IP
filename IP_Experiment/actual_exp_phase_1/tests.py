from otree.api import Bot
import random
from . import *


class PlayerBot(Bot):
    def play_round(self):
        if self.round_number == 1:
            yield PersonalInfoPage, dict(
                age=25,
                gender="M",
                racial_identification="Pacific Islander",
                previous_experiment=2,
            )

            yield Practice_BinaryTopic, dict(
                answer_practice=random.choice(['Option H','Option L']),
                wtl_practice=random.randint(1, 10),
                min_opp_punish_practice=random.randint(0, 10),
            )

            for PageClass in BINARY_TOPIC_PAGES:
                # preguntamos qué campos espera esta página
                field_names = PageClass.get_form_fields(self.player)
                values = {}
                for f in field_names:
                    if f.startswith("answer"):
                        values[f] = random.choice(['Option H','Option L'])
                    elif f.startswith("wtl"):
                        values[f] = random.randint(1, 10)
                    elif f.startswith("min_opp_punish"):
                        values[f] = random.randint(0, 10)
                yield PageClass, values

            yield Submission(ThankYouPage, {}, check_html=False)
