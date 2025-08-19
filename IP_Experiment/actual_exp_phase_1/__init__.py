from __future__ import annotations
from otree.api import *
import secrets
import random as _random  # keep stdlib random under a distinct alias

def _rng_for_participant(participant):
    if 'rng' not in participant.vars:
        seed = secrets.randbits(64)  # 64 bits of OS entropy
        participant.vars['rng'] = _random.Random(seed)
    return participant.vars['rng']

# -----------------------------------------------------------------------------
# Module-level constants
# -----------------------------------------------------------------------------

class C(BaseConstants):
    NAME_IN_URL = 'actual_exp_phase_1'
    PLAYERS_PER_GROUP = None
    PRACTICE_TOPIC_LABEL = 'Emmanuel o Mijares'
    PRACTICE_OPTIONS     = ('Option H', 'Option L')
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
    COST_X = '{ cost_stage_2 }'            # replace later with cu(10) or similar
    YES_NO = ('Yes, I am willing to pay  { cost_stage_2 } to make the decision', 'No, I am not willing to pay { cost_stage_2 } to make the decision')  # canonical label pair
    MAX_WTP = 10          # numeric ceiling for the slider (pesos)

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

    # ---------- derived combinations ----------
    PAIRS = []
    for t_idx in range(len(TOPIC_LABELS)):
        for trt_idx in range(len(TREATMENT_CODES)):
            PAIRS.append((t_idx, trt_idx))

    NUM_ROUNDS = len(PAIRS)

