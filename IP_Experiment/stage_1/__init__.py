import secrets
import random
from otree.api import *
from common.params import TOPIC_LABELS, TREATMENT_CODES, PRACTICE_ROUNDS, TREATMENT_TO_COUNTS, BINARY_OPTIONS

##############################
# Otree Setup
class C(BaseConstants):
    NAME_IN_URL = 'stage_1_separated'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = PRACTICE_ROUNDS + len(TOPIC_LABELS)


class Subsession(BaseSubsession):
    pass


def creating_session(subsession: Subsession):
    n_topics = len(TOPIC_LABELS)
    if subsession.round_number == 1:
        practice = PRACTICE_ROUNDS
        # (Opcional) guardar total de rondas de S1 para referencia global
        subsession.session.vars['NUM_ROUNDS_S1'] = practice + n_topics

    for p in subsession.get_players():
        q_order = _ensure_stage1_order_and_flips(p.participant, n_topics)

        # índice efectivo de ronda pagada (1..n_topics); 0 = práctica
        er = subsession.round_number - PRACTICE_ROUNDS

        if er < 1:
            # ronda de práctica
            p.topic_idx = None
            continue

        if er > len(q_order):
            # más rondas que tópicos: no asignamos (o lanza error en dev)
            total_paid = len(q_order)
            raise RuntimeError(
                f"Round {subsession.round_number} exceeds topic trials ({total_paid}). "
                f"Check NUM_ROUNDS={C.NUM_ROUNDS} vs PRACTICE_ROUNDS+len(TOPICS)"
            )

        # tópico de esta ronda (0-based)
        t_idx = q_order[er - 1]
        p.topic_idx = t_idx


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    # topic indices for the current round
    topic_idx = models.IntegerField(blank=True)
    # fields
    answer = models.StringField(
        choices=[('A', 'Option A'), ('B', 'Option B')],
        widget=widgets.RadioSelectHorizontal,
        blank=True,
        label="What opinion would you express to the rest of your group?"
    )
    wtl = models.IntegerField(
            choices=list(range(1, 11)),
            widget=widgets.RadioSelectHorizontal,
            label="Willingness to lie"
        )
    min_opp_punish = models.IntegerField(
            choices=list(range(0, 11)),
            widget=widgets.RadioSelectHorizontal,
            label="Minimum number of opposite-opinion group members to punish"
        )


### Helper functions ###
def _rng_for_participant(participant):
    if 'rng' not in participant.vars:
        seed = secrets.randbits(64)  # 64 bits of OS entropy
        participant.vars['rng'] = random.Random(seed)
    return participant.vars['rng']


def _ensure_stage1_order_and_flips(participant, n_topics: int):
    """
    Guarda en participant.vars:
      - 'q_order': permutación de índices de topics (0..n_topics-1)
      - 'flip':    lista de booleans (True => invierte L/R en UI), mismo largo
    Devuelve q_order.
    """
    rng = _rng_for_participant(participant)

    if 'q_order' not in participant.vars:
        order = list(range(n_topics))
        rng.shuffle(order)
        participant.vars['q_order'] = order

    if 'flip' not in participant.vars or len(participant.vars['flip']) != n_topics:
        participant.vars['flip'] = [rng.choice([True, False]) for _ in range(n_topics)]

    return participant.vars['q_order']


### Pages ###
class BinaryQuestionsPage_Practice(Page):
    form_model = 'player'
    form_fields = ['answer', 'wtl', 'min_opp_punish']
    template_name = 'stage_1/BinaryQuestionsPage.html'

    @staticmethod
    def is_displayed(player):
        return player.round_number == 1
    
    @staticmethod
    def vars_for_template(player: Player):
        topic_idx = 0  # práctica
        topic_question = "Emmanuel o Mijares"
        left = "A"
        topic_left = "Emmanuel"
        right = "B"
        topic_right = "Mijares"
        punishment_stage_1 = player.session.config['PUNISHMENT_STAGE_1']
        cost_stage_1 = player.session.config['COST_STAGE_1']

        return dict(
            topic_index=topic_idx,
            topic_question=topic_question,
            left=left,
            topic_left=topic_left,
            right=right,
            topic_right=topic_right,
            punishment_stage_1=punishment_stage_1,
            cost_stage_1=cost_stage_1,
            show_help=True,
        )
    

class BinaryQuestionsPage(Page):
    form_model = 'player'
    form_fields = ['answer', 'wtl', 'min_opp_punish']

    @staticmethod
    def is_displayed(player):
        return player.round_number > PRACTICE_ROUNDS

    @staticmethod
    def vars_for_template(player: Player):
        topic_idx = player.topic_idx
        topic_question = TOPIC_LABELS[topic_idx]
        flip = player.participant.vars['flip'][topic_idx]
        if flip:
            left = 'B'
            topic_left = BINARY_OPTIONS[topic_idx][1]
            right = 'A'
            topic_right = BINARY_OPTIONS[topic_idx][0]
        else:
            left = 'A'
            topic_left = BINARY_OPTIONS[topic_idx][1]
            right = 'B'
            topic_right = BINARY_OPTIONS[topic_idx][0]
        punishment_stage_1 = player.session.config['PUNISHMENT_STAGE_1']
        cost_stage_1 = player.session.config['COST_STAGE_1']

        return dict(
            topic_index=topic_idx + 1,
            topic_question=topic_question,
            left=left,
            topic_left=topic_left,
            right=right,
            topic_right=topic_right,
            punishment_stage_1=punishment_stage_1,
            cost_stage_1=cost_stage_1,
            show_help=False,
        )
    
    @staticmethod
    def before_next_page(player: Player, timeout_happened=False):
        """
        Guarda en participant.vars con la forma:
        {
          'topic_0': {
              'answer': 'A'/'B',
              'stage_1': {
                  'wtl': int,
                  'min_opp_punish': int,
              },
          },
          'topic_1': {...},
          ...
        }
        """
        topic_idx = player.topic_idx

        # Por seguridad: si por alguna razón no hay topic, no hacemos nada
        if topic_idx is None:
            raise RuntimeError("No topic_idx assigned for this round.")

        key = f"topic_{topic_idx}"   # 0-based, como pediste

        pv = player.participant.vars

        # dict para este tópico
        topic_data = pv.setdefault(key, {})

        # guardar la respuesta A/B de Stage 1
        topic_data['answer'] = player.answer

        # sub-dict específico de Stage 1
        stage1 = topic_data.setdefault('stage_1', {})
        stage1['wtl'] = player.wtl
        stage1['min_opp_punish'] = player.min_opp_punish

        # (opcional) debug:
        # import pprint
        # print(f"[DEBUG S1] Guardado {key} para p {player.id_in_subsession}")
        # pprint.pprint(player.participant.vars)


class ThankYouPage(Page):
    @staticmethod
    def is_displayed(player: Player) -> bool:
        return player.round_number == C.NUM_ROUNDS

    @staticmethod
    def vars_for_template(player: Player) -> dict:
        return {}


page_sequence = [
    BinaryQuestionsPage_Practice,
    BinaryQuestionsPage,
    ThankYouPage,
]