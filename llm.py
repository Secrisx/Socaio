import os
import json
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import matplotlib.pyplot as plt
import seaborn as sns
from openai import OpenAI
import re
from collections import Counter
import warnings
warnings.filterwarnings('ignore')

# Set up plotting
plt.style.use('default')
sns.set_palette("husl")


# OpenAI API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

# Model configuration
MODEL = "gpt-4o"
MAX_TOKENS = 2000
TEMPERATURE = 0.7


#Data Models
@dataclass
class AudienceSegment:
    name: str
    age: str
    ethnicity: str
    location: str
    values: str
    political_leaning: str
    media_habits: str
    confidence: float

# M1: Enhanced Audience Profiling Metrics
@dataclass
class DemographicProfile:
    age_band: str  # 5-year bands (18-22, 23-27, etc.)
    gender_identity: str
    ethnicity_omb: str  # OMB categories + "prefer not to say"
    geography: Dict[str, str]  # country, state, urban_rural_flag
    education_level: str
    income_tier: str

@dataclass
class PsychographicProfile:
    political_lean: float  # 7-point scale (-3 to +3)
    schwartz_values: Dict[str, float]  # Values/cares using Schwartz value set
    big5_personality: Dict[str, str]  # low/med/high for each trait
    brand_affinity_cluster: str

@dataclass
class MediaHabits:
    top_platforms: List[str]  # Top 3 platforms
    preferred_content_format: str  # short video, long-form, text
    daily_usage_hours: float

@dataclass
class Persona:
    id: str
    name: str
    age: int
    gender: str
    ethnicity: str
    location: str
    occupation: str
    values: List[str]
    political_leaning: str
    personality_traits: Dict[str, float]  # Big-5 traits
    media_habits: List[str]
    system_prompt: str
    age_group: str = ""  # Added for grouping
    location_type: str = ""  # Added for grouping (urban/suburban/rural)
    # M1 Enhanced Metrics
    demographic_profile: DemographicProfile = None
    psychographic_profile: PsychographicProfile = None
    media_profile: MediaHabits = None

# M2: Enhanced Reaction Metrics
@dataclass
class EmotionVector:
    joy: float
    trust: float
    fear: float
    surprise: float
    sadness: float
    disgust: float
    anger: float
    anticipation: float

@dataclass
class PersonaReaction:
    persona_id: str
    # Core metrics
    sentiment: float  # -5 to +5
    share_likelihood: float  # 0-100%
    emotional_triggers: List[str]
    suggested_modifications: str
    raw_response: str
    # M2 Enhanced Metrics
    emotion_vector: EmotionVector = None
    credibility_rating: float = None  # 1-5
    purchase_intent: float = None  # 0-100
    controversy_flag: bool = False
    controversy_driver: str = None

# M3: Simulation-Mode Metrics
@dataclass
class GroupChatMetrics:
    consensus_index: float  # Average pairwise sentiment similarity
    conversation_turns: List[Dict]  # Turn-by-turn conversation
    topic_evolution: List[str]
    dominant_voices: List[str]

@dataclass
class ViralityMetrics:
    reach_24h: int
    peak_hour_reach: int
    diffusion_rate: float
    cascade_depth: int

@dataclass
class PopularityVotingMetrics:
    win_rate: float
    confidence_interval: tuple
    vote_distribution: Dict[str, int]
    preference_patterns: Dict[str, List[str]]

@dataclass
class TraitGroupInsight:
    trait_name: str
    trait_value: str
    persona_count: int
    avg_sentiment: float
    avg_share_likelihood: float
    common_triggers: List[str]
    key_concerns: List[str]
    recommendations: str
    # M2 Enhanced
    avg_credibility: float = None
    avg_purchase_intent: float = None
    emotion_profile: Dict[str, float] = None
    controversy_rate: float = None

@dataclass
class BiasAnalysis:
    potential_biases: List[str]
    inclusivity_score: float  # 0-10
    diversity_gaps: List[str]
    improvement_suggestions: List[str]

@dataclass
class InsightReport:
    mean_sentiment: float
    sentiment_distribution: Dict[str, int]
    mean_share_likelihood: float
    top_risk_flags: List[str]
    emotional_themes: List[str]
    executive_summary: str
    # Enhanced insights
    trait_insights: Dict[str, List[TraitGroupInsight]]  # Grouped by trait type
    bias_analysis: BiasAnalysis
    context_specific_insights: List[str]
    # M2 Enhanced Metrics
    mean_credibility: float = None
    mean_purchase_intent: float = None
    overall_emotion_profile: Dict[str, float] = None
    controversy_analysis: Dict[str, any] = None
    # M3 Simulation Metrics
    group_chat_metrics: GroupChatMetrics = None
    virality_metrics: ViralityMetrics = None
    popularity_metrics: PopularityVotingMetrics = None
    
    
# Stage A: User Prompt Intake
class PromptIntake:
    def __init__(self):
        self.current_prompt = None
        self.metadata = {}
    
    def capture_message(self, message: str, goal: str = None, channel: str = None, 
                       tone: str = None, company_type: str = None, company_size: str = None, 
                       audience_size: str = None, brand_context: str = None, 
                       campaign_type: str = None, target_outcome: str = None):
        """Capture the message to be tested with enhanced context"""
        self.current_prompt = message
        self.metadata = {
            "goal": goal or "general audience testing",
            "channel": channel or "general",
            "desired_tone": tone or "neutral",
            "company_type": company_type or "unknown",
            "company_size": company_size or "unknown", 
            "audience_size": audience_size or "unknown",
            "brand_context": brand_context or "none provided",
            "campaign_type": campaign_type or "general",
            "target_outcome": target_outcome or "engagement"
        }
        return {
            "message": message,
            "metadata": self.metadata
        }
    
    def get_current_prompt(self):
        return self.current_prompt, self.metadata

# Initialize prompt intake
prompt_intake = PromptIntake()


# Stage B: Audience Profiling (Meta-Classifier LLM)
class AudienceProfiler:
    def __init__(self, client):
        self.client = client
        self.system_prompt = """
You are an expert audience analyst and market researcher specializing in diverse, inclusive audience analysis. Your job is to analyze a given message/communication and identify the most relevant audience segments that should react to it.

IMPORTANT GUIDELINES:
1. Ensure racial and ethnic diversity across segments (include African American, Hispanic/Latino, Asian American, Native American, Middle Eastern, White, and Mixed Race perspectives)
2. Consider age diversity (Gen Z, Millennials, Gen X, Boomers)
3. Include urban, suburban, and rural perspectives
4. Consider socioeconomic diversity
5. Account for different ability levels and accessibility needs
6. Include LGBTQ+ perspectives where relevant

For each message, identify 5-7 distinct audience segments that would have meaningfully different reactions. Consider:
- Demographics: age, gender, ethnicity, location, socioeconomic status
- Psychographics: values, political leaning, personality traits
- Media consumption habits
- Cultural background and lived experiences
- Accessibility needs and considerations

Return your analysis as a JSON object with the following structure:
{
  "segments": [
    {
      "name": "Descriptive segment name",
      "age": "Age range",
      "ethnicity": "Specific ethnic/racial composition",
      "location": "Geographic focus",
      "values": "Core values and motivations",
      "political_leaning": "Political orientation if relevant",
      "media_habits": "Primary media consumption patterns",
      "confidence": 0.85
    }
  ],
  "bias_analysis": {
    "potential_biases": ["bias1", "bias2"],
    "inclusivity_concerns": ["concern1", "concern2"],
    "diversity_gaps": ["gap1", "gap2"]
  }
}

Make segments specific and distinct. Confidence should reflect how certain you are this segment will have a unique reaction.
IMPORTANT: Return ONLY the JSON object, no markdown formatting or code blocks.
"""
    
    def profile_audience(self, message: str, metadata: Dict = None) -> tuple[List[AudienceSegment], BiasAnalysis]:
        """Generate audience segments for a given message with bias analysis"""
        context = f"Message to analyze: {message}\n"
        if metadata:
            context += f"Campaign goal: {metadata.get('goal', 'N/A')}\n"
            context += f"Channel: {metadata.get('channel', 'N/A')}\n"
            context += f"Desired tone: {metadata.get('desired_tone', 'N/A')}\n"
            context += f"Company type: {metadata.get('company_type', 'N/A')}\n"
            context += f"Company size: {metadata.get('company_size', 'N/A')}\n"
            context += f"Audience size: {metadata.get('audience_size', 'N/A')}\n"
            context += f"Brand context: {metadata.get('brand_context', 'N/A')}\n"
            context += f"Campaign type: {metadata.get('campaign_type', 'N/A')}\n"
            context += f"Target outcome: {metadata.get('target_outcome', 'N/A')}\n"
        
        print(f"🔍 Analyzing message with context:")
        print(f"   Company: {metadata.get('company_type', 'N/A')} ({metadata.get('company_size', 'N/A')})")
        print(f"   Goal: {metadata.get('goal', 'N/A')}")
        print(f"   Channel: {metadata.get('channel', 'N/A')}")
        
        response = self.client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": context}
            ],
            max_tokens=MAX_TOKENS,
            temperature=TEMPERATURE
        )
        
        try:
            response_text = response.choices[0].message.content.strip()
            
            # Remove markdown code blocks if present
            if response_text.startswith('```json'):
                response_text = response_text[7:]  # Remove ```json
            if response_text.startswith('```'):
                response_text = response_text[3:]   # Remove ```
            if response_text.endswith('```'):
                response_text = response_text[:-3]  # Remove closing ```
            
            response_text = response_text.strip()
            
            result = json.loads(response_text)
            segments = []
            
            print(f"\n📊 Generated audience segments:")
            for i, seg_data in enumerate(result["segments"], 1):
                segment = AudienceSegment(**seg_data)
                segments.append(segment)
                print(f"   {i}. {segment.name}")
                print(f"      Age: {segment.age}, Ethnicity: {segment.ethnicity}")
                print(f"      Location: {segment.location}")
                print(f"      Values: {segment.values}")
            
            # Create bias analysis
            bias_data = result.get("bias_analysis", {})
            bias_analysis = BiasAnalysis(
                potential_biases=bias_data.get("potential_biases", []),
                inclusivity_score=8.0,  # Will be calculated based on diversity
                diversity_gaps=bias_data.get("diversity_gaps", []),
                improvement_suggestions=bias_data.get("inclusivity_concerns", [])
            )
            
            print(f"\n⚠️ Bias Analysis:")
            if bias_analysis.potential_biases:
                print(f"   Potential biases detected: {', '.join(bias_analysis.potential_biases)}")
            if bias_analysis.diversity_gaps:
                print(f"   Diversity gaps: {', '.join(bias_analysis.diversity_gaps)}")
                
            return segments, bias_analysis
            
        except Exception as e:
            print(f"Error parsing audience profile: {e}")
            print(f"Raw response: {response.choices[0].message.content}")
            return [], BiasAnalysis([], 0.0, [], [])

