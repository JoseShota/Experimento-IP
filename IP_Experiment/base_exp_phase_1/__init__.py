from __future__ import annotations
import random
from otree.api import *
import random, secrets

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
    ('Option A', 'Option B'),  # Question 1
    ('Option A', 'Option B'),  # Question 2
    ('Option A', 'Option B'),  # Question 3
    ('Option A', 'Option B'),  # Question 4
    ('Option A', 'Option B'),  # Question 5
    ('Option A', 'Option B'),  # Question 6
    ('Option A', 'Option B'),  # Question 7
    ('Option A', 'Option B'),  # Question 8
    ('Option A', 'Option B'),  # Question 9
    ('Option A', 'Option B'),  # Question 10
    ]

# Willingness to judge fixed cost and maximum cost
    COST_X = 'x'            # replace later with cu(10) or similar
    YES_NO = ('Yes, I am willing to pay x to make the decision', 'No, I am not willing to pay x to make the decision')  # canonical label pair
    MAX_WTP = 20          # numeric ceiling for the slider (pesos)

# Treatment codes for the experiment
    TREATMENT_CODES = [
        'Fifty_Fifty',
        'Seventy_Thirty',
        'Thirty_Seventy',
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
def _get_topic_treatment_order(participant):
    if 'pair_order' not in participant.vars:
        rng = _rng_for_participant(participant)
        order = C.PAIRS.copy()
        rng.shuffle(order)                   # <‑‑ use local RNG
        participant.vars['pair_order'] = order
    return participant.vars['pair_order']


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
        choices=[('Give', 'Give 20 pesos'), ('Take', 'Take 20 pesos')],
        label='',
        blank=True,
    )

    judge_second = models.StringField(
        choices=[('Give', 'Give 20 pesos'), ('Take', 'Take 20 pesos')],
        label='',
        blank=True,
    )

    public_opinion = models.StringField(
        label="What opinion would you express to the rest of your group?"
    )





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


# ---------------------------------------------------------------------
# Utility functions
# ---------------------------------------------------------------------

def get_randomised_questions(participant):
    """
    Draw a random order of the 10 indices *once* per participant
    and decide independently for every question if the options
    should be flipped.
    """
    if 'q_order' not in participant.vars:
        order = list(range(10))
        random.shuffle(order)
        participant.vars['q_order'] = order
        participant.vars['flip'] = [random.choice([True, False]) for _ in order]
    return participant.vars['q_order'], participant.vars['flip']

def get_randomised_wtj(participant):
    """Return (order, flip_list) for WTJ block."""
    if 'wtj_order' not in participant.vars:
        order = list(range(10))
        random.shuffle(order)
        participant.vars['wtj_order'] = order
        participant.vars['wtj_flip'] = [random.choice([True, False]) for _ in order]
    return participant.vars['wtj_order'], participant.vars['wtj_flip']

def get_randomised_wtpmax(participant):
    """Return (order, flip_list) for the slider WTP‑max block."""
    if 'wtpmax_order' not in participant.vars:
        order = list(range(10))
        random.shuffle(order)
        participant.vars['wtpmax_order'] = order
        participant.vars['wtpmax_flip'] = [random.choice([True, False]) for _ in order]
    return participant.vars['wtpmax_order'], participant.vars['wtpmax_flip']

def get_judge_order(participant):
    if 'judge_order' not in participant.vars:
        participant.vars['judge_order'] = random.sample([0, 1], k=2)
    return participant.vars['judge_order']

# --- helper for randomising the “lied” questions -------------
def get_randomised_lied_order(participant):
    if 'lied_order' not in participant.vars:
        rng = _rng_for_participant(participant)
        # shuffle the three scenarios A, B, C
        participant.vars['lied_order'] = rng.sample([0, 1, 2], k=3)
    return participant.vars['lied_order']

# -----------------------------------------------------------------------------
# Page Definitions
# -----------------------------------------------------------------------------

class PersonalInfoPage(Page):
    form_model = 'player'
    form_fields = ['age', 'gender', 'racial_identification', 'previous_experiment']
    
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

class BinaryQuestionsPage(Page):
    """Single page that shows the 10 statements in a random order **for
    this participant** and, independently, flips the left/right option
    labels with 50-50 probability for every statement."""

    form_model = 'player'

    @staticmethod
    def get_form_fields(player: Player):
        # Return the 10 answer_* field names in the participant-specific order
        q_order, _ = get_randomised_questions(player.participant)
        return [f'answer_{idx + 1}' for idx in q_order]

    @staticmethod
    def vars_for_template(player: Player):
        q_order, flips = get_randomised_questions(player.participant)

        items = []
        for pos, q_idx in enumerate(q_order):
            opts = list(C.BINARY_OPTIONS[q_idx])
            if flips[pos]:
                opts.reverse()
            items.append(
                dict(
                    index=pos + 1,
                    field_name=f'answer_{q_idx + 1}',
                    question=C.TOPIC_LABELS[q_idx],
                    left=opts[0],
                    right=opts[1],
                )
            )

        return dict(questions=items)
    
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

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

