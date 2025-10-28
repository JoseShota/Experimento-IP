from __future__ import annotations
from otree.api import *
import secrets
import random

def _rng_for_participant(participant):
    if 'rng' not in participant.vars:
        seed = secrets.randbits(64)  # 64 bits of OS entropy
        participant.vars['rng'] = random.Random(seed)
    return participant.vars['rng']

# -----------------------------------------------------------------------------
# Module-level constants
# -----------------------------------------------------------------------------

class C(BaseConstants):
    NAME_IN_URL = 'actual_exp_phase_1'
    PLAYERS_PER_GROUP = None
    PRACTICE_TOPIC_LABEL = 'Emmanuel o Mijares'
    PRACTICE_OPTIONS     = ('Option H', 'Option L')
    ########################### ADD ON ###########################
    # Stage 2: costos y castigos (ajusta a tus valores reales)
    COST_STAGE_2 = cu(1000)            # cost_stage_2
    COST_TO_LIE = cu(2000)           # cost_to_lie
    BONUS_STAGE_2 = cu(3000)           # bonus_stage_2 (en $$$; si conviertes puntos a $ en otra parte, deja aquí sólo el flag)

    # Mapear tratamiento->(nA, nB). Si ya tienes TREATMENT_CODES/round schedule, usa eso.
    # Ejemplo genérico: 9 tratamientos con 1A–9B ... 9A–1B
    TREATMENT_TO_COMPOSITION = {
        'A1B9': (1, 9), 'A2B8': (2, 8), 'A3B7': (3, 7), 'A4B6': (4, 6),
        'A5B5': (5, 5), 'A6B4': (6, 4), 'A7B3': (7, 3), 'A8B2': (8, 2), 'A9B1': (9, 1),
    }

# 10 Binary Questions 
    TOPIC_LABELS = [
        "Topic 1",
        "Topic 2",
        "Topic 3",
        "Topic 4",
        "Topic 5",
        "Topic 6",
        "Topic 7",
        "Topic 8",
        "Topic 9",
        "Topic 10",
        ]

# Answers for the 10 binary questions
    BINARY_OPTIONS = [
    ('Option H', 'Option L'),  # Question 1
    ('Option H', 'Option L'),  # Question 2
    ('Option H', 'Option L'),  # Question 3
    ('Option H', 'Option L'),  # Question 4
    ('Option H', 'Option L'),  # Question 5
    ('Option H', 'Option L'),  # Question 6
    ('Option H', 'Option L'),  # Question 7
    ('Option H', 'Option L'),  # Question 8
    ('Option H', 'Option L'),  # Question 9
    ('Option H', 'Option L'),  # Question 10
    ]

# Treatment codes for the experiment
    TREATMENT_CODES = [
        'New_Ten_Ninety',
        'New_Twenty_Eighty',
        'New_Thirty_Seventy',
        'New_Forty_Sixty',
        'New_Fifty_Fifty',
        'New_Sixty_Forty',
        'New_Seventy_Thirty',
        'New_Eighty_Twenty',
        'New_Ninety_Ten',
    ]

    PRACTICE_ROUNDS = 1

    # ---------- derived combinations ----------
    PAIRS = []
    for t_idx in range(len(TOPIC_LABELS)):
        for trt_idx in range(len(TREATMENT_CODES)):
            PAIRS.append((t_idx, trt_idx))

# Willingness to judge fixed cost and maximum cost
    YES_NO = ('Yes, I am willing to pay  { cost_stage_2 } to make the decision', 'No, I am not willing to pay { cost_stage_2 } to make the decision')  # canonical label pair
    # NEW: cost text for Stage 1 (used in the new Q3)
    PUNISHMENT_STAGE1 = cu(3000)
    PUNISHMENT_STAGE_2 = cu(3000)          # punishment_stage_2
    COST_STAGE1 = cu(1000)
    NUM_ROUNDS = PRACTICE_ROUNDS + len(PAIRS)
    STARTING_ENDOWMENT_STAGE_1 = cu(2000)
    STARTING_ENDOWMENT_STAGE_2 = cu(2000) * NUM_ROUNDS

# --- Map each treatment code to (#A, #B) among 10 participants ---------------
TREATMENT_TO_COUNTS = {
    'New_Ten_Ninety':   (1, 9),  # note the original spelling is kept
    'New_Twenty_Eighty': (2, 8),
    'New_Thirty_Seventy':(3, 7),
    'New_Forty_Sixty':   (4, 6),
    'New_Fifty_Fifty':   (5, 5),
    'New_Sixty_Forty':   (6, 4),
    'New_Seventy_Thirty':(7, 3),
    'New_Eighty_Twenty': (8, 2),
    'New_Ninety_Ten':    (9, 1),
}

def counts_for_treatment(trt_idx: int) -> tuple[int, int]:
    """Return (n_A, n_B) for a given treatment index. Defaults to 5/5."""
    code = C.TREATMENT_CODES[trt_idx]
    return TREATMENT_TO_COUNTS.get(code, (5, 5))


# -----------------------------------------------------------------------------
# Models
# -----------------------------------------------------------------------------
def _get_topic_treatment_order(participant):
    if 'pair_order' not in participant.vars:
        rng = _rng_for_participant(participant)
        order = C.PAIRS.copy()
        rng.shuffle(order)                   # <‑‑ use local RNG
        participant.vars['pair_order'] = order
    return participant.vars['pair_order']

class Subsession(BaseSubsession):
    pass

