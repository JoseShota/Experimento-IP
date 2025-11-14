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


def _simulate_punishment(player, all_players, topic_idx, prob_punishment,
                         opposite_opinion, public_opinion,
                         punishment_stage_1):
    """
    Simula Stage 1 para 'player' con panel de 10:
      - Si faltan jugadores reales para completar el panel, se re-muestrean (con reposición).
      - Solo si NO hay ningún jugador real disponible, se usa 'ficticio'.
      - Observador ficticio => solo el jugador pierde (sin costo a observador).
      - Observador real castigador => jugador pierde y el observador paga costo AQUÍ.
      - Observador real no castigador => no hay castigo.

    Returns (dict):
      {
        'castigado': bool,
        'observador': Player | None,   # None si fue ficticio o no hubo panel
        'punisher': bool               # True si el observador (real o ficticio) castiga
      }
    """
    PANEL_SIZE = 10

    # 1) Clasificar posibles castigadores / no castigadores (excluyendo al propio jugador)
    castigadores = []
    no_castigadores = []
    for other in all_players:
        if other.id_in_subsession == player.id_in_subsession:
            continue
        min_opp = (
            other.participant.vars
            .get(f'topic_{topic_idx}')
            .get(f'stage_1')
            .get(f'min_opp_punish')
        )
        answer_other = (
            other.participant.vars
            .get(f'topic_{topic_idx}')
            .get(f'answer')
        )

        if (opposite_opinion >= min_opp) and (public_opinion != answer_other):
            castigadores.append(other)
        elif (public_opinion == answer_other) or (opposite_opinion < min_opp):
            no_castigadores.append(other)

    # Si no hay NADIE real disponible, usar ficticios
    if (not castigadores) and (not no_castigadores):
        grupo_total = ["ficticio"] * PANEL_SIZE
    else:
        # 2) Armar panel con objetivo: kC_desired castigadores y (10 - kC_desired) no castigadores
        kC_desired = min(prob_punishment, PANEL_SIZE)

        # 2.a) Bloque de castigadores (preferir sin reposición; si faltan, re-muestrear con reposición)
        if len(castigadores) >= kC_desired:
            grupo_castigadores = random.sample(castigadores, kC_desired)
        else:
            if len(castigadores) > 0:
                grupo_castigadores = random.choices(castigadores, k=kC_desired)  # con reposición
            else:
                grupo_castigadores = []

        # 2.b) Completar hasta PANEL_SIZE con no castigadores (misma lógica)
        remaining = PANEL_SIZE - len(grupo_castigadores)
        if remaining > 0:
            if len(no_castigadores) >= remaining:
                grupo_no_castigadores = random.sample(no_castigadores, remaining)
            elif len(no_castigadores) > 0:
                grupo_no_castigadores = random.choices(no_castigadores, k=remaining)  # con reposición
            else:
                # No hay no castigadores reales; completar re-muestreando castigadores reales
                # (si tampoco hubiera castigadores, ya habríamos entrado al caso de ficticios arriba)
                grupo_no_castigadores = random.choices(
                    castigadores, k=remaining
                ) if castigadores else []
        else:
            grupo_no_castigadores = []

        grupo_total = grupo_castigadores + grupo_no_castigadores

    # 3) Elegir observador
    observador = random.choice(grupo_total)

    # 4) Aplicar resultado
    if observador == "ficticio":
        # Ficticio castiga: solo el jugador pierde; sin costo de observador real
        return {'castigado': True, 'observador': None, 'punisher': True}

    # Si el observador (real) está en el bloque de castigadores, castiga
    # OJO: grupo_castigadores puede no existir si entramos al caso de ficticios directo
    if isinstance(observador, type(player)):
        # Determinar si es castigador revisando su regla respecto al jugador
        min_opp_obs = observador.participant.vars.get(f'topic_{topic_idx}').get('stage_1').get('min_opp_punish', None)
        answer_obs = observador.participant.vars.get(f'topic_{topic_idx}').get('answer', None)
        es_castigador = (min_opp_obs is not None and answer_obs is not None
                         and (opposite_opinion >= min_opp_obs)
                         and (public_opinion != answer_obs))

        if es_castigador:
            return {'castigado': True, 'observador': observador, 'punisher': True}
        else:
            return {'castigado': False, 'observador': observador, 'punisher': False}

    # Por seguridad, si llegara un tipo inesperado
    raise ValueError("Observador tiene tipo inesperado.")

# Stage 1 payoff
def set_stage_1_payoff(player: Player):
    """
    Para cada jugador:
    1) Sortea el tópico pagado (1..10) y parámetros de castigo (prob_punishment, opposite_opinion).
    2) Decide si miente o no según su wtl vs prob_punishment.
    3) Llama a _simulate_punishment y aplica el castigo al jugador si corresponde.
    4) Cobra cost_stage_1 al observador real *una sola vez en toda la ronda*.
    """
    # get cobrados set
    cfs = player.subsession.session.vars
    # setdefault si todavia no hay cobrados
    cobrados = cfs.setdefault('stage_1_cobrados', set())
    topic_idx = random.randint(0, 10)  # tópico pagado aleatorio entre 1 y 10
    # obtener datos de stage 1 del participante
    ans = player.participant.vars[f'topic_{topic_idx}'].get('answer')
    wtl = player.participant.vars[f'topic_{topic_idx}'].get('stage_1').get('wtl')
    # calcular parametros para pagos
    prob_punishment   = random.randint(0, 10)
    opposite_opinion  = random.randint(0, 10)
    # Regla: si la prob. de ser castigado es <= a su umbral wtl, dice su verdad; si no, invierte.
    if prob_punishment <= wtl:
        public_opinion = ans
    else:
        if ans == 'A':
            public_opinion = 'B'
        elif ans == 'B':
            public_opinion = 'A'

    # Simula castigo. Esta función YA no cobra el costo al observador.
    result = _simulate_punishment(
        player=player,
        all_players=player.subsession.get_players(),
        topic_idx=topic_idx,
        prob_punishment=prob_punishment,
        opposite_opinion=opposite_opinion,
        public_opinion=public_opinion,
        punishment_stage_1=player.subsession.session.config['PUNISHMENT_STAGE_1'],
        cost_stage_1=player.subsession.session.config['COST_STAGE_1'],
    )

    # Aplicar castigo al jugador si corresponde
    if result.get('castigado'):
        player.payoff -= cu(player.subsession.session.config['PUNISHMENT_STAGE_1'])
        # guardar en participant.vars para control
        player.participant.vars['stage_1']['got_punished'] = {'topic_idx': topic_idx,
                                'prob_punishment': prob_punishment,
                                'opposite_opinion': opposite_opinion,
                                'judge': result.get('observador').id_in_subsession if result.get('observador') else None}
    # Si hubo observador real que castigó, se le cobra solo una vez en la ronda.
    obs = result.get('observador')
    if result.get('punisher') and (obs is not None):
        if obs.id_in_subsession not in cobrados:
            obs.payoff -= cu(player.subsession.session.config['COST_STAGE_1'])
            # marcar como cobrado
            cobrados.add(obs.id_in_subsession)
            print(cfs.get('stage_1_cobrados',"ERROR"))
            # guardar en participant.vars para control
            obs.participant.vars['stage_1']['got_charged'] = True


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