from otree.api import *

class C(BaseConstants):
    NAME_IN_URL        = 'survey'
    PLAYERS_PER_GROUP  = None
    NUM_ROUNDS         = 1

    # (unchanged) ─ labels and timeline for the 5 conceptual steps
    TIMELINE = [
        ('Pregunta 1', 'Indica tu postura <br> sobre el tema'),
        ('Pregunta 2', 'Indica qué tan seguro(a) <br> te sientes sobre tu postura'),
        ('Pregunta 3', 'Indica cuánto dinero estás <br> dispuesto(a) a pagar …'),
        ('Pregunta 4', 'Indica para qué opinión <br> le darías 20 pesos …'),
        ('Pregunta 5', 'Indica el porcentaje mínimo <br> … estás dispuesto(a) a <br> expresar la opinión alterna'),
    ]
    TIMELINE_PAGES = ['Topic']           # just a placeholder (see mixin note)
    TOTAL_STEPS    = len(TIMELINE)

    QUESTION_TEXT = dict(
        comp_q1=('1. Supón que en la <strong>tercera pregunta</strong> indicaste que el '
            'valor máximo que pagarías para decidir si darle o quitarle 20 pesos '
            'a tu pareja después de que te exprese su opinión sobre un tema es de <strong>13 pesos</strong>. '
            'Si para ese mismo tema seleccionamos aleatoriamente un '
            '<strong>costo Z de 12 pesos</strong>, ¿qué sucede?'),
        comp_q2=('2. Marca las afirmaciónes correctas sobre tus respuestas en la '
            '<strong>primera pregunta</strong> (la postura que más se acerca a tu opinión sobre el tema) y <strong>segunda pregunta</strong> (qué tan seguro(a) te sientes sobre tu respuesta a la primera pregunta):'
            '<br>  1) Tu pareja puede verlas.<br>'
            '  2) Nadie puede identificar quién dio qué respuesta.<br>'
            '  3) Los experimentadores pueden asociarlas contigo.<br>'
            '  4) Las respuestas no afectan directamente tus pagos.'
            '<br><br>'
            'Selecciona la combinación correcta:'),
        comp_q3=('3. Supón que el porcentaje de personas que toman la decisión de dar o quitar 20 '
            'pesos es mayor que tu porcentaje Y, el porcentaje mínimo de personas que toman '
            'la decisión con el que expresarías la opinión alterna a tu opinión privada, '
            '¿Qué situación se puede dar?'),
        comp_q4=('4. La <strong>quinta pregunta</strong> te pide dar un porcentaje '
            '<strong>Y</strong> mínimo con el que estás dispuesto a expresar la opinión alterna a tu opinión privada. Recuerda que Y se refiere al porcentaje de gente que toma la decisión de dar o quitar 20 pesos a su pareja. ¿Cuándo <u>expresas la opinión alterna</u> '
            'a tu opinión privada?'),
        comp_q5=('5. Considera el siguiente escenario:<br>'
            '  • En la tercera pregunta indicaste que estás dispuesto a pagar 10 pesos o menos para decidir dar o quitar 20 pesos a tu pareja.<br>'
            '  • Seleccionamos aleatoriamente un costo Z de 8 pesos.<br>'
            '  • En la cuarta pregunta indicaste <em>dar</em> 20 pesos si tu pareja expresa la '
            'preferencia azul.<br>'
            '  • Tu pareja sí va a decidir entre darte o quitarte 20 pesos dependiendo de lo que le expresas y además te expresa la preferencia azul.<br>'
            '¿Qué puedes afirmar con lo que sabes hasta ahora?'
            '  • Tu pareja sí puede decidir entre darte o quitarte 20 pesos dependiendo de lo que le expresas y además te expresa la primera postura del tema.<br>'
            '¿Qué puedes afirmar con lo que sabes hasta ahora?'),
        comp_q6=('6. “Si declaras en la <strong>tercera pregunta</strong> (disposición a pagar para decidir dar o quitar 20 pesos a tu pareja) un valor '
            'máximo mayor al que realmente estarías dispuesto a pagar, '
            'podrías terminar pagando un costo demasiado alto.”'),
        comp_q7=('7. Considera el siguiente escenario:<br>'
            '  • En la tercera pregunta indicaste que estás dispuesto a pagar 15 pesos o menos para decidir dar o quitar 20 pesos a tu pareja.<br>'
            '  • Seleccionamos aleatoriamente un costo Z de 18 pesos.<br>'
            '  • Tu opinión privada está en la mayoría.<br>'
            '  • En la quinta pregunta indicaste que el procentaje mínimo con el que estarías dispuesto a dar tu opinión alterna a tu opinión privada es de Y = 50 %.<br>'
            '  • El 60 % de los participantes pagaron para decidir dar o quitar 20 pesos a su pareja.<br><br>'
            'Selecciona lo que sucede:'),
    )

    CORRECT_ANSWERS = dict(
        comp_q1='a',
        comp_q2='2-4',
        comp_q3='c',        # tu BooleanField usa True/False
        comp_q4='d',
        comp_q5='a',
        comp_q6='a',
        comp_q7='a',
    )

    # ► Etiquetas en el mismo orden que binary_choice_1 … binary_choice_37
    TOPIC_LABELS = [
        "¿Estás a favor o en contra de la legalización y regularización de la marihuana en México?",
        "¿La quesadilla lleva o no queso?",
        "¿Crees que debería haber más medidas de control de armas en México o que las personas tienen derecho a poseer armas para protegerse?",
        "¿Estás de acuerdo con la frase 'el dinero compra la felicidad'?",
        "¿Crees que el ser humano es inherentemente bueno o malo?",
        "¿Estarías de acuerdo en que los menores de edad puedan iniciar un proceso de transcición de género si así lo quieren?",
        "En China, cuando los abuelos contraen una enfermedad terminal, las familias acostumbran a no decirles. ¿Estás de acuerdo con esta práctica?",
        "¿Crees que las relaciones a distancia pueden ser tan exitosas como las relaciones en persona?",
        "¿Estarías de acuerdo que en tu empresa contraten a un ex convicto, aunque no trabajes con él?",
        "¿Estás de acuerdo que la clave para salir de la pobreza, en México, es el trabajo duro?",
        "Llega contigo tu mejor amiga/o que acaba de hacerse un nuevo corte de pelo. Emocionada/o te pregunta si te gusta, pero a ti te parece que fue una terrible decisión. ¿Crees que mentir en esta situación es justificable, sabiendo que la verdad le haría sentir muy mal?",
        "¿Crees que el gobierno debería tener el poder de prohibirte fumar incluso en espacios al aire libre como playas o parques públicos?",
        "¿Crees que los migrantes deberían tener los mismos derechos y oportunidades que los ciudadanos mexicanos?",
        "¿Qué equipo de futbol es mejor: el América o las Chivas?",
        "¿Estás de acuerdo con la frase 'no hay paz sin la violencia'?",
        "Verdadero o falso: El arte que se exhibe en los museos de arte contemporáneo ya no tiene el mismo virtuosismo que el arte en los museos clásicos",
        "¿Crees que los videojuegos violentos fomentan actitudes violentas en la vida real?",
        "¿Cuál es la forma correcta de llamarle: quesillo o queso Oaxaca?",
        "¿Crees que uno de los criterios principales para contratar a alguien en México es el color de piel?",
        "¿Quién tiene mejor música, Luis Miguel o Juan Gabriel?",
        "¿Estás de acuerdo en que hay que separar el arte de Michael Jackson del artista?",
        "Estás en una guerra y debes decidir si salvar la vida de tu compañero o la de un niño inocente que está en peligro. ¿A quién salvarías?",
        "¿Es ético tener una relación romántica o sexual con alguien en una posición de poder, como un profesor o un jefe?",
        "¿Estás de acuerdo en que el uso de las drogas deteriora la vida de las personas?",
        "¿Estás de acuerdo con la pena de muerte?",
        "¿Estás de acuerdo con la eutanasia y el suicidio asistido?",
        "¿Qué es más importante, afrontar la crisis climática o terminar la pobreza extrema en el mundo?",
        "Imagina que estás en el Titanic al momento de su hundimiento, ¿estás a favor de que se salven primero a los ancianos?",
        "Una persona rica y grosera tira un billete de cien pesos sin darse cuenta. ¿Deberías devolvérselo?",
        "¿Qué región del país es más bonita?",
        "¿Qué es lo más higiénico, bañarse en la mañana o en la noche?",
        "Ves que un tren se dirige hacia cuatro personas. Tienes la posibilidad de desviarlo a un camino que se dirige a una persona. ¿Lo desvías?",
        "¿Qué saga de películas es mejor: Harry Potter o El Señor de los Anillos?",
        "¿Qué lugar mejor: La Condesa o Coyoacán?",
        "¿Qué tan rápido México debería transicionar a las energías renovables, tomando en cuenta que entre más rápido transicionar peor va a ser el crecimiento económico dado que el petróleo es un tercio de la economía del país?",
        "Tienes la opción de salvar la vida de un niño que está en peligro pero para hacerlo, debes poner en riesgo tu propia vida, con un 10 por ciento de probabilidad de perderla. ¿Lo harías?",
        "¿Estás de acuerdo en que enseñar a los alumnos a utilizar adecuadamente los métodos anticonceptivos sea obligatorio en las escuelas mexicanas?"
    ]