def creating_session(subsession: Subsession):
    if subsession.round_number == 1:
        total_rounds = C.NUM_ROUNDS          # o len(C.PAIRS) si NO quieres incluir práctica
        endowment_stage_1 = C.STARTING_ENDOWMENT_STAGE_1
        endowment_stage_2 = C.STARTING_ENDOWMENT_STAGE_2

        for p in subsession.get_players():
            # fija el saldo inicial del jugador
            p.payoff = endowment_stage_1 + endowment_stage_2
            # guarda una copia en participant.vars para auditoría/debug
            p.participant.vars['starting_endowment_stage_1'] = endowment_stage_1
            p.participant.vars['starting_endowment_stage_2'] = endowment_stage_2

    for p in subsession.get_players():
        order = _get_topic_treatment_order(p.participant)  # list of (t_idx, trt_idx), len == len(C.PAIRS)

        # paid index: 1..len(PAIRS); 0 on practice
        er = subsession.round_number - C.PRACTICE_ROUNDS

        if er < 1:
            # practice round: don't bind a paid pair
            p.topic_idx = None
            p.treatment_idx = None
            continue

        if er > len(order):
            raise RuntimeError(
                f"Round {subsession.round_number} exceeds paid trials ({len(order)}). "
                f"Check NUM_ROUNDS={C.NUM_ROUNDS} vs PRACTICE_ROUNDS+len(PAIRS)={C.PRACTICE_ROUNDS + len(C.PAIRS)}."
            )

        t_idx, trt_idx = order[er - 1]   # 0-based into paid portion
        p.topic_idx = t_idx
        p.treatment_idx = trt_idx


class Group(BaseGroup):
    pass

########################### ADD ON ###########################
class Player(BasePlayer):
    # Personal information fields:
    age = models.IntegerField(label="What is your age?", min=18)
    gender = models.StringField(
        choices=[('M', 'Male'), ('F', 'Female'), ('I', 'Intersex'), ('N', 'Prefer not to say')],
        label="What sex were you assigned at birth?"
    )
    racial_identification = models.StringField(
        choices=[
            ('White', 'White / Caucasian'),
            ('Black', 'Black / African American'),
            ('Hispanic', 'Hispanic / Latino'),
            ('Indigenous', 'Indigenous'),
            ('Mixed', 'Mixed / Biracial'),
            ('Pacific Islander', 'Pacific Islander'),
            ('Middle Eastern', 'Middle Eastern'),
            ('Asian', 'Asian'),
            ('Arab', 'Arab'),
            ('Other', 'Other'),
        ],
        label="How do you identify racially?"
    )
    previous_experiment = models.IntegerField(
        label="Approximately how many research experiments (in economics, psychology, or similar fields) have you participated in before?",
        min=0
    )

    # Stage 1 (practice page)
    answer_practice   = models.StringField(blank=True)
    wtl_practice      = models.IntegerField(choices=list(range(1, 11)), widget=widgets.RadioSelectHorizontal, blank=True)
    jr_practice       = models.IntegerField(choices=[1, 2, 3], blank=True)


    # Stage 3 (public opinion practice)
    public_opinion_practice = models.StringField(blank=True)

    # NEW (practice):
    min_opp_punish_practice = models.IntegerField(min=0, max=10, blank=True)

    # Stage 4 (guesses practice)
    paid_cost_A_practice   = models.IntegerField(min=0, max=10, blank=True)
    paid_cost_B_practice   = models.IntegerField(min=0, max=10, blank=True)
    expr_A_from_A_practice = models.IntegerField(min=0, max=10, blank=True)
    expr_A_from_B_practice = models.IntegerField(min=0, max=10, blank=True)

    topic_idx     = models.IntegerField(blank=True)
    treatment_idx = models.IntegerField(blank=True)

    # ─── Stage-2 (decisiones reales) ─────────────────────────────────────────
    # NEW (stage 2): Willingness To Judge (Sí/No)
    wtj = models.BooleanField(
        choices=[(True, 'Yes'), (False, 'No')],
        widget=widgets.RadioSelectHorizontal,
        blank=True,
        label="Are you willing to pay a fixed cost to judge someone who expresses the opposite of your private opinion?"
    )

    # Ajuste: define choices A/B explícitamente (usado por la lógica de pagos)
    public_opinion = models.StringField(
        choices=[('Option H', 'A'), ('Option L', 'B')],
        widget=widgets.RadioSelectHorizontal,
        blank=True,
        label="What opinion would you express to the rest of your group?"
    )

    # ─── Stage-4 guesses (0–10 cada una; evita fijar 'de los 5' en la etiqueta) ─
    paid_cost_A = models.IntegerField(
        min=0, max=10, blank=True,
        label="How many with private opinion A paid the cost?"
    )
    paid_cost_B = models.IntegerField(
        min=0, max=10, blank=True,
        label="How many with private opinion B paid the cost?"
    )
    expr_A_from_A = models.IntegerField(
        min=0, max=10, blank=True,
        label="How many with private opinion A expressed A?"
    )
    expr_A_from_B = models.IntegerField(
        min=0, max=10, blank=True,
        label="How many with private opinion B expressed A?"
    )

    # ─── Variables de pago Stage 2 (se llenan al final) ──────────────────────
    # NEW (stage 2): ronda pagada, puntos/moneda y bono
    paid_round_stage2 = models.IntegerField(initial=0)
    stage2_payoff_points = models.IntegerField(initial=0)   # o CurrencyField si conviertes a dinero directo
    stage2_bonus_hit = models.BooleanField(initial=False)


# --- add StringFields dynamically for Stage 1 ---------------------------
for i in range(1, len(C.TOPIC_LABELS) + 1):
    # Answer field
    setattr(Player, f'answer_{i}', models.StringField(blank=True))
    # Willingness-To-Lie (WTL)
    setattr(
        Player,
        f"wtl_{i}",
        models.IntegerField(
            choices=list(range(1, 11)),
            widget=widgets.RadioSelectHorizontal,
        ),
    )
    # Willingness-To-Judge (WTJ)
    setattr(Player, f'wtj_{i}', models.StringField(blank=True))
    # Judgement Rule (JR)
    setattr(
        Player,
        f'jr_{i}',
        models.IntegerField(
            choices=[(1, 'Approach 1'), (2, 'Approach 2'), (3, 'Approach 3')],
            blank=True,
        ),
    )
    # Minimum Opponent Punishment threshold
    setattr(
        Player,
        f'min_opp_punish_{i}',
        models.IntegerField(min=0, max=10, blank=True),
    )


