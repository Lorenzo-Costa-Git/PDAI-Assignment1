import streamlit as st
import pandas as pd
import plotly.graph_objects as go

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

# --- 2. UI Layout ---
st.set_page_config(page_title="NextRep: Dynamic Workouts Tailored to you", page_icon="📈")

import streamlit as st
import pandas as pd

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

# --- 4. The Recommendation Engine ---
def calculate_plan(selected_sports, y_strain, f_level):
    if not selected_sports: return []
    
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
        
        # Intensity capping for safety and recovery
        if tax_factor < 0.65 or f_level in ["Tired", "Very Tired"]:
            rec_int = "Low"
        elif f_level in ["Want to Move", "Have to Move"] and tax_factor > 0.85:
            rec_int = "High"
        else:
            rec_int = "Medium"
            
        # Recovery Meal Archetypes based on MET demand
        if met > 9.0:
            meal = {"t": "🚀 Glycogen Reload", "f": "High Carbohydrate (4:1 Ratio)", "d": "Replenish glucose oxidation stores used in high-MET cardio."}
        elif met >= 6.0:
            meal = {"t": "🍗 Structural Repair", "f": "High Protein / Moderate Carb", "d": "Focus on amino acids to repair muscle tissue stress."}
        else:
            meal = {"t": "🥗 Micronutrient Maintenance", "f": "High Fiber / Lean Protein", "d": "Support health with vitamins and minerals."}

        recommendations.append({"sport": sport, "dur": dur, "int": rec_int, "meal": meal, "met": met})
    
    return recommendations, tax_factor

# --- 5. Display Results ---
# Logic: Calculate strain and tax without the 0.35 floor
y_met = sport_mets.get(y_sport, 0)
y_mult = {"Low": 0.8, "Medium": 1.0, "High": 1.2}[y_int]
yesterday_strain = y_met * y_dur * y_mult

# Calculating TRUE tax factor (Removed the 0.35 floor)
# If strain >= 2500, tax_factor will be 0 or negative
tax_factor = 1.0 - (yesterday_strain / 2500)

# Check for Metabolic Bankruptcy or Subjective Exhaustion
if tax_factor <= 0 or fatigue == "Dead":
    st.error("🚨 CRITICAL ALERT: METABOLIC BANKRUPTCY DETECTED")
    st.markdown("""
    ### SYSTEM OVERRIDE: MANDATORY REST DAY
    Your calculated physical load has reached the human sustainability ceiling. 
    Further exertion will lead to overtraining or injury. 
    **Recommended Strategy:** 0 mins activity | High hydration | 8+ hours sleep.
    """)
    
    # Optional: Display a 100% Taxed chart even on rest days
    fig_dead = go.Figure(go.Bar(y=['Stamina'], x=[100], orientation='h', marker=dict(color='#ff3131')))
    fig_dead.update_layout(height=100, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False, xaxis=dict(visible=False), yaxis=dict(visible=False))
    st.plotly_chart(fig_dead, use_container_width=True)

elif my_sports:
    recs, tax = calculate_plan(my_sports, yesterday_strain, fatigue)
    
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
    
    st.write(f"### Activity Options for a **{fatigue}** state:")
    
    # CSS to hide the "Arrow_right" and icon-font artifacts
    st.markdown("""
    <style>
    [data-testid="stExpander"] svg { display: none !important; }
    [data-testid="stExpander"] p > span { display: none !important; }
    .st-emotion-cache-p4m61c { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

    for r in recs:
        with st.expander(f"{r['sport'].upper()} | {r['dur']} MINS @ {r['int']}"):
            st.markdown(f"**PROTOCOL:** {r['dur']} MINUTES AT {r['int']} INTENSITY.")
            st.caption(f"MET VALUE: {r['met']}")
            st.divider()
            st.markdown(f"**RECOMMENDED MEAL:** {r['meal']['t']}")
            st.markdown(f"🎯 **FOCUS:** {r['meal']['f']}")