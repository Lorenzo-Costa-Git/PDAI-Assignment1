import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import google.generativeai as genai
import json
import urllib.parse

def apply_nextrep_theme():
    st.markdown("""
        <style>
        /* 1. Force the main container to Black */
        .stApp, [data-testid="stAppViewContainer"] {
            background-color: #000000 !important;
        }

        /* 2. Force the Sidebar to Black */
        [data-testid="stSidebar"] {
            background-color: #000000 !important;
            border-right: 2px solid #39FF14 !important;
        }

        /* 3. Target the Header/Toolbar to prevent white strips at the top */
        header[data-testid="stHeader"] {
            background-color: rgba(0,0,0,0) !important;
            color: #39FF14 !important;
        }

        /* 4. Force every possible text element to Neon Green */
        h1, h2, h3, p, span, label, .stMarkdown, [data-testid="stMetricValue"] {
            color: #39FF14 !important;
            font-family: 'Orbitron', sans-serif !important;
        }

        /* 5. Hide the 'Theme' toggle menu so the user can't find it */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* 6. Fix for white dropdowns/widgets */
        div[data-baseweb="select"] > div, 
        div[data-baseweb="input"] > div,
        div[data-baseweb="popover"] {
            background-color: #050505 !important;
            border: 1px solid #39FF14 !important;
        }
        </style>
    """, unsafe_allow_html=True)

# --- 1. Dynamic Data Loading Engine ---
@st.cache_data
def load_and_map_mets():
    """Reads MET_data.csv and maps app sports to specific data rows."""
    try:
        df = pd.read_csv('MET_data.csv')
    except FileNotFoundError:
        st.error("Error: 'MET_data.csv' not found. Please ensure it is in the same folder as this script.")
        return {}

    # Define the 27 sports and their specific search keys in the CSV
    sport_search_keys = {
        "Football": ("soccer", "competitive"),
        "American Football": ("football", "competitive"),
        "Running": ("running", "7 mph"), 
        "MMA": ("martial arts", "moderate"), 
        "BJJ": ("martial arts", "moderate"),
        "Gym (Weights)": ("weight lifting", "vigorous"),
        "Cycling": ("bicycling", "12-13.9 mph"),
        "Boxing": ("boxing", "in ring"),
        "Muay Thai": ("martial arts", "Muay Thai"),
        "Hockey": ("hockey, field", ""),
        "Hockey on ice": ("hockey, ice", ""),
        "Basketball": ("basketball", "game"),
        "Tennis": ("tennis", "singles"),
        "Badminton": ("badminton", "competitive"),
        "Swimming": ("swimming", "vigorous"),
        "Rugby": ("rugby", "union"),
        "Handball": ("handball", "team"),
        "Skiing": ("skiing", "downhill"),
        "Cross-fit": ("circuit training", "vigorous"),
        "Walking": ("walking", "3.5 mph"),
        "Cricket": ("cricket", ""),
        "Baseball": ("baseball", ""),
        "Wrestling": ("wrestling", ""),
        "Kickboxing": ("kickboxing", ""),
        "Acrobatics": ("gymnastics", ""),
        "Waterpolo": ("water polo", ""),
        "Padel": ("tennis", "moderate") # Proxy search
    }

    final_mapping = {}
    for app_name, (csv_key, qualifier) in sport_search_keys.items():
        # Search Activity Description
        mask = df['Activity Description'].str.contains(csv_key, case=False, na=False)
        if qualifier:
            mask = mask & df['Activity Description'].str.contains(qualifier, case=False, na=False)
        
        matches = df[mask]
        
        # Fallback to broader search if specific qualifier fails
        if matches.empty:
            matches = df[df['Activity Description'].str.contains(csv_key, case=False, na=False)]
        
        if not matches.empty:
            # Pick the most representative (max) MET from the filtered matches
            final_mapping[app_name] = round(matches['MET Value'].max(), 1)
        else:
            final_mapping[app_name] = 6.0 # Safety default
            
    return final_mapping

# Load the dynamic mapping
sport_mets = load_and_map_mets()