# ────────────────────────────────────────────────────────────────────
# 2.  TimelineMixin  — leave as‑is *except* treat every Topic page as
#     one “virtual” step so the existing 5‑segment bar still renders.
# ────────────────────────────────────────────────────────────────────
class TimelineMixin:
    """Calcula el avance de la línea de tiempo (5 segmentos)."""
    @staticmethod
    def vars_for_template(player):
        # every Topic page counts as having completed all 5 questions
        return dict(
            tl_labels = C.TIMELINE,
            current   = C.TOTAL_STEPS - 1,   # highlight the last segment
            progress  = 100,
        )




class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    consent = models.BooleanField(
        label='He leído y doy mi consentimiento para participar en el estudio.',
        widget=widgets.CheckboxInput,   # <- fuerza checkbox
        blank=False                     # requiere marcarla
    )

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

    binary_choice_1 = models.StringField(
        choices=[('H', "A favor"), ('L', "En contra")],
        blank=False,
        label="¿Estás a favor o en contra de la legalización y regularización de la marihuana en México?"
    )
    binary_choice_2 = models.StringField(
        choices=[('H', "Sí, la quesadilla lleva queso"), ('L', "No, la quesadilla no lleva queso")],
        blank=False,
        label="¿La quesadilla lleva o no queso?"
    )
    binary_choice_3 = models.StringField(
        choices=[('H', "Más medidas de control"), ('L', "Derecho a poseer armas")],
        blank=False,
        label="¿Crees que debería haber más medidas de control de armas en México o que las personas tienen derecho a poseer armas para protegerse?"
    )
    binary_choice_4 = models.StringField(
        choices=[('H', "De acuerdo"), ('L', "En desacuerdo")],
        blank=False,
        label="¿Estás de acuerdo con la frase 'el dinero compra la felicidad'?"
    )
    binary_choice_5 = models.StringField(
        choices=[('H', "Bueno"), ('L', "Malo")],
        blank=False,
        label="¿Crees que el ser humano es inherentemente bueno o malo?"
    )
    binary_choice_6 = models.StringField(
        choices=[('H', "De acuerdo"), ('L', "En desacuerdo")],  
        blank=False,
        label="¿Estarías de acuerdo en que los menores de edad puedan iniciar un proceso de transcición de género si así lo quieren?"
    )
    binary_choice_7 = models.StringField(
        choices=[('H', "De acuerdo"), ('L', "En desacuerdo")],
        blank=False,
        label="En China, cuando los abuelos contraen una enfermedad terminal, las familias acostumbran a no decirles. ¿Estás de acuerdo con esta práctica?"
    )
    binary_choice_8 = models.StringField(
        choices=[('H', "Sí lo pueden ser"), ('L', "No pueden llegar a serlo")],
        blank=False,
        label="¿Crees que las relaciones a distancia pueden ser tan exitosas como las relaciones en persona?"
    )
    binary_choice_9 = models.StringField(
        choices=[('H', "De acuerdo"), ('L', "En desacuerdo")],
        blank=False,
        label="¿Estarías de acuerdo que en tu empresa contraten a un ex convicto, aunque no trabajes con él?"
    )
    binary_choice_10 = models.StringField(
        choices=[('H', "De acuerdo"), ('L', "En desacuerdo")],
        blank=False,
        label="¿Estás de acuerdo que la clave para salir de la pobreza, en México, es el trabajo duro?"
    )
    binary_choice_11 = models.StringField(
        choices=[('H', "Sí"), ('L', "No")],
        blank=False,
        label="Llega contigo tu mejor amiga/o que acaba de hacerse un nuevo corte de pelo. Emocionada/o te pregunta si te gusta, pero a ti te parece que fue una terrible decisión. ¿Crees que mentir en esta situación es justificable, sabiendo que la verdad le haría sentir muy mal?"
    )
    binary_choice_12 = models.StringField(
        choices=[('H', "Sí debería"), ('L', "No debería")],
        blank=False,
        label="¿Crees que el gobierno debería tener el poder de prohibirte fumar incluso en espacios al aire libre como playas o parques públicos?"
    )
    binary_choice_13 = models.StringField(
        choices=[('H', "Sí deberían"), ('L', "No deberían")],
        blank=False,
        label="¿Crees que los migrantes deberían tener los mismos derechos y oportunidades que los ciudadanos mexicanos?"
    )
    binary_choice_14 = models.StringField(
        choices=[('H', "El América"), ('L', "Las Chivas")],
        blank=False,
        label="¿Qué equipo de futbol es mejor: el América o las Chivas?"
    )
    binary_choice_15 = models.StringField(
        choices=[('H', "De acuerdo"), ('L', "En desacuerdo")],
        blank=False,
        label="¿Estás de acuerdo con la frase 'no hay paz sin la violencia'?"
    )
    binary_choice_16 = models.StringField(
        choices=[('H', "Verdadero"), ('L', "Falso")],
        blank=False,
        label="Verdadero o falso: El arte que se exhibe en los museos de arte contemporáneo ya no tiene el mismo virtuosismo que el arte en los museos clásicos",
    )
    binary_choice_17 = models.StringField(
        choices=[('H', "Sí"), ('L', "No")],
        blank=False,
        label="¿Crees que los videojuegos violentos fomentan actitudes violentas en la vida real?"
    )
    binary_choice_18 = models.StringField(
        choices=[('H', "Quesillo"), ('L', "Queso Oaxaca")],
        blank=False,
        label="¿Cuál es la forma correcta de llamarle: quesillo o queso Oaxaca?"
    )
    binary_choice_19 = models.StringField(
        choices=[('H', "Sí"), ('L', "No")],
        blank=False,
        label="¿Crees que uno de los criterios principales para contratar a alguien en México es el color de piel?"
    )
    binary_choice_20 = models.StringField(
        choices=[('H', "Luis Miguel"), ('L', "Juan Gabriel")],
        blank=False,
        label="¿Quién tiene mejor música, Luis Miguel o Juan Gabriel?"
    )
    binary_choice_21 = models.StringField(
        choices=[('H', "De acuerdo"), ('L', "En desacuerdo")],
        blank=False,
        label="¿Estás de acuerdo en que hay que separar el arte de Michael Jackson del artista?"
    )
    binary_choice_22 = models.StringField(
        choices=[('H', "A mi compañero"), ('L', "Al niño")],
        blank=False,
        label="Estás en una guerra y debes decidir si salvar la vida de tu compañero o la de un niño inocente que está en peligro. ¿A quién salvarías?"
    )
    binary_choice_23 = models.StringField(
        choices=[('H', "Sí lo es"), ('L', "No lo es")],
        blank=False,
        label="¿Es ético tener una relación romántica o sexual con alguien en una posición de poder, como un profesor o un jefe?"
    )
    binary_choice_24 = models.StringField(
        choices=[('H', "De acuerdo"), ('L', "En desacuerdo")],
        blank=False,
        label="¿Estás de acuerdo en que el uso de las drogas deteriora la vida de las personas?"
    )
    binary_choice_25 = models.StringField(
        choices=[('H', "De acuerdo"), ('L', "En desacuerdo")],
        blank=False,
        label="¿Estás de acuerdo con la pena de muerte?"
    )
    binary_choice_26 = models.StringField(
        choices=[('H', "Sí"), ('L', "No")],
        blank=False,
        label="¿Estás de acuerdo con la eutanasia y el suicidio asistido?"
    )
    binary_choice_27 = models.StringField(
        choices=[('H', "Afrontar la crisis climática"), ('L', "Terminar la pobreza extrema en el mundo")],
        blank=False,
        label="¿Qué es más importante, afrontar la crisis climática o terminar la pobreza extrema en el mundo?"
    )
    binary_choice_28 = models.StringField(
        choices=[('H', "A favor"), ('L', "En contra")],
        blank=False,
        label="Imagina que estás en el Titanic al momento de su hundimiento, ¿estás a favor de que se salven primero a los ancianos?"
    )
    binary_choice_29 = models.StringField(
        choices=[('H', "Sí, debería devolvérselo"), ('L', "No, no debería devolvérselo")],
        blank=False,
        label="Una persona rica y grosera tira un billete de cien pesos sin darse cuenta. ¿Deberías devolvérselo?"
    )
    binary_choice_30 = models.StringField(
        choices=[('H', "El Norte"), ('L', "El Sur")],
        blank=False,
        label="¿Qué región del país es más bonita?"
    )
    binary_choice_31 = models.StringField(
        choices=[('H', "Bañarse en la mañana"), ('L', "Bañarse en la noche")],
        blank=False,
        label="¿Qué es lo más higiénico, bañarse en la mañana o en la noche?"
    )
    binary_choice_32 = models.StringField(
        choices=[('H', "Sí lo desvío"), ('L', "Dejo que siga su trayecto")],
        blank=False,
        label="Ves que un tren se dirige hacia cuatro personas. Tienes la posibilidad de desviarlo a un camino que se dirige a una persona. ¿Lo desvías?"
    )
    binary_choice_33 = models.StringField(
        choices=[('H', "Harry Potter"), ('L', "El Señor de los Anillos")],
        blank=False,
        label="¿Qué saga de películas es mejor: Harry Potter o El Señor de los Anillos?"
    )
    binary_choice_34 = models.StringField(
        choices=[('H', "La Condesa"), ('L', "Coyoacán")],
        blank=False,
        label="¿Qué lugar es mejor: La Condesa o Coyoacán?"
    )
    binary_choice_35 = models.StringField(
        choices=[('H', "En 10 años"), ('L', "En 25 años")],
        blank=False,
        label="¿Qué tan rápido México debería transicionar a las energías renovables, tomando en cuenta que entre más rápido transicionar peor va a ser el crecimiento económico dado que el petróleo es un tercio de la economía del país?"
    )
    binary_choice_36 = models.StringField(
        choices=[('H', "Sí"), ('L', "No")],
        blank=False,
        label="Tienes la opción de salvar la vida de un niño que está en peligro pero para hacerlo, debes poner en riesgo tu propia vida, con un 10 por ciento de probabilidad de perderla. ¿Lo harías?"
    )
    binary_choice_37 = models.StringField(
        choices=[('H', "De acuerdo"), ('L', "En desacuerdo")],
        blank=False,
        label="¿Estás de acuerdo en que enseñar a los alumnos a utilizar adecuadamente los métodos anticonceptivos sea obligatorio en las escuelas mexicanas?"
    )
    more_binary_choice = models.StringField(
        blank=False,
        label="¿Qué otra/s pregunta/s sobre temas divisivos se te vienen a la mente?"
    )

        # ─── Cuestionario de comprensión ────────────────────────────────────
    comp_q1 = models.StringField(
        label=(
            '1. Supón que en la <strong>tercera pregunta</strong> indicaste que el '
            'valor máximo que pagarías para decidir si darle o quitarle 20 pesos '
            'a tu pareja después de que te exprese su opinión sobre un tema es de <strong>13 pesos</strong>. '
            'Si para ese mismo tema seleccionamos aleatoriamente un '
            '<strong>costo Z de 12 pesos</strong>, ¿qué sucede?'
        ),
        choices=[
            ('a', 'a) Pagas 12 pesos y puedes decidir.'),
            ('b', 'b) Pagas 13 pesos y puedes decidir.'),
            ('c', 'c) No pagas nada y no puedes decidir.'),
            ('d', 'd) No pagas nada pero sí puedes decidir.')
        ],
        blank=False,
    )

    comp_q2 = models.StringField(
        label=(
            '2. Marca las afirmaciónes correctas sobre tus respuestas en la '
            '<strong>primera pregunta</strong> (la postura que más se acerca a tu opinión sobre el tema) y <strong>segunda pregunta</strong> (qué tan seguro(a) te sientes sobre tu respuesta a la primera pregunta):'
            '<br>  1) Tu pareja puede verlas.<br>'
            '  2) Nadie puede identificar quién dio qué respuesta.<br>'
            '  3) Los experimentadores pueden asociarlas contigo.<br>'
            '  4) Las respuestas no afectan directamente tus pagos.'
            '<br><br>'
            'Selecciona la combinación correcta:'
        ),
        choices=[
            ('1-3', 'a) Sólo 1 y 3.'),
            ('1-2', 'b) Sólo 1 y 2.'),
            ('2-4', 'c) Sólo 2 y 4.'),
            ('3-4', 'd) Sólo 3 y 4.')
        ],
        blank=False,
    )

    comp_q3 = models.StringField(
        label=(
            '3. Supón que el porcentaje de personas que toman la decisión de dar o quitar 20 '
            'pesos es mayor que tu porcentaje Y, el porcentaje mínimo de personas que toman '
            'la decisión con el que expresarías la opinión alterna a tu opinión privada, '
            '¿Qué situación se puede dar?'
        ),
        choices=[
            ('a', 'a) Si además mi opinión privada es la mayoritaria, entonces expreso la opinión alterna a mi pareja.'),
            ('b', 'b) Si además contesté la segunda pregunta, sobre qué tan seguro estoy de mi respuesta a la primera pregunta, con 5 o menos, entonces expreso mi opinión privada a mi pareja'),
            ('c', 'c) Si además mi opinión privada es la minoritaria, entonces expreso la opinión alterna a mi pareja'),
            ('d', 'd) Si además seleccionamos un costo Z mayor al costo máximo que estoy dispuesto a pagar para decidir dar o quitar 20 pesos a mi pareja, entonces expreso mi opinión privada a mi pareja.')
        ], 
    )

    comp_q4 = models.StringField(
        label=(
            '4. La <strong>quinta pregunta</strong> te pide dar un porcentaje '
            '<strong>Y</strong> mínimo con el que estás dispuesto a expresar la opinión alterna a tu opinión privada. Recuerda que Y se refiere al porcentaje de gente que toma la decisión de dar o quitar 20 pesos a su pareja. ¿Cuándo <u>expresas la opinión alterna</u> '
            'a tu opinión privada?'
        ),
        choices=[
            ('a', 'a) Cuando el costo Z que seleccionamos para ese tema es menor que el monto máximo que estás dispuesto a pagar para decidir dar o quitar 20 pesos a tu pareja después de expresarte una opinión sobre el tema.'),
            ('b', 'b) Cuando tu opinión privada está en mayoría y el procentaje de gente que toma la decisión es exactamente tu Y'),
            ('c', 'c) Siempre que tu pareja tenga la misma opinión privada que tú.'),
            ('d', 'd) Cuando tu opinión privada está en minoría y el procentaje de gente que toma la decisión es mayor o igual a tu Y.'),
        ],
        blank=False,
    )

    comp_q5 = models.StringField(
        label=(
            '5. Considera el siguiente escenario:<br>'
            '  • En la tercera pregunta indicaste que estás dispuesto a pagar 10 pesos o menos para decidir dar o quitar 20 pesos a tu pareja.<br>'
            '  • Seleccionamos aleatoriamente un costo Z de 8 pesos.<br>'
            '  • En la cuarta pregunta indicaste <em>dar</em> 20 pesos si tu pareja expresa la '
            'preferencia azul.<br>'
            '  • Tu pareja sí va a decidir entre darte o quitarte 20 pesos dependiendo de lo que le expresas y además te expresa la preferencia azul.<br>'
            '¿Qué puedes afirmar con lo que sabes hasta ahora?'
        ),
        choices=[
            ('a', 'a) Recibí 50 pesos por participar en la encuesta y se me restaron 8 pesos por decidir dar o quitar 20 pesos a mi pareja.'),
            ('b', 'b) Mi pareja decidió quitarme 20 pesos. Se me restan de los 50 pesos que tengo por participar en la encuesta.'),
            ('c', 'c) Mi pago final hasta ahora es de 50 pesos.'),
            ('d', 'd) No tengo la información suficiente para afirmar que ha pasado algo con mis pagos.'),
        ],
        blank=False,
    )

    comp_q6 = models.StringField(
        label=(
            '6. “Si declaras en la <strong>tercera pregunta</strong> (sobre la disposición a pagar para decidir dar o quitar 20 pesos a tu pareja) un valor '
            'máximo mayor al que realmente estarías dispuesto a pagar, '
            'podrías terminar pagando un costo demasiado alto.”'
        ),
        choices=[
            ('a', 'a) Verdadero'),
            ('b', 'b) Falso')
        ],
        blank=False,
    )

    comp_q7 = models.StringField(
        label=(
            '7. Considera el siguiente escenario:<br>'
            '  • En la tercera pregunta indicaste que estás dispuesto a pagar 15 pesos o menos para decidir dar o quitar 20 pesos a tu pareja.<br>'
            '  • Seleccionamos aleatoriamente un costo Z de 18 pesos.<br>'
            '  • Tu opinión privada está en la mayoría.<br>'
            '  • En la quinta pregunta indicaste que el procentaje mínimo con el que estarías dispuesto a dar tu opinión alterna a tu opinión privada es de Y = 50 %.<br>'
            '  • El 60 % de los participantes pagaron para decidir dar o quitar 20 pesos a su pareja.<br><br>'
            'Selecciona lo que sucede:'
        ),
        choices=[
            ('a', 'a) No pagas y expresas tu opinión privada.'),
            ('b', 'b) No pagas y expresas la opinión alterna a tu opinión privada'),
            ('c', 'c) Pagas 18 pesos y expresas tu opinión privada.'),
            ('d', 'd) Pagas 18 pesos y expresas la opinión alterna a tu opinión privada.'),
        ],
        blank=False,
    )


