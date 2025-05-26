from __future__ import annotations  # For postponed evaluation of annotations
from otree.api import *
import random, json, logging
from typing import List, Tuple

# Define the full survey questions as a module-level constant.
PRACTICE_QUESTION = "¿Qué color es mejor, el rojo o el azul?"
PRACTICE_OPTIONS = ("El rojo", "El azul")
PRACTICE_FIRST_OPTION = "El rojo"
PRACTICE_SECOND_OPTION = "El azul"

SURVEY_QUESTIONS = [
    "¿La quesadilla lleva o no queso?",
    "Verdadero o falso: El arte que se exhibe en los museos de arte contemporáneo ya no tiene el mismo virtuosismo que el arte en los museos clásicos",
    "¿Qué es más importante, afrontar la crisis climática o terminar la pobreza extrema en el mundo?",
    "¿Estás de acuerdo con la frase 'no hay paz sin la violencia'?",
    "​¿Estás de acuerdo con las recientes reformas a la Ley General para el Control del Tabaco en México que prohíben fumar en espacios públicos como playas, parques y plazas comerciales?",
    "¿Qué es lo más higiénico, bañarse en la mañana o en la noche?",
    "¿Crees que las relaciones a distancia pueden ser tan exitosas como las relaciones en persona?",
    "Una persona rica y grosera tira un billete de cien pesos sin darse cuenta. ¿Deberías devolvérselo?",
    "¿Qué lugar es mejor, la Condesa o Coyoacán?",
    "¿Qué equipo de futbol es mejor: el América o las Chivas?"
]

FIRST_OPTIONS = [
    "Sí, la quesadilla lleva queso",
    "Verdadero",
    "Afrontar la crisis climática",
    "De acuerdo",
    "De acuerdo",
    "Bañarse en la mañana",
    "Sí lo pueden ser",
    "Sí, debería devolvérselo",
    "La Condesa",
    "El América"
]

SECOND_OPTIONS = [
    "No, la quesadilla no lleva queso",
    "Falso",
    "Terminar la pobreza extrema en el mundo",
    "En desacuerdo",
    "En desacuerdo",
    "Bañarse en la noche",
    "No pueden llegar a serlo",
    "No, no debería devolvérselo",
    "Coyoacán",
    "Las Chivas"
]

# New constant with both answer options for each survey question
SURVEY_OPTIONS = [
    ("Sí, la quesadilla lleva queso", "No, la quesadilla no lleva queso"),
    ("Verdadero", "Falso"),
    ("Afrontar la crisis climática", "Terminar la pobreza extrema en el mundo"),
    ("De acuerdo", "En desacuerdo"),
    ("De acuerdo", "En desacuerdo"),
    ("Bañarse en la mañana", "Bañarse en la noche"),
    ("Sí lo pueden ser", "No pueden llegar a serlo"),
    ("Sí, debería devolvérselo", "No, no debería devolvérselo"),
    ("La Condesa", "Coyoacán"),
    ("El América", "Las Chivas")
]

# -----------------------------------------------------------------------------
# Logging configuration for debugging
# -----------------------------------------------------------------------------
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# --------------------------------------------------------------------
# Utilidad: sortear el tratamiento según las probabilidades pedidas
# --------------------------------------------------------------------
def draw_treatment() -> Tuple[float, str]:
    u = random.random()
    if u < 0.5:
        return 0.5, '0.5_H'
    elif u < 0.75:
        return 0.7, '0.7_H'
    else:
        return 0.3, '0.7_L'



# -----------------------------------------------------------------------------
# Constants and Helper Functions
# -----------------------------------------------------------------------------
class C(BaseConstants):
    NAME_IN_URL = 'experiment_phase'
    PLAYERS_PER_GROUP = 3
    NUM_BINARY_QUESTIONS = 10  # updated to 10 questions
    NUM_ROUNDS = 13  # now 13 rounds total


def get_partners(player: Player) -> List[Player]:
    ids = json.loads(player.partner_ids or "[]")
    return [p for p in player.subsession.get_players() if p.id_in_subsession in ids]


