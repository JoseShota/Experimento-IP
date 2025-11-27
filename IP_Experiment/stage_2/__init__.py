import secrets
import random
from otree.api import *
from common.params import TOPIC_LABELS, TREATMENT_CODES, PRACTICE_ROUNDS, TREATMENT_TO_COUNTS, BINARY_OPTIONS

##############################
# Otree Setup
class C(BaseConstants):
    NAME_IN_URL = 'stage_2_separated'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = PRACTICE_ROUNDS + len(TOPIC_LABELS) * len(TREATMENT_CODES)


class Subsession(BaseSubsession):
    pass


def creating_session(subsession: Subsession):
    # 1) Solo en la primera ronda, deriva todo
    if subsession.round_number == 1:
        pairs = [(t_idx, trt_idx)
                 for t_idx in range(len(TOPIC_LABELS))
                 for trt_idx in range(len(TREATMENT_CODES))]
        subsession.session.vars['PAIRS'] = pairs
        subsession.session.vars['NUM_ROUNDS_S2'] = PRACTICE_ROUNDS + len(pairs)

    # 2) Para **todas** las rondas, asigna topic/treatment al Player
    for p in subsession.get_players():
        # Tu función que devuelve el orden (lista de pares) por participante
        order = _get_topic_treatment_order(p.participant)  # list[(t_idx, trt_idx)]

        practice = PRACTICE_ROUNDS
        er = subsession.round_number - practice  # índice pagado (1..N); 0 -> práctica

        if er < 1:
            # Ronda de práctica: no asigna par pagado
            p.topic_idx = None
            p.treatment_idx = None
            continue

        if er > len(order):
            total_paid = len(order)
            raise RuntimeError(
                f"Round {subsession.round_number} exceeds paid trials ({total_paid}). "
                f"Check NUM_ROUNDS={C.NUM_ROUNDS} vs PRACTICE_ROUNDS+len(pairs)={practice + total_paid}."
            )

        t_idx, trt_idx = order[er - 1]  # 0-based dentro de la parte pagada
        p.topic_idx = t_idx
        p.treatment_idx = trt_idx

    # asignar que sí jugó stage 2
    if subsession.round_number == C.NUM_ROUNDS:
        for p in subsession.get_players():
            p.participant.vars['played_stage_2'] = True


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    # topic and treatment indices for the current round
    topic_idx = models.IntegerField(blank=True)
    treatment_idx = models.IntegerField(blank=True)
    # fields
    wtj = models.BooleanField(
        choices=[(True, 'Yes'), (False, 'No')],
        widget=widgets.RadioSelectHorizontal,
        blank=True,
        label="Are you willing to pay a fixed cost to judge someone who expresses the opposite of your private opinion?"
    )
    public_opinion = models.StringField(
        choices=[('A', 'Option A'), ('B', 'Option B')],
        widget=widgets.RadioSelectHorizontal,
        blank=True,
        label="What opinion would you express to the rest of your group?"
    )
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


##############################
# Utility functions
def _rng_for_participant(participant):
    if 'rng' not in participant.vars:
        seed = secrets.randbits(64)  # 64 bits of OS entropy
        participant.vars['rng'] = random.Random(seed)
    return participant.vars['rng']


def _get_topic_treatment_order(participant):
    """Return a shuffled list of (topic_idx, treatment_idx) pairs for this participant."""
    if 'pair_order' not in participant.vars:
        rng = _rng_for_participant(participant)

        # Obtener los pairs globales guardados en session.vars
        pairs = participant.session.vars.get('PAIRS')
        if pairs is None:
            raise RuntimeError("PAIRS not found in session.vars — asegúrate de que creating_session lo haya guardado.")

        # Hacer copia para no mutar la lista global
        order = pairs.copy()
        rng.shuffle(order)
        participant.vars['pair_order'] = order

    return participant.vars['pair_order']


