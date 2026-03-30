from otree.api import *
import random 
import os 
import json 
import statistics 

doc = """ 
Phase 1: Recruitment, Demographics, and ESS-based Environmental Opinions. 
Telemetry and bot tracking moved to Opinions page. Task removed for rapid screening.
""" 

class Constants(BaseConstants): 
    name_in_url = 'intake' 
    players_per_group = None 
    num_rounds = 1 

    QUESTIONS = { 
        'opinion_1': {'text': "To what extent do you believe the world's climate is currently changing?", 'left': "Not at all", 'right': "A great deal"}, 
        'opinion_2': {'text': "How likely do you think it is that climate change will lead to significant natural disasters?", 'left': "Not at all likely", 'right': "Extremely likely"}, 
        'opinion_3': {'text': "To what extent do you feel a personal responsibility to try to reduce climate change?", 'left': "Not at all", 'right': "A great deal"}, 
        'opinion_4': {'text': "To what extent do you favor or oppose increasing taxes on fossil fuels?", 'left': "Strongly Oppose", 'right': "Strongly Favor"} 
    } 

class Subsession(BaseSubsession): 
    pass 

def creating_session(subsession: Subsession): 
    for player in subsession.get_players(): 
        q_list = ['opinion_1', 'opinion_2', 'opinion_3', 'opinion_4'] 
        random.shuffle(q_list) 
        player.opinion_order = ",".join(q_list) 

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

    def safe_avg(values): 
        clean_vals = [v for v in values if v is not None] 
        return round(sum(clean_vals) / len(clean_vals), 2) if clean_vals else 0.0 

    demo_overall = {'age': {}, 'gender': {}} 
    demo_by_group = {} 
    trust_overall = [] 
    trust_by_group_lists = {} 
    opinions_overall_lists = {'opinion_1': [], 'opinion_2': [], 'opinion_3': [], 'opinion_4': []} 
    opinions_by_group_lists = {} 

    for p in consented_players: 
        grp = p.field_maybe_none('category') 
        if not grp: 
            grp = "Pending" 
        if grp not in demo_by_group: 
            demo_by_group[grp] = {'age': {}, 'gender': {}} 
            trust_by_group_lists[grp] = [] 
            opinions_by_group_lists[grp] = {'opinion_1': [], 'opinion_2': [], 'opinion_3': [], 'opinion_4': []} 

        age = p.field_maybe_none('age_range') 
        if age: 
            demo_overall['age'][age] = demo_overall['age'].get(age, 0) + 1 
            demo_by_group[grp]['age'][age] = demo_by_group[grp]['age'].get(age, 0) + 1 

        gender = p.field_maybe_none('gender') 
        if gender: 
            demo_overall['gender'][gender] = demo_overall['gender'].get(gender, 0) + 1 
            demo_by_group[grp]['gender'][gender] = demo_by_group[grp]['gender'].get(gender, 0) + 1 

        trust = p.field_maybe_none('trust_score') 
        if trust is not None: 
            trust_overall.append(trust) 
            trust_by_group_lists[grp].append(trust) 

        for i in range(1, 5): 
            val = p.field_maybe_none(f'opinion_{i}') 
            if val is not None: 
                opinions_overall_lists[f'opinion_{i}'].append(val) 
                opinions_by_group_lists[grp][f'opinion_{i}'].append(val) 

    report_data['demo_overall'] = demo_overall 
    report_data['demo_by_group'] = demo_by_group 
    report_data['trust_overall_avg'] = safe_avg(trust_overall) 
    report_data['trust_by_group'] = {k: safe_avg(v) for k, v in trust_by_group_lists.items()} 
    report_data['opinions_overall'] = {k: safe_avg(v) for k, v in opinions_overall_lists.items()} 
    ops_group_avg = {} 
    for grp, ops in opinions_by_group_lists.items(): 
        ops_group_avg[grp] = {k: safe_avg(v) for k, v in ops.items()} 
    report_data['opinions_by_group'] = ops_group_avg 

    return report_data 