# -----------------------------------------------------------------------------
# Models
# -----------------------------------------------------------------------------
class Subsession(BaseSubsession):
    def creating_session(self):
        # Si no existe, créalo y GUAŔDALO inmediatamente
        if 'HL_map' not in self.session.vars:
            hl_map = [random.choice([True, False])
                      for _ in range(C.NUM_BINARY_QUESTIONS)]
            self.session.vars['HL_map'] = hl_map
            # use warning en lugar de debug para que siempre se vea en consola
            logger.warning(f"HL_map creado en creating_session: {hl_map}")




class Group(BaseGroup):
    pass

class Player(BasePlayer):
    # Consent field: participants must affirm their informed consent.
    consent = models.BooleanField(
        label="He leído y doy mi consentimiento para participar en el estudio.",
        widget=widgets.CheckboxInput
    )
    
    # New fields for the Practice Round (pre-practice survey)
    practice_binary_choice = models.StringField(
        choices=[('H', "El rojo"), ('L', "El azul")],
        blank=False,
        doc="Tema de Conversación: ¿Qué color es mejor, el rojo o el azul?"
    )
    practice_pay_to_judge = models.BooleanField(
        choices=[[True, "Sí"], [False, "No"]],
        blank=False,
        doc="Respuesta de práctica sobre disposición a incurrir en el costo"
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
        choices=[('H', "Verdadero"), ('L', "Falso")],
        blank=False
    )
    binary_choice_3 = models.StringField(
        choices=[('H', "Afrontar la crisis climática"), ('L', "Terminar la pobreza extrema en el mundo")],
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
        choices=[('H', "Sí, debería devolvérselo"), ('L', "No, no debería devolvérselo")],
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
        choices=[[True, "Sí"], [False, "No"]],
        blank=False
    )
    pay_to_judge_2 = models.BooleanField(
        choices=[[True, "Sí"], [False, "No"]],
        blank=False
    )
    pay_to_judge_3 = models.BooleanField(
        choices=[[True, "Sí"], [False, "No"]],
        blank=False
    )
    pay_to_judge_4 = models.BooleanField(
        choices=[[True, "Sí"], [False, "No"]],
        blank=False
    )
    pay_to_judge_5 = models.BooleanField(
        choices=[[True, "Sí"], [False, "No"]],
        blank=False
    )
    pay_to_judge_6 = models.BooleanField(
        choices=[[True, "Sí"], [False, "No"]],
        blank=False
    )
    pay_to_judge_7 = models.BooleanField(
        choices=[[True, "Sí"], [False, "No"]],
        blank=False
    )
    pay_to_judge_8 = models.BooleanField(
        choices=[[True, "Sí"], [False, "No"]],
        blank=False
    )
    pay_to_judge_9 = models.BooleanField(
        choices=[[True, "Sí"], [False, "No"]],
        blank=False
    )
    pay_to_judge_10 = models.BooleanField(
        choices=[[True, "Sí"], [False, "No"]],
        blank=False
    )

    treatment = models.LongStringField(blank=False)
    second_choice = models.StringField(choices=['H', 'L'], blank=False)
    juicio_1 = models.StringField(
        choices=[
            ('GIVE',  'Dar 20 pesos a este compañero'),
            ('TAKE',  'Quitar 20 pesos a este compañero')
        ],
        blank=False,
        label='Decide para tu primer compañero'
    )
    juicio_2 = models.StringField(
        choices=[
            ('GIVE',  'Dar 20 pesos a este compañero'),
            ('TAKE',  'Quitar 20 pesos a este compañero')
        ],
        blank=False,
        label='Decide para tu segundo compañero'
    )
    mentira_1 = models.StringField(choices=['Sí','No'], label='¿Consideras que la opinión que tu primer compañero te expresó es la misma que nos expresó en privado?')
    mentira_2 = models.StringField(choices=['Sí','No'], label='¿Consideras que la opinión que tu segundo compañero te expresó es la misma que nos expresó en privado?')
    partner_ids = models.LongStringField(
        blank=True,
        doc="JSON list of the other two id_in_subsession in my group"
    )
    
    # New field: Tag to capture the binary question used for grouping in each round (Stage 2)
    current_question_tag = models.StringField(blank=True)

