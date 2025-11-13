# apps/payment/__init__.py
import random
import pprint
from otree.api import *
from common.params import TREATMENT_TO_COUNTS, TREATMENT_CODES

# Models
doc = """
App final de pagos (invisible). Lee participant.vars y session.config.
"""


class C(BaseConstants):
    NAME_IN_URL = 'payment'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    pass


# -------- Helpers (con defaults) --------
def _stage1_answer(player: Player, topic_idx: int) -> str:
    """Devuelve 'A' o 'B' según respuesta en Stage 1 para el tema dado"""
    stage1_r = player.participant.vars[f'topic_{topic_idx}'].get('answer',
                                                                 random.choice(['A', 'B'])) # in case only run stage 2
    return stage1_r


def _sample_exact(candA, candB, nA: int, nB: int) -> list:
        """Devuelve lista exacta de tamaño 10 (nA de A y nB de B) si alcanza; si no, devuelve None."""
        if len(candA) >= nA and len(candB) >= nB:
            pickA = random.sample(candA, nA)
            pickB = random.sample(candB, nB)
            return pickA + pickB
        return None


def _choose_one_with_probs(candA, candB, nA: int, nB: int) -> list:
        """regresa un grupo de dos jugadores con diferentes opiniones con probabilidades pA=nA/(nA+nB), pB=nB/(nA+nB)."""
        pp_a = random.choice(candA)
        pp_b = random.choice(candB)
        return [pp_a]*nA + [pp_b]*nB


def _build_GH_exact(
    candA: list[Player],
    candB: list[Player],
    nA: int,
    nB: int,
) -> list[tuple[Player, int]]:
    """
    Construye GH con EXACTAMENTE (nA, nB) usando muestreo CON REEMPLAZO.
    - candA/candB: listas de tuplas (Player, r_pp) ya filtradas por (topic_idx, treatment_idx).
    - nA+nB debe ser 10.
    - Si se requiere >0 de un bucket y ese bucket está vacío, levanta ValueError.
    - Devuelve lista de longitud 10: nA de A y nB de B (con duplicados posibles).

    Ejemplo de uso:
        GH = _build_GH_exact(candA, candB, nA, nB, rng=_rng_for_participant(p_i))
    """
    # Muestreo con reemplazo (permite repetir al mismo participante)
    picks_A = [random.choice(candA) for _ in range(nA)]
    picks_B = [random.choice(candB) for _ in range(nB)]

    GH = picks_A + picks_B
    # Sanidad final
    assert len(GH) == 10 and len(picks_A) == nA and len(picks_B) == nB
    return GH


def _build_groups_for_player_in_round(subsession: Subsession, p_i: Player, topic_idx: int, treatment_idx: int
                                      ) -> dict[str, list[tuple[Player,int]]]:
    """
    Construye GJ, GE, GH para el jugador p_i en la ronda dada,
    cumpliendo: (1) composición (nA, nB) del tratamiento de esta ronda,
    (2) coincidencia tratamiento–tema (decisiones de los otros en SU ronda r). 
    Devuelve: dict con claves 'GJ', 'GE', 'GH'"""
    # todos los jugadores menos p_i
    others = [pp for pp in subsession.get_players() if pp.id_in_subsession != p_i.id_in_subsession]
    # crear grupo de 'A' y 'B' según answer Stage 1 para este tema
    candA: list[tuple[Player,int]] = []
    candB: list[tuple[Player,int]] = []
    for pp in others:
        pp_ans = _stage1_answer(pp, topic_idx)
        if pp_ans == 'A':
            candA.append(pp)
        elif pp_ans == 'B':
            candB.append(pp)
    # obtener composición (nA, nB) para este tratamiento
    nA, nB = TREATMENT_TO_COUNTS.get(TREATMENT_CODES[treatment_idx])
    # ¿Qué hacer en caso de que ningún participante escogió 'A' o 'B'?
    # Armar grupos
    GJ = _sample_exact(candA, candB, nA, nB)
    if GJ is None:
        GJ = _choose_one_with_probs(candA, candB, nA, nB)
    GE = _sample_exact(candA, candB, nA, nB)
    if GE is None:
        GE = _choose_one_with_probs(candA, candB, nA, nB)
    GH = _sample_exact(candA, candB, nA, nB)
    if GH is None:
        GH = _build_GH_exact(candA, candB, nA, nB)
    return {'GJ': GJ, 'GE': GE, 'GH': GH}


