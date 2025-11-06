import secrets
import random
from otree.api import *

##############################
# Otree Setup
class C(BaseConstants):
    NAME_IN_URL = 'stage_2_separated'
    PLAYERS_PER_GROUP = None
    PRACTICE_TOPIC_LABEL = 'Emmanuel o Mijares'
    COST_STAGE_2 = cu(1000)
    PUNISHMENT_STAGE_2 = cu(3000)
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
    # Mapping from treatment codes to counts of A and B opinions
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
    # ---------- derived combinations ----------
    PAIRS = []
    for t_idx in range(len(TOPIC_LABELS)):
        for trt_idx in range(len(TREATMENT_CODES)):
            PAIRS.append((t_idx, trt_idx))
    # Willingness to judge fixed cost and maximum cost
    YES_NO = ('Yes, I am willing to pay  { cost_stage_2 } to make the decision', 'No, I am not willing to pay { cost_stage_2 } to make the decision')  # canonical label pair
    PRACTICE_ROUNDS = 1
    NUM_ROUNDS = PRACTICE_ROUNDS + len(PAIRS)


class Subsession(BaseSubsession):
    pass


def creating_session(subsession: Subsession):
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


class Player(BasePlayer):
    # topic and treatment indices for the current round
    topic_idx     = models.IntegerField(blank=True)
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
        order = C.PAIRS.copy()
        rng.shuffle(order)
        participant.vars['pair_order'] = order
    return participant.vars['pair_order']


def counts_for_treatment(trt_idx: int) -> tuple[int, int]:
    """Return (n_A, n_B) for a given treatment index. Defaults to 5/5."""
    code = C.TREATMENT_CODES[trt_idx]
    return C.TREATMENT_TO_COUNTS.get(code, (5, 5))


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


# Practice utilities
def practice_left_right():
    """
    Compute the practice topic's left/right labels with a per-participant flip
    that is *separate* from Stage 1 flips (since practice is outside the 10 topics).
    """
    return "Emmanuel o Mijares", "Emmanuel", "Mijares"


def practice_treatment_idx(session):
    """Resolve practice treatment code to index in C.TREATMENT_CODES."""
    code = session.config.get('practice_treatment', C.TREATMENT_CODES[0])
    try:
        return C.TREATMENT_CODES.index(code)
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

        return dict(
            topic          = topic_label,
            topic_left     = topic_left,
            topic_right    = topic_right,
            cost_stage_2   = C.COST_STAGE_2,
            treatment_png  = f"experiment/{C.TREATMENT_CODES[trt_idx]}.png",
            is_practice    = True,
            n_A            = n_A,
            n_B            = n_B,
            punishment_stage_2 = C.PUNISHMENT_STAGE_2
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
        _, topic_left, topic_right = practice_left_right()
        left, right = "A", "B"
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
            punishment_stage_2 = C.PUNISHMENT_STAGE_2
        )


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

        left, right = ("A", "B")
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