# -------------------------------------------------------------
# 1.  Emparejamiento en la RONDA DE PRÁCTICA
# -------------------------------------------------------------
def practice_pair_players(subsession: Subsession) -> None:
    players = subsession.get_players()
    H_pool  = [p for p in players if p.participant.vars.get('practice_binary_choice') == 'H']
    L_pool  = [p for p in players if p.participant.vars.get('practice_binary_choice') == 'L']
    groups: list[list[Player]] = []
    GROUP_SIZE = 3

    while H_pool and L_pool and len(H_pool) + len(L_pool) >= GROUP_SIZE:

        prob_H, tlabel = draw_treatment()
        inform        = random.choice([True, False])
        failed_attempts = 0

        while failed_attempts < 5:            # ≤ 5 intentos con este tratamiento
            tentative: list[tuple[Player, str]] = []

            for _ in range(GROUP_SIZE):
                pick_H = (random.random() < prob_H and H_pool) or not L_pool
                if pick_H:
                    tentative.append((H_pool.pop(), 'H'))
                else:
                    tentative.append((L_pool.pop(), 'L'))

                if not H_pool or not L_pool:   # pool agotado → revertir
                    for p, pool in tentative:
                        (H_pool if pool == 'H' else L_pool).append(p)
                    failed_attempts += 1
                    break
            else:
                # éxito: formamos el trío definitivo
                trio = [tpl[0] for tpl in tentative]
                treatment = {'prob_H': prob_H,
                             'label' : tlabel,
                             'inform': inform,
                             'practice': True}
                for p in trio:
                    p.treatment   = json.dumps(treatment)
                    p.partner_ids = json.dumps([q.id_in_subsession for q in trio if q != p])
                groups.append(trio)
                break        # sale del while failed_attempts

        # si fallamos 5 veces, no volvemos a intentar con este tratamiento
        if failed_attempts >= 5:
            break

    # ---------- remanentes = grupos Control ----------
    rem = H_pool + L_pool
    random.shuffle(rem)
    while len(rem) >= GROUP_SIZE:
        trio = [rem.pop() for _ in range(GROUP_SIZE)]
        treatment = {'label': 'Control', 'inform': random.choice([True, False]), 'practice': True}
        for p in trio:
            p.treatment   = json.dumps(treatment)
            p.partner_ids = json.dumps([q.id_in_subsession for q in trio if q != p])
        groups.append(trio)

    subsession.set_group_matrix(groups)


# -------------------------------------------------------------
# 2.  Emparejamiento en RONDAS 4-13
# -------------------------------------------------------------
def pair_players(subsession: Subsession) -> None:
    if subsession.round_number <= 3:
        return

    order = subsession.session.vars['question_order']
    qi    = order[subsession.round_number - 4]

    players = subsession.get_players()
    H_pool  = [p for p in players if p.participant.vars['binary_choices'][qi] == 'H']
    L_pool  = [p for p in players if p.participant.vars['binary_choices'][qi] == 'L']
    groups: list[list[Player]] = []
    GROUP_SIZE = 3

    while H_pool and L_pool and len(H_pool) + len(L_pool) >= GROUP_SIZE:

        prob_H, tlabel = draw_treatment()
        inform        = random.choice([True, False])
        failed_attempts = 0

        while failed_attempts < 5:
            tentative: list[tuple[Player, str]] = []

            for _ in range(GROUP_SIZE):
                pick_H = (random.random() < prob_H and H_pool) or not L_pool
                if pick_H:
                    tentative.append((H_pool.pop(), 'H'))
                else:
                    tentative.append((L_pool.pop(), 'L'))

                if not H_pool or not L_pool:
                    for p, pool in tentative:
                        (H_pool if pool == 'H' else L_pool).append(p)
                    failed_attempts += 1
                    break
            else:
                trio = [tpl[0] for tpl in tentative]
                treatment = {'prob_H': prob_H, 'label': tlabel, 'inform': inform}
                for p in trio:
                    p.treatment   = json.dumps(treatment)
                    p.partner_ids = json.dumps([q.id_in_subsession for q in trio if q != p])
                groups.append(trio)
                break

        if failed_attempts >= 5:
            break

    # ---------- remanentes = grupos Control ----------
    rem = H_pool + L_pool
    random.shuffle(rem)
    while len(rem) >= GROUP_SIZE:
        trio = [rem.pop() for _ in range(GROUP_SIZE)]
        treatment = {'label': 'Control', 'inform': random.choice([True, False])}
        for p in trio:
            p.treatment   = json.dumps(treatment)
            p.partner_ids = json.dumps([q.id_in_subsession for q in trio if q != p])
        groups.append(trio)

    subsession.set_group_matrix(groups)