for idx, topic in enumerate(C.TOPIC_LABELS, start=1): 
    setattr( 
        Player, f'reaction_pay_{idx}',
        models.IntegerField(
            min=0,
            max=10,
            blank=False, label=( f'Supón que te volviéramos a preguntar diez veces más sobre cuál de las posturas se acerca más a tu opinión sobre el tema <strong>{topic}</strong>. Imagínate que te volviéramos a preguntar esto tiempo después, y en diferentes estados físicos y emocionales (por ejemplo, más o menos cansado(a), más o menos hambriento(a), más o menos contento(a), etc). ¿En cuántas de las diez veces que preguntamos nos darías la misma respuesta?' ) ), )

# ─── 1) ¿Cuánto dinero pagaría?  (Currency / Integer) ───────────────
for idx, topic in enumerate(C.TOPIC_LABELS, start=1):
    setattr(
        Player,
        f'inc_pay_{idx}',
        models.IntegerField(          # usa CurrencyField si conviertes a puntos
            min=0,
            max=20,
            blank=False,
            label=(
                f'Para el tema <strong>{topic}</strong>: Tú tienes que pagar un costo para poder decidir si darle o quitarle 20 pesos a tu pareja dependiendo de la opinión que exprese. Este costo puede ser desde 0 pesos (en este caso sería gratis para ti tomar la decisión)'
                'hasta 20 pesos. ¿Cuánto dinero estás dispuesto(a) a pagar para que puedas tomar esa decisión?'
            )
        ),
    )