# Initialize audience profiler
audience_profiler = AudienceProfiler(client)


# Stage C: Persona Selection System
class PersonaGenerator:
    def __init__(self, client):
        self.client = client
        self.persona_pool = []
        
    def create_persona_from_segment(self, segment: AudienceSegment, metadata: Dict = None) -> Persona:
        """Generate a specific persona based on audience segment with M1 enhanced profiling"""
        context_prompt = ""
        if metadata:
            context_prompt = f"""
CAMPAIGN CONTEXT:
- Company: {metadata.get('company_type', 'Unknown')} ({metadata.get('company_size', 'Unknown')} size)
- Channel: {metadata.get('channel', 'Unknown')}
- Goal: {metadata.get('goal', 'Unknown')}
- Brand context: {metadata.get('brand_context', 'None')}
- Target outcome: {metadata.get('target_outcome', 'Unknown')}

Consider this context when creating the persona's background and likely relationship to the brand/message.
"""
        
        system_prompt = f"""
You are an expert persona generator specializing in creating authentic, diverse personas with comprehensive M1 profiling metrics.

Create a detailed, realistic persona that represents the following audience segment:

Segment: {segment.name}
Age: {segment.age}
Ethnicity: {segment.ethnicity}
Location: {segment.location}
Values: {segment.values}
Political leaning: {segment.political_leaning}
Media habits: {segment.media_habits}

{context_prompt}

IMPORTANT GUIDELINES:
1. Make this person feel genuinely real with specific details
2. Include cultural background and lived experiences
3. Consider socioeconomic factors realistically
4. Include authentic language patterns and cultural references
5. Ensure the personality traits reflect real human complexity

Create a JSON response with M1 Enhanced Profiling Metrics:
{{
  "name": "First and last name that reflects ethnicity",
  "age": 25,
  "gender": "Gender identity",
  "ethnicity": "Specific ethnicity/race",
  "location": "City, State/Country",
  "occupation": "Specific job title with realistic income level",
  "values": ["value1", "value2", "value3"],
  "political_leaning": "Specific political orientation",
  "personality_traits": {{
    "openness": 0.7,
    "conscientiousness": 0.6,
    "extraversion": 0.5,
    "agreeableness": 0.8,
    "neuroticism": 0.3
  }},
  "media_habits": ["platform1", "platform2", "platform3"],
  "cultural_background": "Brief description of cultural influences",
  "socioeconomic_details": "Income level, education, lifestyle details",
  
  "m1_demographic_profile": {{
    "age_band": "23-27",
    "gender_identity": "Woman/Man/Non-binary/Other",
    "ethnicity_omb": "White/Black or African American/American Indian or Alaska Native/Asian/Native Hawaiian or Other Pacific Islander/Hispanic or Latino/Two or More Races/Prefer not to say",
    "geography": {{
      "country": "United States",
      "state": "California", 
      "urban_rural_flag": "Urban/Suburban/Rural"
    }},
    "education_level": "High School/Some College/Bachelor's/Master's/Doctorate",
    "income_tier": "Under $25k/$25k-$50k/$50k-$75k/$75k-$100k/$100k-$150k/$150k+"
  }},
  
  "m1_psychographic_profile": {{
    "political_lean": 1.5,
    "schwartz_values": {{
      "security": 0.8,
      "conformity": 0.3,
      "tradition": 0.4,
      "benevolence": 0.9,
      "universalism": 0.7,
      "self_direction": 0.6,
      "stimulation": 0.5,
      "hedonism": 0.4,
      "achievement": 0.7,
      "power": 0.2
    }},
    "big5_personality": {{
      "openness": "high/medium/low",
      "conscientiousness": "high/medium/low", 
      "extraversion": "high/medium/low",
      "agreeableness": "high/medium/low",
      "neuroticism": "high/medium/low"
    }},
    "brand_affinity_cluster": "Tech Early Adopter/Luxury Seeker/Value Conscious/Social Cause/Traditional/Premium Quality"
  }},
  
  "m1_media_profile": {{
    "top_platforms": ["Instagram", "TikTok", "LinkedIn"],
    "preferred_content_format": "short video/long-form/text/audio/visual",
    "daily_usage_hours": 3.5
  }}
}}

Use realistic values. Political lean scale: -3 (very liberal) to +3 (very conservative). Schwartz values 0-1 scale.
IMPORTANT: Return ONLY the JSON object, no markdown formatting or code blocks.
"""
        
        response = self.client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": system_prompt}],
            max_tokens=MAX_TOKENS,
            temperature=0.8
        )
        
        try:
            response_text = response.choices[0].message.content.strip()
            
            # Remove markdown code blocks if present
            if response_text.startswith('```json'):
                response_text = response_text[7:]  # Remove ```json
            if response_text.startswith('```'):
                response_text = response_text[3:]   # Remove ```
            if response_text.endswith('```'):
                response_text = response_text[:-3]  # Remove closing ```
            
            response_text = response_text.strip()
            
            persona_data = json.loads(response_text)
            persona_id = f"{segment.name.lower().replace(' ', '_')}_{len(self.persona_pool)}"
            
            # Determine age group and location type for grouping
            age = persona_data['age']
            if age <= 27:
                age_group = "Gen Z (18-27)"
            elif age <= 42:
                age_group = "Millennials (28-42)"
            elif age <= 57:
                age_group = "Gen X (43-57)"
            else:
                age_group = "Boomers (58+)"
            
            location = persona_data['location'].lower()
            if 'rural' in location or 'small town' in location or 'countryside' in location:
                location_type = "Rural"
            elif 'suburb' in location or 'suburban' in location:
                location_type = "Suburban"
            else:
                location_type = "Urban"
            
            # Create M1 enhanced profiles
            demo_data = persona_data.get('m1_demographic_profile', {})
            demographic_profile = DemographicProfile(
                age_band=demo_data.get('age_band', f"{age}-{age+4}"),
                gender_identity=demo_data.get('gender_identity', persona_data['gender']),
                ethnicity_omb=demo_data.get('ethnicity_omb', persona_data['ethnicity']),
                geography=demo_data.get('geography', {"country": "Unknown", "state": "Unknown", "urban_rural_flag": location_type}),
                education_level=demo_data.get('education_level', 'Unknown'),
                income_tier=demo_data.get('income_tier', 'Unknown')
            )
            
            psycho_data = persona_data.get('m1_psychographic_profile', {})
            psychographic_profile = PsychographicProfile(
                political_lean=psycho_data.get('political_lean', 0.0),
                schwartz_values=psycho_data.get('schwartz_values', {}),
                big5_personality=psycho_data.get('big5_personality', {}),
                brand_affinity_cluster=psycho_data.get('brand_affinity_cluster', 'Unknown')
            )
            
            media_data = persona_data.get('m1_media_profile', {})
            media_profile = MediaHabits(
                top_platforms=media_data.get('top_platforms', persona_data['media_habits']),
                preferred_content_format=media_data.get('preferred_content_format', 'Unknown'),
                daily_usage_hours=media_data.get('daily_usage_hours', 2.0)
            )
            
            # Enhanced system prompt for persona reactions
            persona_system_prompt = f"""
You are {persona_data['name']}, a {persona_data['age']}-year-old {persona_data['gender']} from {persona_data['location']}.

PERSONAL BACKGROUND:
- Occupation: {persona_data['occupation']}
- Ethnicity/Race: {persona_data['ethnicity']}
- Political leaning: {persona_data['political_leaning']} (Scale position: {psychographic_profile.political_lean})
- Core values: {', '.join(persona_data['values'])}
- Media you use: {', '.join(persona_data['media_habits'])}
- Cultural background: {persona_data.get('cultural_background', 'Not specified')}
- Socioeconomic details: {persona_data.get('socioeconomic_details', 'Not specified')}

M1 ENHANCED PROFILE:
Demographics: {demographic_profile.age_band}, {demographic_profile.education_level}, {demographic_profile.income_tier}
Schwartz Values (strongest): {max(psychographic_profile.schwartz_values.items(), key=lambda x: x[1])[0] if psychographic_profile.schwartz_values else 'Unknown'}
Brand Affinity: {psychographic_profile.brand_affinity_cluster}
Media Preference: {media_profile.preferred_content_format} content, {media_profile.daily_usage_hours}h/day

PERSONALITY (Big 5 traits, 0-1 scale):
- Openness to experience: {persona_data['personality_traits']['openness']} ({psychographic_profile.big5_personality.get('openness', 'medium')})
- Conscientiousness: {persona_data['personality_traits']['conscientiousness']} ({psychographic_profile.big5_personality.get('conscientiousness', 'medium')})
- Extraversion: {persona_data['personality_traits']['extraversion']} ({psychographic_profile.big5_personality.get('extraversion', 'medium')})
- Agreeableness: {persona_data['personality_traits']['agreeableness']} ({psychographic_profile.big5_personality.get('agreeableness', 'medium')})
- Neuroticism: {persona_data['personality_traits']['neuroticism']} ({psychographic_profile.big5_personality.get('neuroticism', 'medium')})

REACTION GUIDELINES:
1. React authentically based on your specific background and M1 profile
2. Consider how your cultural background and Schwartz values influence your perspective
3. Factor in your socioeconomic situation and education when evaluating products/services
4. Use language and references that reflect your background and media preferences
5. Be specific about WHY something resonates based on your values and brand affinity
6. Consider how your personality traits and political lean influence reaction intensity
7. Think about credibility through your education/income lens
8. Evaluate purchase intent based on your income tier and brand affinity

{context_prompt}

When responding to messages, embody this persona completely with M1 precision. Your reactions should reflect the complexity of your detailed profile.
"""
            
            persona = Persona(
                id=persona_id,
                name=persona_data['name'],
                age=persona_data['age'],
                gender=persona_data['gender'],
                ethnicity=persona_data['ethnicity'],
                location=persona_data['location'],
                occupation=persona_data['occupation'],
                values=persona_data['values'],
                political_leaning=persona_data['political_leaning'],
                personality_traits=persona_data['personality_traits'],
                media_habits=persona_data['media_habits'],
                system_prompt=persona_system_prompt,
                age_group=age_group,
                location_type=location_type,
                demographic_profile=demographic_profile,
                psychographic_profile=psychographic_profile,
                media_profile=media_profile
            )
            
            self.persona_pool.append(persona)
            print(f"   ✅ Created: {persona.name} ({persona.demographic_profile.age_band}, {persona.demographic_profile.ethnicity_omb})")
            print(f"      💰 {persona.demographic_profile.income_tier} | 🎓 {persona.demographic_profile.education_level} | 🏷️ {persona.psychographic_profile.brand_affinity_cluster}")
            return persona
            
        except Exception as e:
            print(f"Error creating persona: {e}")
            print(f"Raw response: {response.choices[0].message.content}")
            return None
    
    def select_personas_for_segments(self, segments: List[AudienceSegment], personas_per_segment: int = 3, metadata: Dict = None) -> List[Persona]:
        """Create multiple personas for each segment"""
        selected_personas = []
        
        print(f"\n👥 Creating {personas_per_segment} personas per segment with M1 enhanced profiling:")
        for segment in segments:
            print(f"\n📋 Segment: {segment.name}")
            for i in range(personas_per_segment):
                persona = self.create_persona_from_segment(segment, metadata)
                if persona:
                    selected_personas.append(persona)
        
        return selected_personas