# -----------------------------------------------------------------------------
# Page Definitions
# -----------------------------------------------------------------------------
# Stage 1: Survey pages (only in round 1)
class ConsentFormPage(Page):
    form_model = 'player'
    form_fields = ['consent']
    
    @staticmethod
    def is_displayed(player: Player) -> bool:
        return player.round_number == 1

class IntroductionPage(Page):
    # This page is only shown in round 1
    @staticmethod
    def is_displayed(player: Player) -> bool:
        return player.round_number == 1

    @staticmethod
    def vars_for_template(player: Player) -> dict:
        return {}

class ExperimentInstructions(Page):
    template_name = 'experiment_phase/ExperimentInstructions.html'

    @staticmethod
    def is_displayed(player: Player) -> bool:
        return player.round_number == 1

    @staticmethod
    def vars_for_template(player: Player) -> dict:
        return {}

class PracticeBinaryQuestion(Page):
    form_model = 'player'
    form_fields = ['practice_binary_choice']
    
    # Display this page only in Round 1 (practice stage added after consent)
    @staticmethod
    def is_displayed(player: Player) -> bool:
        return player.round_number == 1

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Set the practice question and options.
        context.update({
            'practice_question': PRACTICE_QUESTION,
            'practice_options': PRACTICE_OPTIONS,
            'practice_notice': "ESTO ES UNA PRÁCTICA. La respuesta no contará para el estudio.",
        })
        return context

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        # Optionally, store the practice response in participant.vars if preferred.
        player.participant.vars['practice_binary_choice'] = player.practice_binary_choice
        logger.debug(f"Stored practice_binary_choice: {player.practice_binary_choice}")

class PracticeWillingnessToPayCost(Page):
    form_model = 'player'
    form_fields = ['practice_pay_to_judge']

    @staticmethod
    def is_displayed(player: Player) -> bool:
        return player.round_number == 1

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Use the PRACTICE_QUESTION as the reference text for judging.
        context['practice_question'] = PRACTICE_QUESTION
        context['practice_notice'] = "ESTO ES UNA PRÁCTICA. La respuesta no se usará en el emparejamiento real."
        # Here you can hardcode the question text or even add extra instructions
        return context

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.participant.vars['practice_pay_to_judge'] = player.practice_pay_to_judge
        logger.debug(f"Stored practice_pay_to_judge: {player.practice_pay_to_judge}")

class PracticeSurveyWaitPage(WaitPage):
    wait_for_all_groups = True

    @staticmethod
    def is_displayed(player: Player) -> bool:
        return player.round_number == 1

    @staticmethod
    def after_all_players_arrive(subsession: Subsession):
        # (Optional) Log that all practice responses were received.
        logger.debug("All players have completed the practice survey.")

class PracticeGroupingWaitPage(WaitPage):
    wait_for_all_groups = True

    @staticmethod
    def is_displayed(player: Player) -> bool:
        return player.round_number == 2

    @staticmethod
    def after_all_players_arrive(subsession: Subsession):
        practice_pair_players(subsession)

