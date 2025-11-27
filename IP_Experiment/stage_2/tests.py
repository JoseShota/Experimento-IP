from otree.api import Bot, Submission
import random
from . import *
from common.params import TREATMENT_CODES, TREATMENT_TO_COUNTS

class PlayerBot(Bot):
    def play_round(self):

        # ========= RONDA DE PRÁCTICA (round 1) =========
        if self.round_number == 1:
            
            yield Practice_TopicTreatment

            yield Practice_WTJ, dict(
                wtj=random.choice([True, False])
            )

            yield Practice_ExpressYourOpinion, dict(
                public_opinion = random.choice(['A', 'B'])
            )

            trt_idx_practice = practice_treatment_idx(self.player.session)
            n_A, n_B = counts_for_treatment(trt_idx_practice)
            yield Practice_HowManyLied, {
            'paid_cost_A':   random.randint(0, n_A),
            'paid_cost_B':   random.randint(0, n_B),
            'expr_A_from_A': random.randint(0, n_A),
            'expr_A_from_B': random.randint(0, n_B),
        }

            return

        # ========= RONDAS PAGADAS (round >= 2) =========

        # 1) Ver tratamiento (solo visual)
        yield TopicTreatment

        # 2) WTJ con costo fijo
        #    El campo se llama dinámicamente 'wtj_{topic_idx+1}'
        #    (topic_idx y treatment_idx sí están definidos desde round >= 2)
        yield WillingnessToJudgeFixedCost, {'wtj': random.choice([True, False])}

        # 3) Expresa tu opinión pública
        #    La validación revisa que sea uno de los 2 strings originales (sin necesidad
        #    de replicar el flip de UI). Así que tomamos el par crudo:
        yield ExpressYourOpinion, {
            'public_opinion': random.choice(['A', 'B'])
        }

        # 4) “How many lied / paid…” (usar conteos reales del tratamiento de esa ronda)
        n_A, n_B = counts_for_treatment(self.player.treatment_idx)
        # Generamos números válidos dentro del rango permitido:
        yield HowManyLied, {
            'paid_cost_A':   random.randint(0, n_A),
            'paid_cost_B':   random.randint(0, n_B),
            'expr_A_from_A': random.randint(0, n_A),
            'expr_A_from_B': random.randint(0, n_B),
        }

        # 5) Cierre / espera de pago (si están en tu sequence)
        #    (Si ThankYouPage no tiene form, usamos Submission para saltar el check de HTML)
        if self.round_number == C.NUM_ROUNDS:
            yield Submission(ThankYouPage, {}, check_html=False)