SPORTS_PHYSIOLOGY_NOTES = """
- Recovery tax reflects how close yesterday's load was to ~2,500 MET-mins (approx. one maximal day).
- High MET sports (boxing, running) deplete glycogen quickly; lower MET strength sessions stress musculoskeletal systems differently.
- Alternating heavy neurological days with aerobic/skill or rest days prevents overreaching and keeps HRV within sustainable ranges.
- Refueling should scale carbs with MET load (3-5 g/kg) and protein with tissue repair (0.3 g/kg per meal).
"""

@st.cache_data
def met_reference_excerpt(rows: int = 30) -> str:
    try:
        df = pd.read_csv("MET_data.csv")
    except FileNotFoundError:
        return ""
    cols = [c for c in df.columns if "Activity" in c or "MET" in c]
    subset = df[cols].head(rows)
    return subset.to_csv(index=False)

if "meal_plans" not in st.session_state:
    st.session_state["meal_plans"] = {}
if "meal_dislikes" not in st.session_state:
    st.session_state["meal_dislikes"] = {}
if "coach_chat" not in st.session_state:
    st.session_state["coach_chat"] = []

if "meal_plans" not in st.session_state:
    st.session_state["meal_plans"] = {}
if "meal_dislikes" not in st.session_state:
    st.session_state["meal_dislikes"] = {}

# --- 2. UI Layout ---
st.set_page_config(page_title="NextRep: Dynamic Workouts Tailored to you", page_icon="📈")


st.set_page_config(page_title="NextRep: Dynamic Workouts Tailored to you", page_icon="📈", layout="wide")

