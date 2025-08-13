from __future__ import annotations
import random
import secrets
from otree.api import *


def _rng_for_participant(participant):
    if 'rng' not in participant.vars:
        seed = secrets.randbits(64)          # 64 bits of OS entropy
        participant.vars['rng'] = random.Random(seed)
    return participant.vars['rng']


# -----------------------------------------------------------------------------
# Module-level constants
# -----------------------------------------------------------------------------

class C(BaseConstants):
    NAME_IN_URL = 'actual_exp_phase_1'
    PLAYERS_PER_GROUP = None

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

# Willingness to judge fixed cost and maximum cost
    COST_X = 'x'            # replace later with cu(10) or similar
    YES_NO = ('Yes, I am willing to pay x to make the decision', 'No, I am not willing to pay x to make the decision')  # canonical label pair
    MAX_WTP = 20          # numeric ceiling for the slider (dollars)

# Treatment codes for the experiment
    TREATMENT_CODES = [
        'N_Fifty_Fifty',
        'N_Seventy_Thirty',
        'N_Thirty_Seventy',
    ]

    # ---------- derived combinations ----------
    PAIRS = []
    for t_idx in range(len(TOPIC_LABELS)):
        for trt_idx in range(len(TREATMENT_CODES)):
            PAIRS.append((t_idx, trt_idx))

    NUM_ROUNDS = len(PAIRS)


# -----------------------------------------------------------------------------
# Models
# -----------------------------------------------------------------------------



class Subsession(BaseSubsession):
    def creating_session(subsession):
        for p in subsession.get_players():
            _get_topic_treatment_order(p.participant)   # ensures it exists


class Group(BaseGroup):
    pass

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

    topic_idx     = models.IntegerField()
    treatment_idx = models.IntegerField()

    # Judgment fields based on the two binary options of the current topic
    judge_first = models.StringField(
        choices=[('Give', 'Give 20 dollars'), ('Take', 'Take 20 dollars')],
        label='',
        blank=True,
    )

    judge_second = models.StringField(
        choices=[('Give', 'Give 20 dollars'), ('Take', 'Take 20 dollars')],
        label='',
        blank=True,
    )

    public_opinion = models.StringField(
        label="What opinion would you express to the rest of your group?"
    )

    paid_cost_A = models.IntegerField(min=0, max=5, blank=True,
                                label="How many of the 5 with opinion A paid the cost?")
    paid_cost_B = models.IntegerField(min=0, max=5, blank=True,
                                label="How many of the 5 with opinion B paid the cost?")
    expr_A_from_A = models.IntegerField(min=0, max=5, blank=True,
                                label="How many of the 5 with opinion A expressed A?")
    expr_A_from_B = models.IntegerField(min=0, max=5, blank=True,
                                label="How many of the 5 with opinion B expressed A?")



# --- add 10 StringFields dynamically ---------------------------
for i in range(1, 11):
    setattr(Player, f'answer_{i}', models.StringField(blank=True))

# --- add 10 WTJ fields dynamically -------------
for i in range(1, 11):
    setattr(Player, f'wtj_{i}', models.StringField(blank=True))

# --- add 10 IntegerFields for maximum WTP --------------------
for i in range(1, 11):
    setattr(
        Player,
        f'wtpmax_{i}',
        models.IntegerField(min=0, max=C.MAX_WTP, blank=True),
    )

# --- add 3 IntegerFields for “How many lied” -----------------
for letter in ['A', 'B', 'C']:
    setattr(
        Player,
        f'lied_{letter}',
        models.IntegerField(
            min=0,
            max=2,           # two other members
            blank=True,
        ),
    )

# NEW: Willingness‑To‑Lie importance ratings (1‑10)
for i in range(1, 11):
    setattr(
        Player,
        f"wtl_{i}",
        models.IntegerField(
            choices=list(range(1, 11)),  # 1–10 inclusive
            widget=widgets.RadioSelectHorizontal,
        ),
    )


# ---------------------------------------------------------------------
# Utility functions
# ---------------------------------------------------------------------