# --- Map each treatment code to (#A, #B) among 10 participants ---------------
TREATMENT_TO_COUNTS = {
    'New_Ten_Ninenty':   (1, 9),  # note the original spelling is kept
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
    # Ensure participant-level pair order exists
    for p in subsession.get_players():
        order = _get_topic_treatment_order(p.participant)
        # Proactively bind the (topic_idx, treatment_idx) for this round
        t_idx, trt_idx = order[subsession.round_number - 1]
        p.topic_idx = t_idx
        p.treatment_idx = trt_idx

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
    # Stage 1 (practice page)
    answer_practice   = models.StringField(blank=True)
    wtl_practice      = models.IntegerField(choices=list(range(1, 11)), widget=widgets.RadioSelectHorizontal, blank=True)
    jr_practice       = models.IntegerField(choices=[1, 2, 3], blank=True)
    wtpmax_practice   = models.IntegerField(min=0, max=C.MAX_WTP, blank=True)
    # Stage 2 (WTJ practice)
    wtj_practice      = models.StringField(blank=True)
    # Stage 3 (public opinion practice)
    public_opinion_practice = models.StringField(blank=True)
    # Stage 4 (guesses practice)
    paid_cost_A_practice   = models.IntegerField(min=0, max=10, blank=True)
    paid_cost_B_practice   = models.IntegerField(min=0, max=10, blank=True)
    expr_A_from_A_practice = models.IntegerField(min=0, max=10, blank=True)
    expr_A_from_B_practice = models.IntegerField(min=0, max=10, blank=True)
    topic_idx     = models.IntegerField()
    treatment_idx = models.IntegerField()

    public_opinion = models.StringField(
        label="What opinion would you express to the rest of your group?"
    )
    # ─── Stage-4 guesses (0–5 each) ──────────────────────────────────────────
    paid_cost_A = models.IntegerField(min=0, max=10, blank=True,
                                label="How many of the 5 with opinion A paid the cost?")
    paid_cost_B = models.IntegerField(min=0, max=10, blank=True,
                                label="How many of the 5 with opinion B paid the cost?")
    expr_A_from_A = models.IntegerField(min=0, max=10, blank=True,
                                label="How many of the 5 with opinion A expressed A?")
    expr_A_from_B = models.IntegerField(min=0, max=10, blank=True,
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

# Willingness-To-Lie importance ratings (keep as-is)
for i in range(1, 11):
    setattr(
        Player,
        f"wtl_{i}",
        models.IntegerField(
            choices=list(range(1, 11)),  # If switching to 0..10, use range(0, 11)
            widget=widgets.RadioSelectHorizontal,
        ),
    )

# --- add 10 IntegerFields for JudgementRule (Approach 1/2/3) -------------
for i in range(1, 11):
    setattr(
        Player,
        f'jr_{i}',
        models.IntegerField(
            choices=[(1, 'Approach 1'), (2, 'Approach 2'), (3, 'Approach 3')],
            blank=True,       # UI will enforce selection; keep DB tolerant
        ),
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


def _practice_treatment_idx(session):
    """Resolve practice treatment code to index in C.TREATMENT_CODES."""
    code = session.config.get('practice_treatment', C.TREATMENT_CODES[0])
    try:
        return C.TREATMENT_CODES.index(code)
    except ValueError:
        return 0


def _practice_left_right(player: Player):
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
    """
    Short, grammatically clean clause describing WHEN punishment would be applied,
    matching the labels shown on the BinaryQuestionsPage.
    """
    mapping = {
        1: "if the opinion they express is different from your own",
        2: "if their actual true opinion is different from your own",
        3: "if the opinion they express is different from their own true opinion",
    }
    # default to approach 2 (closest to current generic text) if missing
    return mapping.get(approach, mapping[2])


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
        return ['answer_practice', 'wtl_practice', 'jr_practice', 'wtpmax_practice']

    @staticmethod
    def vars_for_template(player: Player):
        topic_label, left, right = _practice_left_right(player)

        item = dict(
            index     = 1,
            question  = topic_label,
            ans_field = 'answer_practice',
            left      = left,
            right     = right,
            wtl_field = 'wtl_practice',
            wtp_field = 'wtpmax_practice',
            jr_field  = 'jr_practice',
        )

        a1 = "someone if they expressed an opinion different from your own"
        a2 = "someone if their actual true opinion is different from your own"
        a3 = "someone if they expressed an opinion different from their own true opinion"

        return dict(
            items=[item],
            scale_prob = range(1, 11),
            scale_cost = range(0, C.MAX_WTP + 1),
            max_wtp = C.MAX_WTP,
            show_help = True,  # long help on the practice page
            cost_clause_by_approach = {1: a1, 2: a2, 3: a3},
            is_practice=True, 
        )

    @staticmethod
    def error_message(player: Player, values):
        _, left, right = _practice_left_right(player)
        allowed = {left, right}
        if values.get('answer_practice') not in allowed:
            return "Please select one of the two options."
        if values.get('wtl_practice') is None:
            return "Please choose a maximum punishment probability."
        if values.get('jr_practice') not in {1, 2, 3}:
            return "Please choose one approach."
        wtp = values.get('wtpmax_practice')
        if wtp is None or not (0 <= wtp <= C.MAX_WTP):
            return f"Please set your maximum willingness to pay between 0 and {C.MAX_WTP}."


class Practice_TopicTreatment(Page):
    template_name = 'actual_exp_phase_1/TopicTreatment.html'
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    @staticmethod
    def vars_for_template(player: Player):
        topic_label, left, right = _practice_left_right(player)
        trt_idx = _practice_treatment_idx(player.session)
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
    template_name = 'actual_exp_phase_1/WillingnessToJudgeFixedCost.html'

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    @staticmethod
    def get_form_fields(player: Player):
        return ['wtj_practice']

    @staticmethod
    def error_message(player: Player, values):
        if values.get('wtj_practice') not in C.YES_NO:
            return "Please choose Yes or No."

    @staticmethod
    def vars_for_template(player: Player):
        topic_label, topic_left, topic_right = _practice_left_right(player)
        yes, no = _practice_yes_no(player)
        trt_idx = _practice_treatment_idx(player.session)
        n_A, n_B = counts_for_treatment(trt_idx)

        # NEW:
        jr_approach = player.jr_practice
        jr_clause   = approach_clause(jr_approach)

        return dict(
            field_name     = 'wtj_practice',
            topic          = topic_label,
            topic_left     = topic_left,
            topic_right    = topic_right,
            yes_label      = yes,
            no_label       = no,
            cost_stage_2   = C.COST_X,
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
        # Use the Stage-1–oriented A/B for THIS topic (same logic as vars_for_template)
        topic_left, topic_right = C.BINARY_OPTIONS[player.topic_idx]
        q_order, flips_q = get_randomised_questions(player.participant)
        pos_topic = q_order.index(player.topic_idx)
        if flips_q[pos_topic]:
            topic_left, topic_right = topic_right, topic_left

        v = values.get('public_opinion')
        if v not in {topic_left, topic_right}:
            return "Please select one of the two opinions."

    @staticmethod
    def vars_for_template(player: Player):
        topic_label, topic_left, topic_right = _practice_left_right(player)
        rng = _rng_for_participant(player.participant)
        flip = player.participant.vars.setdefault('public_flip_practice', rng.choice([True, False]))
        left, right = (topic_right, topic_left) if flip else (topic_left, topic_right)
        trt_idx = _practice_treatment_idx(player.session)
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
        topic_label, topic_left, topic_right = _practice_left_right(player)
        trt_idx = _practice_treatment_idx(player.session)
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
        trt_idx = _practice_treatment_idx(player.session)
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
                f'jr_{q_idx + 1}',
                f'wtpmax_{q_idx + 1}',
            ]

        @staticmethod
        def vars_for_template(player: Player):
            # Which topic is shown on this n-th Stage-1 page?
            q_idx, flip = _stage1_topic(player, n)

            # Canonical left/right for that topic, maybe flipped for this participant
            left, right = C.BINARY_OPTIONS[q_idx]
            if flip:
                left, right = right, left

            item = dict(
                index     = n,
                question  = C.TOPIC_LABELS[q_idx],
                ans_field = f'answer_{q_idx + 1}',
                left      = left,
                right     = right,
                wtl_field = f'wtl_{q_idx + 1}',     # 1..10 radios
                wtp_field = f'wtpmax_{q_idx + 1}',  # 0..MAX_WTP radios
                jr_field  = f'jr_{q_idx + 1}',      # approach 1/2/3
            )

            # Approach-specific clauses the JS interpolates into prompts
            a1 = "someone if they expressed an opinion different from your own"
            a2 = "someone if their actual true opinion is different from your own"
            a3 = "someone if they expressed an opinion different from their own true opinion"

            return dict(
                items=[item],                         # <-- the thing the template expects
                scale_prob = range(1, 11),            # keep 1..10 to match your wtl_* choices
                scale_cost = range(0, C.MAX_WTP + 1), # 0..MAX_WTP
                max_wtp = C.MAX_WTP,
                show_help = (n == 1),                 # long help on the first topic only
                cost_clause_by_approach = {1: a1, 2: a2, 3: a3},
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

            jr = values.get(f'jr_{q_idx + 1}')
            if jr not in {1, 2, 3}:
                return "Please choose one approach."

            wtp = values.get(f'wtpmax_{q_idx + 1}')
            if wtp is None or not (0 <= wtp <= C.MAX_WTP):
                return f"Please set your maximum willingness to pay between 0 and {C.MAX_WTP}."

    _BinaryTopicPage.__name__ = f'BinaryTopic_{n}'
    return _BinaryTopicPage

# Create and register 10 classes: BinaryTopic_1 .. BinaryTopic_10
BINARY_TOPIC_PAGES = []
for i in range(1, 11):
    cls = make_binary_topic_page(i)
    globals()[cls.__name__] = cls
    BINARY_TOPIC_PAGES.append(cls)

class TopicTreatment(Page):
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

    @staticmethod
    def get_form_fields(player):
        return [f'wtj_{player.topic_idx + 1}']

    @staticmethod
    def error_message(player: Player, values):
        v = values.get(f'wtj_{player.topic_idx + 1}')
        if v not in C.YES_NO:
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

        # NEW: pull the judgment rule chosen on Stage-1 for this topic
        jr_field = f'jr_{player.topic_idx + 1}'
        jr_approach = getattr(player, jr_field, None)
        jr_clause = approach_clause(jr_approach)  # uses the helper above

        return dict(
            field_name     = f'wtj_{player.topic_idx + 1}',
            topic          = C.TOPIC_LABELS[player.topic_idx],
            topic_left     = topic_left,
            topic_right    = topic_right,
            yes_label      = yes,
            no_label       = no,
            cost_stage_2   = C.COST_X,
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


    is_displayed = staticmethod(lambda p: True)

  
class ExpressYourOpinion(Page):
    form_model = 'player'
    form_fields = ['public_opinion']

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
]