# --- FUTURISTIC NEON THEME (Orbitron + neon green on black) ---
st.markdown("""
<style>
/* 1) Import Orbitron */
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;800&display=swap');

/* 2) Theme variables */
:root{
  --bg: #050608;
  --panel: #0a0d10;
  --panel2: #07090c;
  --neon: #39ff14;
  --neon2: #00ffcc;
  --text: #c9ffd0;
  --muted: rgba(57,255,20,0.65);
  --border: rgba(57,255,20,0.25);
  --glow: 0 0 10px rgba(57,255,20,0.45), 0 0 24px rgba(57,255,20,0.25);
}

/* 3) Global background + font */
html, body, [class*="css"]  {
  font-family: 'Orbitron', system-ui, -apple-system, Segoe UI, Roboto, sans-serif !important;
}
.stApp {
  background:
    radial-gradient(1000px 600px at 15% 10%, rgba(57,255,20,0.10), transparent 55%),
    radial-gradient(900px 500px at 85% 30%, rgba(0,255,204,0.08), transparent 50%),
    linear-gradient(180deg, var(--bg), #000 70%);
  color: var(--text);
}

/* 4) Sidebar */
section[data-testid="stSidebar"]{
  background: linear-gradient(180deg, #050608, #020304 70%) !important;
  border-right: 1px solid var(--border);
  box-shadow: inset -10px 0 30px rgba(57,255,20,0.06);
}
section[data-testid="stSidebar"] *{
  color: var(--text) !important;
}

/* 5) Titles + neon glow */
h1, h2, h3 {
  color: var(--neon) !important;
  text-shadow: var(--glow);
  letter-spacing: 0.5px;
}
p, li, label, .stMarkdown, .stCaption {
  color: var(--text) !important;
}
small, .stCaption { color: var(--muted) !important; }

/* 6) Cards/containers vibe */
div[data-testid="stVerticalBlockBorderWrapper"]{
  background: rgba(10, 13, 16, 0.65);
  border: 1px solid var(--border);
  border-radius: 14px;
  box-shadow: 0 0 0 1px rgba(57,255,20,0.08), 0 10px 40px rgba(0,0,0,0.6);
  padding: 8px 10px;
}

/* 7) Inputs (selectbox, multiselect, number_input, slider etc.) */
div[data-baseweb="select"] > div,
div[data-baseweb="input"] > div,
div[data-baseweb="textarea"] > div{
  background: var(--panel) !important;
  border: 1px solid var(--border) !important;
  box-shadow: var(--glow);
}

/* Dropdown text */
div[data-baseweb="select"] span,
div[data-baseweb="select"] input,
div[data-baseweb="input"] input {
  color: var(--neon) !important;
  text-shadow: 0 0 8px rgba(57,255,20,0.35);
}

/* Dropdown menu panel */
ul[role="listbox"]{
  background: #050608 !important;
  border: 1px solid var(--border) !important;
  box-shadow: 0 0 30px rgba(57,255,20,0.15);
}
ul[role="listbox"] li{
  color: var(--text) !important;
}
ul[role="listbox"] li:hover{
  background: rgba(57,255,20,0.08) !important;
  color: var(--neon) !important;
}

/* 8) Slider styling */
div[data-testid="stSlider"] > div{
  background: transparent !important;
}
div[data-testid="stSlider"] [role="slider"]{
  box-shadow: var(--glow);
  border: 1px solid rgba(57,255,20,0.55) !important;
}

/* 9) Metric styling */
div[data-testid="stMetric"]{
  background: rgba(10,13,16,0.55);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 14px 16px;
  box-shadow: 0 0 0 1px rgba(57,255,20,0.08);
}
div[data-testid="stMetric"] *{
  color: var(--neon) !important;
  text-shadow: var(--glow);
}

/* 10) Expander */
details{
  background: rgba(10, 13, 16, 0.55) !important;
  border: 1px solid var(--border) !important;
  border-radius: 14px !important;
  box-shadow: 0 0 20px rgba(57,255,20,0.10);
}
details summary{
  color: var(--neon) !important;
  text-shadow: var(--glow);
}
details summary:hover{
  background: rgba(57,255,20,0.06) !important;
}

/* 11) Buttons (if you add any later) */
.stButton button{
  background: linear-gradient(180deg, rgba(57,255,20,0.18), rgba(57,255,20,0.08)) !important;
  border: 1px solid rgba(57,255,20,0.55) !important;
  color: var(--neon) !important;
  box-shadow: var(--glow);
  border-radius: 12px;
}
.stButton button:hover{
  transform: translateY(-1px);
  border-color: var(--neon) !important;
}

/* 12) Alerts (success/info/error) */
div[data-testid="stAlert"]{
  border: 1px solid var(--border) !important;
  background: rgba(0,0,0,0.55) !important;
  box-shadow: 0 0 20px rgba(57,255,20,0.12);
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
/* ---------- DROPDOWN / MULTISELECT MENUS (BaseWeb portal) ---------- */

/* The popover container that holds the dropdown menu */
div[data-baseweb="popover"],
div[data-baseweb="popover"] > div {
  background: #050608 !important;
}

/* Menu surface */
div[data-baseweb="menu"]{
  background: #050608 !important;
  border: 1px solid rgba(57,255,20,0.35) !important;
  box-shadow: 0 0 16px rgba(57,255,20,0.35), 0 0 36px rgba(57,255,20,0.18) !important;
  border-radius: 14px !important;
  overflow: hidden !important;
}

/* Menu list itself */
ul[role="listbox"]{
  background: #050608 !important;
}

/* Menu items */
div[data-baseweb="menu"] li,
ul[role="listbox"] li{
  background: transparent !important;
  color: rgba(201,255,208,0.92) !important;
  font-family: 'Orbitron', system-ui, -apple-system, Segoe UI, Roboto, sans-serif !important;
  letter-spacing: 0.2px !important;
}

/* Hover / active item */
div[data-baseweb="menu"] li:hover,
ul[role="listbox"] li:hover{
  background: rgba(57,255,20,0.10) !important;
  color: #39ff14 !important;
  text-shadow: 0 0 8px rgba(57,255,20,0.35) !important;
}

/* Selected item (varies by BaseWeb version; these usually catch it) */
div[data-baseweb="menu"] li[aria-selected="true"],
ul[role="listbox"] li[aria-selected="true"]{
  background: rgba(57,255,20,0.14) !important;
  color: #39ff14 !important;
}

/* Dropdown scrollbar (WebKit) */
div[data-baseweb="menu"]::-webkit-scrollbar,
ul[role="listbox"]::-webkit-scrollbar{
  width: 10px;
}
div[data-baseweb="menu"]::-webkit-scrollbar-track,
ul[role="listbox"]::-webkit-scrollbar-track{
  background: #050608;
}
div[data-baseweb="menu"]::-webkit-scrollbar-thumb,
ul[role="listbox"]::-webkit-scrollbar-thumb{
  background: rgba(57,255,20,0.25);
  border: 1px solid rgba(57,255,20,0.35);
  border-radius: 20px;
}

/* ---------- MULTISELECT "CHIPS" (selected tags) ---------- */
div[data-baseweb="tag"]{
  background: rgba(57,255,20,0.10) !important;
  border: 1px solid rgba(57,255,20,0.45) !important;
  box-shadow: 0 0 10px rgba(57,255,20,0.25) !important;
}
div[data-baseweb="tag"] *{
  color: #39ff14 !important;
  font-family: 'Orbitron', system-ui, -apple-system, Segoe UI, Roboto, sans-serif !important;
}

/* Tag remove (x) icon */
div[data-baseweb="tag"] svg{
  filter: drop-shadow(0 0 6px rgba(57,255,20,0.35));
}

/* ---------- INPUT CARET / PLACEHOLDER ---------- */
div[data-baseweb="select"] input::placeholder{
  color: rgba(57,255,20,0.45) !important;
}

/* Ensure the select "control" stays black and glowy */
div[data-baseweb="select"] > div{
  background: #0a0d10 !important;
  border: 1px solid rgba(57,255,20,0.30) !important;
  box-shadow: 0 0 10px rgba(57,255,20,0.25), 0 0 24px rgba(57,255,20,0.12) !important;
}

/* The little dropdown arrow */
div[data-baseweb="select"] svg{
  filter: drop-shadow(0 0 8px rgba(57,255,20,0.35));
}
</style>
""", unsafe_allow_html=True)


