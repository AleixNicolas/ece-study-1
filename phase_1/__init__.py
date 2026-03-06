from otree.api import *
import random
import csv
import os

doc = """
Phase 1: Recruitment, Demographics, and ESS-based Environmental Opinions.
With upgraded Telemetry, Bot/LLM mitigation tracking, and IMC.
Updated: Renamed 'backlog' to 'pending_items' for Phase 1 clarity.
"""

class Constants(BaseConstants):
    name_in_url = 'intake'
    players_per_group = None
    num_rounds = 1
    
    csv_path = os.path.join(os.path.dirname(__file__), 'news_items.csv')
    if os.path.exists(csv_path):
        with open(csv_path, encoding='utf-8') as f:
            NEWS_ITEMS = list(csv.DictReader(f))
    else:
        NEWS_ITEMS = [{'id': str(i), 'headline': f'News {i}', 'additional_text': 'Text'} for i in range(1, 10)]

    QUESTIONS = {
        'opinion_1': {
            'text': "To what extent do you believe the world's climate is currently changing?",
            'left': "Not at all",
            'right': "A great deal"
        },
        'opinion_2': {
            'text': "How likely do you think it is that climate change will lead to significant natural disasters, such as floods or droughts?",
            'left': "Not at all likely",
            'right': "Extremely likely"
        },
        'opinion_3': {
            'text': "To what extent do you feel a personal responsibility to try to reduce climate change?",
            'left': "Not at all",
            'right': "A great deal"
        },
        'opinion_4': {
            'text': "To what extent do you favor or oppose increasing taxes on fossil fuels (oil, gas, coal) to reduce climate change?",
            'left': "Strongly Oppose",
            'right': "Strongly Favor"
        }
    }

class Subsession(BaseSubsession):
    pass

def creating_session(subsession: Subsession):
    for player in subsession.get_players():
        selected_items = random.sample(Constants.NEWS_ITEMS, 4)
        player.item_1_id = selected_items[0]['id']
        player.item_2_id = selected_items[1]['id']
        player.item_3_id = selected_items[2]['id']
        player.item_4_id = selected_items[3]['id']

        q_list = ['opinion_1', 'opinion_2', 'opinion_3', 'opinion_4']
        random.shuffle(q_list)
        player.opinion_order = ",".join(q_list)

class Group(BaseGroup):
    pass

class Player(BasePlayer):
    prolific_id = models.StringField(blank=True)
    
    # Consent Fields
    consent_participate = models.BooleanField(widget=widgets.CheckboxInput, label="I GIVE MY CONSENT to participate in this study.", blank=True)
    consent_climate = models.BooleanField(widget=widgets.CheckboxInput, label="I GIVE MY CONSENT to being exposed to arguments regarding climate change.", blank=True)
    consent_data = models.BooleanField(widget=widgets.CheckboxInput, label="I GIVE MY CONSENT to processing data about political opinions.", blank=True)
    consent_reuse = models.BooleanField(widget=widgets.CheckboxInput, label="I GIVE MY CONSENT to reusing the data generated in this study for other projects by the same UPF Team in the same field of research.", blank=True)
    consent_electronic_signature = models.BooleanField(widget=widgets.CheckboxInput, label="By checking this box, I electronically sign this consent form and confirm I am over 18 years old.", blank=True)
    
    # Demographics & IMC
    age_range = models.StringField(choices=['18-24', '25-34', '35-44', '45-54', '55-64', '65+'], label="What is your age range?")
    gender = models.StringField(choices=['Male', 'Female', 'Non-binary', 'Prefer not to say'], label="What is your gender?")
    education = models.StringField(
        choices=['Less Than High School', 'High School', 'Bachelor\'s or Associate', 'Graduate degree'], 
        label="What is your highest level of education completed?"
    )
    imc_question = models.StringField(
        choices=['Red', 'Blue', 'Green', 'Yellow', 'Purple'], 
        label="To demonstrate that you are reading the instructions carefully, please select 'Green' from the options below.",
        blank=True
    )
    imc_failed = models.BooleanField(initial=False)
    political_party = models.StringField(choices=['Republican', 'Democrat', 'Independent', 'Other'], label="Which political party do you identify with most?")
    
    # Opinions
    opinion_1 = models.IntegerField(choices=[1, 2, 3, 4, 5, 6, 7], widget=widgets.RadioSelectHorizontal)
    opinion_2 = models.IntegerField(choices=[1, 2, 3, 4, 5, 6, 7], widget=widgets.RadioSelectHorizontal)
    opinion_3 = models.IntegerField(choices=[1, 2, 3, 4, 5, 6, 7], widget=widgets.RadioSelectHorizontal)
    opinion_4 = models.IntegerField(choices=[1, 2, 3, 4, 5, 6, 7], widget=widgets.RadioSelectHorizontal)
    
    opinion_order = models.StringField()
    opinion_summary = models.LongStringField(label="Please provide a brief summary of your opinion on the environmental issues presented above.")
    
    # Telemetry & Mitigation
    user_reference_code = models.StringField(blank=True) 
    is_ai_bot = models.BooleanField(initial=False)
    is_honeypot_bot = models.BooleanField(initial=False)
    typing_cpm = models.FloatField(initial=0.0, blank=True)
    typing_active_time = models.FloatField(initial=0.0, blank=True)
    iki_variance = models.FloatField(initial=0.0, blank=True)
    large_text_jumps = models.IntegerField(initial=0, blank=True)
    typing_while_unfocused = models.IntegerField(initial=0, blank=True)

    # Feed Telemetry
    dirty_click_count = models.IntegerField(initial=0) 
    click_log = models.LongStringField(initial="", blank=True)
    mouse_trajectory_log = models.LongStringField(initial="", blank=True)
    total_time_on_feed = models.FloatField(blank=True)
    window_width = models.IntegerField(blank=True)
    window_height = models.IntegerField(initial=0, blank=True)
    
    average_feed_size = models.FloatField(blank=True)
    max_feed_size = models.IntegerField(blank=True)
    
    average_pending_items = models.FloatField(blank=True)
    max_pending_items = models.IntegerField(blank=True)

    item_1_id = models.StringField()
    item_2_id = models.StringField()
    item_3_id = models.StringField()
    item_4_id = models.StringField()
    decision_1 = models.StringField(choices=['Share', 'Not Share'], widget=widgets.RadioSelect)
    decision_2 = models.StringField(choices=['Share', 'Not Share'], widget=widgets.RadioSelect)
    decision_3 = models.StringField(choices=['Share', 'Not Share'], widget=widgets.RadioSelect)
    decision_4 = models.StringField(choices=['Share', 'Not Share'], widget=widgets.RadioSelect)

    # RT Telemetry
    read_time_1 = models.IntegerField(blank=True)
    read_time_2 = models.IntegerField(blank=True)
    read_time_3 = models.IntegerField(blank=True)
    read_time_4 = models.IntegerField(blank=True)
    rt_first_1 = models.IntegerField(blank=True)
    rt_first_2 = models.IntegerField(blank=True)
    rt_first_3 = models.IntegerField(blank=True)
    rt_first_4 = models.IntegerField(blank=True)
    rt_final_1 = models.IntegerField(blank=True)
    rt_final_2 = models.IntegerField(blank=True)
    rt_final_3 = models.IntegerField(blank=True)
    rt_final_4 = models.IntegerField(blank=True)