def _calculate_how_many_lied(group:list,option:str,type:str,topic_idx:int,treatment_idx:int)->int:
    """
    Calcula el número de participantes con respuesta {option} para.
    - type == 'wtj': # de peronas dispuestas a juzgar (wtj==True)
    - type == 'public_opinion': # de personas que expresaron 'A'
    - group: lista de tuplas (Player, ronda del Player)
    - option: 'A' o 'B' (opciones mapeadas a 'A'/'B')
    Devuelve el el número de personas en el grupo que cumplen la condición.
    """
    count = 0
    for player in group:
        # verificar si el jugador escogió la opción dada en Stage 1 (### Preguntar ### si esta respuesa 'A/B' se refiere a Stage 1 o public opinion)
        ans = _stage1_answer(player, topic_idx)
        if type == 'wtj' and ans == option:
            if player.participant.vars[f'topic_{topic_idx}'].get(f'treatment_{treatment_idx}').get('wtj'):
                count += 1
        elif type == 'public_opinion' and ans == option:
            po = player.participant.vars[f'topic_{topic_idx}'].get(f'treatment_{treatment_idx}').get('public_opinion')
            if po == 'A':
                count += 1
    return count


# Stage 1 payoff
def set_stage_1_payoff(player):
    pass

# Stage 2 payoff
def set_stage_2_payoff(player: Player, pairs: list, cost_stage_2, punishment_stage_2, cost_to_lie_stage_2, bonus_stage_2):
    # 1) Topic y treatment aleatorio
    pairs = player.subsession.session.vars['PAIRS']
    topic_idx,treatment_idx = pairs[random.randint(0, len(pairs)-1)]
    # Formar grupos GJ, GE, GH
    groups = _build_groups_for_player_in_round(
        subsession=player.subsession,
        p_i=player,
        topic_idx=topic_idx,
        treatment_idx=treatment_idx,
    )
    GJ, GE, GH = groups['GJ'], groups['GE'], groups['GH']

    #### Lógica de pago para WillingnessToJudgeFixedCost_r ####
    wtj = player.participant.vars[f"topic_{topic_idx}"].get(f'treatment_{treatment_idx}').get('wtj')
    # si wtj=Sí, extraer al azar un jugador de GJ para posible comparación
    if wtj:
        target_player = random.choice(GJ)
        target_opinion = target_player.participant.vars[f"topic_{topic_idx}"].get(f'treatment_{treatment_idx}').get('public_opinion') 
        ### PREGUNTAR ###
        # public_opinion vs stage_1 opinion?
        # si la opinion del juzgado difiere de la propia, cobrar costo y castigo
        if target_opinion != player.participant.vars[f"topic_{topic_idx}"].get('answer',
                                                                 random.choice(['A', 'B'])):  # in case only run stage 2
            player.payoff -= cost_stage_2
            target_player.payoff -= punishment_stage_2
            # marcar en particiant.vars para control
            player.participant.vars['wtj_result'] = {
                'punished_other_player': True,
                'target_player_id': target_player.id_in_subsession}
        else:
            # marcar en participant.vars para control
            player.participant.vars['wtj_result'] = {
                'punished_other_player': False,
                'target_player_id': target_player.id_in_subsession}
    else:
        # marcar en participant.vars para control
        player.participant.vars['wtj_result'] = {
            'punished_other_player': False}
        
    #### Lógica de pago para ExpressYourOpinion_r ####
    player_opinion = player.participant.vars[f"topic_{topic_idx}"].get(f'treatment_{treatment_idx}').get('public_opinion')
    # si la opinion expresada difiere de la propia, cobrar costo por mentir
    lie = False # guardar si mintió o no
    if player_opinion != player.participant.vars[f"topic_{topic_idx}"].get('answer',
                                                                 random.choice(['A', 'B'])):  # in case only run stage 2
        player.payoff -= cost_to_lie_stage_2
        lie = True # cambiar valor a mintió
    # obtener una persona del grupo
    judge = random.choice(GE)
    wtj_j = judge.participant.vars[f"topic_{topic_idx}"].get(f'treatment_{treatment_idx}').get('wtj')
    # si esa persona está dispuesta a juzgar y la opinión difiere, cobrar castigo
    if wtj_j:
        judge_opinion = judge.participant.vars[f"topic_{topic_idx}"].get(f'treatment_{treatment_idx}').get('public_opinion') ### PREGUNTAR ### public_opinion o answer Stage 1?
        # si la opinion del juez difiere de la propia, cobrar costo y castigo
        if judge_opinion != player_opinion:
            player.payoff -= punishment_stage_2
            judge.payoff -= cost_stage_2
            # marcar en particiant.vars para control
            player.participant.vars['eyo_result'] = {
                'got_punished': True,
                'judge_player_id': judge.id_in_subsession,
                'player_lied': lie}
        else:
            # marcar en participant.vars para control
            player.participant.vars['eyo_result'] = {
                'got_punished': False,
                'judge_player_id': judge.id_in_subsession,
                'player_lied': lie}
    else:
        # marcar en participant.vars para control
        player.participant.vars['eyo_result'] = {
            'got_punished': False,
            'player_lied': lie}

    #### Lógica de pago para HowManyLied_r ####
    prediction_idx = random.randint(1, 4)
    prediction_list = ['paid_cost_A', 'paid_cost_B', 'expr_A_from_A', 'expr_A_from_B']
    if prediction_idx == 1:
        real = _calculate_how_many_lied(GH, 'A', 'wtj', topic_idx, treatment_idx)
        prediction = player.participant.vars[f"topic_{topic_idx}"].get(f'treatment_{treatment_idx}').get('paid_cost_A')
        if real == prediction:
            player.payoff += bonus_stage_2
            # marcar en participant.vars para control
            player.participant.vars['hml_result'] = {
                'correct_prediction': True,
                'prediction': prediction_list[prediction_idx - 1]}
        else:
            player.participant.vars['hml_result'] = {
                'correct_prediction': False,
                'prediction': prediction_list[prediction_idx - 1]}
    elif prediction_idx == 2:
        real = _calculate_how_many_lied(GH, 'B', 'wtj', topic_idx, treatment_idx)
        prediction = player.participant.vars[f"topic_{topic_idx}"].get(f'treatment_{treatment_idx}').get('paid_cost_B')
        if real == prediction:
            player.payoff += bonus_stage_2
            # marcar en participant.vars para control
            player.participant.vars['hml_result'] = {
                'correct_prediction': True,
                'prediction': prediction_list[prediction_idx - 1]}
        else:
            player.participant.vars['hml_result'] = {
                'correct_prediction': False,
                'prediction': prediction_list[prediction_idx - 1]}
    elif prediction_idx == 3:
        real = _calculate_how_many_lied(GH, 'A', 'public_opinion', topic_idx, treatment_idx)
        prediction = player.participant.vars[f"topic_{topic_idx}"].get(f'treatment_{treatment_idx}').get('expr_A_from_A')
        if real == prediction:
            player.payoff += bonus_stage_2
            # marcar en participant.vars para control
            player.participant.vars['hml_result'] = {
                'correct_prediction': True,
                'prediction': prediction_list[prediction_idx - 1]}
        else:
            player.participant.vars['hml_result'] = {
                'correct_prediction': False,
                'prediction': prediction_list[prediction_idx - 1]}
    else:  # prediction_idx == 4
        real = _calculate_how_many_lied(GH, 'B', 'public_opinion', topic_idx, treatment_idx)
        prediction = player.participant.vars[f"topic_{topic_idx}"].get(f'treatment_{treatment_idx}').get('expr_A_from_B')
        if real == prediction:
            player.payoff += bonus_stage_2
            # marcar en participant.vars para control
            player.participant.vars['hml_result'] = {
                'correct_prediction': True,
                'prediction': prediction_list[prediction_idx - 1]}
        else:
            player.participant.vars['hml_result'] = {
                'correct_prediction': False,
                'prediction': prediction_list[prediction_idx - 1]}
    # debugging prints
    # print("Payment calculation stage_2 for player: ", player.id_in_subsession)
    # pprint.pprint(player.participant.vars['wtj_result'])
    # pprint.pprint(player.participant.vars['eyo_result'])
    # pprint.pprint(player.participant.vars['hml_result'])

# -------- Página invisible que ejecuta el cálculo --------
class ComputePayoffs(WaitPage):
    wait_for_all_groups = True

    def after_all_players_arrive(self):
        for pl in self.subsession.get_players():
            # set_stage_1_payoff(pl)
            set_stage_2_payoff(
                player=pl,
                pairs=self.subsession.session.vars['PAIRS'],
                cost_stage_2=cu(self.subsession.session.config['COST_STAGE_2']),
                punishment_stage_2=cu(self.subsession.session.config['PUNISHMENT_STAGE_2']),
                cost_to_lie_stage_2=cu(self.subsession.session.config['COST_STAGE_2']),
                bonus_stage_2=cu(self.subsession.session.config['BONUS_STAGE_2']),
                )


page_sequence = [ComputePayoffs]