st.title("NextRep: Dynamic Workouts Tailored to you")
st.markdown("All metabolic data is read directly from your `MET_data.csv` file.")

with st.sidebar:
    st.header("1. Your Sports Universe")
    my_sports = st.multiselect("Pick up to 5 preferred sports:", sorted(list(sport_mets.keys())), max_selections=5)

# --- 3. Yesterday's History & Today's Fatigue ---
st.subheader("2. Physical History & Readiness")
c1, c2, c3 = st.columns(3)
with c1:
    y_sport = st.selectbox("Sport Done Yesterday", ["None"] + sorted(list(sport_mets.keys())))
with c2:
    y_dur = st.number_input("Duration (mins)", min_value=0, value=60, step=15)
with c3:
    y_int = st.select_slider("Intensity", options=["Low", "Medium", "High"], value="Medium")

# Calculate objective strain from yesterday
y_met = sport_mets.get(y_sport, 0)
y_mult = {"Low": 0.8, "Medium": 1.0, "High": 1.2}[y_int]
yesterday_strain = y_met * y_dur * y_mult

st.subheader("3. Current State")
fatigue = st.select_slider(
    "How tired are you?",
    options=["Dead", "Very Tired", "Tired", "Slightly Tired", "Normal", "Energized", "Want to Move", "Have to Move"],
    value="Normal"
)

# Initialize the Gemini API using Streamlit Secrets
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

def get_dynamic_meal(sport, duration, intensity, strain, fatigue_level, disliked=None):
    model = genai.GenerativeModel('gemini-2.5-flash')
    prompt = f"""
    The user is an athlete. They just played {sport} for {duration} mins at {intensity} intensity. 
    Their current metabolic strain is {strain} points and their fatigue level is {fatigue_level}.
    Suggest a specific recovery meal that rotates cuisines and avoids repeating generic chicken-and-rice style dishes.
    {"Do NOT repeat these meals: " + str(disliked) if disliked else ""}
    You MUST output ONLY valid JSON with the exact following keys: 
    "Meal_Name", "Protein_grams", "Carb_grams", "Fat_grams",
    "Key_Ingredients" (an array where each element is an object with "Ingredient" and "Gram_Range" such as "20-30g"),
    "Rationale".
    """
    response = model.generate_content(
        prompt,
        generation_config=genai.GenerationConfig(response_mime_type="application/json")
    )
    
    raw_text = response.text or ""
    try:
        meal_data = json.loads(raw_text)
    except (json.JSONDecodeError, TypeError):
        st.error("AI returned invalid nutrition data. Please retry.")
        return None
    return meal_data


