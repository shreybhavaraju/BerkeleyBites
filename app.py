import streamlit as st
import pandas as pd
import json
from datetime import date, datetime
import os
import random

# Import food agent
from food_agent import set_context, process_command, clear_session_history

# ============================================
# PAGE SETUP
# ============================================

st.set_page_config(
    page_title="BerkeleyBites",
    page_icon="🍽️",
    layout="wide"
)

st.title("🍽️ BerkeleyBites")
st.subheader("Find your perfect meal at Berkeley dining halls")

# ============================================
# LOAD DATA (with auto-scrape)
# ============================================

from scraper import is_data_fresh, scrape_and_transform

@st.cache_data(ttl=3600)  # Cache for 1 hour within session
def load_menu_data():
    """
    Load menu data, auto-scraping if data is stale or missing.
    Data is considered stale if not from today.
    """
    if not is_data_fresh():
        # Need to scrape fresh data
        return None  # Signal that scraping is needed
    return pd.read_csv('dining_data_clean.csv')

# Check if we need to scrape
cached_df = load_menu_data()

if cached_df is None:
    # Data is stale, scrape fresh
    with st.spinner("Fetching today's menu from Berkeley Dining..."):
        clean_df = scrape_and_transform()
        st.cache_data.clear()  # Clear cache so next load uses fresh data
    st.success(f"Loaded {len(clean_df)} dishes from today's menu!")
else:
    clean_df = cached_df

if clean_df.empty:
    st.error("No menu data available. The dining website may be unavailable.")
    st.stop()

# ============================================
# FEEDBACK COLLECTION FUNCTIONS
# ============================================

def get_user_id():
    """
    Generate a consistent user ID for this browser session
    Uses Streamlit session_state to persist across page reloads
    """
    if 'user_id' not in st.session_state:
        st.session_state.user_id = f"user_{random.randint(1000, 9999)}"
    
    return st.session_state.user_id

def load_feedback():
    """Load existing feedback from CSV"""
    try:
        return pd.read_csv('feedback.csv')
    except FileNotFoundError:
        return pd.DataFrame(columns=['user_id', 'dish_id', 'dish_name', 'liked', 'timestamp', 'date'])

def save_feedback(user_id, dish_id, dish_name, liked):
    """
    Save feedback to CSV
    
    Args:
        user_id: User identifier
        dish_id: Dish identifier  
        dish_name: Name of the dish
        liked: 1 for like, 0 for dislike
    """
    feedback_df = load_feedback()
    
    # Create new feedback entry
    new_feedback = {
        'user_id': user_id,
        'dish_id': dish_id,
        'dish_name': dish_name,
        'liked': liked,
        'timestamp': datetime.now().isoformat(),
        'date': str(date.today())
    }
    
    # Append to DataFrame
    feedback_df = pd.concat([feedback_df, pd.DataFrame([new_feedback])], ignore_index=True)
    
    # Save to CSV
    feedback_df.to_csv('feedback.csv', index=False)

def has_feedback_today(user_id, dish_id):
    """
    Check if user already gave feedback for this dish today
    
    Returns:
        None if no feedback, or 1/0 if feedback exists
    """
    feedback_df = load_feedback()
    
    if feedback_df.empty:
        return None
    
    # Filter for this user, dish, and today's date
    today = str(date.today())
    existing = feedback_df[
        (feedback_df['user_id'] == user_id) & 
        (feedback_df['dish_id'] == dish_id) & 
        (feedback_df['date'] == today)
    ]
    
    if existing.empty:
        return None
    else:
        return existing.iloc[0]['liked']

# ============================================
# USER PROFILE SECTION
# ============================================

st.sidebar.title("👤 Your Dietary Profile")

# Use session state to persist profile during session
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = {
        "is_vegetarian": False,
        "is_vegan": False,
        "is_pescatarian": False,
        "is_halal": False,
        "is_kosher": False,
        "eats_chicken": True,
        "eats_beef": True,
        "eats_pork": True,
        "eats_fish": True,
        "eats_shellfish": True,
        "avoid_milk": False,
        "avoid_eggs": False,
        "avoid_gluten": False,
        "avoid_nuts": False,
        "avoid_soy": False,
        "prefer_low_carbon": False,
    }