# Initialize persona generator
persona_generator = PersonaGenerator(client)


# Stage D: Response Simulation (Personified LLMs)
class ResponseSimulator:
    def __init__(self, client):
        self.client = client
        
    def get_persona_reaction(self, persona: Persona, message: str, show_details: bool = True) -> PersonaReaction:
        """Get a specific persona's reaction to a message with M2 enhanced metrics"""
        reaction_prompt = f"""
Please react to the following message/communication:

"{message}"

Provide your reaction with M2 Enhanced Metrics in the following JSON format:
{{
  "sentiment": -2.5,
  "share_likelihood": 35,
  "emotional_triggers": ["trigger1", "trigger2"],
  "suggested_modifications": "Your suggestions for improvement",
  "explanation": "Detailed explanation of your reaction as this persona",
  
  "m2_emotion_vector": {{
    "joy": 0.2,
    "trust": 0.7,
    "fear": 0.1,
    "surprise": 0.3,
    "sadness": 0.0,
    "disgust": 0.1,
    "anger": 0.0,
    "anticipation": 0.6
  }},
  "credibility_rating": 3.5,
  "purchase_intent": 45,
  "controversy_flag": false,
  "controversy_driver": "none or specific driver if true"
}}

M2 METRICS EXPLANATION:
- sentiment: Scale from -5 (very negative) to +5 (very positive)
- share_likelihood: 0-100% chance you would share/forward this
- emotion_vector: Plutchik 8-way emotions with intensities 0-1 (how much each emotion this triggers)
- credibility_rating: 1-5 scale (how believable/trustworthy you find this message)
- purchase_intent: 0-100% likelihood you'd buy/adopt what's being promoted
- controversy_flag: true/false if you think this message could be controversial
- controversy_driver: main reason for controversy if flag is true

IMPORTANT INSTRUCTIONS:
1. React as the specific person you are based on your complete M1 profile
2. Consider your Schwartz values, income tier, education, and brand affinity
3. Let your political lean influence credibility and controversy assessment
4. Factor purchase intent based on your income tier and brand affinity cluster
5. Use your media preferences to evaluate share likelihood
6. Be precise with emotion vector - which specific emotions does this trigger in YOU
7. Assess credibility through your education and socioeconomic lens

Be honest and authentic to your character with M1/M2 precision.
IMPORTANT: Return ONLY the JSON object, no markdown formatting or code blocks.
"""
        
        response = self.client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": persona.system_prompt},
                {"role": "user", "content": reaction_prompt}
            ],
            max_tokens=MAX_TOKENS,
            temperature=0.8
        )
        
        try:
            response_text = response.choices[0].message.content.strip()
            
            # Remove markdown code blocks if present
            if response_text.startswith('```json'):
                response_text = response_text[7:]  # Remove ```json
            if response_text.startswith('```'):
                response_text = response_text[3:]   # Remove ```
            if response_text.endswith('```'):
                response_text = response_text[:-3]  # Remove closing ```
            
            response_text = response_text.strip()
            
            reaction_data = json.loads(response_text)
            
            # Create M2 emotion vector
            emotion_data = reaction_data.get('m2_emotion_vector', {})
            emotion_vector = EmotionVector(
                joy=emotion_data.get('joy', 0.0),
                trust=emotion_data.get('trust', 0.0),
                fear=emotion_data.get('fear', 0.0),
                surprise=emotion_data.get('surprise', 0.0),
                sadness=emotion_data.get('sadness', 0.0),
                disgust=emotion_data.get('disgust', 0.0),
                anger=emotion_data.get('anger', 0.0),
                anticipation=emotion_data.get('anticipation', 0.0)
            )
            
            reaction = PersonaReaction(
                persona_id=persona.id,
                sentiment=reaction_data['sentiment'],
                share_likelihood=reaction_data['share_likelihood'],
                emotional_triggers=reaction_data['emotional_triggers'],
                suggested_modifications=reaction_data['suggested_modifications'],
                raw_response=reaction_data['explanation'],
                # M2 Enhanced Metrics
                emotion_vector=emotion_vector,
                credibility_rating=reaction_data.get('credibility_rating', 3.0),
                purchase_intent=reaction_data.get('purchase_intent', 50.0),
                controversy_flag=reaction_data.get('controversy_flag', False),
                controversy_driver=reaction_data.get('controversy_driver', None)
            )
            
            if show_details:
                sentiment_emoji = "😍" if reaction.sentiment >= 3 else "😊" if reaction.sentiment >= 1 else "😐" if reaction.sentiment >= -1 else "😞" if reaction.sentiment >= -3 else "😡"
                share_emoji = "🔥" if reaction.share_likelihood >= 70 else "👍" if reaction.share_likelihood >= 40 else "🤷" if reaction.share_likelihood >= 20 else "👎"
                credibility_emoji = "💯" if reaction.credibility_rating >= 4 else "✅" if reaction.credibility_rating >= 3 else "⚠️" if reaction.credibility_rating >= 2 else "❌"
                purchase_emoji = "💳" if reaction.purchase_intent >= 70 else "🛒" if reaction.purchase_intent >= 40 else "🤔" if reaction.purchase_intent >= 20 else "🚫"
                controversy_emoji = "🚨" if reaction.controversy_flag else "✅"
                
                # Top emotions
                emotions = {k: v for k, v in asdict(emotion_vector).items() if v > 0.3}
                top_emotions = sorted(emotions.items(), key=lambda x: x[1], reverse=True)[:2]
                emotion_str = ", ".join([f"{e[0]}({e[1]:.1f})" for e in top_emotions]) if top_emotions else "low emotional response"
                
                print(f"      {sentiment_emoji} Sentiment: {reaction.sentiment:.1f}/5  {share_emoji} Share: {reaction.share_likelihood:.0f}%")
                print(f"      {credibility_emoji} Credibility: {reaction.credibility_rating:.1f}/5  {purchase_emoji} Purchase: {reaction.purchase_intent:.0f}%  {controversy_emoji} Controversy: {reaction.controversy_flag}")
                print(f"      🎭 Emotions: {emotion_str}")
                print(f"      💡 Key insight: {reaction.raw_response[:80]}...")
            
            return reaction
            
        except Exception as e:
            print(f"      ❌ Error parsing reaction from {persona.name}: {e}")
            print(f"Raw response: {response.choices[0].message.content}")
            return None
    
    def simulate_all_reactions(self, personas: List[Persona], message: str) -> List[PersonaReaction]:
        """Get reactions from all personas with M2 enhanced metrics"""
        reactions = []
        
        print(f"\n🎭 Simulating M2-enhanced reactions from {len(personas)} personas:")
        
        for persona in personas:
            print(f"\n   🗣️  {persona.name} ({persona.demographic_profile.age_band}, {persona.demographic_profile.ethnicity_omb}):")
            print(f"        💰 {persona.demographic_profile.income_tier} | 🏷️ {persona.psychographic_profile.brand_affinity_cluster}")
            reaction = self.get_persona_reaction(persona, message, show_details=True)
            if reaction:
                reactions.append(reaction)
        
        print(f"\n   ✅ Collected {len(reactions)} M2-enhanced reactions")
        return reactions