class PracticeTreatmentInformation(Page):
    @staticmethod
    def is_displayed(player: Player) -> bool:
        return player.round_number == 2

    @staticmethod
    def vars_for_template(player: Player) -> dict:
        current_question = PRACTICE_QUESTION
        player.current_question_tag = current_question

        first_option = PRACTICE_FIRST_OPTION
        second_option = PRACTICE_SECOND_OPTION

        players = player.subsession.get_players()
        judge_yes = sum(
            1 for p in players
            if p.participant.vars.get('practice_pay_to_judge')
        )
        judge_percent = (judge_yes / len(players)) * 100 if players else 0
        logger.debug(f"[PAGE] P{player.id_in_subsession} treatment crudo: {player.treatment}")
        try:
            treatment = json.loads(player.treatment)
        except (TypeError, json.JSONDecodeError):
            treatment = {'label': 'Control', 'inform': False, 'practice': True}

        # Selección según tratamiento
        if treatment.get('label') == '0.5_H':
            selection_text = (
                f"Para determinar cada individuo del trío, tomamos un grupo de diez candidatos. "
                f"Hay <strong>cinco</strong> a favor de '{first_option}' y "
                f"<strong>cinco</strong> a favor de '{second_option}'. Escogemos uno al azar."
            )
        elif treatment.get('label') == '0.7_H':
            selection_text = (
                f"Para determinar cada individuo del trío, tomamos un grupo de diez candidatos. "
                f"Hay <strong>siete</strong> a favor de '{first_option}' y "
                f"<strong>tres</strong> a favor de '{second_option}'. Escogemos uno al azar."
            )
        elif treatment.get('label') == '0.7_L':
            selection_text = (
                f"Para determinar cada individuo del trío, tomamos un grupo de diez candidatos. "
                f"Hay <strong>siete</strong> a favor de '{second_option}' y "
                f"<strong>tres</strong> a favor de '{first_option}'. Escogemos uno al azar."
            )
        else:  # Control u otro
            selection_text = "Escogimos el grupo sin tomar en cuenta las posturas de las diez personas."


        # Texto principal
        treatment_text = (
            f"Para esta “conversación”, te hemos agrupado con otros dos compañeros usando la pregunta: '{current_question}'. "
            f"{selection_text}"
        )

        # Información adicional (si aplica)
        inform_text = ""
        if treatment.get('inform'):
            inform_text = f"Te informamos que el {judge_percent:.0f}% de los participantes están dispuestos a pagar 5 pesos para darle o quitarle 20 pesos a cada uno de sus compañeros después de observar la opinión que le expresó."

        # ⬅️ Se devuelven ambos textos juntos
        return {
            'treatment_text': treatment_text,
            'inform_text': inform_text
        }


class PracticePublicDecision(Page):
    form_model = 'player'
    form_fields = ['second_choice']

    @staticmethod
    def is_displayed(player: Player) -> bool:
        return player.round_number == 2

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_question = PRACTICE_QUESTION
        options = PRACTICE_OPTIONS
        form = kwargs.get('form')
        if form:
            form.second_choice.choices = [('H', options[0]), ('L', options[1])]
            form.second_choice.label = current_question
        context.update({
            'current_question': current_question,
            'options': options,
            'practice_notice': "ESTA ES UNA PRÁCTICA. Tu decisión pública es solo para entrenamiento.",
        })
        return context

class PracticeSecondDecisionWaitPageForGroup(WaitPage):
    wait_for_all_groups = False
    template_name = 'otree/WaitPage.html'
    
    @staticmethod
    def is_displayed(player: Player) -> bool:
        return player.round_number == 2

class PracticePublicDisplayPage(Page):
    form_model = 'player'

    @staticmethod
    def is_displayed(player: Player) -> bool:
        return player.round_number == 2

    @staticmethod
    def get_form_fields(player):
        pay_choices = player.participant.vars.get('pay_to_judge_choices',
                                                [False]*C.NUM_BINARY_QUESTIONS)
        qi = player.session.vars['question_order'][player.round_number - 4]
        return ['juicio_1', 'juicio_2'] if pay_choices[qi] else []


    @staticmethod
    def vars_for_template(player: Player) -> dict:
        partners = get_partners(player)
        current_question = PRACTICE_QUESTION
        options = PRACTICE_OPTIONS

        # Collect each partner's choice text
        partner_choices = []
        for comp in partners:
            if comp.second_choice == 'H':
                partner_choices.append(options[0])
            elif comp.second_choice == 'L':
                partner_choices.append(options[1])
            else:
                partner_choices.append("No ha respondido")

        return {
            'partner_choices': partner_choices,
            'current_question': current_question,
            'show_judge_form': player.participant.vars.get('practice_pay_to_judge') is True,
        }
    