# Show profile editor in sidebar
with st.sidebar.expander("⚙️ Edit Profile", expanded=False):
    st.write("**Dietary Identity**")
    
    st.session_state.user_profile["is_vegan"] = st.checkbox(
        "🌱 Vegan (no animal products)",
        value=st.session_state.user_profile["is_vegan"]
    )
    
    st.session_state.user_profile["is_vegetarian"] = st.checkbox(
        "🥗 Vegetarian (no meat/fish)",
        value=st.session_state.user_profile["is_vegetarian"]
    )
    
    st.session_state.user_profile["is_pescatarian"] = st.checkbox(
        "🐟 Pescatarian (fish OK, no other meat)",
        value=st.session_state.user_profile["is_pescatarian"]
    )
    
    st.session_state.user_profile["is_halal"] = st.checkbox(
        "☪️ Halal only",
        value=st.session_state.user_profile["is_halal"]
    )
    
    st.session_state.user_profile["is_kosher"] = st.checkbox(
        "✡️ Kosher only",
        value=st.session_state.user_profile["is_kosher"]
    )
    
    st.divider()
    st.write("**Specific Meats** (if not vegetarian)")
    
    if not st.session_state.user_profile["is_vegetarian"] and not st.session_state.user_profile["is_vegan"]:
        st.session_state.user_profile["eats_chicken"] = st.checkbox(
            "🍗 Eats chicken",
            value=st.session_state.user_profile["eats_chicken"]
        )
        
        st.session_state.user_profile["eats_beef"] = st.checkbox(
            "🥩 Eats beef",
            value=st.session_state.user_profile["eats_beef"]
        )
        
        st.session_state.user_profile["eats_pork"] = st.checkbox(
            "🥓 Eats pork",
            value=st.session_state.user_profile["eats_pork"]
        )
        
        st.session_state.user_profile["eats_fish"] = st.checkbox(
            "🐟 Eats fish",
            value=st.session_state.user_profile["eats_fish"]
        )
        
        st.session_state.user_profile["eats_shellfish"] = st.checkbox(
            "🦐 Eats shellfish",
            value=st.session_state.user_profile["eats_shellfish"]
        )
    
    st.divider()
    st.write("**Allergens to Avoid**")
    
    st.session_state.user_profile["avoid_milk"] = st.checkbox(
        "🥛 Avoid dairy/milk",
        value=st.session_state.user_profile["avoid_milk"]
    )
    
    st.session_state.user_profile["avoid_eggs"] = st.checkbox(
        "🥚 Avoid eggs",
        value=st.session_state.user_profile["avoid_eggs"]
    )
    
    st.session_state.user_profile["avoid_gluten"] = st.checkbox(
        "🌾 Avoid gluten",
        value=st.session_state.user_profile["avoid_gluten"]
    )
    
    st.session_state.user_profile["avoid_nuts"] = st.checkbox(
        "🥜 Avoid nuts",
        value=st.session_state.user_profile["avoid_nuts"]
    )
    
    st.session_state.user_profile["avoid_soy"] = st.checkbox(
        "🫘 Avoid soy",
        value=st.session_state.user_profile["avoid_soy"]
    )

# Show current profile summary
st.sidebar.markdown("### 📋 Current Profile")
profile_summary = []

if st.session_state.user_profile["is_vegan"]:
    profile_summary.append("🌱 Vegan")
elif st.session_state.user_profile["is_vegetarian"]:
    profile_summary.append("🥗 Vegetarian")
elif st.session_state.user_profile["is_pescatarian"]:
    profile_summary.append("🐟 Pescatarian")

if st.session_state.user_profile["is_halal"]:
    profile_summary.append("☪️ Halal")
if st.session_state.user_profile["is_kosher"]:
    profile_summary.append("✡️ Kosher")

if not st.session_state.user_profile["is_vegetarian"] and not st.session_state.user_profile["is_vegan"]:
    meats = []
    if not st.session_state.user_profile["eats_chicken"]:
        meats.append("no chicken")
    if not st.session_state.user_profile["eats_beef"]:
        meats.append("no beef")
    if not st.session_state.user_profile["eats_pork"]:
        meats.append("no pork")
    if not st.session_state.user_profile["eats_fish"]:
        meats.append("no fish")
    if not st.session_state.user_profile["eats_shellfish"]:
        meats.append("no shellfish")
    
    if meats:
        profile_summary.append(f"Avoids: {', '.join(meats)}")

allergens = []
if st.session_state.user_profile["avoid_milk"]:
    allergens.append("dairy")
if st.session_state.user_profile["avoid_eggs"]:
    allergens.append("eggs")