def get_progress(step):
    total_steps = 4
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
    trust_score = models.IntegerField(blank=True, null=True) 
    trust_score_breakdown = models.LongStringField(blank=True) 
    consent_participate = models.BooleanField(widget=widgets.CheckboxInput, label="I GIVE MY CONSENT to participate.", blank=True) 
    consent_climate = models.BooleanField(widget=widgets.CheckboxInput, label="I GIVE MY CONSENT to being exposed to arguments.", blank=True) 
    consent_data = models.BooleanField(widget=widgets.CheckboxInput, label="I GIVE MY CONSENT to processing data.", blank=True) 
    consent_reuse = models.BooleanField(widget=widgets.CheckboxInput, label="I GIVE MY CONSENT to reusing the data.", blank=True) 
    consent_electronic_signature = models.BooleanField(widget=widgets.CheckboxInput, label="I confirm I am over 18.", blank=True) 
    age_range = models.StringField(choices=['18-24', '25-34', '35-44', '45-54', '55-64', '65+'], label="What is your age range?") 
    gender = models.StringField(choices=['Male', 'Female', 'Non-binary', 'Prefer not to say'], label="What is your gender?") 
    education = models.StringField( 
        choices=['Less Than High School', 'High School', 'Bachelor\'s or Associate', 'Graduate degree'], 
        label="What is your highest level of education completed?" 
    ) 
    imc_question = models.StringField( 
        choices=['Red', 'Blue', 'Green', 'Yellow', 'Purple'], 
        label="Please select 'Green' from the options below.", 
        blank=True 
    ) 
    imc_failed = models.BooleanField(initial=False) 
    political_party = models.StringField(choices=['Republican', 'Democrat', 'Independent', 'Other'], label="Political party?") 
    opinion_1 = models.IntegerField(choices=[1, 2, 3, 4, 5,], widget=widgets.RadioSelectHorizontal) 
    opinion_2 = models.IntegerField(choices=[1, 2, 3, 4, 5,], widget=widgets.RadioSelectHorizontal) 
    opinion_3 = models.IntegerField(choices=[1, 2, 3, 4, 5,], widget=widgets.RadioSelectHorizontal) 
    opinion_4 = models.IntegerField(choices=[1, 2, 3, 4, 5,], widget=widgets.RadioSelectHorizontal) 
    opinion_order = models.StringField() 
    opinion_summary = models.LongStringField(label="Provide a brief summary of your opinion.") 
    user_reference_code = models.StringField(blank=True) 
    is_ai_bot = models.BooleanField(initial=False) 
    is_honeypot_bot = models.BooleanField(initial=False) 
    
    typing_cpm = models.FloatField(initial=0.0, blank=True) 
    typing_active_time = models.FloatField(initial=0.0, blank=True) 
    iki_variance = models.FloatField(initial=0.0, blank=True) 
    large_text_jumps = models.IntegerField(initial=0, blank=True) 
    typing_while_unfocused = models.IntegerField(initial=0, blank=True) 
    dirty_click_count = models.IntegerField(initial=0) 
    click_log = models.LongStringField(initial="", blank=True) 
    mouse_trajectory_log = models.LongStringField(initial="", blank=True) 
    window_width = models.IntegerField(blank=True, initial=1920) 
    window_height = models.IntegerField(initial=0, blank=True) 

    def calculate_trust_metrics(self): 
        score = 100 
        reasons = [] 

        width = self.window_width if self.window_width else 1920 
        is_mobile = width < 800 

        if self.is_honeypot_bot: 
            score -= 100 
            reasons.append("Honeypot Triggered") 
        if self.is_ai_bot: 
            score -= 100 
            reasons.append("AI Phrase Detected") 
        if self.imc_failed: 
            score -= 50 
            reasons.append("Failed IMC Check") 
        unfocused_typing = self.typing_while_unfocused if self.typing_while_unfocused else 0 
        if unfocused_typing > 0: 
            score -= 60 
            reasons.append(f"Unfocused Typing ({int(unfocused_typing)}x)") 
        jumps = self.large_text_jumps if self.large_text_jumps else 0 
        active_time = self.typing_active_time if self.typing_active_time else 0.0 
        if jumps > 0 and active_time < 10: 
            score -= 40 
            reasons.append(f"Fast Copypaste ({int(jumps)}x in {active_time:.1f}s)") 

        if not is_mobile: 
            iki = self.iki_variance if self.iki_variance else 0.0 
            if 0 < iki < 500: 
                score -= 30 
                reasons.append("Robotic Typing (Extreme Low Var)") 
            cpm = self.typing_cpm if self.typing_cpm else 0.0 
            if cpm > 800: 
                score -= 40 
                reasons.append(f"High CPM ({cpm:.0f})") 

        if not is_mobile: 
            traj_str = self.mouse_trajectory_log 
            if traj_str and traj_str.startswith('['): 
                try: 
                    trajectories = json.loads(traj_str) 
                    teleports = sum(1 for action in trajectories if len(action.get('path', [])) < 2) 
                    if teleports >= 2: 
                        score -= 30 
                        reasons.append(f"Mouse Teleporting ({teleports}x)") 
                except Exception: 
                    pass 

        blurs = self.dirty_click_count if self.dirty_click_count else 0 
        if blurs > 3: 
            penalty = int((blurs - 3) * 10) 
            score -= penalty 
            reasons.append(f"Hidden Tabs ({int(blurs)}x)") 

        self.trust_score = max(0, score) 
        self.trust_score_breakdown = f"Score: {self.trust_score} [{' | '.join(reasons) if reasons else 'Clean'}]" 

        if self.opinion_4 is not None:
            if self.opinion_4 < 3:
                self.category = 'Low_Concern'
            elif self.opinion_4 == 3:
                self.category = 'Undecided'
            elif self.opinion_4 > 3:
                self.category = 'High_Concern'
        else:
            self.category = 'Pending'


