from __future__ import annotations  # For postponed evaluation of annotations
from otree.api import *

# -----------------------------------------------------------------------------
# Module-level constants
# -----------------------------------------------------------------------------
# Define the answers for the binary questions as a module-level constant.
BINARY_TEXTS = [
    ("A favor", "En contra"),
    ("Sí, la quesadilla lleva queso", "No, la quesadilla no lleva queso"),
    ("Más medidas de control", "Derecho a poseer armas"),
    ("De acuerdo", "En desacuerdo"),
    ("Bueno", "Malo"),
    ("De acuerdo", "En desacuerdo"),
    ("De acuerdo", "En desacuerdo"),
    ("Sí lo pueden ser", "No pueden llegar a serlo"),
    ("De acuerdo", "En desacuerdo"),
    ("De acuerdo", "En desacuerdo"),
    ("Sí", "No"),
    ("Sí debería", "No debería"),
    ("Sí deberían", "No deberían"),
    ("El América", "Las Chivas"),
    ("De acuerdo", "En desacuerdo"),
    ("Verdadero", "Falso"),
    ("Sí", "No"),
    ("Quesillo", "Queso Oaxaca"),
    ("Sí", "No"),
    ("Luis Miguel", "Juan Gabriel"),
    ("De acuerdo", "En desacuerdo"),
    ("A mi compañero", "Al niño"),
    ("Sí lo es", "No lo es"),
    ("De acuerdo", "En desacuerdo"),
    ("De acuerdo", "En desacuerdo"),
    ("Sí", "No"),
    ("Afrontar la crisis climática", "Terminar la pobreza extrema en el mundo"),
    ("A favor", "En contra"),
    ("Sí, debería devolvérselo", "No, no debería devolvérselo"),
    ("El Norte", "El Sur"),
    ("Bañarse en la mañana", "Bañarse en la noche"),
    ("Sí lo desvío", "Dejo que siga su trayecto"),
    ("Harry Potter", "El Señor de los Anillos"),
    ("La Condesa", "Coyoacán"),
    ("En 10 años", "En 25 años"),
    ("Sí", "No"),
    ("De acuerdo", "En desacuerdo"),
]


class C(BaseConstants):
    NAME_IN_URL = 'actual_exp_phase_1'
    PLAYERS_PER_GROUP = 3


# -----------------------------------------------------------------------------
# Models
# -----------------------------------------------------------------------------
class Subsession(BaseSubsession):
    pass

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

# -----------------------------------------------------------------------------
# Page Definitions
# -----------------------------------------------------------------------------
class ConsentFormPage(Page):
    form_model = 'player'
    form_fields = ['consent']
    
    @staticmethod
    def is_displayed(player: Player) -> bool:
        return player.round_number == 1

class ExperimentInstructions(Page):
    template_name = 'actual_exp_phase_1/ExperimentInstructions.html'

    @staticmethod
    def is_displayed(player: Player) -> bool:
        return player.round_number == 1

    @staticmethod
    def vars_for_template(player: Player) -> dict:
        return {}

class PersonalInfoPage(Page):
    form_model = 'player'
    form_fields = ['age', 'gender', 'racial_identification', 'previous_experiment']
    
    @staticmethod
    def is_displayed(player: Player) -> bool:
        return player.round_number == 1

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
    #ConsentFormPage,
    #ExperimentInstructions,
    PersonalInfoPage,
    #ThankYouPage
]