# ---------------------------------------------------------------------
# Utility functions
# ---------------------------------------------------------------------

def get_randomised_questions(participant):
    """Order of 10 topics + per-topic flip, once per participant."""
    if 'q_order' not in participant.vars:
        rng = _rng_for_participant(participant)
        order = list(range(10))
        rng.shuffle(order)
        participant.vars['q_order'] = order
        participant.vars['flip'] = [rng.choice([True, False]) for _ in order]
    return participant.vars['q_order'], participant.vars['flip']

def get_randomised_wtj(participant):
    """Order/flip for WTJ block."""
    if 'wtj_order' not in participant.vars:
        rng = _rng_for_participant(participant)
        order = list(range(10))
        rng.shuffle(order)
        participant.vars['wtj_order'] = order
        participant.vars['wtj_flip'] = [rng.choice([True, False]) for _ in order]
    return participant.vars['wtj_order'], participant.vars['wtj_flip']

def _practice_topic_config(session):
    """Return (label, (optL,optR)) for practice from session.config or constants."""
    label = session.config.get('practice_topic_label', C.PRACTICE_TOPIC_LABEL)
    opts  = session.config.get('practice_binary_options', C.PRACTICE_OPTIONS)
    # Normalize to a 2-tuple of strings
    if not isinstance(opts, (list, tuple)) or len(opts) != 2:
        opts = C.PRACTICE_OPTIONS
    return str(label), (str(opts[0]), str(opts[1]))


def practice_treatment_idx(session):
    """Resolve practice treatment code to index in C.TREATMENT_CODES."""
    code = session.config.get('practice_treatment', C.TREATMENT_CODES[0])
    try:
        return C.TREATMENT_CODES.index(code)
    except ValueError:
        return 0


def practice_left_right(player: Player):
    """
    Compute the practice topic's left/right labels with a per-participant flip
    that is *separate* from Stage 1 flips (since practice is outside the 10 topics).
    """
    label, (L, R) = _practice_topic_config(player.session)
    rng = _rng_for_participant(player.participant)
    flip = player.participant.vars.setdefault('practice_flip', rng.choice([True, False]))
    left, right = (R, L) if flip else (L, R)
    return label, left, right


def _practice_yes_no(player: Player):
    """
    Optionally flip Yes/No for the practice WTJ page, independent from real WTJ flips.
    """
    yes, no = C.YES_NO
    rng = _rng_for_participant(player.participant)
    flip = player.participant.vars.setdefault('practice_wtj_flip', rng.choice([True, False]))
    return (no, yes) if flip else (yes, no)

# --- text helper for the 3 judgment approaches ------------------------------
def approach_clause(approach: int) -> str:
    mapping = {
        1: "if the opinion they express is different from your own",
        2: "if their actual true opinion is different from your own",
        3: "if the opinion they express is different from their own true opinion",
    }
    return mapping.get(approach, mapping[1])  # default → 1

def set_stage1_payoffs(subsession: Subsession):
    """
    Para cada jugador:
    1) Sortea el tópico pagado (1..10) y parámetros de castigo (prob_punishment, opposite_opinion).
    2) Decide si miente o no según su wtl vs prob_punishment.
    3) Llama a _simulate_punishment y aplica el castigo al jugador si corresponde.
    4) Cobra cost_stage_1 al observador real *una sola vez en toda la ronda*.
    """

    players = subsession.get_players()
    cobrados = set()  # ids de observadores a los que ya se les cobró en esta ronda

    for p1 in players:
        p = p1.in_round(1)
        topic_idx = random.randint(1, 10)

        ans = getattr(p, f"answer_{topic_idx}", None)
        wtl = getattr(p, f"wtl_{topic_idx}", None)
        if ans is None:
            # Si el jugador no respondió ese tópico, pasa al siguiente.
            continue

        prob_punishment   = random.randint(0, 10)
        opposite_opinion  = random.randint(0, 10)
        options = C.BINARY_OPTIONS[topic_idx - 1]
        left_opt, right_opt = options

        # Regla: si la prob. de ser castigado es <= a su umbral wtl, dice su verdad; si no, invierte.
        if prob_punishment <= wtl:
            public_opinion = ans
        else:
            if ans == left_opt:
                public_opinion = right_opt
            elif ans == right_opt:
                public_opinion = left_opt

        # Simula castigo. Esta función YA no cobra el costo al observador.
        result = _simulate_punishment(
            player=p,
            all_players=players,
            topic_idx=topic_idx,
            prob_punishment=prob_punishment,
            opposite_opinion=opposite_opinion,
            public_opinion=public_opinion,
            punishment_stage_1=C.PUNISHMENT_STAGE1,
            cost_stage_1=C.COST_STAGE1,   # mantenemos firma aunque no se use aquí
        )

        # Si hubo observador real que castigó, se le cobra solo una vez en la ronda.
        obs = result.get('observador')
        if result.get('punisher') and (obs is not None):
            if obs.id_in_subsession not in cobrados:
                obs.payoff -= C.COST_STAGE1
                cobrados.add(obs.id_in_subsession)


    print("Stage 1 payoffs set for group.")