# Initialize response simulator
response_simulator = ResponseSimulator(client)


# Stage E: Insight Aggregation
class InsightAggregator:
    def __init__(self, client):
        self.client = client
    
    def aggregate_insights(self, reactions: List[PersonaReaction], personas: List[Persona], 
                          bias_analysis: BiasAnalysis, metadata: Dict = None, 
                          run_simulations: bool = False) -> InsightReport:
        """Aggregate individual reactions into comprehensive insights with M1/M2/M3 metrics"""
        if not reactions:
            return None
        
        print(f"\n📊 Aggregating M1/M2/M3 enhanced insights from {len(reactions)} reactions...")
        
        # Core metrics
        sentiments = [r.sentiment for r in reactions]
        share_likelihoods = [r.share_likelihood for r in reactions]
        
        mean_sentiment = np.mean(sentiments)
        mean_share_likelihood = np.mean(share_likelihoods)
        
        # M2 Enhanced metrics
        credibility_ratings = [r.credibility_rating for r in reactions if r.credibility_rating is not None]
        purchase_intents = [r.purchase_intent for r in reactions if r.purchase_intent is not None]
        
        mean_credibility = np.mean(credibility_ratings) if credibility_ratings else None
        mean_purchase_intent = np.mean(purchase_intents) if purchase_intents else None
        
        # Emotion profile aggregation
        overall_emotion_profile = self._aggregate_emotion_vectors(reactions)
        
        # Controversy analysis
        controversy_analysis = self._analyze_controversy(reactions, personas)
        
        # Sentiment distribution
        sentiment_labels = []
        for s in sentiments:
            if s >= 3: sentiment_labels.append('Very Positive')
            elif s >= 1: sentiment_labels.append('Positive')
            elif s >= -1: sentiment_labels.append('Neutral')
            elif s >= -3: sentiment_labels.append('Negative')
            else: sentiment_labels.append('Very Negative')
        
        sentiment_distribution = dict(Counter(sentiment_labels))
        
        # Extract emotional themes
        all_triggers = []
        for reaction in reactions:
            all_triggers.extend(reaction.emotional_triggers)
        
        emotional_themes = [item for item, count in Counter(all_triggers).most_common(7)]
        
        # Enhanced risk flags
        risk_flags = []
        for reaction in reactions:
            if reaction.sentiment < -2:
                persona = next((p for p in personas if p.id == reaction.persona_id), None)
                if persona:
                    risk_flags.append(f"Strong negative reaction from {persona.name} ({persona.demographic_profile.age_band}, {persona.demographic_profile.ethnicity_omb}): {reaction.sentiment:.1f}")
            
            if reaction.controversy_flag:
                persona = next((p for p in personas if p.id == reaction.persona_id), None)
                if persona:
                    risk_flags.append(f"Controversy flagged by {persona.name}: {reaction.controversy_driver}")
        
        top_risk_flags = risk_flags[:5]
        
        # Enhanced trait-based insights with M1/M2 metrics
        trait_insights = self._analyze_by_enhanced_traits(reactions, personas)
        
        # Context-specific insights
        context_insights = self._generate_context_insights(reactions, personas, metadata)
        
        # M3 Simulation metrics (optional)
        group_chat_metrics = None
        virality_metrics = None
        popularity_metrics = None
        
        if run_simulations:
            print(f"\n🎮 Running M3 Simulation-Mode Metrics...")
            # Group chat simulation
            group_chat_metrics = simulation_engine.run_group_chat_simulation(personas, metadata.get('message', ''), turns=6)
            
            # Virality cascade simulation
            virality_metrics = simulation_engine.simulate_virality_cascade(reactions, personas)
            
            # Popularity voting (create variants)
            original_message = metadata.get('message', '')
            message_variants = [
                original_message,
                original_message.replace("!", "."),
                original_message + " Don't miss out!"
            ]
            popularity_metrics = simulation_engine.run_popularity_voting(message_variants, personas)
        
        # Enhanced executive summary
        exec_summary = self._generate_enhanced_executive_summary(
            reactions, personas, mean_sentiment, mean_share_likelihood, 
            trait_insights, metadata, mean_credibility, mean_purchase_intent,
            group_chat_metrics, virality_metrics, popularity_metrics
        )
        
        print(f"   ✅ Generated comprehensive M1/M2/M3 insights")
        
        return InsightReport(
            mean_sentiment=mean_sentiment,
            sentiment_distribution=sentiment_distribution,
            mean_share_likelihood=mean_share_likelihood,
            top_risk_flags=top_risk_flags,
            emotional_themes=emotional_themes,
            executive_summary=exec_summary,
            trait_insights=trait_insights,
            bias_analysis=bias_analysis,
            context_specific_insights=context_insights,
            # M2 Enhanced
            mean_credibility=mean_credibility,
            mean_purchase_intent=mean_purchase_intent,
            overall_emotion_profile=overall_emotion_profile,
            controversy_analysis=controversy_analysis,
            # M3 Simulation
            group_chat_metrics=group_chat_metrics,
            virality_metrics=virality_metrics,
            popularity_metrics=popularity_metrics
        )
    
    def _aggregate_emotion_vectors(self, reactions: List[PersonaReaction]) -> Dict[str, float]:
        """Aggregate emotion vectors across all reactions"""
        emotion_totals = {}
        valid_reactions = [r for r in reactions if r.emotion_vector is not None]
        
        if not valid_reactions:
            return {}
        
        for reaction in valid_reactions:
            emotion_dict = asdict(reaction.emotion_vector)
            for emotion, value in emotion_dict.items():
                emotion_totals[emotion] = emotion_totals.get(emotion, 0) + value
        
        # Average emotions
        for emotion in emotion_totals:
            emotion_totals[emotion] /= len(valid_reactions)
        
        return emotion_totals
    
    def _analyze_controversy(self, reactions: List[PersonaReaction], personas: List[Persona]) -> Dict[str, any]:
        """Analyze controversy patterns"""
        controversial_reactions = [r for r in reactions if r.controversy_flag]
        total_reactions = len(reactions)
        
        if not controversial_reactions:
            return {"controversy_rate": 0.0, "main_drivers": [], "risk_demographics": []}
        
        controversy_rate = len(controversial_reactions) / total_reactions
        
        # Analyze drivers
        drivers = [r.controversy_driver for r in controversial_reactions if r.controversy_driver]
        main_drivers = [item for item, count in Counter(drivers).most_common(3)]
        
        # Risk demographics (groups with high controversy rates)
        risk_demographics = []
        for reaction in controversial_reactions:
            persona = next((p for p in personas if p.id == reaction.persona_id), None)
            if persona:
                risk_demographics.append(f"{persona.demographic_profile.age_band} {persona.demographic_profile.ethnicity_omb}")
        
        risk_demographics = list(set(risk_demographics))[:3]
        
        return {
            "controversy_rate": controversy_rate,
            "main_drivers": main_drivers,
            "risk_demographics": risk_demographics
        }
    
    def _analyze_by_enhanced_traits(self, reactions: List[PersonaReaction], personas: List[Persona]) -> Dict[str, List[TraitGroupInsight]]:
        """Enhanced trait analysis with M1/M2 metrics"""
        trait_insights = {}
        
        # Group by M1 Enhanced Demographics
        trait_groupings = {
            "Income Tiers": lambda p: p.demographic_profile.income_tier,
            "Education Levels": lambda p: p.demographic_profile.education_level,
            "Brand Affinity": lambda p: p.psychographic_profile.brand_affinity_cluster,
            "Political Lean": lambda p: "Liberal" if p.psychographic_profile.political_lean < -1 else "Conservative" if p.psychographic_profile.political_lean > 1 else "Moderate",
            "Age Bands": lambda p: p.demographic_profile.age_band,
            "Ethnicity (OMB)": lambda p: p.demographic_profile.ethnicity_omb,
            "Geography": lambda p: p.demographic_profile.geography.get('urban_rural_flag', 'Unknown')
        }
        
        for trait_name, grouping_func in trait_groupings.items():
            trait_groups = {}
            
            for persona in personas:
                trait_value = grouping_func(persona)
                if trait_value not in trait_groups:
                    trait_groups[trait_value] = []
                
                persona_reactions = [r for r in reactions if r.persona_id == persona.id]
                if persona_reactions:
                    trait_groups[trait_value].extend(persona_reactions)
            
            trait_group_insights = []
            for trait_value, group_reactions in trait_groups.items():
                if group_reactions:
                    insight = self._create_enhanced_trait_insight(trait_name, trait_value, group_reactions, personas)
                    trait_group_insights.append(insight)
            
            trait_insights[trait_name] = trait_group_insights
        
        return trait_insights
    
    def _create_enhanced_trait_insight(self, trait_name: str, trait_value: str, 
                                     group_reactions: List[PersonaReaction], personas: List[Persona]) -> TraitGroupInsight:
        """Create enhanced trait insight with M2 metrics"""
        sentiments = [r.sentiment for r in group_reactions]
        share_likelihoods = [r.share_likelihood for r in group_reactions]
        credibility_ratings = [r.credibility_rating for r in group_reactions if r.credibility_rating is not None]
        purchase_intents = [r.purchase_intent for r in group_reactions if r.purchase_intent is not None]
        
        all_triggers = []
        all_concerns = []
        controversy_count = 0
        
        for reaction in group_reactions:
            all_triggers.extend(reaction.emotional_triggers)
            if reaction.sentiment < 0:
                all_concerns.append(reaction.suggested_modifications)
            if reaction.controversy_flag:
                controversy_count += 1
        
        common_triggers = [item for item, count in Counter(all_triggers).most_common(3)]
        key_concerns = list(set(all_concerns))[:3]
        
        # Enhanced metrics
        avg_sentiment = np.mean(sentiments)
        avg_share = np.mean(share_likelihoods)
        avg_credibility = np.mean(credibility_ratings) if credibility_ratings else None
        avg_purchase_intent = np.mean(purchase_intents) if purchase_intents else None
        controversy_rate = controversy_count / len(group_reactions) if group_reactions else 0
        
        # Emotion profile for this group
        emotion_profile = {}
        valid_emotions = [r.emotion_vector for r in group_reactions if r.emotion_vector is not None]
        if valid_emotions:
            for emotion_name in ['joy', 'trust', 'fear', 'surprise', 'sadness', 'disgust', 'anger', 'anticipation']:
                emotion_values = [getattr(ev, emotion_name) for ev in valid_emotions]
                emotion_profile[emotion_name] = np.mean(emotion_values)
        
        # Enhanced recommendations
        if avg_sentiment < -1:
            recommendation = f"Critical concerns from {trait_value}. Address: {', '.join(key_concerns[:2])}. Credibility: {avg_credibility:.1f}/5."
        elif avg_sentiment < 1:
            recommendation = f"Mixed reactions from {trait_value}. A/B test messaging. Purchase intent: {avg_purchase_intent:.0f}%."
        else:
            recommendation = f"Strong positive response from {trait_value}. High credibility ({avg_credibility:.1f}/5). Amplify to similar audiences."
        
        if controversy_rate > 0.3:
            recommendation += f" ⚠️ High controversy rate ({controversy_rate:.0%})."
        
        return TraitGroupInsight(
            trait_name=trait_name,
            trait_value=trait_value,
            persona_count=len(set(r.persona_id for r in group_reactions)),
            avg_sentiment=avg_sentiment,
            avg_share_likelihood=avg_share,
            common_triggers=common_triggers,
            key_concerns=key_concerns,
            recommendations=recommendation,
            # M2 Enhanced
            avg_credibility=avg_credibility,
            avg_purchase_intent=avg_purchase_intent,
            emotion_profile=emotion_profile,
            controversy_rate=controversy_rate
        )
    
    def _generate_context_insights(self, reactions: List[PersonaReaction], personas: List[Persona], 
                                  metadata: Dict = None) -> List[str]:
        """Generate insights specific to the campaign context with M2 metrics"""
        insights = []
        
        if not metadata:
            return insights
        
        company_type = metadata.get('company_type', '')
        target_outcome = metadata.get('target_outcome', '')
        
        avg_sentiment = np.mean([r.sentiment for r in reactions])
        avg_share = np.mean([r.share_likelihood for r in reactions])
        avg_credibility = np.mean([r.credibility_rating for r in reactions if r.credibility_rating is not None])
        avg_purchase = np.mean([r.purchase_intent for r in reactions if r.purchase_intent is not None])
        controversy_rate = sum(1 for r in reactions if r.controversy_flag) / len(reactions)
        
        if company_type == 'startup':
            if avg_share < 50:
                insights.append(f"Low viral potential ({avg_share:.0f}% share rate). For startups, consider more provocative angles.")
            if avg_credibility < 3.0:
                insights.append(f"Credibility concerns ({avg_credibility:.1f}/5). Startups need strong trust signals.")
        
        elif 'major' in company_type or 'large' in company_type:
            if controversy_rate > 0.2:
                insights.append(f"High controversy risk ({controversy_rate:.0%}). Large brands should be cautious.")
            if avg_credibility > 4.0:
                insights.append(f"Strong credibility ({avg_credibility:.1f}/5). Leverage established brand trust.")
        
        if target_outcome == 'sales conversion' and avg_purchase < 40:
            insights.append(f"Low purchase intent ({avg_purchase:.0f}%). Consider stronger value propositions or incentives.")
        
        if target_outcome == 'viral engagement' and avg_share < 60:
            insights.append(f"Below-target viral potential. Current share likelihood: {avg_share:.0f}%")
        
        return insights
    
    def _generate_enhanced_executive_summary(self, reactions: List[PersonaReaction], personas: List[Persona], 
                                           mean_sentiment: float, mean_share: float, trait_insights: Dict, 
                                           metadata: Dict = None, mean_credibility: float = None, 
                                           mean_purchase: float = None, group_chat: GroupChatMetrics = None,
                                           virality: ViralityMetrics = None, popularity: PopularityVotingMetrics = None) -> str:
        """Generate comprehensive executive summary with M1/M2/M3 metrics"""
        
        # Prepare enhanced trait summaries
        trait_summary = ""
        for trait_type, insights in trait_insights.items():
            trait_summary += f"\n{trait_type}:\n"
            for insight in insights:
                trait_summary += f"  - {insight.trait_value}: {insight.avg_sentiment:.1f} sentiment"
                if insight.avg_credibility:
                    trait_summary += f", {insight.avg_credibility:.1f} credibility"
                if insight.avg_purchase_intent:
                    trait_summary += f", {insight.avg_purchase_intent:.0f}% purchase intent"
                trait_summary += "\n"
        
        # M3 simulation summaries
        simulation_summary = ""
        if group_chat:
            simulation_summary += f"\nGroup Chat Simulation: {group_chat.consensus_index:.2f} consensus index"
        if virality:
            simulation_summary += f"\nVirality Projection: {virality.reach_24h:,} 24h reach, {virality.peak_hour_reach:,} peak hour"
        if popularity:
            simulation_summary += f"\nPopularity Testing: {popularity.win_rate:.1%} win rate for preferred variant"
        
        company_context = ""
        if metadata:
            company_context = f"""
CAMPAIGN CONTEXT:
- Company: {metadata.get('company_type', 'Unknown')} ({metadata.get('company_size', 'Unknown')} size)
- Goal: {metadata.get('goal', 'Unknown')}
- Target outcome: {metadata.get('target_outcome', 'Unknown')}
- Channel: {metadata.get('channel', 'Unknown')}
"""
        
        summary_prompt = f"""
Analyze the following comprehensive audience reaction data and create a strategic executive summary.

{company_context}

M1/M2/M3 ENHANCED METRICS:
- Average sentiment: {mean_sentiment:.2f} (scale: -5 to +5)
- Average share likelihood: {mean_share:.1f}%
- Average credibility: {mean_credibility:.1f}/5 if mean_credibility else 'N/A'
- Average purchase intent: {mean_purchase:.1f}% if mean_purchase else 'N/A'
- Total personas analyzed: {len(personas)}

Breakdown by Enhanced Demographics:
{trait_summary}

M3 Simulation Results:
{simulation_summary}

Provide a strategic executive summary with:
1. Overall reception analysis with credibility and purchase intent insights
2. Key demographic patterns from M1 profiling (income, education, brand affinity)
3. M2 emotional and controversy risk assessment
4. M3 simulation-based projections for virality and consensus
5. Specific actionable recommendations for optimization
6. Context-specific strategic advice

Keep it actionable for decision makers.
"""
        
        response = self.client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": summary_prompt}],
            max_tokens=1000,
            temperature=0.5
        )
        
        return response.choices[0].message.content