def render_meal(meal_data, sport):
    st.markdown(f"### 🍽️ {meal_data.get('Meal_Name', 'Recovery Meal')}")
    st.write(f"**Rationale:** {meal_data.get('Rationale', '')}")
    ingredients = []
    for item in meal_data.get("Key_Ingredients", []):
        if isinstance(item, dict):
            ingredients.append(f"{item.get('Ingredient', 'Ingredient')} ({item.get('Gram_Range', 'n/a')})")
        else:
            ingredients.append(str(item))
    st.write(f"**Ingredients:** {', '.join(ingredients)}")
    
    c1, c2, c3 = st.columns(3)
    c1.metric("PROTEIN", f"{meal_data.get('Protein_grams', 0)}g")
    c2.metric("CARBS", f"{meal_data.get('Carb_grams', 0)}g")
    c3.metric("FATS", f"{meal_data.get('Fat_grams', 0)}g")

    video_query = urllib.parse.quote_plus(f"{meal_data.get('Meal_Name', sport)} recovery recipe")
    video_url = f"https://www.youtube.com/results?search_query={video_query}"
    st.link_button("📺 Watch a recipe walkthrough", video_url)


def answer_recovery_coach(question, fatigue_level, yesterday_load, tax_factor):
    met_data = met_reference_excerpt()
    model = genai.GenerativeModel('gemini-2.5-flash')
    prompt = f"""
    You are the NextRep Recovery Coach. Use the provided MET reference and sports physiology primer to answer user questions.
    MET reference (CSV excerpt):
    {met_data if met_data else "Unavailable"}

    Sports physiology primer:
    {SPORTS_PHYSIOLOGY_NOTES}

    Current context:
    - Fatigue state: {fatigue_level}
    - Yesterday's strain: {int(yesterday_load)} MET-minutes
    - Recovery tax factor: {tax_factor:.2f}
    Question: {question}

    Respond with a conversational explanation that cites specific MET insights or primer concepts.
    """
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Recovery Coach is unavailable right now ({e})."


def generate_weekly_plan(budget, sports, fatigue_level, yesterday_load, tax_factor):
    model = genai.GenerativeModel('gemini-2.5-flash')
    sport_payload = [{"sport": s, "met": round(sport_mets.get(s, 6.0), 2)} for s in sports]
    prompt = f"""
    You are a sports periodization coach. Build a 7-day plan that uses at most {int(budget)} MET-minutes in total.
    Preferred sports with MET demand: {sport_payload}. Yesterday's strain was {int(yesterday_load)} MET-minutes; current fatigue is {fatigue_level}; today's recovery tax factor is {tax_factor:.2f}.
    Rules:
      - Heavy days must be followed by light or rest days.
      - Once cumulative MET-minutes reach the budget, remaining days must be Rest (0 strain).
      - Vary sports and intensities; keep each day's Target Strain realistic for that sport's MET value.
    Output ONLY JSON with key "schedule" -> array of 7 entries.
    Each entry must include "Day" (1-7), "Sport", "Duration (mins)" (integer), "Target Strain" (integer),
    "Intensity" (Low/Medium/High/Rest), and "Reasoning".
    """
    response = model.generate_content(
        prompt,
        generation_config=genai.GenerationConfig(response_mime_type="application/json")
    )
    raw_text = response.text or ""
    payload = json.loads(raw_text)
    schedule = payload.get("schedule", [])

    for entry in schedule:
        if "Duration (mins)" not in entry and "Duration_mins" in entry:
            entry["Duration (mins)"] = entry["Duration_mins"]
        if "Target Strain" not in entry and "Target_Strain" in entry:
            entry["Target Strain"] = entry["Target_Strain"]
        if "Intensity" not in entry or not entry["Intensity"]:
            entry["Intensity"] = "Rest" if entry.get("Sport", "").lower() == "rest" else "Medium"
    return ensure_rest_day(schedule, budget)


def _safe_positive(value):
    try:
        return max(0.0, float(value))
    except (TypeError, ValueError):
        return 0.0