def _simulate_punishment(player, all_players, topic_idx, prob_punishment,
                         opposite_opinion, public_opinion,
                         punishment_stage_1, cost_stage_1):
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
    for other_c in all_players:
        other = other_c.in_round(1)
        if other.id_in_subsession == player.id_in_subsession:
            continue
        min_opp = getattr(other, f"min_opp_punish_{topic_idx}", None)
        answer_other = getattr(other, f"answer_{topic_idx}", None)
        if min_opp is None or answer_other is None:
            continue

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

        # Como salvaguarda extrema (poco probable): si aún quedó vacío, usar ficticios
        if not grupo_total:
            grupo_total = ["ficticio"] * PANEL_SIZE

    # 3) Elegir observador
    observador = random.choice(grupo_total)

    # 4) Aplicar resultado
    if observador == "ficticio":
        # Ficticio castiga: solo el jugador pierde; sin costo de observador real
        player.payoff -= punishment_stage_1
        return {'castigado': True, 'observador': None, 'punisher': True}

    # Si el observador (real) está en el bloque de castigadores, castiga
    # OJO: grupo_castigadores puede no existir si entramos al caso de ficticios directo
    if isinstance(observador, type(player)):
        # Determinar si es castigador revisando su regla respecto al jugador
        min_opp_obs = getattr(observador, f"min_opp_punish_{topic_idx}", None)
        answer_obs  = getattr(observador, f"answer_{topic_idx}", None)
        es_castigador = (min_opp_obs is not None and answer_obs is not None
                         and (opposite_opinion >= min_opp_obs)
                         and (public_opinion != answer_obs))

        if es_castigador:
            # Jugador pierde  AQUÍ
            player.payoff -= punishment_stage_1
            return {'castigado': True, 'observador': observador, 'punisher': True}
        else:
            return {'castigado': False, 'observador': observador, 'punisher': False}

    # Por seguridad, si llegara un tipo inesperado
    return {'castigado': False, 'observador': None, 'punisher': False}

########################### ADD ON ###########################
def _topic_treatment_code_for_round(player:Player,round:int):
    """Devuelve el topic_id y treatment_id de esta ronda r (Stage 2)."""
    t_idx = player.in_round(round).topic_idx
    t_code = player.in_round(round).treatment_idx
    return t_idx, t_code

def _get_round_for_topic_treatment(player:Player, topic_idx:int, treatment_idx:int):
    """Devuelve la ronda r donde el jugador tiene este (topic_idx, treatment_idx)."""
    for r in range(2, C.NUM_ROUNDS + 1):
        p_r = player.in_round(r)
        if p_r.topic_idx == topic_idx and p_r.treatment_idx == treatment_idx:
            return r
    raise ValueError(f"Player {player.id_in_subsession} has no round with topic {topic_idx} and treatment {treatment_idx}.")

def _stage1_answer(pp: Player, topic_idx: int, map_A_B: bool = True) -> str | None:
        """
        Devuelve 'A' o 'B' según la respuesta de Stage 1 del jugador pp para el tópico topic_idx.
        Supone que en Stage 1 almacenaste answer_{k} como string del par BINARY_OPTIONS[k].
        Mapea izquierda->'A', derecha->'B'. Si no encuentra, devuelve None.
        """
        k = topic_idx + 1
        field = f'answer_{k}'
        left_raw, right_raw = C.BINARY_OPTIONS[topic_idx]
        try:
            # muchas implementaciones guardan Stage1 en round 1
            p1 = pp.in_round(1)
            ans = getattr(p1, field, None)
            if not map_A_B:
                return ans
        except Exception:
            ans = None
        # Mapea a 'A'/'B'
        if ans is None:
            return None
        if ans == left_raw:
            return 'A'
        if ans == right_raw:
            return 'B'

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
    candA: list[tuple[Player, int]],
    candB: list[tuple[Player, int]],
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
        r_pp = _get_round_for_topic_treatment(pp, topic_idx, treatment_idx)  # <- llave: coincidencia tto–tema
        ab = _stage1_answer(pp, topic_idx)
        if ab == 'A':
            candA.append((pp, r_pp))
        elif ab == 'B':
            candB.append((pp, r_pp))
    # obtener composición (nA, nB) para este tratamiento
    nA, nB = counts_for_treatment(treatment_idx)
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

def _calculate_how_many_lied(group:list,option:str,type:str)->int:
    """
    Calcula el número de participantes con respuesta {option} para.
    - type == 'wtj': # de peronas dispuestas a juzgar (wtj==True)
    - type == 'public_opinion': # de personas que expresaron 'A'
    - group: lista de tuplas (Player, ronda del Player)
    - option: 'A' o 'B' (opciones mapeadas a 'A'/'B')
    Devuelve el el número de personas en el grupo que cumplen la condición.
    """
    count = 0
    for pp, r_pp in group:
        player_in_round = pp.in_round(r_pp)
        # verificar si el jugador escogió la opción dada en Stage 1 (#Preguntar# si esta respuesa 'A/B' se refiere a Stage 1 o public opinion)
        ans_mapped = _stage1_answer(pp, pp.in_round(r_pp).topic_idx)
        if type == 'wtj' and ans_mapped == option:
            if player_in_round.wtj:
                count += 1
        elif type == 'public_opinion' and ans_mapped == option:
            po = player_in_round.public_opinion
            # mappear public opinion a 'A'/'B'
            options = C.BINARY_OPTIONS[pp.in_round(r_pp).topic_idx - 1]
            left_opt, right_opt = options
            if po == left_opt:
                po_mapped = 'A'
            elif po == right_opt:
                po_mapped = 'B'
            # comparar
            if po_mapped == 'A':
                count += 1
    return count

    