if st.session_state.user_profile["avoid_gluten"]:
    allergens.append("gluten")
if st.session_state.user_profile["avoid_nuts"]:
    allergens.append("nuts")
if st.session_state.user_profile["avoid_soy"]:
    allergens.append("soy")

if allergens:
    profile_summary.append(f"Allergens: {', '.join(allergens)}")

if profile_summary:
    for item in profile_summary:
        st.sidebar.write(f"• {item}")
else:
    st.sidebar.write("_No restrictions set_")

# ============================================
# FEEDBACK STATISTICS
# ============================================

st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Your Feedback")

feedback_df = load_feedback()

if not feedback_df.empty:
    user_feedback = feedback_df[feedback_df['user_id'] == get_user_id()]
    
    if not user_feedback.empty:
        total_feedback = len(user_feedback)
        liked_count = user_feedback['liked'].sum()
        disliked_count = total_feedback - liked_count
        
        st.sidebar.write(f"Total ratings: **{total_feedback}**")
        st.sidebar.write(f"👍 Liked: **{liked_count}**")
        st.sidebar.write(f"👎 Disliked: **{disliked_count}**")
        
        today_feedback = user_feedback[user_feedback['date'] == str(date.today())]
        st.sidebar.caption(f"Today: {len(today_feedback)} ratings")
    else:
        st.sidebar.write("_No feedback yet_")
        st.sidebar.caption("Rate some dishes to get started!")
else:
    st.sidebar.write("_No feedback yet_")

# ============================================
# FILTERING LOGIC
# ============================================

def filter_by_profile(df, profile):
    """
    Filter dishes based on user profile
    Returns filtered DataFrame
    """
    filtered = df.copy()
    
    if profile["is_vegan"]:
        filtered = filtered[filtered['is_vegan'] == True]
        return filtered
    
    if profile["is_vegetarian"]:
        filtered = filtered[filtered['is_vegetarian'] == True]
    
    if profile["is_pescatarian"]:
        filtered = filtered[
            (filtered['is_vegetarian'] == True) | 
            (filtered['has_fish'] == True)
        ]
    
    if profile["is_halal"]:
        filtered = filtered[filtered['is_halal'] == True]
    
    if profile["is_kosher"]:
        filtered = filtered[filtered['is_kosher'] == True]
    
    if not profile["eats_pork"]:
        filtered = filtered[filtered['has_pork'] == False]
    
    if not profile["eats_fish"]:
        filtered = filtered[filtered['has_fish'] == False]
    
    if not profile["eats_shellfish"]:
        filtered = filtered[filtered['has_shellfish'] == False]
    
    if profile["avoid_milk"]:
        filtered = filtered[filtered['has_milk'] == False]
    
    if profile["avoid_eggs"]:
        filtered = filtered[filtered['has_egg'] == False]
    
    if profile["avoid_gluten"]:
        filtered = filtered[filtered['has_gluten'] == False]
    
    if profile["avoid_nuts"]:
        filtered = filtered[filtered['has_tree_nuts'] == False]
    
    if profile["avoid_soy"]:
        filtered = filtered[filtered['has_soybeans'] == False]
    
    return filtered

# Apply profile filtering
filtered_df = filter_by_profile(clean_df, st.session_state.user_profile)

# ============================================
# SET AGENT CONTEXT
# ============================================

# Update agent context with current data
set_context(
    menu_df=filtered_df,
    feedback_df=load_feedback(),
    user_profile=st.session_state.user_profile,
    user_id=get_user_id()
)

# ============================================
# AI ASSISTANT SECTION (Sidebar)
# ============================================

st.sidebar.markdown("---")
st.sidebar.markdown("### 🤖 AI Assistant")
st.sidebar.success("Powered by Perplexity AI")

# Initialize chat history in session state
if 'agent_messages' not in st.session_state:
    st.session_state.agent_messages = []

# Command input
with st.sidebar.form(key="agent_form", clear_on_submit=True):
    agent_input = st.text_input(
        "Ask me anything:",
        placeholder="/recommend lunch",
        label_visibility="collapsed"
    )
    submit_button = st.form_submit_button("Ask")

if submit_button and agent_input:
    with st.spinner("Thinking..."):
        response = process_command(agent_input, session_id=get_user_id())
        st.session_state.agent_messages.append({"role": "user", "content": agent_input})
        st.session_state.agent_messages.append({"role": "assistant", "content": response})