class PracticeLieQuestionPage(Page):
    form_model = 'player'
    form_fields = ['mentira_1', 'mentira_2']

    @staticmethod
    def is_displayed(player: Player) -> bool:
        return player.round_number == 2

    @staticmethod
    def vars_for_template(player: Player) -> dict:
        partners = get_partners(player)
        current_question = PRACTICE_QUESTION
        options = PRACTICE_OPTIONS

        partner_choices = []
        for comp in partners:
            if comp.second_choice == 'H':
                partner_choices.append(options[0])
            elif comp.second_choice == 'L':
                partner_choices.append(options[1])
            else:
                partner_choices.append("No ha respondido")

        return {
            'partner_choices': partner_choices,
            'current_question': current_question
        }


class ExperimentInstructions2(Page):
    template_name = 'experiment_phase/ExperimentInstructions2.html'

    @staticmethod
    def is_displayed(player: Player) -> bool:
        return player.round_number == 2

    @staticmethod
    def vars_for_template(player: Player) -> dict:
        return {}

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
        return player.round_number == 3

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.participant.vars['binary_choices'] = [
            getattr(player, f"binary_choice_{i}") for i in range(1, C.NUM_BINARY_QUESTIONS + 1)
        ]
        logger.debug(f"Stored binary_choices: {player.participant.vars['binary_choices']}")


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        session = self.player.session
        hl_map = session.vars.get('HL_map')
        if hl_map is None:
            # Generarlo on the fly y guardarlo para próximas páginas
            hl_map = [random.choice([True, False])
                    for _ in range(C.NUM_BINARY_QUESTIONS)]
            session.vars['HL_map'] = hl_map
            logger.warning(f"HL_map no encontrado: creado sobre la marcha: {hl_map}")


        rendered_fields = []
        for i in range(C.NUM_BINARY_QUESTIONS):
            field = form[f"binary_choice_{i+1}"]

            if hl_map[i]:
                field.choices = [('H', FIRST_OPTIONS[i]), ('L', SECOND_OPTIONS[i])]
            else:
                field.choices = [('H', SECOND_OPTIONS[i]), ('L', FIRST_OPTIONS[i])]

            field.label = SURVEY_QUESTIONS[i]
            rendered_fields.append(field)

        context['rendered_fields'] = rendered_fields
        context['question_list']    = list(range(1, C.NUM_BINARY_QUESTIONS + 1))
        return context


class WillingnessToPayCost(Page):
    form_model = 'player'
    
    @staticmethod
    def get_form_fields(player: Player):
        return [f"pay_to_judge_{i}" for i in range(1, C.NUM_BINARY_QUESTIONS + 1)]
    
    @staticmethod
    def is_displayed(player: Player) -> bool:
        return player.round_number == 3
    
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
        return player.round_number == 3

    @staticmethod
    def after_all_players_arrive(subsession: Subsession):
        if 'question_order' not in subsession.session.vars:
            order = list(range(C.NUM_BINARY_QUESTIONS))
            random.shuffle(order)
            subsession.session.vars['question_order'] = order
            logger.debug(f"SurveyWaitPage set question_order: {order}")

# Stage 2: Group interaction pages (only for rounds > 3)
class GroupingWaitPage(WaitPage):
    wait_for_all_groups = True
    @staticmethod
    def is_displayed(player: Player) -> bool:
        return player.round_number > 3

    @staticmethod
    def after_all_players_arrive(subsession: Subsession):
        pair_players(subsession)