########################### ADD ON ###########################
def set_stage2_payoffs(subsession):
    """
    Para CADA participante:
      1) Elige aleatoriamente una ronda r ∈ [2, C.NUM_ROUNDS].
      2) Construye GJ, GE, GH en esa ronda y aplica las reglas de pago de:
         - WillingnessToJudgeFixedCost (J)
         - ExpressYourOpinion (E)
         - HowManyLied (H)
      3) Suma puntos de Stage 2 y marca si ganó bono.
    """
    for p in subsession.get_players():
        # 1) Ronda aleatoria para Stage 2
        paid_round = random.randint(2, C.NUM_ROUNDS)
        p.paid_round_stage2 = paid_round
        topic_idx, treatment_idx = _topic_treatment_code_for_round(p, paid_round)
        # Formar grupos GJ, GE, GH
        groups = _build_groups_for_player_in_round(subsession, p, topic_idx, treatment_idx)
        GJ, GE, GH = groups['GJ'], groups['GE'], groups['GH']
        
        #### Lógica de pago para WillingnessToJudgeFixedCost_r ####
        wtj = p.in_round(paid_round).wtj
        # si wtj=Sí, extraer al azar un jugador de GJ para posible comparación
        if wtj:
            judged_set = random.choice(GJ)
            judged_player = judged_set[0]
            judged_round  = judged_set[1]   
            judged_opinion = judged_player.in_round(judged_round).public_opinion
            # si la opinion del juzgado difiere de la propia, cobrar costo y castigo
            if judged_opinion != _stage1_answer(p, topic_idx, map_A_B=False):
                p.payoff -= C.COST_STAGE_2
                judged_player.payoff -= C.PUNISHMENT_STAGE_2
        
        #### Lógica de pago para ExpressYourOpinion_r ####
        judged_opinion = p.in_round(paid_round).public_opinion
        # si la opinion expresada difiere de la propia, cobrar costo por mentir
        if judged_opinion != _stage1_answer(p, topic_idx, map_A_B=False):
            p.payoff -= C.COST_TO_LIE
        # obtener una persona del grupo
        judge_set = random.choice(GE)
        judge_player = judge_set[0]
        judge_round  = judge_set[1]
        wtj_j = judge_player.in_round(judge_round).wtj
        # si esa persona está dispuesta a juzgar y la opinión difiere, cobrar castigo
        if wtj_j:
            judge_opinion = judge_player.in_round(judge_round).public_opinion
            # si la opinion del juez difiere de la propia, cobrar costo y castigo
            if judge_opinion != judged_opinion:
                p.payoff -= C.PUNISHMENT_STAGE_2
                judge_player.payoff -= C.COST_STAGE_2
        
        #### Lógica de pago para HowManyLied_r ####
        prediction_idx = random.randint(1, 4)
        if prediction_idx == 1:
            real = _calculate_how_many_lied(GH, 'A', 'wtj')
            prediction = p.in_round(paid_round).paid_cost_A
            if real == prediction:
                p.payoff += C.BONUS_STAGE_2
        elif prediction_idx == 2:
            real = _calculate_how_many_lied(GH, 'B', 'wtj')
            prediction = p.in_round(paid_round).paid_cost_B
            if real == prediction:
                p.payoff += C.BONUS_STAGE_2
        elif prediction_idx == 3:
            real = _calculate_how_many_lied(GH, 'A', 'public_opinion')
            prediction = p.in_round(paid_round).expr_A_from_A
            if real == prediction:
                p.payoff += C.BONUS_STAGE_2
        else:  # prediction_idx == 4
            real = _calculate_how_many_lied(GH, 'B', 'public_opinion')
            prediction = p.in_round(paid_round).expr_A_from_B
            if real == prediction:
                p.payoff += C.BONUS_STAGE_2
    print("Stage 2 payoffs set for group.")

    


                

        

# -----------------------------------------------------------------------------
# Page Definitions
# -----------------------------------------------------------------------------
class PersonalInfoPage(Page):
    form_model = 'player'
    form_fields = ['age', 'gender', 'racial_identification', 'previous_experiment']
    
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

# ----------------- PRACTICE PAGES -----------------

class Practice_BinaryTopic(Page):
    form_model    = 'player'
    template_name = 'actual_exp_phase_1/BinaryQuestionsPage.html'

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    @staticmethod
    def get_form_fields(player: Player):
        return ['answer_practice', 'wtl_practice', 'min_opp_punish_practice']

    @staticmethod
    def vars_for_template(player: Player):
        topic_label, left, right = practice_left_right(player)
        item = dict(
            index     = 1,
            question  = topic_label,
            ans_field = 'answer_practice',
            left      = left,
            right     = right,
            wtl_field = 'wtl_practice',
            thr_field = 'min_opp_punish_practice',   # NEW
        )
        return dict(
            items=[item],
            scale_prob  = range(1, 11),
            scale_opp   = range(0, 11),              # NEW (0..10)
            cost_stage_1 = C.COST_STAGE1,           # NEW
            show_help = True,
            is_practice=True,
        )

    @staticmethod
    def error_message(player: Player, values):
        _, left, right = practice_left_right(player)
        allowed = {left, right}
        if values.get('answer_practice') not in allowed:
            return "Please select one of the two options."
        if values.get('wtl_practice') is None:
            return "Please choose a maximum punishment probability."
        v = values.get('min_opp_punish_practice')
        if v is None or not (0 <= v <= 10):
            return "Please choose a number between 0 and 10."

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        # Fix the practice judgment rule to "Approach 1" without raising on None
        if player.field_maybe_none('jr_practice') in (None, 0):
            player.jr_practice = 1


class Practice_TopicTreatment(Page):
    template_name = 'actual_exp_phase_1/TopicTreatment.html'
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    @staticmethod
    def vars_for_template(player: Player):
        topic_label, left, right = practice_left_right(player)
        trt_idx = practice_treatment_idx(player.session)
        n_A, n_B = counts_for_treatment(trt_idx)   # NEW
        return dict(
            topic         = topic_label,
            treatment_png = f"experiment/{C.TREATMENT_CODES[trt_idx]}.png",
            left          = left,
            right         = right,
            n_A           = n_A,   # NEW
            n_B           = n_B,   # NEW
            is_practice   = True,
        )


