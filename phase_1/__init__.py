from otree.api import *
import random 
import os 
import json 
import statistics 

doc = """ 
Phase 1: Recruitment, Demographics, and Dual-Topic Opinions. 
Categorizes participants into LL, LR, RL, RR based on baseline responses (using Q2 as the categorizer).
""" 

class Constants(BaseConstants): 
    name_in_url = 'intake' 
    players_per_group = None 
    num_rounds = 1 

    QUESTIONS = { 
        'climate_opinion_1': {'text': "To what extent do you favor or oppose transitioning the country away from fossil fuels toward renewable energy?", 'left': "Strongly Oppose", 'right': "Strongly Favor"}, 
        'climate_opinion_2': {'text': "To what extent do you favor or oppose increasing taxes on fossil fuels?", 'left': "Strongly Oppose", 'right': "Strongly Favor"}, 
        'imm_opinion_1': {'text': "To what extent do you favor reducing federal immigration enforcement?", 'left': "Strongly Oppose", 'right': "Strongly Favor"}, 
        'imm_opinion_2': {'text': "To what extent do you favor the government providing immigrants a pathway to legal status over deportation?", 'left': "Strongly Oppose", 'right': "Strongly Favor"} 
    }
    

class Subsession(BaseSubsession): 
    pass 

def creating_session(subsession: Subsession): 
    for player in subsession.get_players(): 
        # Decide which topic block is shown first to prevent ordering effects
        blocks = ['climate', 'imm']
        random.shuffle(blocks)
        player.opinion_order = ",".join(blocks) 

def vars_for_admin_report(subsession: Subsession): 
    players = subsession.get_players() 
    consented_players = [p for p in players if p.field_maybe_none('consent_participate') == True] 
    screened_out = sum([1 for p in players if p.field_maybe_none('consent_participate') == False]) 
    report_data = { 
        'total_players': len(players), 
        'consented': len(consented_players), 
        'screened_out': screened_out, 
        'failed_imc': sum([1 for p in consented_players if p.field_maybe_none('imc_failed') == True]), 
        'total_bots': sum([1 for p in consented_players if (p.field_maybe_none('is_ai_bot') == True or p.field_maybe_none('is_honeypot_bot') == True)]), 
    } 

    categories_count = {'LL': 0, 'LR': 0, 'RL': 0, 'RR': 0, 'Ineligible_Neutral': 0, 'Pending': 0}

    for p in consented_players: 
        cat = p.field_maybe_none('category') 
        if not cat: 
            cat = "Pending" 
        if cat in categories_count:
            categories_count[cat] += 1
        else:
            categories_count[cat] = 1

    report_data['categories_count'] = categories_count
    return report_data 

def get_progress(step):
    total_steps = 3
    percentage = int((step / total_steps) * 100)
    return {
        'current_step': step,
        'total_steps': total_steps,
        'progress_percentage': percentage
    }

class Group(BaseGroup): 
    pass 