def ensure_rest_day(schedule, budget):
    total_strain = sum(_safe_positive(item.get("Target Strain", item.get("Target_Strain", 0))) for item in schedule)
    has_rest = any(str(item.get("Sport", "")).strip().lower() == "rest" for item in schedule)
    if total_strain < budget or has_rest:
        return schedule

    used_days = {item.get("Day") for item in schedule if isinstance(item.get("Day"), int)}
    rest_entry = {
        "Day": next((day for day in range(1, 8) if day not in used_days), 7),
        "Sport": "Rest",
        "Duration (mins)": 0,
        "Target Strain": 0,
        "Intensity": "Rest",
        "Reasoning": "Budget exhausted—prioritize recovery."
    }

    if len(schedule) >= 7:
        replace_idx = min(
            range(len(schedule)),
            key=lambda idx: _safe_positive(schedule[idx].get("Target Strain", schedule[idx].get("Target_Strain", float("inf"))))
        )
        rest_entry["Day"] = schedule[replace_idx].get("Day", rest_entry["Day"])
        schedule[replace_idx] = rest_entry
    else:
        schedule.append(rest_entry)
    return schedule

def derive_activity_intensity(met_value, fatigue_state, tax_factor):
    """Calculate effort level using sport MET cost, subjective fatigue, and recovery tax."""
    fatigue_bias = {
        "Dead": -2.0,
        "Very Tired": -1.5,
        "Tired": -1.0,
        "Slightly Tired": -0.5,
        "Normal": 0.0,
        "Energized": 0.5,
        "Want to Move": 1.0,
        "Have to Move": 1.5,
    }
    bias = fatigue_bias.get(fatigue_state, 0.0)

    if met_value >= 9.0:
        met_adjust = -1.0
    elif met_value >= 7.0:
        met_adjust = -0.5
    elif met_value <= 5.0:
        met_adjust = 0.5
    else:
        met_adjust = 0.0

    if tax_factor <= 0.55:
        load_adjust = -0.75
    elif tax_factor >= 0.9:
        load_adjust = 0.5
    else:
        load_adjust = 0.0

    score = bias + met_adjust + load_adjust
    if score >= 1.0:
        return "High"
    if score <= -0.5:
        return "Low"
    return "Medium"

# --- 4. The Recommendation Engine ---
def calculate_plan(selected_sports, y_strain, f_level):
    if not selected_sports: 
        return [], 0.0, 0.0
    
    # Base Energy Budgets (MET-minutes) based on Subjective Fatigue
    f_budgets = {
        "Dead": 0, "Very Tired": 250, "Tired": 400, "Slightly Tired": 550,
        "Normal": 750, "Energized": 950, "Want to Move": 1150, "Have to Move": 1400
    }
    base_budget = f_budgets[f_level]
    
    # The Residual Load Penalty (Taxing today's budget based on yesterday's strain)
    # A heavy load (>1000) will reduce today's available energy significantly
    tax_factor = max(0.10, 1.0 - (y_strain / 2500))
    final_budget = base_budget * tax_factor

    recommendations = []
    for sport in selected_sports:
        met = sport_mets[sport]
        
        # DURATION CALCULATION: Balanced Time = Budget / MET
        # Higher MET sports = Shorter duration
        dur = int(final_budget / met)
        dur = max(10, min(150, dur)) 
        
        rec_int = derive_activity_intensity(met, f_level, tax_factor)
            
        # Recovery Meal Archetypes based on MET demand
        if met > 9.0:
            meal = {"t": "🚀 Glycogen Reload", "f": "High Carbohydrate (4:1 Ratio)", "d": "Replenish glucose oxidation stores used in high-MET cardio."}
        elif met >= 6.0:
            meal = {"t": "🍗 Structural Repair", "f": "High Protein / Moderate Carb", "d": "Focus on amino acids to repair muscle tissue stress."}
        else:
            meal = {"t": "🥗 Micronutrient Maintenance", "f": "High Fiber / Lean Protein", "d": "Support health with vitamins and minerals."}

        recommendations.append({"sport": sport, "dur": dur, "int": rec_int, "meal": meal, "met": met})
    
    return recommendations, tax_factor, final_budget

# --- 5. Display Results ---
# Logic: Calculate strain and tax without the 0.35 floor
y_met = sport_mets.get(y_sport, 0)
y_mult = {"Low": 0.8, "Medium": 1.0, "High": 1.2}[y_int]
yesterday_strain = y_met * y_dur * y_mult