class Consent(Page): 
    form_model = 'player' 
    form_fields = ['consent_participate', 'consent_climate', 'consent_data', 'consent_reuse', 'consent_electronic_signature'] 
    
    @staticmethod
    def vars_for_template(player: Player):
        return get_progress(1)

class Introduction(Page): 
    @staticmethod 
    def is_displayed(player: Player): 
        return player.field_maybe_none('consent_participate') == True 
        
    @staticmethod
    def vars_for_template(player: Player):
        return get_progress(2)
        
    @staticmethod 
    def before_next_page(player: Player, timeout_happened): 
        if player.participant.label: 
            player.prolific_id = player.participant.label 

class Demographics(Page): 
    form_model = 'player' 
    form_fields = ['age_range', 'gender', 'education', 'imc_question', 'political_party', 'user_reference_code'] 
    
    @staticmethod 
    def is_displayed(player: Player): 
        return player.field_maybe_none('consent_participate') == True 
        
    @staticmethod
    def vars_for_template(player: Player):
        return get_progress(3)
        
    @staticmethod 
    def before_next_page(player: Player, timeout_happened): 
        if player.user_reference_code: 
            player.is_honeypot_bot = True 
        if player.imc_question != 'Green': 
            player.imc_failed = True 

class Opinions(Page): 
    form_model = 'player' 
    form_fields = ['opinion_1', 'opinion_2', 'opinion_3', 'opinion_4', 'opinion_summary', 
                   'typing_cpm', 'typing_active_time', 'iki_variance', 'large_text_jumps', 'typing_while_unfocused',
                   'click_log', 'mouse_trajectory_log', 'window_width', 'window_height', 'dirty_click_count'] 
                   
    @staticmethod 
    def is_displayed(player: Player): 
        return player.field_maybe_none('consent_participate') == True 
        
    @staticmethod 
    def vars_for_template(player: Player): 
        ordered_fields = player.opinion_order.split(',') 
        questions_data = [{'name': f, 'text': Constants.QUESTIONS[f]['text'], 'left': Constants.QUESTIONS[f]['left'], 'right': Constants.QUESTIONS[f]['right']} for f in ordered_fields] 
        vars_dict = {'questions_data': questions_data}
        vars_dict.update(get_progress(4))
        return vars_dict 
        
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
        player.calculate_trust_metrics()

class SuccessScreen(Page): 
    @staticmethod 
    def is_displayed(player: Player): 
        return player.field_maybe_none('consent_participate') == True 

class Screenout(Page): 
    @staticmethod 
    def is_displayed(player: Player): 
        return player.field_maybe_none('consent_participate') == False 

page_sequence = [Consent, Introduction, Demographics, Opinions, SuccessScreen, Screenout]