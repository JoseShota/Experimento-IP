# from otree.api import Bot
# import random
# from . import *


# class PlayerBot(Bot):
#     def play_round(self):

#         if self.round_number == 1:
#             yield PersonalInfoPage, dict(
#                 age=25,
#                 gender="M",
#                 racial_identification="Pacific Islander",
#                 previous_experiment=2,
#             )

#             yield Practice_BinaryTopic, dict(
#                 answer_practice=random.choice(['Option H','Option L']),
#                 wtl_practice=random.randint(1, 10),
#                 min_opp_punish_practice=random.randint(0, 10),
#             )

#             yield Practice_TopicTreatment

#             yield Practice_WTJ, dict(
#                 wtj_practice=random.choice(C.YES_NO)
#             )

#             _, left, right = practice_left_right(self.player)
#             yield Practice_ExpressYourOpinion, dict(
#                 public_opinion=random.choice([left, right])
#             )

#             trt_idx = practice_treatment_idx(self.player.session)
#             n_A, n_B = counts_for_treatment(trt_idx)
#             yield Practice_HowManyLied, dict(
#                 paid_cost_A_practice=random.randint(0, n_A),
#                 paid_cost_B_practice=random.randint(0, n_B),
#                 expr_A_from_A_practice=random.randint(0, n_A),
#                 expr_A_from_B_practice=random.randint(0, n_B),
#             )

#             for PageClass in BINARY_TOPIC_PAGES:
#                 # preguntamos qué campos espera esta página
#                 field_names = PageClass.get_form_fields(self.player)
#                 values = {}
#                 for f in field_names:
#                     if f.startswith("answer"):
#                         values[f] = random.choice(['Option H','Option L'])
#                     elif f.startswith("wtl"):
#                         values[f] = random.randint(1, 10)
#                     elif f.startswith("min_opp_punish"):
#                         values[f] = random.randint(0, 10)
#                 yield PageClass, values

#             yield TopicTreatment

#             field_name = f'wtj_{self.player.topic_idx + 1}'
#             choice = C.YES_NO[(self.player.id_in_group + self.player.round_number) % 2]
#             yield WillingnessToJudgeFixedCost, {
#                 field_name: choice
#             }

#             left_raw, right_raw = C.BINARY_OPTIONS[self.player.topic_idx]
#             opinion = left_raw if (self.player.id_in_group + self.player.round_number) % 2 == 0 else right_raw
#             yield ExpressYourOpinion, {
#                 'public_opinion': opinion
#             }

#             n_A, n_B = counts_for_treatment(self.player.treatment_idx)
#             seed = self.player.id_in_group + self.player.round_number
#             paid_cost_A   = seed % (n_A + 1)
#             paid_cost_B   = (seed // 2) % (n_B + 1)
#             expr_A_from_A = (seed + 1) % (n_A + 1)
#             expr_A_from_B = (seed + 2) % (n_B + 1)
#             yield HowManyLied, {
#                 'paid_cost_A':   int(paid_cost_A),
#                 'paid_cost_B':   int(paid_cost_B),
#                 'expr_A_from_A': int(expr_A_from_A),
#                 'expr_A_from_B': int(expr_A_from_B),
#             }

#             yield Submission(ThankYouPage, {}, check_html=False)

#             if self.player.round_number >= 1:
#                 yield PaymentWaitPage

# tests.py
from otree.api import Bot, Submission
import random
from . import *

class PlayerBot(Bot):
    def play_round(self):

        # ========= RONDA DE PRÁCTICA (round 1) =========
        if self.round_number == 1:
            # 1) Datos demográficos
            yield PersonalInfoPage, dict(
                age=25,
                gender="M",
                racial_identification="Pacific Islander",
                previous_experiment=2,
            )

            # 2) Tema binario de práctica
            yield Practice_BinaryTopic, dict(
                answer_practice=random.choice(['Option H', 'Option L']),
                wtl_practice=random.randint(1, 10),
                min_opp_punish_practice=random.randint(0, 10),
            )

            # 3) Tratamiento (solo visual) de práctica
            yield Practice_TopicTreatment

            # 4) WTJ práctica
            yield Practice_WTJ, dict(
                wtj_practice=random.choice(C.YES_NO)
            )

            # 5) Opinión pública práctica (usar orientación de práctica)
            _, left_p, right_p = practice_left_right(self.player)
            yield Practice_ExpressYourOpinion, dict(
                public_opinion=random.choice([left_p, right_p])
            )

            # 6) “How many…” práctica (usar conteos del tratamiento de práctica)
            trt_idx_practice = practice_treatment_idx(self.player.session)
            n_A_p, n_B_p = counts_for_treatment(trt_idx_practice)
            yield Practice_HowManyLied, dict(
                paid_cost_A_practice=random.randint(0, n_A_p),
                paid_cost_B_practice=random.randint(0, n_B_p),
                expr_A_from_A_practice=random.randint(0, n_A_p),
                expr_A_from_B_practice=random.randint(0, n_B_p),
            )

            # 7) Las 10 pantallas de Stage 1 (BinaryTopic_1..10) se muestran también en round 1
            for PageClass in BINARY_TOPIC_PAGES:
                field_names = PageClass.get_form_fields(self.player)
                values = {}
                for f in field_names:
                    if f.startswith("answer"):
                        values[f] = random.choice(['Option H', 'Option L'])
                    elif f.startswith("wtl"):
                        values[f] = random.randint(1, 10)
                    elif f.startswith("min_opp_punish"):
                        values[f] = random.randint(0, 10)
                yield PageClass, values

            # Importante: NO intentamos visitar aquí páginas de la fase pagada.
            # Si dejas ExpressYourOpinion con is_displayed >= 1 en __init__.py,
            # el servidor intentará mostrar la versión "pagada" en la práctica y se romperá
            # por topic_idx=None. Cambia is_displayed a >=2 en __init__.py.

            return

        # ========= RONDAS PAGADAS (round >= 2) =========

        # 1) Ver tratamiento (solo visual)
        yield TopicTreatment

        # 2) WTJ con costo fijo
        #    El campo se llama dinámicamente 'wtj_{topic_idx+1}'
        #    (topic_idx y treatment_idx sí están definidos desde round >= 2)
        field_name = f'wtj_{self.player.topic_idx + 1}'
        choice = random.choice(C.YES_NO)
        yield WillingnessToJudgeFixedCost, {
            field_name: choice
        }

        # 3) Expresa tu opinión pública
        #    La validación revisa que sea uno de los 2 strings originales (sin necesidad
        #    de replicar el flip de UI). Así que tomamos el par crudo:
        left_raw, right_raw = C.BINARY_OPTIONS[self.player.topic_idx]
        yield ExpressYourOpinion, {
            'public_opinion': random.choice([left_raw, right_raw])
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
        if 'ThankYouPage' in globals():
            yield Submission(ThankYouPage, {}, check_html=False)
        