# Calculating TRUE tax factor (Removed the 0.35 floor)
# If strain >= 2500, tax_factor will be 0 or negative
tax_factor = 1.0 - (yesterday_strain / 2500)

with st.sidebar:
    st.divider()
    st.subheader("Recovery Coach Chat")
    for message in st.session_state["coach_chat"]:
        prefix = "🧍‍♂️" if message["role"] == "user" else "🤖"
        st.markdown(f"{prefix} {message['content']}")
    coach_prompt = st.chat_input("Ask your Recovery Coach...")

if coach_prompt:
    st.session_state["coach_chat"].append({"role": "user", "content": coach_prompt})
    reply = answer_recovery_coach(coach_prompt, fatigue, yesterday_strain, tax_factor)
    st.session_state["coach_chat"].append({"role": "assistant", "content": reply})
    st.rerun()

# Check for Metabolic Bankruptcy or Subjective Exhaustion
if tax_factor <= 0 or fatigue == "Dead":
    st.error("🚨 CRITICAL ALERT: METABOLIC BANKRUPTCY DETECTED")
    st.markdown("""
    ### SYSTEM OVERRIDE: MANDATORY REST DAY
    Your calculated physical load has reached the human sustainability ceiling. 
    Further exertion will lead to overtraining or injury. 
    **Recommended Strategy:** 0 mins activity | High hydration | 8+ hours sleep.
    """)
    
    # Display a 100% Taxed chart even on rest days
    fig_dead = go.Figure(go.Bar(y=['Stamina'], x=[100], orientation='h', marker=dict(color='#ff3131')))
    fig_dead.update_layout(height=100, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False, xaxis=dict(visible=False), yaxis=dict(visible=False))
    st.plotly_chart(fig_dead, use_container_width=True)

