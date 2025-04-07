from __future__ import annotations  # For postponed evaluation of annotations
from otree.api import *
import random, json, logging
from typing import List, Tuple

# Define the full survey questions as a module-level constant.
SURVEY_QUESTIONS = [
    "¿La quesadilla lleva o no queso?",
    "¿El arte que se exhibe en los museos de arte contemporáneo ya no tiene el mismo virtuosismo que el arte en los museos clásicos?",
    "¿Qué es más importante, afrontar la crisis climática o terminar la pobreza extrema en México?",
    "¿Estás de acuerdo con la frase 'no hay paz sin la violencia'?",
    "¿Estás de acuerdo con la nueva ley antitabaco en México?",
    "¿Qué es lo más higiénico, bañarse en la mañana o en la noche?",
    "¿Crees que las relaciones a distancia pueden ser tan satisfactorias como las relaciones en persona?",
    "Una persona rica y grosera tira un billete de cien pesos sin darse cuenta. ¿Se lo regresas?",
    "¿Qué es mejor, la Condesa o Coyoacán?",
    "¿Qué equipo de futbol es mejor: el América o las Chivas?"
]

FIRST_OPTIONS = [
    "Sí, la quesadilla lleva queso",
    "Sí tiene el mismo virtuosismo",
    "Afrontar la crisis climática",
    "De acuerdo",
    "De acuerdo",
    "Bañarse en la mañana",
    "Sí lo pueden ser",
    "Sí, se lo regreso",
    "La Condesa",
    "El América"
]

# New constant with both answer options for each survey question
SURVEY_OPTIONS = [
    ("Sí, la quesadilla lleva queso", "No, la quesadilla no lleva queso"),
    ("Sí tiene el mismo virtuosismo", "No tiene el mismo virtuosismo"),
    ("Afrontar la crisis climática", "Terminar la pobreza extrema en México"),
    ("De acuerdo", "En desacuerdo"),
    ("De acuerdo", "En desacuerdo"),
    ("Bañarse en la mañana", "Bañarse en la noche"),
    ("Sí lo pueden ser", "No pueden llegar a serlo"),
    ("Sí, se lo regreso", "No, no se lo regreso"),
    ("La Condesa", "Coyoacán"),
    ("El América", "Las Chivas")
]

# -----------------------------------------------------------------------------
# Logging configuration for debugging
# -----------------------------------------------------------------------------
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# -----------------------------------------------------------------------------
# Constants and Helper Functions
# -----------------------------------------------------------------------------
class C(BaseConstants):
    NAME_IN_URL = 'experiment'
    PLAYERS_PER_GROUP = 2
    NUM_BINARY_QUESTIONS = 10  # updated to 10 questions
    NUM_ROUNDS = NUM_BINARY_QUESTIONS + 1  # now 11 rounds total

def set_partner(player: Player, partner: Player) -> None:
    """Store the partner's id_in_subsession in player's partner_id field."""
    player.partner_id = partner.id_in_subsession

def get_partner(player: Player) -> Player:
    """Retrieve the player's partner using the stored partner_id."""
    for p in player.subsession.get_players():
        if p.id_in_subsession == player.partner_id:
            return p
    return None

# -----------------------------------------------------------------------------
# Models
# -----------------------------------------------------------------------------
class Subsession(BaseSubsession):
    def creating_session(self) -> None:
        # Nothing special in round 1; stage-1 responses are collected on survey pages.
        pass

class Group(BaseGroup):
    pass