# Initialize insight aggregator
insight_aggregator = InsightAggregator(client)

class SimulationModeEngine:
    """M3 Simulation-Mode Metrics Engine"""
    def __init__(self, client):
        self.client = client
    
    def run_group_chat_simulation(self, personas: List[Persona], message: str, turns: int = 8) -> GroupChatMetrics:
        """M3: Group-Chat Mode - 6-10 personas converse for N turns"""
        print(f"\n💬 Running Group Chat Simulation ({turns} turns)...")
        
        # Select 6-8 personas for the chat
        chat_personas = personas[:min(8, len(personas))]
        conversation_turns = []
        topic_evolution = [message]
        
        current_topic = message
        
        for turn in range(turns):
            print(f"   Turn {turn + 1}/{turns}...")
            
            # Each persona responds to the current topic/conversation
            turn_responses = []
            for persona in chat_personas:
                response = self._get_chat_response(persona, current_topic, conversation_turns, turn)
                if response:
                    turn_responses.append({
                        'persona_id': persona.id,
                        'persona_name': persona.name,
                        'response': response['message'],
                        'sentiment': response['sentiment'],
                        'turn': turn + 1
                    })
            
            conversation_turns.extend(turn_responses)
            
            # Extract evolving topic from responses
            if turn_responses:
                latest_responses = [r['response'] for r in turn_responses[-3:]]  # Last 3 responses
                evolved_topic = self._extract_evolved_topic(latest_responses)
                topic_evolution.append(evolved_topic)
                current_topic = evolved_topic
        
        # Calculate consensus index (average pairwise sentiment similarity)
        consensus_index = self._calculate_consensus_index(conversation_turns)
        
        # Identify dominant voices (personas with most responses or highest engagement)
        persona_counts = {}
        for turn in conversation_turns:
            persona_id = turn['persona_id']
            persona_counts[persona_id] = persona_counts.get(persona_id, 0) + 1
        
        dominant_voices = [
            next(p.name for p in chat_personas if p.id == pid) 
            for pid, _ in sorted(persona_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        ]
        
        print(f"   ✅ Consensus Index: {consensus_index:.2f}")
        print(f"   👑 Dominant voices: {', '.join(dominant_voices)}")
        
        return GroupChatMetrics(
            consensus_index=consensus_index,
            conversation_turns=conversation_turns,
            topic_evolution=topic_evolution,
            dominant_voices=dominant_voices
        )
    
    def simulate_virality_cascade(self, reactions: List[PersonaReaction], personas: List[Persona]) -> ViralityMetrics:
        """M3: Virality Cascade - simple SI diffusion on synthetic social graph"""
        print(f"\n🦠 Running Virality Cascade Simulation...")
        
        # Create synthetic social graph based on persona similarities
        network_size = max(1000, len(personas) * 50)  # Scale up from our personas
        
        # Calculate initial reach based on share likelihoods
        initial_sharers = sum(1 for r in reactions if r.share_likelihood > 50)
        initial_reach = initial_sharers * 10  # Each sharer reaches ~10 people initially
        
        # Simulate 24-hour cascade
        current_reach = initial_reach
        peak_hour_reach = 0
        diffusion_rate = np.mean([r.share_likelihood / 100 for r in reactions])
        
        # Hour-by-hour simulation
        for hour in range(24):
            # Growth rate based on sentiment and credibility
            avg_sentiment = np.mean([r.sentiment for r in reactions])
            avg_credibility = np.mean([r.credibility_rating for r in reactions])
            
            # Growth factor (higher for positive sentiment and high credibility)
            growth_factor = max(0.1, (avg_sentiment + 5) / 10 * (avg_credibility / 5) * diffusion_rate)
            
            # Exponential growth with decay
            time_decay = max(0.1, 1 - (hour / 24) * 0.7)  # Decay over time
            hour_growth = current_reach * growth_factor * time_decay * np.random.uniform(0.8, 1.2)
            
            current_reach += int(hour_growth)
            peak_hour_reach = max(peak_hour_reach, int(hour_growth))
            
            # Controversy can boost or hurt reach
            controversy_count = sum(1 for r in reactions if r.controversy_flag)
            if controversy_count > len(reactions) * 0.3:  # If >30% find it controversial
                current_reach *= 1.5  # Controversy can boost reach
        
        reach_24h = min(current_reach, network_size)  # Cap at network size
        cascade_depth = int(np.log10(reach_24h)) if reach_24h > 0 else 0
        
        print(f"   📈 24h Reach: {reach_24h:,}")
        print(f"   ⚡ Peak Hour: {peak_hour_reach:,}")
        print(f"   🌊 Cascade Depth: {cascade_depth}")
        
        return ViralityMetrics(
            reach_24h=reach_24h,
            peak_hour_reach=peak_hour_reach,
            diffusion_rate=diffusion_rate,
            cascade_depth=cascade_depth
        )
    
    def run_popularity_voting(self, message_variants: List[str], personas: List[Persona]) -> PopularityVotingMetrics:
        """M3: Popularity Voting - multiple message variants, personas vote"""
        print(f"\n🗳️ Running Popularity Voting ({len(message_variants)} variants)...")
        
        if len(message_variants) < 2:
            # Create variants from the original message
            message_variants = [
                message_variants[0],  # Original
                message_variants[0].replace("!", "."),  # Less excited
                message_variants[0] + " Limited time offer!",  # More urgent
            ]
        
        votes = {f"variant_{i}": 0 for i in range(len(message_variants))}
        persona_preferences = {}
        
        for persona in personas:
            print(f"   🗳️ {persona.name} voting...")
            vote = self._get_popularity_vote(persona, message_variants)
            if vote is not None:
                variant_key = f"variant_{vote}"
                votes[variant_key] += 1
                persona_preferences[persona.id] = vote
        
        total_votes = sum(votes.values())
        if total_votes == 0:
            return PopularityVotingMetrics(0.0, (0.0, 0.0), {}, {})
        
        # Calculate win rate and confidence interval
        winner_votes = max(votes.values())
        win_rate = winner_votes / total_votes
        
        # Bootstrap confidence interval
        confidence_interval = self._bootstrap_confidence_interval(list(votes.values()), winner_votes)
        
        # Analyze preference patterns by demographics
        preference_patterns = self._analyze_preference_patterns(personas, persona_preferences, message_variants)
        
        print(f"   🏆 Win Rate: {win_rate:.1%}")
        print(f"   📊 Votes: {votes}")
        
        return PopularityVotingMetrics(
            win_rate=win_rate,
            confidence_interval=confidence_interval,
            vote_distribution=votes,
            preference_patterns=preference_patterns
        )
    
    def _get_chat_response(self, persona: Persona, topic: str, conversation_history: List[Dict], turn: int) -> Dict:
        """Get a persona's response in group chat context"""
        # Simplified chat response (in real implementation, would be more sophisticated)
        recent_history = conversation_history[-6:] if conversation_history else []
        history_text = "\n".join([f"{h['persona_name']}: {h['response']}" for h in recent_history])
        
        chat_prompt = f"""
You're in a group chat discussing: "{topic}"

Recent conversation:
{history_text}

Respond naturally as yourself in 1-2 sentences. Be authentic to your personality and background.
Provide response as JSON: {{"message": "your response", "sentiment": 1.5}}
"""
        
        try:
            response = self.client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": persona.system_prompt},
                    {"role": "user", "content": chat_prompt}
                ],
                max_tokens=200,
                temperature=0.9
            )
            
            response_text = response.choices[0].message.content.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:-3]
            elif response_text.startswith('```'):
                response_text = response_text[3:-3]
            
            return json.loads(response_text)
        except:
            return {"message": f"I think this is interesting.", "sentiment": 1.0}
    
    def _extract_evolved_topic(self, responses: List[str]) -> str:
        """Extract how the topic has evolved from recent responses"""
        combined = " ".join(responses)
        # Simplified topic extraction (would use more sophisticated NLP in reality)
        return combined[:100] + "..." if len(combined) > 100 else combined
    
    def _calculate_consensus_index(self, conversation_turns: List[Dict]) -> float:
        """Calculate average pairwise sentiment similarity"""
        sentiments = [turn['sentiment'] for turn in conversation_turns]
        if len(sentiments) < 2:
            return 1.0
        
        similarities = []
        for i in range(len(sentiments)):
            for j in range(i + 1, len(sentiments)):
                # Similarity based on sentiment distance (inverted)
                similarity = 1 - abs(sentiments[i] - sentiments[j]) / 10  # Max distance is 10 (-5 to +5)
                similarities.append(max(0, similarity))
        
        return np.mean(similarities) if similarities else 0.0
    
    def _get_popularity_vote(self, persona: Persona, variants: List[str]) -> int:
        """Get persona's vote for preferred message variant"""
        variants_text = "\n".join([f"{i}: {variant}" for i, variant in enumerate(variants)])
        
        vote_prompt = f"""
Choose your preferred message from these options:
{variants_text}

Consider your background, values, and preferences. Respond with just the number (0, 1, 2, etc.) of your preferred option.
"""
        
        try:
            response = self.client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": persona.system_prompt},
                    {"role": "user", "content": vote_prompt}
                ],
                max_tokens=50,
                temperature=0.7
            )
            
            vote_text = response.choices[0].message.content.strip()
            vote = int(vote_text)
            return vote if 0 <= vote < len(variants) else 0
        except:
            return 0  # Default to first option
    
    def _bootstrap_confidence_interval(self, vote_counts: List[int], winner_votes: int, n_bootstrap: int = 1000) -> tuple:
        """Calculate bootstrap confidence interval for win rate"""
        total_votes = sum(vote_counts)
        if total_votes == 0:
            return (0.0, 0.0)
        
        bootstrap_rates = []
        for _ in range(n_bootstrap):
            # Resample with replacement
            bootstrap_votes = np.random.choice(vote_counts, size=total_votes, replace=True)
            bootstrap_winner = np.max(np.bincount(bootstrap_votes))
            bootstrap_rates.append(bootstrap_winner / total_votes)
        
        return (np.percentile(bootstrap_rates, 2.5), np.percentile(bootstrap_rates, 97.5))
    
    def _analyze_preference_patterns(self, personas: List[Persona], preferences: Dict[str, int], 
                                   variants: List[str]) -> Dict[str, List[str]]:
        """Analyze preference patterns by demographics"""
        patterns = {}
        
        # Group by age groups
        age_preferences = {}
        for persona in personas:
            if persona.id in preferences:
                age_group = persona.age_group
                if age_group not in age_preferences:
                    age_preferences[age_group] = []
                age_preferences[age_group].append(preferences[persona.id])
        
        # Find majority preference per age group
        for age_group, prefs in age_preferences.items():
            if prefs:
                majority_pref = max(set(prefs), key=prefs.count)
                patterns[f"Age: {age_group}"] = [f"Prefers variant {majority_pref}"]
        
        return patterns