class Practice_WTJ(Page):
    form_model = 'player'
    form_fields = ['wtj']
    template_name = 'actual_exp_phase_1/WillingnessToJudgeFixedCost.html'

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    @staticmethod
    def error_message(player: Player, values):
        v = values.get('wtj')
        if not isinstance(v, bool):
            return "Please choose Yes or No."

    @staticmethod
    def vars_for_template(player: Player):
        topic_label, topic_left, topic_right = practice_left_right(player)
        yes, no = _practice_yes_no(player)
        trt_idx = practice_treatment_idx(player.session)
        n_A, n_B = counts_for_treatment(trt_idx)

        # NEW:
        jr_approach = player.jr_practice
        jr_clause   = approach_clause(jr_approach)

        return dict(
            topic          = topic_label,
            topic_left     = topic_left,
            topic_right    = topic_right,
            yes_label      = yes,
            no_label       = no,
            cost_stage_2   = C.COST_STAGE_2,
            treatment_png  = f"experiment/{C.TREATMENT_CODES[trt_idx]}.png",
            round_number   = player.round_number,
            total_rounds   = C.NUM_ROUNDS,
            is_practice    = True,
            n_A            = n_A,
            n_B            = n_B,

            # NEW -> used by the template
            jr_approach    = jr_approach,
            jr_clause      = jr_clause,
        )


class Practice_ExpressYourOpinion(Page):
    form_model  = 'player'
    form_fields = ['public_opinion']   # <— match the template’s fixed name
    template_name = 'actual_exp_phase_1/ExpressYourOpinion.html'

    @staticmethod
    def is_displayed(player: Player):          # <— you were missing this
        return player.round_number == 1

    @staticmethod
    def error_message(player: Player, values):
        _, left, right = practice_left_right(player)
        v = values.get('public_opinion')
        if v not in {left, right}:
            return "Please select one of the two opinions."


    @staticmethod
    def vars_for_template(player: Player):
        topic_label, topic_left, topic_right = practice_left_right(player)
        rng = _rng_for_participant(player.participant)
        flip = player.participant.vars.setdefault('public_flip_practice', rng.choice([True, False]))
        left, right = (topic_right, topic_left) if flip else (topic_left, topic_right)
        trt_idx = practice_treatment_idx(player.session)
        n_A, n_B = counts_for_treatment(trt_idx)   # NEW
        return dict(
            topic         = C.PRACTICE_TOPIC_LABEL,
            treatment_png = f"experiment/{C.TREATMENT_CODES[trt_idx]}.png",
            topic_left    = topic_left,
            topic_right   = topic_right,
            left          = left,
            right         = right,
            is_practice   = True,
            n_A           = n_A,  # NEW
            n_B           = n_B,  # NEW
        )

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        # copy to the dedicated practice field, then clear the real one
        player.public_opinion_practice = player.public_opinion
        player.public_opinion = None


class Practice_HowManyLied(Page):
    form_model  = 'player'
    form_fields = [
        'paid_cost_A_practice',
        'paid_cost_B_practice',
        'expr_A_from_A_practice',
        'expr_A_from_B_practice',
    ]
    template_name = 'actual_exp_phase_1/HowManyLied.html'

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    @staticmethod
    def vars_for_template(player: Player):
        topic_label, topic_left, topic_right = practice_left_right(player)
        trt_idx = practice_treatment_idx(player.session)
        n_A, n_B = counts_for_treatment(trt_idx)   # NEW
        items = [
            dict(index=1, field_name='paid_cost_A_practice',
                 prompt=f'How many out of the <strong>{n_A}</strong> with opinion <strong>{topic_left}</strong> decided to pay the cost to punish?',
                 max=n_A),
            dict(index=2, field_name='paid_cost_B_practice',
                 prompt=f'How many out of the <strong>{n_B}</strong> with opinion <strong>{topic_right}</strong> decided to pay the cost to punish?',
                 max=n_B),
            dict(index=3, field_name='expr_A_from_A_practice',
                 prompt=(f'How many out of the <strong>{n_A}</strong> with opinion <strong>{topic_left}</strong> '
                         f'expressed <strong>{topic_left}</strong>?'),
                 max=n_A),
            dict(index=4, field_name='expr_A_from_B_practice',
                 prompt=(f'How many out of the <strong>{n_B}</strong> with opinion <strong>{topic_right}</strong> '
                         f'expressed <strong>{topic_left}</strong>?'),
                 max=n_B),
        ]
        return dict(
            topic         = topic_label,
            treatment_png = f"experiment/{C.TREATMENT_CODES[trt_idx]}.png",
            items         = items,
            topic_left    = topic_left,
            topic_right   = topic_right,
            is_practice   = True,
            n_A           = n_A,   # NEW
            n_B           = n_B,   # NEW
        )
    @staticmethod
    def error_message(player: Player, values):
        trt_idx = practice_treatment_idx(player.session)
        n_A, n_B = counts_for_treatment(trt_idx)
        errs = {}

        def check(name, max_allowed):
            v = values.get(name)
            if v is None:
                errs[name] = "Please enter a number."
            elif not (0 <= v <= max_allowed):
                errs[name] = f"Please enter a number between 0 and {max_allowed}."

        check('paid_cost_A_practice',   n_A)
        check('paid_cost_B_practice',   n_B)
        check('expr_A_from_A_practice', n_A)
        check('expr_A_from_B_practice', n_B)

        return errs or None


# --- helper: nth topic for Stage 1 -------------------------------------------
def _stage1_topic(player: Player, n: int):
    """
    Return (q_idx, flip) for the n-th topic in this participant's Stage-1 order.
    n is 1-based (1..10).
    """
    q_order, flips = get_randomised_questions(player.participant)
    q_idx = q_order[n - 1]
    flip  = flips[n - 1]
    return q_idx, flip