def counts_for_treatment(trt_idx: int) -> tuple[int, int]:
    """Return (n_A, n_B) for a given treatment index. Defaults to 5/5."""
    code = TREATMENT_CODES[trt_idx]
    return TREATMENT_TO_COUNTS.get(code, (5, 5))


def get_randomised_questions(participant):
    """Order of 10 topics + per-topic flip, once per participant."""
    if 'q_order' not in participant.vars:
        rng = _rng_for_participant(participant)
        order = list(range(10))
        rng.shuffle(order)
        participant.vars['q_order'] = order
        participant.vars['flip'] = [rng.choice([True, False]) for _ in order]
    return participant.vars['q_order'], participant.vars['flip']


## save data participant level functions
def _topic_key_from_idx(topic_idx: int) -> str:
    # Si topic_idx es 0-based en tus listas, esto produce 'topic_1', 'topic_2', ...
    return f"topic_{topic_idx}"


def _treatment_key(treatment_idx: int) -> str:
    # Si treatment_idx ya es 1-based, elimina el +1 donde lo uses abajo.
    return f"treatment_{treatment_idx}"


def _ensure_topic_dict(pvars: dict, topic_key: str) -> dict:
    return pvars.setdefault(topic_key, {})


def _ensure_treatment_dict(topic_dict: dict, treatment_key: str) -> dict:
    return topic_dict.setdefault(treatment_key, {})


# Practice utilities
def practice_left_right():
    return "Emmanuel o Mijares", "Emmanuel", "Mijares"


def practice_treatment_idx(session):
    """Resolve practice treatment code to index in C.TREATMENT_CODES."""
    code = session.config.get('practice_treatment', TREATMENT_CODES[0])
    try:
        return TREATMENT_CODES.index(code)
    except ValueError:
        return 0


##############################
# PAGES
## Practice Pages
class Practice_TopicTreatment(Page):
    template_name = 'stage_2/TopicTreatment.html'
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    @staticmethod
    def vars_for_template(player: Player):
        topic_label, left, right = practice_left_right()
        trt_idx = practice_treatment_idx(player.session)
        n_A, n_B = counts_for_treatment(trt_idx)   # NEW
        return dict(
            topic         = topic_label,
            treatment_png = f"experiment/{TREATMENT_CODES[trt_idx]}.png",
            left          = left,
            right         = right,
            n_A           = n_A,   # NEW
            n_B           = n_B,   # NEW
            is_practice   = True,
        )


class Practice_WTJ(Page):
    form_model = 'player'
    form_fields = ['wtj']
    template_name = 'stage_2/WillingnessToJudgeFixedCost.html'

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
        topic_label, topic_left, topic_right = practice_left_right()
        trt_idx = practice_treatment_idx(player.session)
        n_A, n_B = counts_for_treatment(trt_idx)
        cfg = player.session.config
        cost_stage_2 = cu(cfg['COST_STAGE_2'])
        punishment_stage_2 = cu(cfg['PUNISHMENT_STAGE_2'])
        return dict(
            topic          = topic_label,
            topic_left     = topic_left,
            topic_right    = topic_right,
            cost_stage_2   = cost_stage_2,
            treatment_png  = f"experiment/{TREATMENT_CODES[trt_idx]}.png",
            is_practice    = True,
            n_A            = n_A,
            n_B            = n_B,
            punishment_stage_2 = punishment_stage_2
        )


class Practice_ExpressYourOpinion(Page):
    form_model  = 'player'
    form_fields = ['public_opinion']   # <— match the template’s fixed name
    template_name = 'stage_2/ExpressYourOpinion.html'

    @staticmethod
    def is_displayed(player: Player):          # <— you were missing this
        return player.round_number == 1

    @staticmethod
    def error_message(player: Player, values):
        v = values.get('public_opinion')
        if v not in {'A', 'B'}:
            return "Please select one of the two opinions."


    @staticmethod
    def vars_for_template(player: Player):
        topic_label, topic_left, topic_right = practice_left_right()
        left, right = "A", "B"
        trt_idx = practice_treatment_idx(player.session)
        n_A, n_B = counts_for_treatment(trt_idx)   # NEW
        return dict(
            topic         = topic_label,
            treatment_png = f"experiment/{TREATMENT_CODES[trt_idx]}.png",
            topic_left    = topic_left,
            topic_right   = topic_right,
            left          = left,
            right         = right,
            is_practice   = True,
            n_A           = n_A,  # NEW
            n_B           = n_B,  # NEW
        )