def get_randomised_questions(participant):
    """Return (order, flip_list) for the 10 binary questions."""
    if 'q_order' not in participant.vars:
        rng = _rng_for_participant(participant)
        order = list(range(10))
        rng.shuffle(order)
        participant.vars['q_order'] = order
        participant.vars['flip'] = [rng.choice([True, False]) for _ in order]
    return participant.vars['q_order'], participant.vars['flip']


def get_randomised_wtj(participant):
    """Return (order, flip_list) for WTJ block."""
    if 'wtj_order' not in participant.vars:
        order = list(range(10))
        random.shuffle(order)
        participant.vars['wtj_order'] = order
        participant.vars['wtj_flip'] = [random.choice([True, False]) for _ in order]
    return participant.vars['wtj_order'], participant.vars['wtj_flip']

def _get_topic_treatment_order(participant):
    if 'pair_order' not in participant.vars:
        rng = _rng_for_participant(participant)
        order = C.PAIRS.copy()
        rng.shuffle(order)
        participant.vars['pair_order'] = order
    return participant.vars['pair_order']

# -----------------------------------------------------------------------------
# Page Definitions
# -----------------------------------------------------------------------------

class PersonalInfoPage(Page):
    form_model = 'player'
    form_fields = ['age', 'gender', 'racial_identification', 'previous_experiment']
    
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

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
        form_model   = 'player'
        template_name = 'actual_exp_phase_1/BinaryQuestionsPage.html'  # reuse your template

        @staticmethod
        def is_displayed(player: Player):
            return player.round_number == 1

        @staticmethod
        def get_form_fields(player: Player):
            q_idx, _ = _stage1_topic(player, n)
            return [f'answer_{q_idx + 1}', f'wtl_{q_idx + 1}']

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
            )
            # Your template loops `{% for item in items %}` — we pass exactly one.
            return dict(items=[item], scale=range(1, 11))

    _BinaryTopicPage.__name__ = f'BinaryTopic_{n}'
    return _BinaryTopicPage

# Create and register 10 classes: BinaryTopic_1 .. BinaryTopic_10
BINARY_TOPIC_PAGES = []
for i in range(1, 11):
    cls = make_binary_topic_page(i)
    globals()[cls.__name__] = cls
    BINARY_TOPIC_PAGES.append(cls)

class WillingnessToJudgeFixedCost(Page):
    form_model = 'player'

    @staticmethod
    def get_form_fields(player):
        order, _ = get_randomised_wtj(player.participant)
        return [f'wtj_{idx + 1}' for idx in order]

    @staticmethod
    def vars_for_template(player):
        order, flips = get_randomised_wtj(player.participant)
        items = []
        for pos, q_idx in enumerate(order):
            labels = list(C.YES_NO)
            if flips[pos]:
                labels.reverse()
            items.append(
                dict(
                    index=pos + 1,
                    field_name=f'wtj_{q_idx + 1}',
                    question=C.TOPIC_LABELS[q_idx],          # Spanish statement
                    cost=C.COST_X,
                    left=labels[0],                          # Yes/No (maybe flipped)
                    right=labels[1],
                )
            )
        return dict(items=items)
    
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

class TopicTreatment(Page):
    @staticmethod
    def vars_for_template(player: Player):

        # ---------- one-off assignment (unchanged) ----------
        if player.field_maybe_none('topic_idx') is None:
            order = _get_topic_treatment_order(player.participant)
            t_idx, trt_idx = order[player.round_number - 1]
            player.topic_idx     = t_idx
            player.treatment_idx = trt_idx

        # ---------- core info ----------
        topic       = C.TOPIC_LABELS[player.topic_idx]
        trt_code    = C.TREATMENT_CODES[player.treatment_idx]
        png_path    = f"experiment/{trt_code}.png"

        # ---------- retrieve the canonical A/B pair ----------
        left, right = C.BINARY_OPTIONS[player.topic_idx]

        # ---------- OPTIONAL: keep the same flip used on Q-page ----------
        q_order, flips = get_randomised_questions(player.participant)
        try:
            pos = q_order.index(player.topic_idx)
            if flips[pos]:
                left, right = right, left    # flip orientation
        except ValueError:
            pass  # should not happen, but fail-safe

        return dict(
            topic         = topic,
            treatment_png = png_path,
            left          = left,
            right         = right,
        )
    