# --- factory for the 10 per-topic pages (still shown only in round 1) --------
def make_binary_topic_page(n: int):
    class _BinaryTopicPage(Page):
        form_model    = 'player'
        template_name = 'actual_exp_phase_1/BinaryQuestionsPage.html'

        @staticmethod
        def is_displayed(player: Player):
            return player.round_number == 1

        @staticmethod
        def get_form_fields(player: Player):
            q_idx, _ = _stage1_topic(player, n)
            return [
                f'answer_{q_idx + 1}',
                f'wtl_{q_idx + 1}',
                f'min_opp_punish_{q_idx + 1}',  # NEW
            ]


        @staticmethod
        def vars_for_template(player: Player):
            q_idx, flip = _stage1_topic(player, n)
            left, right = C.BINARY_OPTIONS[q_idx]
            if flip:
                left, right = right, left

            item = dict(
                index     = n,
                question  = C.TOPIC_LABELS[q_idx],
                ans_field = f'answer_{q_idx + 1}',
                left      = left,
                right     = right,
                wtl_field = f'wtl_{q_idx + 1}',
                thr_field = f'min_opp_punish_{q_idx + 1}',   # NEW
            )
            return dict(
                items=[item],
                scale_prob  = range(1, 11),
                scale_opp   = range(0, 11),                  # NEW
                cost_stage_1 = C.COST_STAGE1,               # NEW                     # (unused by the new Q3; harmless)
                show_help = (n == 1),
            )

        @staticmethod
        def error_message(player: Player, values):
            q_idx, _ = _stage1_topic(player, n)
            allowed = set(C.BINARY_OPTIONS[q_idx])
            ans = values.get(f'answer_{q_idx + 1}')
            if ans not in allowed:
                return "Please select one of the two options."

            wtl = values.get(f'wtl_{q_idx + 1}')
            if wtl is None:
                return "Please choose a maximum punishment probability."

            thr = values.get(f'min_opp_punish_{q_idx + 1}')
            if thr is None or not (0 <= thr <= 10):
                return "Please choose a number between 0 and 10."
        
        @staticmethod
        def before_next_page(player: Player, timeout_happened):
            q_idx, _ = _stage1_topic(player, n)
            jr_field = f'jr_{q_idx + 1}'
            val = player.field_maybe_none(jr_field)
            if val in (None, 0):
                setattr(player, jr_field, 1)




    _BinaryTopicPage.__name__ = f'BinaryTopic_{n}'
    return _BinaryTopicPage

# Create and register 10 classes: BinaryTopic_1 .. BinaryTopic_10
BINARY_TOPIC_PAGES = []
for i in range(1, len(C.TOPIC_LABELS) + 1):
    cls = make_binary_topic_page(i)
    globals()[cls.__name__] = cls
    BINARY_TOPIC_PAGES.append(cls)