class Practice_HowManyLied(Page):
    form_model  = 'player'
    form_fields = ['paid_cost_A', 'paid_cost_B', 'expr_A_from_A', 'expr_A_from_B']
    template_name = 'stage_2/HowManyLied.html'

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    @staticmethod
    def vars_for_template(player: Player):
        topic_label, topic_left, topic_right = practice_left_right()
        trt_idx = practice_treatment_idx(player.session)
        n_A, n_B = counts_for_treatment(trt_idx)   # NEW
        items = [
            dict(index=1, field_name='paid_cost_A',
                 prompt=f'How many out of the <strong>{n_A}</strong> with opinion <strong>{topic_left}</strong> decided to pay the cost to punish?',
                 max=n_A),
            dict(index=2, field_name='paid_cost_B',
                 prompt=f'How many out of the <strong>{n_B}</strong> with opinion <strong>{topic_right}</strong> decided to pay the cost to punish?',
                 max=n_B),
            dict(index=3, field_name='expr_A_from_A',
                 prompt=(f'How many out of the <strong>{n_A}</strong> with opinion <strong>{topic_left}</strong> '
                         f'expressed <strong>{topic_left}</strong>?'),
                 max=n_A),
            dict(index=4, field_name='expr_A_from_B',
                 prompt=(f'How many out of the <strong>{n_B}</strong> with opinion <strong>{topic_right}</strong> '
                         f'expressed <strong>{topic_left}</strong>?'),
                 max=n_B),
        ]
        return dict(
            topic         = topic_label,
            treatment_png = f"experiment/{TREATMENT_CODES[trt_idx]}.png",
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

        check('paid_cost_A',   n_A)
        check('paid_cost_B',   n_B)
        check('expr_A_from_A', n_A)
        check('expr_A_from_B', n_B)

        return errs or None

## Actual Experiment Pages
class TopicTreatment(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number >= 2

    @staticmethod
    def vars_for_template(player: Player):
        topic       = TOPIC_LABELS[player.topic_idx]
        trt_code    = TREATMENT_CODES[player.treatment_idx]
        png_path    = f"experiment/{trt_code}.png"

        left, right = BINARY_OPTIONS[player.topic_idx]

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
        topic_left, topic_right = BINARY_OPTIONS[player.topic_idx]

        # keep Stage-1 orientation
        q_order, flips_q = get_randomised_questions(player.participant)
        pos_topic = q_order.index(player.topic_idx)
        if flips_q[pos_topic]:
            topic_left, topic_right = topic_right, topic_left

        # NEW: dynamic A/B counts
        n_A, n_B = counts_for_treatment(player.treatment_idx)
        cfg = player.session.config
        cost_stage_2 = cu(cfg['COST_STAGE_2'])
        punishment_stage_2 = cu(cfg['PUNISHMENT_STAGE_2'])

        return dict(
            topic          = TOPIC_LABELS[player.topic_idx],
            topic_left     = topic_left,
            topic_right    = topic_right,
            cost_stage_2   = cost_stage_2,
            treatment_png  = f"experiment/{TREATMENT_CODES[player.treatment_idx]}.png",
            round_number   = player.round_number,
            total_rounds   = C.NUM_ROUNDS,
            is_practice    = False,
            n_A            = n_A,
            n_B            = n_B,
            punishment_stage_2 = punishment_stage_2
        )


    def before_next_page(player, timeout_happened):
        p = player
        topic_key     = _topic_key_from_idx(p.topic_idx)
        treatment_key = _treatment_key(p.treatment_idx)

        topic_dict     = _ensure_topic_dict(p.participant.vars, topic_key)
        treatment_dict = _ensure_treatment_dict(topic_dict, treatment_key)

        treatment_dict['wtj'] = bool(p.wtj)


class ExpressYourOpinion(Page):
    form_model = 'player'
    form_fields = ['public_opinion']

    @staticmethod
    def is_displayed(player):
        return player.round_number >= 2

    @staticmethod
    def error_message(player: Player, values):
        v = values.get('public_opinion')
        if v not in {'A', 'B'}:
            return "Please select one of the two opinions."

    @staticmethod
    def vars_for_template(player: Player):
        topic_left, topic_right = BINARY_OPTIONS[player.topic_idx]

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

        left, right = ("A", "B")
        if flips[player.round_number]:
            left, right = right, left

        # NEW: dynamic A/B counts
        n_A, n_B = counts_for_treatment(player.treatment_idx)

        return dict(
            topic          = TOPIC_LABELS[player.topic_idx],
            treatment_png  = f"experiment/{TREATMENT_CODES[player.treatment_idx]}.png",
            topic_left     = topic_left,
            topic_right    = topic_right,
            left           = left,
            right          = right,
            is_practice    = False,
            n_A            = n_A,
            n_B            = n_B,
        )

    def before_next_page(player, timeout_happened):
        p = player
        topic_key     = _topic_key_from_idx(p.topic_idx)
        treatment_key = _treatment_key(p.treatment_idx)

        topic_dict     = _ensure_topic_dict(p.participant.vars, topic_key)
        treatment_dict = _ensure_treatment_dict(topic_dict, treatment_key)

        treatment_dict['public_opinion'] = p.public_opinion  # 'A' o 'B'


class HowManyLied(Page):
    form_model  = 'player'
    form_fields = ['paid_cost_A', 'paid_cost_B', 'expr_A_from_A', 'expr_A_from_B']

    @staticmethod
    def is_displayed(player):
        return player.round_number >= 2

    @staticmethod
    def vars_for_template(player: Player):
        topic_left, topic_right = BINARY_OPTIONS[player.topic_idx]

        # keep Stage-1 orientation
        q_order, flips_q = get_randomised_questions(player.participant)
        pos_topic = q_order.index(player.topic_idx)
        if flips_q[pos_topic]:
            topic_left, topic_right = topic_right, topic_left

        topic         = TOPIC_LABELS[player.topic_idx]
        treatment_png = f"experiment/{TREATMENT_CODES[player.treatment_idx]}.png"

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
    
    def before_next_page(player, timeout_happened):
        p = player
        topic_key     = _topic_key_from_idx(p.topic_idx)
        treatment_key = _treatment_key(p.treatment_idx)

        topic_dict     = _ensure_topic_dict(p.participant.vars, topic_key)
        treatment_dict = _ensure_treatment_dict(topic_dict, treatment_key)

        # Guarda enteros (o float si así lo modelaste):
        treatment_dict['paid_cost_A']   = int(p.paid_cost_A)
        treatment_dict['paid_cost_B']   = int(p.paid_cost_B)
        treatment_dict['expr_A_from_A'] = int(p.expr_A_from_A)
        treatment_dict['expr_A_from_B'] = int(p.expr_A_from_B)


class ThankYouPage(Page):
    @staticmethod
    def is_displayed(player: Player) -> bool:
        return player.round_number == C.NUM_ROUNDS

    @staticmethod
    def vars_for_template(player: Player) -> dict:
        return {}


page_sequence = [
    Practice_TopicTreatment,
    Practice_WTJ,
    Practice_ExpressYourOpinion,
    Practice_HowManyLied,
    TopicTreatment,
    WillingnessToJudgeFixedCost,
    ExpressYourOpinion,
    HowManyLied,
    ThankYouPage,
]
