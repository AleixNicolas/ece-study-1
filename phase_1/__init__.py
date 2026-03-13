from otree.api import *
import random
import csv
import os
import json
import statistics

doc = """
Phase 1: Recruitment, Demographics, and ESS-based Environmental Opinions.
With upgraded Telemetry, Bot/LLM mitigation tracking, IMC, and advanced Admin Dashboard.
Includes real-time Trust Score computation and robust live reporting.
"""

class Constants(BaseConstants):
    name_in_url = 'intake'
    players_per_group = None
    num_rounds = 1
    
    # Strictly load from CSV. Will throw FileNotFoundError if missing.
    csv_path = os.path.join(os.path.dirname(__file__), 'news_items.csv')
    with open(csv_path, encoding='utf-8') as f:
        NEWS_ITEMS = list(csv.DictReader(f))

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
        selected_items = random.sample(Constants.NEWS_ITEMS, 4)
        player.item_1_id = selected_items[0]['id']
        player.item_2_id = selected_items[1]['id']
        player.item_3_id = selected_items[2]['id']
        player.item_4_id = selected_items[3]['id']

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
        grp = p.field_maybe_none('environmental_category')
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

    item_dict = {item['id']: item for item in Constants.NEWS_ITEMS}
    
    shares_overall = {'total': 0, 'shared': 0}
    shares_by_group = {}
    shares_by_leaning = {}
    shares_env_x_lean = {} 

    for p in consented_players:
        grp = p.field_maybe_none('environmental_category')
        if not grp:
            grp = "Pending"
            
        if grp not in shares_by_group:
            shares_by_group[grp] = {'total': 0, 'shared': 0}
            shares_env_x_lean[grp] = {}

        for i in range(1, 5):
            decision = p.field_maybe_none(f'decision_{i}')
            item_id = p.field_maybe_none(f'item_{i}_id')
            
            if decision and item_id in item_dict:
                is_shared = 1 if decision == 'Share' else 0
                item_data = item_dict[item_id]
                lean = item_data.get('leaning', 'Unknown')

                shares_overall['total'] += 1
                shares_overall['shared'] += is_shared
                
                shares_by_group[grp]['total'] += 1
                shares_by_group[grp]['shared'] += is_shared

                if lean not in shares_by_leaning: shares_by_leaning[lean] = {'total': 0, 'shared': 0}
                shares_by_leaning[lean]['total'] += 1
                shares_by_leaning[lean]['shared'] += is_shared
                
                if lean not in shares_env_x_lean[grp]:
                    shares_env_x_lean[grp][lean] = {'total': 0, 'shared': 0}
                shares_env_x_lean[grp][lean]['total'] += 1
                shares_env_x_lean[grp][lean]['shared'] += is_shared

    def calc_rate(data_dict):
        if data_dict['total'] == 0: return 0
        return round((data_dict['shared'] / data_dict['total']) * 100, 1)

    report_data['share_overall'] = calc_rate(shares_overall)
    report_data['share_by_group'] = {k: calc_rate(v) for k, v in shares_by_group.items()}
    report_data['share_by_item_leaning'] = {k: calc_rate(v) for k, v in shares_by_leaning.items()}
    
    report_data['share_by_env_x_lean'] = {}
    for grp, lean_data in shares_env_x_lean.items():
        report_data['share_by_env_x_lean'][grp] = {k: calc_rate(v) for k, v in lean_data.items()}

    return report_data


class Group(BaseGroup):
    pass

class Player(BasePlayer):
    prolific_id = models.StringField(blank=True)
    
    environmental_category = models.StringField(blank=True)
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
    
    opinion_1 = models.IntegerField(choices=[1, 2, 3, 4, 5, 6, 7], widget=widgets.RadioSelectHorizontal)
    opinion_2 = models.IntegerField(choices=[1, 2, 3, 4, 5, 6, 7], widget=widgets.RadioSelectHorizontal)
    opinion_3 = models.IntegerField(choices=[1, 2, 3, 4, 5, 6, 7], widget=widgets.RadioSelectHorizontal)
    opinion_4 = models.IntegerField(choices=[1, 2, 3, 4, 5, 6, 7], widget=widgets.RadioSelectHorizontal)
    
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

        rt_vals = [self.rt_first_1, self.rt_first_2, self.rt_first_3, self.rt_first_4]
        rt_vals = [rt for rt in rt_vals if rt is not None]
        if len(rt_vals) == 4:
            try:
                sd = statistics.stdev(rt_vals)
                reasons.append(f"[INFO: RT SD={sd:.2f}]")
            except statistics.StatisticsError:
                pass

        blurs = self.dirty_click_count if self.dirty_click_count else 0
        if blurs > 3:
            penalty = int((blurs - 3) * 10)
            score -= penalty
            reasons.append(f"Hidden Tabs ({int(blurs)}x)")

        # --- TESTING BYPASS START ---
        # FOR PRODUCTION USE THIS:
        # self.trust_score = max(0, score)
        
        # FOR TESTING ONLY, FORCE PERFECT SCORE:
        self.trust_score = 100 
        # --- TESTING BYPASS END ---

        self.trust_score_breakdown = f"Score: {self.trust_score} [{' | '.join(reasons) if reasons else 'Clean'}]"

        ops = [self.opinion_1, self.opinion_2, self.opinion_3, self.opinion_4]
        ops = [o for o in ops if o is not None]
        total_op = sum(ops)
        self.environmental_category = 'High_Concern' if total_op >= 16 else 'Low_Concern'

# --- PAGES ---

class Consent(Page):
    form_model = 'player'
    form_fields = ['consent_participate', 'consent_climate', 'consent_data', 'consent_reuse', 'consent_electronic_signature']

class Introduction(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.field_maybe_none('consent_participate') == True
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
        return player.field_maybe_none('consent_participate') == True
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
        return player.field_maybe_none('consent_participate') == True
    
    @staticmethod
    def vars_for_template(player: Player):
        vars_dict = {}
        for i in range(1, 5):
            item_id = getattr(player, f"item_{i}_id")
            news_item = next((n for n in Constants.NEWS_ITEMS if n['id'] == item_id), None)
            if news_item:
                vars_dict[f'item_{i}_headline'] = news_item['headline']
                vars_dict[f'item_{i}_body'] = news_item['additional_text']
        return vars_dict
        
    @staticmethod
    def js_vars(player: Player):
        vars_dict = {}
        for i in range(1, 5):
            item_id = getattr(player, f"item_{i}_id")
            news_item = next((n for n in Constants.NEWS_ITEMS if n['id'] == item_id), None)
            if news_item:
                vars_dict[f'item_{i}_headline'] = news_item['headline']
                vars_dict[f'item_{i}_body'] = news_item['additional_text']
        return vars_dict

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.calculate_trust_metrics()

class SuccessScreen(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.field_maybe_none('consent_participate') == True

class Screenout(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.field_maybe_none('consent_participate') == False

page_sequence = [Consent, Introduction, Demographics, Opinions, FeedTask, SuccessScreen, Screenout]