elif my_sports:
    recs, tax, daily_budget = calculate_plan(my_sports, yesterday_strain, fatigue)
    
    st.divider()
    st.subheader("⚡ Stamina Budget")
    
    # Calculate values for the plot
    tax_pct = min(100, int((1-tax)*100))
    avail_pct = max(0, 100 - tax_pct)
    
    fig = go.Figure()
    # Yesterday's Tax
    fig.add_trace(go.Bar(
        y=['Stamina'], x=[tax_pct], name='TAXED',
        orientation='h', marker=dict(color='#111111', line=dict(color='#39ff14', width=2))
    ))
    # Available Budget
    fig.add_trace(go.Bar(
        y=['Stamina'], x=[avail_pct], name='READY',
        orientation='h', marker=dict(color='#39ff14', line=dict(color='#39ff14', width=1))
    ))

    fig.update_layout(
        barmode='stack', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False, height=150, margin=dict(t=0,b=0,l=0,r=0),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[0, 100]),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
    )
    
    # UNIFORM FONTS: Using Orbitron for both annotations
    fig.add_annotation(x=tax_pct/2 if tax_pct > 15 else 5, y=0, text=f"TAXED {tax_pct}%", 
                       showarrow=False, font=dict(color="#ff3131", size=14, family="Orbitron"))
    fig.add_annotation(x=tax_pct + (avail_pct/2) if avail_pct > 15 else 95, y=0, text=f"READY {avail_pct}%", 
                       showarrow=False, font=dict(color="#000000", size=14, family="Orbitron"))

    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    # --- METRICS AND OPTIONS ---
    cols = st.columns(2)
    cols[0].metric("Yesterday's Load", f"{int(yesterday_strain)} pts")
    cols[1].metric("Recovery Adjustment", f"-{tax_pct}%")
    
    # CSS to hide the "Arrow_right" and icon-font artifacts
    st.markdown("""
    <style>
    [data-testid="stExpander"] svg { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

    st.write(f"### Activity Options for a **{fatigue}** state:")
    
    for idx, r in enumerate(recs):
        with st.expander(f"{r['sport'].upper()} | {r['dur']} MINS @ {r['int']}"):
            st.markdown(f"**PROTOCOL:** {r['dur']} MINUTES AT {r['int']} INTENSITY.")
            st.caption(f"MET VALUE: {r['met']}")
            st.divider()
            
            # AI Fuel Integration
            state_key = f"{r['sport']}_{idx}"
            dislikes = st.session_state["meal_dislikes"].setdefault(state_key, [])
            if st.button(f"🧠 Generate AI Fuel Plan", key=f"btn_{state_key}"):
                with st.spinner("Consulting AI Nutritionist..."):
                    meal = get_dynamic_meal(r['sport'], r['dur'], r['int'], int(yesterday_strain), fatigue, dislikes)
                    if meal:
                        st.session_state["meal_plans"][state_key] = meal

            meal_plan = st.session_state["meal_plans"].get(state_key)
            if meal_plan:
                render_meal(meal_plan, r['sport'])
                if st.button("I don't like this", key=f"btn_dislike_{state_key}_{len(dislikes)}"):
                    if meal_plan.get("Meal_Name"):
                        dislikes.append(meal_plan["Meal_Name"])
                    with st.spinner("Finding an alternative..."):
                        alt = get_dynamic_meal(r['sport'], r['dur'], r['int'], int(yesterday_strain), fatigue, dislikes)
                        if alt:
                            st.session_state["meal_plans"][state_key] = alt
                    st.rerun()

#AI Weekly Periodization Module
st.divider()
st.markdown("## 📅 AI PERIODIZATION (7-DAY FORECAST)")

if not my_sports:
    st.info("Pick at least one sport above to unlock the weekly planner.")
else:
    weekly_budget = max(0, int(daily_budget * 7))
    st.caption(f"Weekly MET budget available: {weekly_budget} pts.")

    if weekly_budget == 0:
        st.warning("Recovery tax exhausted the weekly budget. Take rest before planning the next block.")
    elif st.button("🔮 Generate Weekly Plan", type="primary"):
        with st.spinner("Calculating weekly MET budget and generating schedule..."):
            try:
                schedule = generate_weekly_plan(
                    weekly_budget,
                    my_sports,
                    fatigue,
                    yesterday_strain,
                    tax_factor
                )
                df_schedule = pd.DataFrame(schedule)
                required_cols = ["Day", "Sport", "Intensity", "Duration (mins)", "Target Strain", "Reasoning"]
                for col in required_cols:
                    if col not in df_schedule.columns:
                        df_schedule[col] = ""
                df_schedule = df_schedule.sort_values("Day")

                fig_week = go.Figure(
                    data=[go.Bar(
                        x=df_schedule["Day"].astype(str),
                        y=df_schedule["Target Strain"],
                        marker_color='#39FF14',
                        text=df_schedule["Target Strain"],
                        textposition='auto'
                    )]
                )
                fig_week.update_layout(
                    title="Weekly Strain Distribution",
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#39FF14', family='Orbitron'),
                    xaxis=dict(showgrid=False),
                    yaxis=dict(showgrid=False, title="Target Strain (MET-mins)")
                )
                st.plotly_chart(fig_week, use_container_width=True)

                styled_html = df_schedule[required_cols].to_html(index=False, classes="weekly-plan-table")
                st.markdown("""
                <style>
                table.weekly-plan-table{
                    width: 100%;
                    table-layout: fixed;
                    border-collapse: collapse;
                    margin-bottom: 1rem;
                }
                table.weekly-plan-table th,
                table.weekly-plan-table td{
                    border: 1px solid var(--border);
                    padding: 8px;
                    color: var(--text);
                    font-family: 'Orbitron', system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
                    font-size: 0.85rem;
                    word-wrap: break-word;
                    white-space: normal;
                }
                table.weekly-plan-table th{
                    background: rgba(57,255,20,0.12);
                    color: var(--neon);
                    text-transform: uppercase;
                }
                </style>
                """, unsafe_allow_html=True)
                st.markdown(styled_html, unsafe_allow_html=True)

                for _, row in df_schedule.iterrows():
                    with st.expander(f"Day {int(row['Day'])}: {row['Sport']} ({row['Duration (mins)']} mins @ {row['Intensity']})"):
                        st.write(f"**Target Strain:** {row['Target Strain']} pts")
                        st.write(f"**Coach's Note:** {row['Reasoning']}")

                if any(str(s).lower() == "rest" for s in df_schedule["Sport"]):
                    st.caption("Rest day inserted automatically once the weekly MET budget is fully consumed.")
            except Exception as e:
                st.error(f"Error generating weekly plan: {e}")