class Player(BasePlayer):
    # Consent field: participants must affirm their informed consent.
    consent = models.BooleanField(
        label="He leído y doy mi consentimiento para participar en el estudio.",
        widget=widgets.CheckboxInput
    )
    
    # Personal information fields:
    age = models.IntegerField(label="Edad", min=18)
    gender = models.StringField(
        choices=[('M', 'Masculino'), ('F', 'Femenino'), ('O', 'Otro')],
        label="Sexo"
    )
    racial_identification = models.StringField(
        choices=[
            ('Mestizo', 'Mestiza/o'),
            ('Indigena', 'Indígena'),
            ('Caucasico', 'Caucásico'),
            ('Afro', 'Afrodescendiente'),
            ('Asiatico', 'Asiática/o'),
            ('Arabe', 'Árabe'),
            ('Otros', 'Otros:')
        ],
        label="¿Cómo te identificas racialmente?"
    )
    previous_experiment = models.IntegerField(
        label="¿En cuántos experimentos has participado previamente?",
        min=0
    )
    

    # Binary survey responses for 10 questions with custom labels:
    binary_choice_1 = models.StringField(
        choices=[('H', "Sí, la quesadilla lleva queso"), ('L', "No, la quesadilla no lleva queso")],
        blank=False
    )
    binary_choice_2 = models.StringField(
        choices=[('H', "Sí tiene el mismo virtuosismo"), ('L', "No tiene el mismo virtuosismo")],
        blank=False
    )
    binary_choice_3 = models.StringField(
        choices=[('H', "Afrontar la crisis climática"), ('L', "Terminar la pobreza extrema")],
        blank=False
    )
    binary_choice_4 = models.StringField(
        choices=[('H', "De acuerdo"), ('L', "En desacuerdo")],
        blank=False
    )
    binary_choice_5 = models.StringField(
        choices=[('H', "De acuerdo"), ('L', "En desacuerdo")],
        blank=False
    )
    binary_choice_6 = models.StringField(
        choices=[('H', "Bañarse en la mañana"), ('L', "Bañarse en la noche")],
        blank=False
    )
    binary_choice_7 = models.StringField(
        choices=[('H', "Sí lo pueden ser"), ('L', "No pueden llegar a serlo")],
        blank=False
    )
    binary_choice_8 = models.StringField(
        choices=[('H', "Sí, se lo regreso"), ('L', "No, no se lo regreso")],
        blank=False
    )
    binary_choice_9 = models.StringField(
        choices=[('H', "La Condesa"), ('L', "Coyoacán")],
        blank=False
    )
    binary_choice_10 = models.StringField(
        choices=[('H', "El América"), ('L', "Las Chivas")],
        blank=False
    )

    # Updated willingness-to-judge fields with custom display choices:
    pay_to_judge_1 = models.BooleanField(
        choices=[[True, "Sí estoy dispuesto"], [False, "No estoy dispuesto"]],
        blank=False
    )
    pay_to_judge_2 = models.BooleanField(
        choices=[[True, "Sí estoy dispuesto"], [False, "No estoy dispuesto"]],
        blank=False
    )
    pay_to_judge_3 = models.BooleanField(
        choices=[[True, "Sí estoy dispuesto"], [False, "No estoy dispuesto"]],
        blank=False
    )
    pay_to_judge_4 = models.BooleanField(
        choices=[[True, "Sí estoy dispuesto"], [False, "No estoy dispuesto"]],
        blank=False
    )
    pay_to_judge_5 = models.BooleanField(
        choices=[[True, "Sí estoy dispuesto"], [False, "No estoy dispuesto"]],
        blank=False
    )
    pay_to_judge_6 = models.BooleanField(
        choices=[[True, "Sí estoy dispuesto"], [False, "No estoy dispuesto"]],
        blank=False
    )
    pay_to_judge_7 = models.BooleanField(
        choices=[[True, "Sí estoy dispuesto"], [False, "No estoy dispuesto"]],
        blank=False
    )
    pay_to_judge_8 = models.BooleanField(
        choices=[[True, "Sí estoy dispuesto"], [False, "No estoy dispuesto"]],
        blank=False
    )
    pay_to_judge_9 = models.BooleanField(
        choices=[[True, "Sí estoy dispuesto"], [False, "No estoy dispuesto"]],
        blank=False
    )
    pay_to_judge_10 = models.BooleanField(
        choices=[[True, "Sí estoy dispuesto"], [False, "No estoy dispuesto"]],
        blank=False
    )

    # The rest of your fields remain unchanged.
    treatment = models.LongStringField(blank=False)
    second_choice = models.StringField(choices=['H', 'L'], blank=False)
    juicio = models.StringField(choices=['Positivo', 'Negativo'], blank=False)
    Mentira = models.StringField(choices=['Sí', 'No'], blank=False, label="¿Crees que tu compañero mintió?")
    partner_id = models.IntegerField(blank=True, null=True)
    
    # New field: Tag to capture the binary question used for grouping in each round (Stage 2)
    current_question_tag = models.StringField(blank=True)