class TopicTreatment(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number >= 2

    @staticmethod
    def vars_for_template(player: Player):
        topic       = C.TOPIC_LABELS[player.topic_idx]
        trt_code    = C.TREATMENT_CODES[player.treatment_idx]
        png_path    = f"experiment/{trt_code}.png"

        left, right = C.BINARY_OPTIONS[player.topic_idx]

        # Keep orientation from Stage 1
        q_order, flips = get_randomised_questions(player.participant)
        try:
            pos = q_order.index(player.topic_idx)
            if flips[pos]:
                left, right = right, left
        except ValueError:
            pass

        # NEW: dynamic A/B counts from treatment
        n_A, n_B = counts_for_treatment(player.treatment_idx)

        return dict(
            topic         = topic,
            treatment_png = png_path,
            left          = left,
            right         = right,
            n_A           = n_A,     # NEW
            n_B           = n_B,     # NEW
            is_practice   = False,
        )

class WillingnessToJudgeFixedCost(Page):
    form_model = 'player'
    form_fields = ['wtj']

    @staticmethod
    def is_displayed(player):
        return player.round_number >= 2


    @staticmethod
    def error_message(player: Player, values):
        v = values.get('wtj')
        if not isinstance(v, bool):
            return "Please choose Yes or No."

    @staticmethod
    def vars_for_template(player):
        topic_left, topic_right = C.BINARY_OPTIONS[player.topic_idx]

        # keep Stage-1 orientation
        q_order, flips_q = get_randomised_questions(player.participant)
        pos_topic = q_order.index(player.topic_idx)
        if flips_q[pos_topic]:
            topic_left, topic_right = topic_right, topic_left

        yes, no = C.YES_NO
        order, flips_w = get_randomised_wtj(player.participant)
        pos_wtj = order.index(player.topic_idx)
        if flips_w[pos_wtj]:
            yes, no = no, yes

        # NEW: dynamic A/B counts
        n_A, n_B = counts_for_treatment(player.treatment_idx)

        jr_field = f'jr_{player.topic_idx + 1}'
        jr_approach = player.field_maybe_none(jr_field) or 1
        jr_clause = approach_clause(jr_approach)


        return dict(
            topic          = C.TOPIC_LABELS[player.topic_idx],
            topic_left     = topic_left,
            topic_right    = topic_right,
            yes_label      = yes,
            no_label       = no,
            cost_stage_2   = C.COST_STAGE_2,
            treatment_png  = f"experiment/{C.TREATMENT_CODES[player.treatment_idx]}.png",
            round_number   = player.round_number,
            total_rounds   = C.NUM_ROUNDS,
            is_practice    = False,
            n_A            = n_A,
            n_B            = n_B,

            # NEW -> used by the template
            jr_approach    = jr_approach,
            jr_clause      = jr_clause,
        )

class ExpressYourOpinion(Page):
    form_model = 'player'
    form_fields = ['public_opinion']

    @staticmethod
    def is_displayed(player):
        return player.round_number >= 2

    @staticmethod
    def error_message(player: Player, values):
        left, right = C.BINARY_OPTIONS[player.topic_idx]
        v = values.get('public_opinion')
        if v not in {left, right}:
            return "Please select one of the two opinions."

    @staticmethod
    def vars_for_template(player: Player):
        topic_left, topic_right = C.BINARY_OPTIONS[player.topic_idx]

        # keep Stage-1 orientation
        q_order, flips_q = get_randomised_questions(player.participant)
        pos_topic = q_order.index(player.topic_idx)
        if flips_q[pos_topic]:
            topic_left, topic_right = topic_right, topic_left

        # per-round UI L/R flip (does not change A/B meaning)
        rng   = _rng_for_participant(player.participant)
        flips = player.participant.vars.setdefault('public_flip', {})
        if player.round_number not in flips:
            flips[player.round_number] = rng.choice([True, False])

        left, right = (topic_left, topic_right)
        if flips[player.round_number]:
            left, right = right, left

        # NEW: dynamic A/B counts
        n_A, n_B = counts_for_treatment(player.treatment_idx)

        return dict(
            topic          = C.TOPIC_LABELS[player.topic_idx],
            treatment_png  = f"experiment/{C.TREATMENT_CODES[player.treatment_idx]}.png",
            topic_left     = topic_left,
            topic_right    = topic_right,
            left           = left,
            right          = right,
            is_practice    = False,
            n_A            = n_A,   # NEW
            n_B            = n_B,   # NEW
        )

class HowManyLied(Page):
    form_model  = 'player'
    form_fields = ['paid_cost_A', 'paid_cost_B', 'expr_A_from_A', 'expr_A_from_B']

    @staticmethod
    def is_displayed(player):
        return player.round_number >= 2

    @staticmethod
    def vars_for_template(player: Player):
        topic_left, topic_right = C.BINARY_OPTIONS[player.topic_idx]

        # keep Stage-1 orientation
        q_order, flips_q = get_randomised_questions(player.participant)
        pos_topic = q_order.index(player.topic_idx)
        if flips_q[pos_topic]:
            topic_left, topic_right = topic_right, topic_left

        topic         = C.TOPIC_LABELS[player.topic_idx]
        treatment_png = f"experiment/{C.TREATMENT_CODES[player.treatment_idx]}.png"

        # NEW: dynamic A/B counts
        n_A, n_B = counts_for_treatment(player.treatment_idx)

        items = [
            dict(
                index       = 1,
                field_name  = 'paid_cost_A',
                prompt      = f'How many out of the <strong>{n_A}</strong> with opinion <strong>{topic_left}</strong> decided to pay the cost to punish?',
                max         = n_A,   # NEW
            ),
            dict(
                index       = 2,
                field_name  = 'paid_cost_B',
                prompt      = f'How many out of the <strong>{n_B}</strong> with opinion <strong>{topic_right}</strong> decided to pay the cost to punish?',
                max         = n_B,   # NEW
            ),
            dict(
                index       = 3,
                field_name  = 'expr_A_from_A',
                prompt      = (f'How many out of the <strong>{n_A}</strong> with opinion <strong>{topic_left}</strong> '
                               f'expressed <strong>{topic_left}</strong>?'),
                max         = n_A,   # NEW
            ),
            dict(
                index       = 4,
                field_name  = 'expr_A_from_B',
                prompt      = (f'How many out of the <strong>{n_B}</strong> with opinion <strong>{topic_right}</strong> '
                               f'expressed <strong>{topic_left}</strong>?'),
                max         = n_B,   # NEW
            ),
        ]

        return dict(
            topic         = topic,
            treatment_png = treatment_png,
            items         = items,
            topic_left    = topic_left,
            topic_right   = topic_right,
            n_A           = n_A,   # NEW
            n_B           = n_B,   # NEW
            is_practice   = False,
        )
    @staticmethod
    def error_message(player: Player, values):
        n_A, n_B = counts_for_treatment(player.treatment_idx)
        errs = {}

        def check(name, max_allowed):
            v = values.get(name)
            if v is None:
                errs[name] = "Please enter a number."
            elif not (0 <= v <= max_allowed):
                errs[name] = f"Please enter a number between 0 and {max_allowed}."

        check('paid_cost_A',   n_A)
        check('paid_cost_B',   n_B)
        check('expr_A_from_A', n_A)
        check('expr_A_from_B', n_B)

        return errs or None

class ThankYouPage(Page):
    @staticmethod
    def is_displayed(player: Player) -> bool:
        return player.round_number == C.NUM_ROUNDS

    @staticmethod
    def vars_for_template(player: Player) -> dict:
        return {}


class PaymentWaitPage(WaitPage):
    wait_for_all_groups = True
    @staticmethod
    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS

    # Ejecuta la lógica cuando todos llegaron
    @staticmethod
    def after_all_players_arrive(subsession):
        set_stage1_payoffs(subsession)

########################### ADD ON ###########################
class FinalPaymentWaitPage(WaitPage):
    wait_for_all_groups = True

    @staticmethod
    def is_displayed(player: Player):
        # Al terminar TODAS las rondas
        return player.round_number == C.NUM_ROUNDS

    @staticmethod
    def after_all_players_arrive(subsession: Subsession):
        set_stage2_payoffs(subsession)


# -----------------------------------------------------------------------------
# Page Sequence
# -----------------------------------------------------------------------------
page_sequence = [
    PersonalInfoPage,

    # ----- PRACTICE (one topic, once) -----
    Practice_BinaryTopic,
    Practice_TopicTreatment,
    Practice_WTJ,
    Practice_ExpressYourOpinion,
    Practice_HowManyLied,

] + BINARY_TOPIC_PAGES + [
    TopicTreatment,
    WillingnessToJudgeFixedCost,
    ExpressYourOpinion,
    HowManyLied,
    ThankYouPage,
    PaymentWaitPage,
    FinalPaymentWaitPage
]