class Player(BasePlayer): 
    prolific_id = models.StringField(blank=True) 
    category = models.StringField(blank=True) 
    
    consent_participate = models.BooleanField(widget=widgets.CheckboxInput, label="I GIVE MY CONSENT to participate.", blank=True) 
    consent_climate = models.BooleanField(widget=widgets.CheckboxInput, label="I GIVE MY CONSENT to being exposed to arguments.", blank=True) 
    consent_data = models.BooleanField(widget=widgets.CheckboxInput, label="I GIVE MY CONSENT to processing data.", blank=True) 
    consent_reuse = models.BooleanField(widget=widgets.CheckboxInput, label="I GIVE MY CONSENT to reusing the data.", blank=True) 
    consent_electronic_signature = models.BooleanField(widget=widgets.CheckboxInput, label="I confirm I am over 18.", blank=True) 
    
    age_range = models.StringField(choices=['18-24', '25-34', '35-44', '45-54', '55-64', '65+'], label="What is your age range?") 
    gender = models.StringField(choices=['Male', 'Female', 'Non-binary', 'Prefer not to say'], label="What is your gender?") 
    education = models.StringField(choices=['Less Than High School', 'High School', 'Bachelor\'s or Associate', 'Graduate degree'], label="What is your highest level of education completed?") 
    imc_question = models.StringField(choices=['Red', 'Blue', 'Green', 'Yellow', 'Purple'], label="Please select 'Green' from the options below.", blank=True) 
    imc_failed = models.BooleanField(initial=False) 
    political_party = models.StringField(choices=['Republican', 'Democrat', 'Independent', 'Other'], label="Political party?") 
    
    climate_opinion_1 = models.IntegerField(choices=[1, 2, 3, 4, 5], widget=widgets.RadioSelectHorizontal) 
    climate_opinion_2 = models.IntegerField(choices=[1, 2, 3, 4, 5], widget=widgets.RadioSelectHorizontal) 
    imm_opinion_1 = models.IntegerField(choices=[1, 2, 3, 4, 5], widget=widgets.RadioSelectHorizontal) 
    imm_opinion_2 = models.IntegerField(choices=[1, 2, 3, 4, 5], widget=widgets.RadioSelectHorizontal) 
    
    opinion_order = models.StringField() 
    climate_opinion_summary = models.LongStringField(label="Provide a brief summary of your climate opinion.") 
    imm_opinion_summary = models.LongStringField(label="Provide a brief summary of your immigration opinion.") 
    
    system_status_flag = models.StringField(blank=True) 
    is_ai_bot = models.BooleanField(initial=False) 
    is_honeypot_bot = models.BooleanField(initial=False) 
    
    typing_cpm = models.FloatField(initial=0.0, blank=True) 
    typing_active_time = models.FloatField(initial=0.0, blank=True) 
    iki_variance = models.FloatField(initial=0.0, blank=True) 
    typing_while_unfocused = models.IntegerField(initial=0, blank=True) 
    paste_count = models.IntegerField(initial=0, blank=True)
    time_to_first_interaction = models.FloatField(initial=0.0, blank=True)
    time_of_first_paste = models.FloatField(initial=0.0, blank=True)
    total_page_time = models.FloatField(initial=0.0, blank=True)
    
    dirty_click_count = models.IntegerField(initial=0) 
    click_log = models.LongStringField(initial="", blank=True) 
    mouse_trajectory_log = models.LongStringField(initial="", blank=True) 
    window_width = models.IntegerField(blank=True, initial=1920) 
    window_height = models.IntegerField(initial=0, blank=True) 

class Consent(Page): 
    form_model = 'player' 
    form_fields = ['consent_participate', 'consent_climate', 'consent_data', 'consent_reuse', 'consent_electronic_signature'] 
    
    @staticmethod
    def vars_for_template(player: Player):
        return get_progress(1)

    @staticmethod 
    def before_next_page(player: Player, timeout_happened): 
        if player.participant.label: 
            player.prolific_id = player.participant.label 

class Demographics(Page): 
    form_model = 'player' 
    form_fields = ['age_range', 'gender', 'education', 'imc_question', 'political_party', 'system_status_flag'] 
    
    @staticmethod 
    def is_displayed(player: Player): 
        return player.field_maybe_none('consent_participate') == True 
        
    @staticmethod
    def vars_for_template(player: Player):
        return get_progress(2)
        
    @staticmethod 
    def before_next_page(player: Player, timeout_happened): 
        if player.system_status_flag: 
            player.is_honeypot_bot = True 
        if player.imc_question != 'Green': 
            player.imc_failed = True 