# -----------------------------------------------------------------------------
# Pairing Function for Group Interaction Rounds (Stage 2)
# -----------------------------------------------------------------------------
def pair_players(subsession: Subsession) -> None:
    current_round = subsession.round_number
    if current_round == 1:
        # Do nothing in the survey round.
        return

    players = subsession.get_players()
    # Retrieve the common random ordering of question indices generated in round 1.
    question_order = subsession.session.vars.get('question_order', list(range(C.NUM_BINARY_QUESTIONS)))
    # For stage-2 round r (r>=2), the corresponding survey question index is:
    question_index = question_order[current_round - 2]

    # Build pools based on each player's answer for the current survey question.
    H_pool: List[Player] = [
        p for p in players
        if p.participant.vars['binary_choices'][question_index] == 'H'
    ]
    L_pool: List[Player] = [
        p for p in players
        if p.participant.vars['binary_choices'][question_index] == 'L'
    ]
    logger.debug(f"Round {current_round}: H_pool: {[p.id_in_subsession for p in H_pool]}, L_pool: {[p.id_in_subsession for p in L_pool]}")
    paired_groups: List[Tuple[Player, Player]] = []

    while H_pool and L_pool:
        prob_H = random.choice([0.5, 0.7])
        logger.debug(f"Round {current_round}: Chosen treatment probability: {prob_H}")
        candidate_H = H_pool.pop()
        candidate_L = L_pool.pop()
        if random.random() < prob_H:
            first_member = candidate_H
            L_pool.append(candidate_L)  # delay pairing candidate_L
            logger.debug(f"Round {current_round}: Member 1 from H: {first_member.id_in_subsession}; returned L candidate {candidate_L.id_in_subsession}")
        else:
            first_member = candidate_L
            H_pool.append(candidate_H)  # delay pairing candidate_H
            logger.debug(f"Round {current_round}: Member 1 from L: {first_member.id_in_subsession}; returned H candidate {candidate_H.id_in_subsession}")

        if H_pool and L_pool:
            candidate_H2 = H_pool.pop()
            candidate_L2 = L_pool.pop()
            if random.random() < prob_H:
                second_member = candidate_H2
                L_pool.append(candidate_L2)
                logger.debug(f"Round {current_round}: Member 2 from H: {second_member.id_in_subsession}; returned L candidate {candidate_L2.id_in_subsession}")
            else:
                second_member = candidate_L2
                H_pool.append(candidate_H2)
                logger.debug(f"Round {current_round}: Member 2 from L: {second_member.id_in_subsession}; returned H candidate {candidate_H2.id_in_subsession}")

            inform = random.choice([True, False])
            treatment = {'prob_H': prob_H, 'inform': inform}
            for p in [first_member, second_member]:
                p.treatment = json.dumps(treatment)
            set_partner(first_member, second_member)
            set_partner(second_member, first_member)
            paired_groups.append((first_member, second_member))
            logger.debug(f"Round {current_round}: Paired players: {first_member.id_in_subsession} and {second_member.id_in_subsession}")
        else:
            # Not enough candidates for pairing.
            if first_member.participant.vars['binary_choices'][question_index] == 'H':
                H_pool.append(first_member)
            else:
                L_pool.append(first_member)
            break

    remaining_players = H_pool + L_pool
    random.shuffle(remaining_players)
    while len(remaining_players) >= 2:
        member1 = remaining_players.pop()
        member2 = remaining_players.pop()
        inform = random.choice([True, False])
        treatment = {'prob_H': 'Control', 'inform': inform}
        for p in [member1, member2]:
            p.treatment = json.dumps(treatment)
        set_partner(member1, member2)
        set_partner(member2, member1)
        paired_groups.append((member1, member2))
        logger.debug(f"Round {current_round}: Control paired players: {member1.id_in_subsession} and {member2.id_in_subsession}")

    subsession.set_group_matrix(paired_groups)
    logger.debug(f"Round {current_round}: Set new group matrix: {[[p.id_in_subsession for p in pair] for pair in paired_groups]}")

# -----------------------------------------------------------------------------
# Page Definitions
# -----------------------------------------------------------------------------
# Stage 1: Survey pages (only in round 1)
class IntroductionPage(Page):
    # This page is only shown in round 1
    @staticmethod
    def is_displayed(player: Player) -> bool:
        return player.round_number == 1

    @staticmethod
    def vars_for_template(player: Player) -> dict:
        return {}

class ExperimentInstructions(Page):
    template_name = 'experiment/ExperimentInstructions.html'

    @staticmethod
    def is_displayed(player: Player) -> bool:
        return player.round_number == 1

    @staticmethod
    def vars_for_template(player: Player) -> dict:
        return {}

class ConsentFormPage(Page):
    form_model = 'player'
    form_fields = ['consent']
    
    @staticmethod
    def is_displayed(player: Player) -> bool:
        return player.round_number == 1

class PersonalInfoPage(Page):
    form_model = 'player'
    form_fields = ['age', 'gender', 'racial_identification', 'previous_experiment']
    
    @staticmethod
    def is_displayed(player: Player) -> bool:
        return player.round_number == 1