class TreatmentInformation(Page):
    @staticmethod
    def is_displayed(player: Player) -> bool:
        return player.round_number > 3

    @staticmethod
    def vars_for_template(player: Player):
        qi      = player.session.vars['question_order'][player.round_number - 4]
        hl_map  = player.session.vars['HL_map']

        first_option  = FIRST_OPTIONS[qi]
        second_option = SECOND_OPTIONS[qi]
        if not hl_map[qi]:                      # invertimos si H es la 2.ª
            first_option, second_option = second_option, first_option

        # ---- resto del código idéntico, solo usando las nuevas vars ----
        current_question = SURVEY_QUESTIONS[qi]
        player.current_question_tag = current_question

        # porcentaje dispuestos a juzgar
        players = player.subsession.get_players()
        judge_yes = sum(1 for p in players
                        if p.participant.vars['pay_to_judge_choices'][qi])
        judge_percent = (judge_yes / len(players)) * 100 if players else 0

        treatment = json.loads(player.treatment or '{"label":"Control","inform":false}')
        label = treatment.get('label', 'Control')
        # Build the partner selection text.
        if label == '0.5_H':
            selection_text = (
                f"Para determinar cada individuo del trío, tomamos un grupo de diez candidatos. "
                f"Hay <strong>cinco</strong> a favor de '{first_option}' y "
                f"<strong>cinco</strong> a favor de '{second_option}'. Escogemos uno al azar."
            )
        elif label == '0.7_H':
            selection_text = (
                f"Para determinar cada individuo del trío, tomamos un grupo de diez candidatos. "
                f"Hay <strong>siete</strong> a favor de '{first_option}' y "
                f"<strong>tres</strong> a favor de '{second_option}'. Escogemos uno al azar."
            )
        elif label == '0.7_L':
            selection_text = (
                f"Para determinar cada individuo del trío, tomamos un grupo de diez candidatos. "
                f"Hay <strong>siete</strong> a favor de '{second_option}' y "
                f"<strong>tres</strong> a favor de '{first_option}'. Escogemos uno al azar."
            )
        else:  # Control u otro
            selection_text = "Escogimos el grupo sin tomar en cuenta las posturas de las diez personas."

        
        # Texto principal
        treatment_text = (
            f"Para esta “conversación”, te hemos agrupado con otro compañero usando la pregunta de práctica: '{current_question}'. "
            f"{selection_text}"
        )

        # Información adicional (si aplica)
        inform_text = ""
        if treatment.get('inform'):
            inform_text = f"Te informamos que el {judge_percent:.0f}% de los participantes están dispuestos a pagar 5 pesos para darle o quitarle 20 pesos a su pareja después de observar la opinión que le expresó."

        # ⬅️ Se devuelven ambos textos juntos
        return {
            'treatment_text': treatment_text,
            'inform_text': inform_text
        }



class PublicDecision(Page):
    form_model = 'player'
    form_fields = ['second_choice']
    
    @staticmethod
    def is_displayed(player: Player) -> bool:
        return player.round_number > 3

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qi      = self.player.session.vars['question_order'][self.player.round_number - 4]
        hl_map  = self.player.session.vars['HL_map']

        current_question = SURVEY_QUESTIONS[qi]
        if hl_map[qi]:
            options = (FIRST_OPTIONS[qi], SECOND_OPTIONS[qi])
        else:
            options = (SECOND_OPTIONS[qi], FIRST_OPTIONS[qi])

        form = kwargs['form']
        form.second_choice.choices = [('H', options[0]), ('L', options[1])]
        form.second_choice.label   = current_question

        context.update(current_question=current_question,
                       options=options)
        return context

class SecondDecisionWaitPageForGroup(WaitPage):
    wait_for_all_groups = False
    template_name = 'otree/WaitPage.html'
    
    @staticmethod
    def is_displayed(player: Player) -> bool:
        return player.round_number > 3