# Initialize simulation engine
simulation_engine = SimulationModeEngine(client)

class InteractiveExplorer:
    def __init__(self):
        self.reactions = []
        self.personas = []
    
    def set_data(self, reactions: List[PersonaReaction], personas: List[Persona]):
        self.reactions = reactions
        self.personas = personas
    
    def plot_sentiment_distribution(self):
        """Plot sentiment distribution"""
        sentiments = [r.sentiment for r in self.reactions]
        persona_names = []
        
        for reaction in self.reactions:
            persona = next((p for p in self.personas if p.id == reaction.persona_id), None)
            persona_names.append(persona.name if persona else reaction.persona_id)
        
        plt.figure(figsize=(12, 6))
        
        # Sentiment by persona
        plt.subplot(1, 2, 1)
        colors = ['red' if s < -1 else 'orange' if s < 1 else 'lightgreen' if s < 3 else 'green' for s in sentiments]
        bars = plt.bar(range(len(sentiments)), sentiments, color=colors)
        plt.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        plt.title('Sentiment by Persona')
        plt.ylabel('Sentiment (-5 to +5)')
        plt.xticks(range(len(persona_names)), [name.split()[0] for name in persona_names], rotation=45)
        
        # Add value labels on bars
        for bar, sentiment in zip(bars, sentiments):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1 if sentiment >= 0 else bar.get_height() - 0.3,
                    f'{sentiment:.1f}', ha='center', va='bottom' if sentiment >= 0 else 'top')
        
        # Sentiment histogram
        plt.subplot(1, 2, 2)
        plt.hist(sentiments, bins=10, color='skyblue', alpha=0.7, edgecolor='black')
        plt.axvline(x=np.mean(sentiments), color='red', linestyle='--', label=f'Mean: {np.mean(sentiments):.2f}')
        plt.title('Sentiment Distribution')
        plt.xlabel('Sentiment')
        plt.ylabel('Frequency')
        plt.legend()
        
        plt.tight_layout()
        plt.show()
    
    def plot_share_likelihood(self):
        """Plot share likelihood by persona"""
        share_likelihoods = [r.share_likelihood for r in self.reactions]
        persona_names = []
        
        for reaction in self.reactions:
            persona = next((p for p in self.personas if p.id == reaction.persona_id), None)
            persona_names.append(persona.name if persona else reaction.persona_id)
        
        plt.figure(figsize=(10, 6))
        colors = ['red' if s < 25 else 'orange' if s < 50 else 'lightgreen' if s < 75 else 'green' for s in share_likelihoods]
        bars = plt.bar(range(len(share_likelihoods)), share_likelihoods, color=colors)
        
        plt.title('Share Likelihood by Persona')
        plt.ylabel('Share Likelihood (%)')
        plt.xticks(range(len(persona_names)), [name.split()[0] for name in persona_names], rotation=45)
        
        # Add value labels on bars
        for bar, likelihood in zip(bars, share_likelihoods):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                    f'{likelihood:.0f}%', ha='center', va='bottom')
        
        plt.axhline(y=np.mean(share_likelihoods), color='red', linestyle='--', 
                   label=f'Mean: {np.mean(share_likelihoods):.1f}%')
        plt.legend()
        plt.tight_layout()
        plt.show()
    
    def show_persona_details(self):
        """Display detailed persona information with their reactions"""
        for persona in self.personas:
            reaction = next((r for r in self.reactions if r.persona_id == persona.id), None)
            if reaction:
                print(f"\n{'='*60}")
                print(f"PERSONA: {persona.name}")
                print(f"{'='*60}")
                print(f"Age: {persona.age} | Gender: {persona.gender} | Location: {persona.location}")
                print(f"Occupation: {persona.occupation}")
                print(f"Values: {', '.join(persona.values)}")
                print(f"Political leaning: {persona.political_leaning}")
                print(f"\nREACTION:")
                print(f"Sentiment: {reaction.sentiment:.1f}/5 | Share likelihood: {reaction.share_likelihood:.0f}%")
                print(f"Emotional triggers: {', '.join(reaction.emotional_triggers)}")
                print(f"\nDetailed response:\n{reaction.raw_response}")
                print(f"\nSuggested modifications:\n{reaction.suggested_modifications}")
    
    def filter_by_demographic(self, age_range: str = None, location: str = None, political_leaning: str = None):
        """Filter results by demographic criteria"""
        filtered_personas = self.personas.copy()
        
        if age_range:
            filtered_personas = [p for p in filtered_personas if age_range.lower() in str(p.age).lower()]
        
        if location:
            filtered_personas = [p for p in filtered_personas if location.lower() in p.location.lower()]
        
        if political_leaning:
            filtered_personas = [p for p in filtered_personas if political_leaning.lower() in p.political_leaning.lower()]
        
        filtered_reactions = [r for r in self.reactions if any(p.id == r.persona_id for p in filtered_personas)]
        
        print(f"Filtered to {len(filtered_personas)} personas matching criteria:")
        if filtered_reactions:
            avg_sentiment = np.mean([r.sentiment for r in filtered_reactions])
            avg_share = np.mean([r.share_likelihood for r in filtered_reactions])
            print(f"Average sentiment: {avg_sentiment:.2f}")
            print(f"Average share likelihood: {avg_share:.1f}%")
        
        return filtered_personas, filtered_reactions