class Opinions(Page): 
    form_model = 'player' 
    form_fields = ['climate_opinion_1', 'climate_opinion_2', 'imm_opinion_1', 'imm_opinion_2', 
                   'climate_opinion_summary', 'imm_opinion_summary', 
                   'typing_cpm', 'typing_active_time', 'iki_variance', 'typing_while_unfocused', 'paste_count', 
                   'time_to_first_interaction', 'time_of_first_paste', 'total_page_time',
                   'click_log', 'mouse_trajectory_log', 'window_width', 'window_height', 'dirty_click_count'] 
                   
    @staticmethod 
    def is_displayed(player: Player): 
        return player.field_maybe_none('consent_participate') == True 
        
    @staticmethod 
    def vars_for_template(player: Player): 
        blocks = player.opinion_order.split(',') 
        blocks_data = []
        
        for block in blocks:
            if block == 'climate':
                blocks_data.append({
                    'title': 'Climate Policy',
                    'topic_label': 'climate policy',
                    'questions': [
                        {'name': 'climate_opinion_1', 'text': Constants.QUESTIONS['climate_opinion_1']['text'], 'left': Constants.QUESTIONS['climate_opinion_1']['left'], 'right': Constants.QUESTIONS['climate_opinion_1']['right']},
                        {'name': 'climate_opinion_2', 'text': Constants.QUESTIONS['climate_opinion_2']['text'], 'left': Constants.QUESTIONS['climate_opinion_2']['left'], 'right': Constants.QUESTIONS['climate_opinion_2']['right']}
                    ],
                    'summary_field': 'climate_opinion_summary'
                })
            elif block == 'imm':
                blocks_data.append({
                    'title': 'Immigration',
                    'topic_label': 'immigration',
                    'questions': [
                        {'name': 'imm_opinion_1', 'text': Constants.QUESTIONS['imm_opinion_1']['text'], 'left': Constants.QUESTIONS['imm_opinion_1']['left'], 'right': Constants.QUESTIONS['imm_opinion_1']['right']},
                        {'name': 'imm_opinion_2', 'text': Constants.QUESTIONS['imm_opinion_2']['text'], 'left': Constants.QUESTIONS['imm_opinion_2']['left'], 'right': Constants.QUESTIONS['imm_opinion_2']['right']}
                    ],
                    'summary_field': 'imm_opinion_summary'
                })
                
        vars_dict = {'blocks_data': blocks_data}
        vars_dict.update(get_progress(3))
        return vars_dict
        
    @staticmethod 
    def error_message(player, values):
        errors = dict()
        c_sum = values.get('climate_opinion_summary', '')
        if c_sum and (len(c_sum) < 20 or len(c_sum) > 150):
            errors['climate_opinion_summary'] = "Your climate policy summary must be between 20 and 150 characters."
            
        i_sum = values.get('imm_opinion_summary', '')
        if i_sum and (len(i_sum) < 20 or len(i_sum) > 150):
            errors['imm_opinion_summary'] = "Your immigration summary must be between 20 and 150 characters."
            
        if errors:
            return errors
            
    @staticmethod 
    def before_next_page(player: Player, timeout_happened): 
        c_text = (player.climate_opinion_summary or "").strip().lower() 
        i_text = (player.imm_opinion_summary or "").strip().lower()
        
        # Check either field for the invisible prompt honeypot
        if "undeniably complex" in c_text or "undeniably complex" in i_text: 
            player.is_ai_bot = True 
            
        # Using the SECOND question to categorize the participant
        c_op = player.climate_opinion_2
        i_op = player.imm_opinion_2
        
        if c_op is not None and i_op is not None:
            if c_op == 3 or i_op == 3:
                player.category = 'Ineligible_Neutral'
            else:
                # 4,5 = Favor (Left), 1,2 = Oppose (Right)
                c_val = 'L' if c_op > 3 else 'R'
                i_val = 'L' if i_op > 3 else 'R'
                player.category = f"{c_val}{i_val}"
        else:
            player.category = 'Pending'

class SuccessScreen(Page): 
    @staticmethod 
    def is_displayed(player: Player): 
        return player.field_maybe_none('consent_participate') == True 
        
    @staticmethod
    def vars_for_template(player: Player):
        return {'experiment_start_time': os.environ.get('EXPERIMENT_START_TIME', 'within the next 48 hours')}

class Screenout(Page): 
    @staticmethod 
    def is_displayed(player: Player): 
        return player.field_maybe_none('consent_participate') == False 

page_sequence = [Consent, Demographics, Opinions, SuccessScreen, Screenout]