# --- PAGES ---

class Consent(Page):
    form_model = 'player'
    form_fields = ['consent_participate', 'consent_climate', 'consent_data', 'consent_reuse', 'consent_electronic_signature']

class Introduction(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.consent_participate
    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if player.participant.label:
            player.prolific_id = player.participant.label

class Demographics(Page):
    form_model = 'player'
    form_fields = ['age_range', 'gender', 'education', 'imc_question', 'political_party', 'user_reference_code']
    @staticmethod
    def is_displayed(player: Player):
        return player.consent_participate
    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if player.user_reference_code:
            player.is_honeypot_bot = True
        if player.imc_question != 'Green':
            player.imc_failed = True

class Opinions(Page):
    form_model = 'player'
    form_fields = ['opinion_1', 'opinion_2', 'opinion_3', 'opinion_4', 'opinion_summary', 
                   'typing_cpm', 'typing_active_time', 'iki_variance', 'large_text_jumps', 'typing_while_unfocused']
    @staticmethod
    def is_displayed(player: Player):
        return player.consent_participate
    @staticmethod
    def vars_for_template(player: Player):
        ordered_fields = player.opinion_order.split(',')
        questions_data = [{'name': f, 'text': Constants.QUESTIONS[f]['text'], 'left': Constants.QUESTIONS[f]['left'], 'right': Constants.QUESTIONS[f]['right']} for f in ordered_fields]
        return {'questions_data': questions_data}
    @staticmethod
    def error_message(player, values):
        summary = values.get('opinion_summary', '')
        if summary and (len(summary) < 20 or len(summary) > 150):
            return "Your summary must be between 20 and 150 characters."
    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        text = (player.opinion_summary or "").strip().lower()
        if text.startswith("in essence, truly"):
            player.is_ai_bot = True

class FeedTask(Page):
    form_model = 'player'
    form_fields = [
        'decision_1', 'decision_2', 'decision_3', 'decision_4', 
        'click_log', 'mouse_trajectory_log', 'total_time_on_feed', 'window_width', 'window_height', 'dirty_click_count',
        'average_feed_size', 'max_feed_size', 'average_pending_items', 'max_pending_items',
        'read_time_1', 'read_time_2', 'read_time_3', 'read_time_4',
        'rt_first_1', 'rt_first_2', 'rt_first_3', 'rt_first_4',
        'rt_final_1', 'rt_final_2', 'rt_final_3', 'rt_final_4'
    ]
    @staticmethod
    def is_displayed(player: Player):
        return player.consent_participate
    @staticmethod
    def vars_for_template(player: Player):
        return {f'item_{i}_headline': next(n['headline'] for n in Constants.NEWS_ITEMS if n['id'] == getattr(player, f"item_{i}_id")) for i in range(1, 5)}
    @staticmethod
    def js_vars(player: Player):
        vars_dict = {}
        for i in range(1, 5):
            item_id = getattr(player, f"item_{i}_id")
            news_item = next(n for n in Constants.NEWS_ITEMS if n['id'] == item_id)
            vars_dict[f'item_{i}_headline'] = news_item['headline']
            vars_dict[f'item_{i}_body'] = news_item['additional_text']
        return vars_dict

class SuccessScreen(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.consent_participate

class Screenout(Page):
    @staticmethod
    def is_displayed(player: Player):
        return not player.consent_participate

page_sequence = [Consent, Introduction, Demographics, Opinions, FeedTask, SuccessScreen, Screenout]