class BinaryQuestions(Page):
    form_model = 'player'
    
    @staticmethod
    def get_form_fields(player: Player):
        return [f"binary_choice_{i}" for i in range(1, C.NUM_BINARY_QUESTIONS + 1)]
    
    @staticmethod
    def is_displayed(player: Player) -> bool:
        return player.round_number == 1

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = kwargs.get('form')
        field_names = [f"binary_choice_{i}" for i in range(1, C.NUM_BINARY_QUESTIONS + 1)]
        context['rendered_fields'] = [form[field_name] for field_name in field_names]
        context['question_list'] = list(range(1, C.NUM_BINARY_QUESTIONS + 1))
        return context

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        binary_choices = []
        for i in range(1, C.NUM_BINARY_QUESTIONS + 1):
            field_name = f"binary_choice_{i}"
            binary_choices.append(getattr(player, field_name))
        player.participant.vars['binary_choices'] = binary_choices
        logger.debug(f"Stored binary_choices: {binary_choices}")

class WillingnessToPayCost(Page):
    form_model = 'player'
    
    @staticmethod
    def get_form_fields(player: Player):
        return [f"pay_to_judge_{i}" for i in range(1, C.NUM_BINARY_QUESTIONS + 1)]
    
    @staticmethod
    def is_displayed(player: Player) -> bool:
        return player.round_number == 1
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = kwargs.get('form')
        field_names = [f"pay_to_judge_{i}" for i in range(1, C.NUM_BINARY_QUESTIONS + 1)]
        rendered_fields = [form[field_name] for field_name in field_names]
        question_texts = SURVEY_QUESTIONS  
        context['questions_and_fields'] = list(zip(question_texts, rendered_fields))
        return context

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        pay_choices = []
        for i in range(1, C.NUM_BINARY_QUESTIONS + 1):
            field_name = f"pay_to_judge_{i}"
            pay_choices.append(getattr(player, field_name))
        player.participant.vars['pay_to_judge_choices'] = pay_choices
        logger.debug(f"Stored pay_to_judge_choices: {pay_choices}")

class SurveyWaitPage(WaitPage):
    wait_for_all_groups = True

    @staticmethod
    def is_displayed(player: Player) -> bool:
        return player.round_number == 1

    @staticmethod
    def after_all_players_arrive(subsession: Subsession):
        if 'question_order' not in subsession.session.vars:
            order = list(range(C.NUM_BINARY_QUESTIONS))
            random.shuffle(order)
            subsession.session.vars['question_order'] = order
            logger.debug(f"SurveyWaitPage set question_order: {order}")

# Stage 2: Group interaction pages (only for rounds > 1)
class GroupingWaitPage(WaitPage):
    wait_for_all_groups = True
    @staticmethod
    def is_displayed(player: Player) -> bool:
        return player.round_number > 1

    @staticmethod
    def after_all_players_arrive(subsession: Subsession):
        pair_players(subsession)

class TreatmentInformation(Page):
    @staticmethod
    def is_displayed(player: Player) -> bool:
        return player.round_number > 1

    @staticmethod
    def vars_for_template(player: Player) -> dict:
        # Get the index for the current survey question used for grouping.
        question_order = player.session.vars['question_order']
        question_index = question_order[player.round_number - 2]
        
        # Get the current question text from SURVEY_QUESTIONS.
        current_question = SURVEY_QUESTIONS[question_index]
        # Update the player's tag (no need to call player.save())
        player.current_question_tag = current_question
        
        # Retrieve the first option text for the current question.
        first_option = FIRST_OPTIONS[question_index]
        
        # Calculate the percentage of players willing to pay.
        players = player.subsession.get_players()
        judge_yes = sum(
            1 for p in players
            if p.participant.vars['pay_to_judge_choices'][question_index]
        )
        judge_percent = (judge_yes / len(players)) * 100 if players else 0
        
        # Load the treatment stored in player.treatment.
        try:
            treatment = json.loads(player.treatment)
        except (TypeError, json.JSONDecodeError):
            treatment = {'prob_H': 'Control', 'inform': False}
        
        # Build the partner selection text.
        if treatment['prob_H'] == "Control":
            selection_text = "Escogimos al otro compañero de manera aleatoria, sin considerar su respuesta a la pregunta actual."
        elif treatment['prob_H'] == 0.5:
            selection_text = f"La probabilidad de que el otro compañero prefiera '{first_option}' a la pregunta '{current_question}' es del 50%."
        elif treatment['prob_H'] == 0.7:
            selection_text = f"La probabilidad de que el otro compañero prefiera '{first_option}' a la pregunta '{current_question}' es del 70%."
        else:
            selection_text = "Método de agrupación desconocido."
        
        # Construct the complete treatment message.
        treatment_text = (
            f"Bienvenido a la ronda {player.round_number-1} de interacción grupal. "
            f"Te hemos agrupado con otro compañero de la siguiente forma: "
            f"Hemos usado la pregunta: '{current_question}' para agruparte con otro compañero. "
            f"{selection_text} "
            f"Ahora pasarán a la interacción grupal donde ambos responderán simultáneamente a la pregunta: '{current_question}' de manera pública."
        )
        
        if treatment.get('inform'):
            treatment_text += f" Te informamos que el {judge_percent:.0f}% de los participantes totales están dispuestos a incurrir en el costo de juzgar."
        
        return {'treatment_text': treatment_text}