# Show recent conversation
if st.session_state.agent_messages:
    st.sidebar.markdown("**Recent:**")
    # Show last 2 exchanges
    recent = st.session_state.agent_messages[-4:]
    for msg in recent:
        if msg["role"] == "user":
            st.sidebar.caption(f"You: {msg['content'][:50]}...")
        else:
            st.sidebar.info(msg["content"][:200] + "..." if len(msg["content"]) > 200 else msg["content"])

st.sidebar.caption("Commands: /recommend, /why, /search, /help")

# ============================================
# DISPLAY RESULTS
# ============================================

st.markdown("---")
st.write(f"📅 **Date:** {date.today().strftime('%B %d, %Y')}")

if len(filtered_df) == 0:
    st.warning("😕 No dishes match your profile. Try adjusting your preferences.")
    st.stop()

st.success(f"✅ Found {len(filtered_df)} dishes matching your profile")

# ============================================
# AI CHAT INTERFACE (Main Area)
# ============================================

st.markdown("---")
st.subheader("🤖 Ask BerkeleyBites AI")

# Main area chat interface
col1, col2 = st.columns([4, 1])
with col1:
    main_input = st.text_input(
        "Enter command or question:",
        placeholder="Try: /recommend dinner  or  /why Pizza  or  /search tofu protein",
        key="main_agent_input",
        label_visibility="collapsed"
    )
with col2:
    main_submit = st.button("Ask AI", use_container_width=True)

if main_submit and main_input:
    with st.spinner("🤔 Analyzing your preferences..."):
        # Refresh context before each query
        set_context(
            menu_df=filtered_df,
            feedback_df=load_feedback(),
            user_profile=st.session_state.user_profile,
            user_id=get_user_id()
        )
        response = process_command(main_input, session_id=get_user_id())
        st.session_state.agent_messages.append({"role": "user", "content": main_input})
        st.session_state.agent_messages.append({"role": "assistant", "content": response})
        st.rerun()

# Display last agent response prominently
if st.session_state.agent_messages:
    last_response = st.session_state.agent_messages[-1]
    if last_response["role"] == "assistant":
        st.markdown("**AI Response:**")
        st.markdown(last_response["content"])

st.markdown("---")

# Let user select dining hall and meal
dining_halls = filtered_df['dining_hall'].unique()
selected_hall = st.selectbox("🏛️ Select Dining Hall", options=dining_halls)

hall_df = filtered_df[filtered_df['dining_hall'] == selected_hall]

meals = hall_df['meal_period'].unique()
selected_meal = st.selectbox("🍽️ Select Meal", options=meals)

meal_df = hall_df[hall_df['meal_period'] == selected_meal]

# Display by category
st.markdown("---")
st.subheader(f"Menu for {selected_hall} - {selected_meal}")

# Get user ID
user_id = get_user_id()

for category in meal_df['category'].unique():
    cat_df = meal_df[meal_df['category'] == category]

    with st.expander(f"**{category}** ({len(cat_df)} items)", expanded=True):
        for idx, (_, dish) in enumerate(cat_df.iterrows()):
            # Build tags
            tags = []
            if dish['is_vegan']:
                tags.append("🌱 Vegan")
            elif dish['is_vegetarian']:
                tags.append("🥗 Vegetarian")
            if dish['is_halal']:
                tags.append("☪️ Halal")
            if dish['is_kosher']:
                tags.append("✡️ Kosher")

            st.markdown(f"**{dish['dish_name']}**")

            # Create columns: [tags | feedback buttons]
            col1, col2 = st.columns([3, 2])

            with col1:
                if tags:
                    st.caption(" | ".join(tags))

            with col2:
                # Check if user already gave feedback today
                existing_feedback = has_feedback_today(user_id, dish['dish_id'])

                if existing_feedback is None:
                    # No feedback yet - show buttons
                    col_like, col_dislike = st.columns(2)

                    with col_like:
                        if st.button("👍", key=f"like_{dish['dish_id']}", help="I'd eat this"):
                            save_feedback(user_id, dish['dish_id'], dish['dish_name'], liked=1)
                            st.rerun()

                    with col_dislike:
                        if st.button("👎", key=f"dislike_{dish['dish_id']}", help="Not for me"):
                            save_feedback(user_id, dish['dish_id'], dish['dish_name'], liked=0)
                            st.rerun()

                elif existing_feedback == 1:
                    st.success("👍 Liked")
                else:
                    st.error("👎 Passed")

            st.divider()