# apps/personal_info/__init__.py
from otree.api import *

# Models
doc = """
App para recopilar información personal básica de los participantes.
"""


class C(BaseConstants):
    NAME_IN_URL = 'personal_info'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


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


## PAGES
class PersonalInfoPage(Page):
    form_model = 'player'
    form_fields = ['age', 'gender', 'racial_identification', 'previous_experiment']


page_sequence = [PersonalInfoPage]