class PublicDecision(Page):
    form_model = 'player'
    form_fields = ['second_choice']
    
    @staticmethod
    def is_displayed(player: Player) -> bool:
        return player.round_number > 1

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        question_order = self.player.session.vars['question_order']
        question_index = question_order[self.player.round_number - 2]
        current_question = SURVEY_QUESTIONS[question_index]
        options = SURVEY_OPTIONS[question_index]
        
        form = kwargs.get('form')
        if form:
            form.second_choice.choices = [('H', options[0]), ('L', options[1])]
            form.second_choice.label = current_question
        
        context.update({
            'current_question': current_question,
            'options': options,
        })
        return context

class SecondDecisionWaitPageForGroup(WaitPage):
    wait_for_all_groups = False
    template_name = 'otree/WaitPage.html'
    
    @staticmethod
    def is_displayed(player: Player) -> bool:
        return player.round_number > 1

class PublicDisplayPage(Page):
    @staticmethod
    def is_displayed(player: Player) -> bool:
        return player.round_number > 1

    @staticmethod
    def vars_for_template(player: Player) -> dict:
        partner = get_partner(player)
        question_order = player.session.vars['question_order']
        question_index = question_order[player.round_number - 2]
        current_question = SURVEY_QUESTIONS[question_index]
        options = SURVEY_OPTIONS[question_index]
        
        if partner:
            if partner.second_choice == 'H':
                partner_choice_text = options[0]
            elif partner.second_choice == 'L':
                partner_choice_text = options[1]
            else:
                partner_choice_text = "No ha respondido"
        else:
            partner_choice_text = "No se asignó compañero"
        return {'partner_choice': partner_choice_text, 'current_question': current_question}

class JudgeOpinionPage(Page):
    form_model = 'player'
    form_fields = ['juicio']

    @staticmethod
    def is_displayed(player: Player) -> bool:
        question_order = player.session.vars['question_order']
        question_index = question_order[player.round_number - 2]
        return player.round_number > 1 and player.participant.vars['pay_to_judge_choices'][question_index]

    @staticmethod
    def vars_for_template(player: Player) -> dict:
        partner = get_partner(player)
        question_order = player.session.vars['question_order']
        question_index = question_order[player.round_number - 2]
        current_question = SURVEY_QUESTIONS[question_index]
        options = SURVEY_OPTIONS[question_index]
        
        if partner:
            if partner.second_choice == 'H':
                partner_choice_text = options[0]
            elif partner.second_choice == 'L':
                partner_choice_text = options[1]
            else:
                partner_choice_text = "No ha respondido"
        else:
            partner_choice_text = "No se asignó compañero"
        return {'partner_choice': partner_choice_text, 'current_question': current_question}

class LieQuestionPage(Page):
    form_model = 'player'
    form_fields = ['Mentira']

    @staticmethod
    def is_displayed(player: Player) -> bool:
        return player.round_number > 1

    @staticmethod
    def vars_for_template(player: Player) -> dict:
        partner = get_partner(player)
        question_order = player.session.vars['question_order']
        question_index = question_order[player.round_number - 2]
        current_question = SURVEY_QUESTIONS[question_index]
        options = SURVEY_OPTIONS[question_index]
        
        if partner:
            if partner.second_choice == 'H':
                partner_choice_text = options[0]
            elif partner.second_choice == 'L':
                partner_choice_text = options[1]
            else:
                partner_choice_text = "No ha respondido"
        else:
            partner_choice_text = "No se asignó compañero"
        return {'partner_choice': partner_choice_text, 'current_question': current_question}

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
    IntroductionPage,
    ExperimentInstructions,
    ConsentFormPage,
    PersonalInfoPage,
    BinaryQuestions,
    WillingnessToPayCost,
    SurveyWaitPage,
    GroupingWaitPage,
    TreatmentInformation,
    PublicDecision,
    SecondDecisionWaitPageForGroup,
    PublicDisplayPage,
    JudgeOpinionPage,
    LieQuestionPage,
    ThankYouPage
]