class ExpressYourOpinion(Page):
    form_model = 'player'
    form_fields = ['public_opinion']

    @staticmethod
    def vars_for_template(player: Player):
        # ── canonical A/B wording for THIS topic ──────────────────────────
        topic_left, topic_right = C.BINARY_OPTIONS[player.topic_idx]

        # keep the orientation each participant saw on BinaryQuestionsPage
        q_order, flips_q = get_randomised_questions(player.participant)
        pos_topic = q_order.index(player.topic_idx)
        if flips_q[pos_topic]:
            topic_left, topic_right = topic_right, topic_left

        # ── radio buttons may be flipped again, round-by-round ───────────
        rng   = _rng_for_participant(player.participant)
        flips = player.participant.vars.setdefault('public_flip', {})
        if player.round_number not in flips:
            flips[player.round_number] = rng.choice([True, False])

        left, right = (topic_left, topic_right)
        if flips[player.round_number]:
            left, right = right, left

        return dict(
            topic          = C.TOPIC_LABELS[player.topic_idx],
            treatment_png  = f"experiment/{C.TREATMENT_CODES[player.treatment_idx]}.png",
            topic_left     = topic_left,      # ← now in the context
            topic_right    = topic_right,     # ← now in the context
            left           = left,            # radio-button label L
            right          = right,           # radio-button label R
        )


class HowManyLied(Page):
    form_model  = 'player'
    form_fields = [
        'paid_cost_A',   # cost-to-punish, among A-holders
        'paid_cost_B',   # cost-to-punish, among B-holders
        'expr_A_from_A', # expressed A, among A-holders
        'expr_A_from_B', # expressed A, among B-holders
    ]

    @staticmethod
    def vars_for_template(player: Player):
        # ── canonical A/B wording for THIS topic ──────────────────────────
        topic_left, topic_right = C.BINARY_OPTIONS[player.topic_idx]

        # keep the orientation each participant saw on BinaryQuestionsPage
        q_order, flips_q = get_randomised_questions(player.participant)
        pos_topic = q_order.index(player.topic_idx)
        if flips_q[pos_topic]:
            topic_left, topic_right = topic_right, topic_left

        topic         = C.TOPIC_LABELS[player.topic_idx]
        treatment_png = f"experiment/{C.TREATMENT_CODES[player.treatment_idx]}.png"

        items = [
            dict(
                index       = 1,
                field_name  = 'paid_cost_A',
                prompt      = f' How many out of the five with opinion <strong>{topic_left}</strong> decided to pay the cost to punish?',
            ),
            dict(
                index       = 2,
                field_name  = 'paid_cost_B',
                prompt      = f'How many out of the five with opinion <strong>{topic_right}</strong> decided to pay the cost to punish?',
            ),
            dict(
                index       = 3,
                field_name  = 'expr_A_from_A',
                prompt      = (f'How many out of the five with opinion <strong>{topic_left}</strong> '
                               f'expressed <strong>{topic_left}</strong>?'),
            ),
            dict(
                index       = 4,
                field_name  = 'expr_A_from_B',
                prompt      = (f'How many out of the five with opinion <strong>{topic_right}</strong> '
                               f'expressed <strong>{topic_left}</strong>?'),
            ),
        ]

        return dict(
            topic         = topic,
            treatment_png = treatment_png,
            items         = items,
            topic_left    = topic_left,
            topic_right   = topic_right,
        )

class ThankYouPage(Page):
    @staticmethod
    def is_displayed(player: Player) -> bool:
        return player.round_number == C.NUM_ROUNDS

    @staticmethod
    def vars_for_template(player: Player) -> dict:
        return {}

# -----------------------------------------------------------------------------
# Page Sequence
# -----------------------------------------------------------------------------
page_sequence = [
    #PersonalInfoPage,
] + BINARY_TOPIC_PAGES + [
    WillingnessToJudgeFixedCost,
    TopicTreatment,
    ExpressYourOpinion,
    HowManyLied,
    ThankYouPage
]
