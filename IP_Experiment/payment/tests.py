# apps/payment/tests.py
from otree.api import Bot

class PlayerBot(Bot):
    def play_round(self):
        # Esta app no tiene interacción con el participante.
        # Se ejecuta solo la lógica de payoff en WaitPage.
        pass