class PublicDisplayPage(Page):
    form_model = 'player'

    @staticmethod
    def is_displayed(player: Player) -> bool:
        return player.round_number > 3

    @staticmethod
    def get_form_fields(player):
        qi = player.session.vars['question_order'][player.round_number - 4]
        pay_choices = player.participant.vars.get('pay_to_judge_choices',
                                                  [False]*C.NUM_BINARY_QUESTIONS)
        return ['juicio_1', 'juicio_2'] if pay_choices[qi] else []


    @staticmethod
    def vars_for_template(player: Player):
        qi      = player.session.vars['question_order'][player.round_number - 4]
        hl_map  = player.session.vars['HL_map']
        partners = get_partners(player)

        if hl_map[qi]:
            options = (FIRST_OPTIONS[qi], SECOND_OPTIONS[qi])
        else:
            options = (SECOND_OPTIONS[qi], FIRST_OPTIONS[qi])

        partner_choices = [
            options[0] if p.second_choice == 'H'
            else options[1] if p.second_choice == 'L'
            else "No ha respondido"
            for p in partners
        ]

        show_judge_form = player.participant.vars['pay_to_judge_choices'][qi]
        return dict(partner_choices=partner_choices,
                    current_question=SURVEY_QUESTIONS[qi],
                    show_judge_form=show_judge_form)

class LieQuestionPage(Page):
    form_model = 'player'
    form_fields = ['mentira_1', 'mentira_2']

    @staticmethod
    def is_displayed(player: Player) -> bool:
        return player.round_number > 3

    @staticmethod
    def vars_for_template(player: Player):
        qi      = player.session.vars['question_order'][player.round_number - 4]
        hl_map  = player.session.vars['HL_map']
        partners = get_partners(player)

        if hl_map[qi]:
            options = (FIRST_OPTIONS[qi], SECOND_OPTIONS[qi])
        else:
            options = (SECOND_OPTIONS[qi], FIRST_OPTIONS[qi])

        partner_choices = [
            options[0] if p.second_choice == 'H'
            else options[1] if p.second_choice == 'L'
            else "No ha respondido"
            for p in partners
        ]

        return dict(partner_choices=partner_choices,
                    current_question=SURVEY_QUESTIONS[qi])

class ThankYouPage(Page):
    @staticmethod
    def is_displayed(player: Player) -> bool:
        return player.round_number == 13

    @staticmethod
    def vars_for_template(player: Player) -> dict:
        return {}

# -----------------------------------------------------------------------------
# Page Sequence
# -----------------------------------------------------------------------------
page_sequence = [
    # --- Round 1: Pre-Practice Survey Stage ---
    #ConsentFormPage,              # Only in round 1
    ExperimentInstructions,       # Only in round 1
    #PersonalInfoPage,            # Only in round 1
    #PracticeBinaryQuestion,       # Only in round 1 (practice survey)
    #PracticeWillingnessToPayCost, # Only in round 1 (practice survey)
    #PracticeSurveyWaitPage,       # Only in round 1 (practice survey wait)

    # --- Round 2: Practice Group Interaction Stage ---
    #PracticeGroupingWaitPage,             # Only in round 2
    #PracticeTreatmentInformation,         # Only in round 2
    #PracticePublicDecision,               # Only in round 2
    #PracticeSecondDecisionWaitPageForGroup,  # Only in round 2
    #PracticePublicDisplayPage,            # Only in round 2
    #PracticeLieQuestionPage,              # Only in round 2
    #ExperimentInstructions2,

    # --- Round 3: Actual Survey Stage ---
    #BinaryQuestions,             # Only in round 3
    #WillingnessToPayCost,        # Only in round 3
    #SurveyWaitPage,              # Only in round 3

    # --- Rounds 4 - 13: Actual Group Interaction Stage ---
    #GroupingWaitPage,            # Only in rounds >=4
    #TreatmentInformation,        # Only in rounds >=4
    #PublicDecision,              # Only in rounds >=4
    #SecondDecisionWaitPageForGroup,  # Only in rounds >=4
    #PublicDisplayPage,           # Only in rounds >=4
    #LieQuestionPage,             # Only in rounds >=4
    #ThankYouPage                 # Only in round 13
]