# ─── 2) ¿Decir la verdad o mentir? (prob. juzgado = 50 %) ───────────
for idx, topic in enumerate(C.TOPIC_LABELS, start=1):
    setattr(
        Player,
        f'truth50_{idx}',
        models.StringField(
            choices=[('T', 'Le daría 20 pesos si expresa la primera postura y le quitaría 20 pesos si expresa la segunda postura'), ('M', 'Le quitaría 20 pesos si expresa la primera postura y le daría 20 pesos si expresa la segunda postura')],
            blank=False,
            label=(
                f'Para el tema <strong>{topic}</strong>: ¿Para cuál opinión que te exprese tu pareja le darías 20 pesos y para cuál opinión le quitarías 20 pesos?'
            )
        ),
    )

# ─── 3) Probabilidad‑umbral para mentir ─────────────────────────────
for idx, topic in enumerate(C.TOPIC_LABELS, start=1):
    setattr(
        Player,
        f'threshold_prob_{idx}',
        models.IntegerField(
            min=0,
            max=100,
            label=(
                f'Para el tema <strong>{topic}</strong>: Supón que tu opinión privada es la opinión minoritaria entre los participantes en esta sesión y al menos Y por ciento de los participantes en esta sesión pagaron el costo para decidir si le dan o le quitan 20 pesos a su pareja, ¿Cuál es el valor de Y mínimo con el que estás dispuesto a expresar la opinión alterna a tu opinión privada?'
            )
        ),
    )