# Initialize interactive explorer
interactive_explorer = InteractiveExplorer()


# Complete Pipeline Integration
class SocaioPipeline:
    def __init__(self, client):
        self.prompt_intake = PromptIntake()
        self.audience_profiler = AudienceProfiler(client)
        self.persona_generator = PersonaGenerator(client)
        self.response_simulator = ResponseSimulator(client)
        self.insight_aggregator = InsightAggregator(client)
        self.interactive_explorer = InteractiveExplorer()
    
    def run_full_pipeline(self, message: str, goal: str = None, channel: str = None, 
                         tone: str = None, personas_per_segment: int = 3, company_type: str = None, 
                         company_size: str = None, audience_size: str = None, brand_context: str = None, 
                         campaign_type: str = None, target_outcome: str = None, run_simulations: bool = False):
        """Run the complete Socaio pipeline with M1/M2/M3 enhanced metrics"""
        print("🚀 Starting M1/M2/M3 Enhanced Socaio Pipeline...\n")
        
        # Stage A: Prompt Intake
        print("📝 Stage A: Capturing message with enhanced context...")
        prompt_data = self.prompt_intake.capture_message(
            message, goal, channel, tone, company_type, company_size, 
            audience_size, brand_context, campaign_type, target_outcome
        )
        prompt_data['metadata']['message'] = message  # Store for M3 simulations
        print(f"✅ Message captured: {len(message)} characters")
        print(f"📋 Context captured: {prompt_data['metadata']['company_type']} campaign")
        
        # Stage B: Audience Profiling with M1 Demographics
        print(f"\n🎯 Stage B: M1 Enhanced audience profiling with bias analysis...")
        segments, bias_analysis = self.audience_profiler.profile_audience(message, prompt_data['metadata'])
        print(f"✅ Generated {len(segments)} audience segments")
        
        # Stage C: M1 Enhanced Persona Creation
        print(f"\n👥 Stage C: Creating {personas_per_segment} M1-enhanced personas per segment...")
        personas = self.persona_generator.select_personas_for_segments(segments, personas_per_segment, prompt_data['metadata'])
        print(f"✅ Created {len(personas)} total personas with M1 profiling")
        
        # Stage D: M2 Enhanced Response Simulation
        print(f"\n🎭 Stage D: M2 Enhanced reaction simulation...")
        reactions = self.response_simulator.simulate_all_reactions(personas, message)
        print(f"✅ Collected {len(reactions)} M2-enhanced reactions")
        
        # Stage E: M1/M2/M3 Comprehensive Insight Aggregation
        print(f"\n📊 Stage E: Comprehensive M1/M2/M3 insight aggregation...")
        insights = self.insight_aggregator.aggregate_insights(
            reactions, personas, bias_analysis, prompt_data['metadata'], run_simulations
        )
        print("✅ M1/M2/M3 comprehensive insights generated")
        
        # Stage F: Setup Interactive Explorer
        print(f"\n🔍 Stage F: Setting up enhanced interactive exploration...")
        self.interactive_explorer.set_data(reactions, personas)
        print("✅ Explorer ready with M1/M2/M3 capabilities")
        
        return {
            'message': message,
            'metadata': prompt_data['metadata'],
            'segments': segments,
            'personas': personas,
            'reactions': reactions,
            'insights': insights,
            'bias_analysis': bias_analysis,
            'explorer': self.interactive_explorer
        }
    
    def display_results(self, results):
        """Display M1/M2/M3 enhanced pipeline results"""
        insights = results['insights']
        metadata = results.get('metadata', {})
        
        print("\n" + "="*100)
        print("                M1/M2/M3 ENHANCED SOCAIO ANALYSIS RESULTS")
        print("="*100)
        
        if insights is None:
            print("\n❌ No insights available - pipeline may have failed to generate reactions.")
            print("Please check if audience segments and personas were created successfully.")
            return
        
        # Campaign Context
        print(f"\n📋 CAMPAIGN CONTEXT:")
        print(f"   Company: {metadata.get('company_type', 'N/A')} ({metadata.get('company_size', 'N/A')})")
        print(f"   Goal: {metadata.get('goal', 'N/A')}")
        print(f"   Channel: {metadata.get('channel', 'N/A')}")
        print(f"   Target outcome: {metadata.get('target_outcome', 'N/A')}")
        
        # M2 Enhanced Overall Metrics
        print(f"\n📈 M2 ENHANCED OVERALL METRICS:")
        print(f"   Sentiment: {insights.mean_sentiment:.2f}/5 ", end="")
        if insights.mean_sentiment >= 3:
            print("(Very Positive 😍)")
        elif insights.mean_sentiment >= 1:
            print("(Positive 😊)")
        elif insights.mean_sentiment >= -1:
            print("(Neutral 😐)")
        elif insights.mean_sentiment >= -3:
            print("(Negative 😞)")
        else:
            print("(Very Negative 😡)")
            
        print(f"   Share Likelihood: {insights.mean_share_likelihood:.1f}%")
        
        if insights.mean_credibility is not None:
            print(f"   Credibility: {insights.mean_credibility:.1f}/5")
        
        if insights.mean_purchase_intent is not None:
            print(f"   Purchase Intent: {insights.mean_purchase_intent:.1f}%")
        
        # M2 Emotion Profile
        if insights.overall_emotion_profile:
            top_emotions = sorted(insights.overall_emotion_profile.items(), key=lambda x: x[1], reverse=True)[:3]
            print(f"   Top Emotions: {', '.join([f'{e[0]}({e[1]:.1f})' for e in top_emotions])}")
        
        # M2 Controversy Analysis
        if insights.controversy_analysis and insights.controversy_analysis['controversy_rate'] > 0:
            print(f"   Controversy Rate: {insights.controversy_analysis['controversy_rate']:.1%}")
            if insights.controversy_analysis['main_drivers']:
                print(f"   Main Drivers: {', '.join(insights.controversy_analysis['main_drivers'])}")
        
        # M3 Simulation Results
        if insights.group_chat_metrics or insights.virality_metrics or insights.popularity_metrics:
            print(f"\n🎮 M3 SIMULATION RESULTS:")
            
            if insights.group_chat_metrics:
                print(f"   💬 Group Chat Consensus: {insights.group_chat_metrics.consensus_index:.2f}")
                print(f"   👑 Dominant Voices: {', '.join(insights.group_chat_metrics.dominant_voices)}")
            
            if insights.virality_metrics:
                print(f"   🦠 Projected 24h Reach: {insights.virality_metrics.reach_24h:,}")
                print(f"   ⚡ Peak Hour Reach: {insights.virality_metrics.peak_hour_reach:,}")
                print(f"   🌊 Cascade Depth: {insights.virality_metrics.cascade_depth}")
            
            if insights.popularity_metrics:
                print(f"   🗳️ Win Rate: {insights.popularity_metrics.win_rate:.1%}")
                print(f"   📊 Vote Distribution: {insights.popularity_metrics.vote_distribution}")
        
        # M1/M2 Enhanced Trait-based Insights
        print(f"\n🎯 M1/M2 ENHANCED DEMOGRAPHIC INSIGHTS:")
        for trait_type, trait_insights in insights.trait_insights.items():
            if not trait_insights:
                continue
                
            print(f"\n   📌 {trait_type}:")
            for insight in trait_insights:
                sentiment_emoji = "😍" if insight.avg_sentiment >= 3 else "😊" if insight.avg_sentiment >= 1 else "😐" if insight.avg_sentiment >= -1 else "😞" if insight.avg_sentiment >= -3 else "😡"
                
                print(f"      {sentiment_emoji} {insight.trait_value}:")
                print(f"         📊 Sentiment: {insight.avg_sentiment:.1f}, Share: {insight.avg_share_likelihood:.0f}%", end="")
                
                if insight.avg_credibility:
                    print(f", Credibility: {insight.avg_credibility:.1f}/5", end="")
                if insight.avg_purchase_intent:
                    print(f", Purchase: {insight.avg_purchase_intent:.0f}%", end="")
                if insight.controversy_rate and insight.controversy_rate > 0:
                    print(f", Controversy: {insight.controversy_rate:.0%}", end="")
                print()
                
                if insight.common_triggers:
                    print(f"         🔥 Triggers: {', '.join(insight.common_triggers)}")
                
                # Top emotions for this group
                if insight.emotion_profile:
                    top_emotions = sorted(insight.emotion_profile.items(), key=lambda x: x[1], reverse=True)[:2]
                    if top_emotions and top_emotions[0][1] > 0.3:
                        print(f"         🎭 Emotions: {', '.join([f'{e[0]}({e[1]:.1f})' for e in top_emotions])}")
                
                print(f"         💡 {insight.recommendations}")
        
        # Bias Analysis
        if insights.bias_analysis and (insights.bias_analysis.potential_biases or insights.bias_analysis.diversity_gaps):
            print(f"\n⚠️  BIAS & DIVERSITY ANALYSIS:")
            if insights.bias_analysis.potential_biases:
                print(f"   Potential biases detected: {', '.join(insights.bias_analysis.potential_biases)}")
            if insights.bias_analysis.diversity_gaps:
                print(f"   Diversity gaps: {', '.join(insights.bias_analysis.diversity_gaps)}")
            print(f"   Inclusivity score: {insights.bias_analysis.inclusivity_score:.1f}/10")
        
        # Context-specific insights
        if insights.context_specific_insights:
            print(f"\n🎯 CONTEXT-SPECIFIC INSIGHTS:")
            for insight in insights.context_specific_insights:
                print(f"   • {insight}")
        
        # Risk Flags
        if insights.top_risk_flags:
            print(f"\n⚠️  TOP RISK FLAGS:")
            for flag in insights.top_risk_flags:
                print(f"   • {flag}")
        
        # Emotional Themes
        print(f"\n🎭 EMOTIONAL THEMES:")
        for theme in insights.emotional_themes:
            print(f"   • {theme}")
        
        # M1/M2/M3 Enhanced Executive Summary
        print(f"\n📋 M1/M2/M3 STRATEGIC EXECUTIVE SUMMARY:")
        print(f"{insights.executive_summary}")
        
        print("\n" + "="*100)

# Initialize the complete pipeline
socaio = SocaioPipeline(client)

print("🎉 M1/M2/M3 Enhanced Socaio Pipeline initialized!")
print("\nCOMPREHENSIVE METRICS INTEGRATION:")
print("📊 M1: Demographics (5-yr age bands, OMB ethnicity, income tiers, education, Schwartz values, Big-5)")
print("🎭 M2: Reactions (sentiment, Plutchik emotions, credibility, purchase intent, controversy)")
print("🎮 M3: Simulations (group chat consensus, virality cascade, popularity voting)")
print("\nTo run analysis: results = socaio.run_full_pipeline('message', company_type='startup', run_simulations=True)")