class WillingnessToJudgeMaximumCost(Page):
    form_model = 'player'

    @staticmethod
    def get_form_fields(player):
        order, _ = get_randomised_wtpmax(player.participant)
        return [f'wtpmax_{idx + 1}' for idx in order]

    @staticmethod
    def vars_for_template(player):
        order, flips = get_randomised_wtpmax(player.participant)
        items = []
        for pos, q_idx in enumerate(order):
            labels = list(C.YES_NO)          # (‘Yes’, ‘No’) for left/right text
            if flips[pos]:
                labels.reverse()
            items.append(
                dict(
                    index=pos + 1,
                    field_name=f'wtpmax_{q_idx + 1}',
                    question=C.TOPIC_LABELS[q_idx],   # Spanish topic
                    left=labels[0],                   # only for label positions
                    right=labels[1],
                )
            )
        return dict(items=items, max_wtp=C.MAX_WTP)
    
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

class TopicTreatment(Page):
    @staticmethod
    def vars_for_template(player: Player):
        # ---------------------------------------------------------
        # Only assign once, using field_maybe_none() to test safely
        # ---------------------------------------------------------
        if player.field_maybe_none('topic_idx') is None:
            order = _get_topic_treatment_order(player.participant)
            t_idx, trt_idx = order[player.round_number - 1]
            player.topic_idx     = t_idx
            player.treatment_idx = trt_idx

        # Now these will never be None
        topic    = C.TOPIC_LABELS[player.topic_idx]
        trt_code = C.TREATMENT_CODES[player.treatment_idx]
        png_path = f"experiment/{trt_code}.png"

        return dict(topic=topic, treatment_png=png_path)

class JudgeStrategicMethod(Page):
    form_model = 'player'

    @staticmethod
    def get_form_fields(player):
        order = get_judge_order(player.participant)
        fields = ['judge_first', 'judge_second']
        return [fields[i] for i in order]

    @staticmethod
    def vars_for_template(player):
        topic_idx = player.topic_idx
        topic = C.TOPIC_LABELS[topic_idx]
        treatment_code = C.TREATMENT_CODES[player.treatment_idx]
        treatment_png = f"experiment/{treatment_code}.png"
        binary_opts = C.BINARY_OPTIONS[topic_idx]
        order = get_judge_order(player.participant)

        # Assemble question text with flip-aware ordering
        items = []
        field_names = ['judge_first', 'judge_second']
        for i in order:
            items.append(
                dict(
                    field_name=field_names[i],
                    statement=binary_opts[i],
                )
            )

        return dict(
            topic=topic,
            treatment_png=treatment_png,
            items=items,
            round_number=player.round_number,
            total_rounds=C.NUM_ROUNDS,
        )
    
class ExpressYourOpinion(Page):
    form_model = 'player'
    form_fields = ['public_opinion']

    @staticmethod
    def vars_for_template(player: Player):
        # topic text + diagram
        topic = C.TOPIC_LABELS[player.topic_idx]
        treatment_png = f"experiment/{C.TREATMENT_CODES[player.treatment_idx]}.png"

        # grab the two original binary options for this topic
        opts = list(C.BINARY_OPTIONS[player.topic_idx])

        # optional flip
        rng = _rng_for_participant(player.participant)
        flips = player.participant.vars.setdefault('public_flip', {})
        if player.round_number not in flips:
            flips[player.round_number] = rng.choice([True, False])
        if flips[player.round_number]:
            opts.reverse()

        left, right = opts
        return dict(topic=topic, treatment_png=treatment_png, left=left, right=right)

class HowManyLied(Page):
    form_model = 'player'

    @staticmethod
    def get_form_fields(player):
        order = get_randomised_lied_order(player.participant)
        # letters A, B, C correspond to the three scenarios
        return [f'lied_{chr(ord("A") + idx)}' for idx in order]

    @staticmethod
    def vars_for_template(player: Player):
        order = get_randomised_lied_order(player.participant)
        # retrieve the two binary options for this topic
        opts = list(C.BINARY_OPTIONS[player.topic_idx])

        # build text for each scenario index
        descriptions = {
            0: f'one member expressed "{opts[0]}" and one member expressed "{opts[1]}"',
            1: f'both members expressed "{opts[0]}"',
            2: f'both members expressed "{opts[1]}"',
        }

        # re‑compute topic + diagram for display
        topic = C.TOPIC_LABELS[player.topic_idx]
        treatment_png = f'experiment/{C.TREATMENT_CODES[player.treatment_idx]}.png'

        items = []
        for pos, idx in enumerate(order):
            items.append(
                dict(
                    index=pos + 1,
                    field_name=f'lied_{chr(ord("A") + idx)}',
                    description=descriptions[idx],
                )
            )
        return dict(topic=topic, treatment_png=treatment_png, items=items)

    @staticmethod
    def is_displayed(player: Player):
        # show in every round, immediately after ExpressYourOpinion
        return True

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
    PersonalInfoPage,
    BinaryQuestionsPage,
    WillingnessToJudgeFixedCost,
    WillingnessToJudgeMaximumCost,
    TopicTreatment,
    JudgeStrategicMethod,
    ExpressYourOpinion,
    HowManyLied,
    ThankYouPage
]