class ConsentForm(Page):
    form_model = 'player'
    form_fields = ['consent']

    # optional: don’t let them continue without the box ticked
    def error_message(player, values):
        if not values['consent']:
            return 'Debes aceptar para continuar.'
    

class Intro(TimelineMixin, Page):
    @staticmethod
    def is_displayed(player):
        return player.consent  # sólo si aceptó el consentimiento

class Comprehension(Page):
    form_model = 'player'
    form_fields = list(C.CORRECT_ANSWERS.keys())

    @staticmethod
    def before_next_page(player, timeout_happened):
        res, score = {}, 0
        for f in C.CORRECT_ANSWERS:
            given   = getattr(player, f)
            correct = C.CORRECT_ANSWERS[f]
            ok      = given == correct
            res[f] = dict(
            text    = C.QUESTION_TEXT[f],  # enunciado completo (HTML)
            given   = str(given),          # lo que marcó el participante
            correct = str(correct),        # clave correcta
            ok      = ok,                  # booleano
)

            score += ok
        # SOLO datos primitivos → siempre json-/pickle-safe
        player.participant.vars.update(comp_results=res, comp_score=score)





class ComprehensionFeedback(Page):
    @staticmethod
    def vars_for_template(player):
        results = player.participant.vars.get('comp_results', {})
        score   = player.participant.vars.get('comp_score', 0)
        return dict(
            results=results,
            score=score,
            total=len(C.CORRECT_ANSWERS),
        )





