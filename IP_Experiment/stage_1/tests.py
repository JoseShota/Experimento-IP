# stage_1_separated/tests.py

import random
from otree.api import Bot, Submission
from . import BinaryQuestionsPage, BinaryQuestionsPage_Practice, ThankYouPage, C

class PlayerBot(Bot):
    def play_round(self):
        """
        Bot para Stage 1:
        - Ronda 1 → página de práctica
        - Rondas >= 2 → páginas normales
        """

        # valores aleatorios válidos
        ans = random.choice(['A', 'B'])
        wtl_val = random.randint(1, 10)
        opp_val = random.randint(0, 10)

        if self.player.round_number == 1:
            yield BinaryQuestionsPage_Practice, {
                "answer": ans,
                "wtl": wtl_val,
                "min_opp_punish": opp_val,
            }

        else:
            yield BinaryQuestionsPage, {
                "answer": ans,
                "wtl": wtl_val,
                "min_opp_punish": opp_val,
            }
        
        if self.round_number == C.NUM_ROUNDS:
            yield Submission(ThankYouPage, {}, check_html=False)