class PersonalInfo(Page):
    form_model = 'player'
    form_fields = ['age', 'gender', 'racial_identification', 'previous_experiment']
    
    @staticmethod
    def is_displayed(player):
        return player.consent  # sólo si aceptó el consentimiento

# ────────────────────────────────────────────────────────────────────
# 6.  Factory that generates 37 per‑topic pages on the fly
# ────────────────────────────────────────────────────────────────────
def make_topic_page(idx: int):
    """
    Returns a Page subclass for topic #idx (1‑based) that bundles the
    five inputs: stance, certainty, WTP, give/take rule, threshold.
    """
    field_names = [
        f'binary_choice_{idx}',
        f'reaction_pay_{idx}',
        f'inc_pay_{idx}',
        f'truth50_{idx}',
        f'threshold_prob_{idx}',
    ]

    class TopicPage(TimelineMixin, Page):
        form_model  = 'player'
        form_fields = field_names
        template_name = 'topic_generic.html'     # <<— use one generic template
      # one template per topic

        @staticmethod
        def vars_for_template(player):
            return dict(
                topic_idx   = idx,
                topic_label = C.TOPIC_LABELS[idx - 1],
            )

    TopicPage.__name__ = f'Topic{idx}'           # nice debugger names
    return TopicPage


# build the 37 Topic* classes and expose them to oTree’s import‑scanner
TOPIC_PAGES = [make_topic_page(i) for i in range(1, 38)]
globals().update({cls.__name__: cls for cls in TOPIC_PAGES})

# ────────────────────────────────────────────────────────────────────
# 7.  Final page sequence
# ────────────────────────────────────────────────────────────────────
page_sequence = [
    ConsentForm,
    Comprehension, ComprehensionFeedback,
    PersonalInfo,
    *TOPIC_PAGES,        # 37 pages, one per topic
]



