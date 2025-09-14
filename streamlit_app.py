import streamlit as st
import os
import requests

# ------------------------------
# Page Config
# ------------------------------
st.set_page_config(page_title="AI Goal Planner", page_icon="🤖", layout="wide")
st.title("🌟 AI Goal Planner (English + Hindi)")

# ------------------------------
# Input
# ------------------------------
goal = st.text_input("Enter your goal (English or Hindi):")

# ------------------------------
# Hugging Face Token & Model
# ------------------------------
HF_API_TOKEN = os.getenv("HF_API_TOKEN", "")
HF_MODEL_URL = "https://api-inference.huggingface.co/models/bigscience/bloom-560m"

# ------------------------------
# Function to get plan from HF
# ------------------------------
def get_ai_plan(goal: str):
    if not HF_API_TOKEN:
        # Fallback demo plan
        return f"[Demo Mode] Plan for '{goal}':\n- Morning: Learn basics\n- Afternoon: Practice\n- Evening: Reflect"
    
    headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
    payload = {"inputs": f"Create a simple daily plan for the goal: {goal}", "parameters": {"max_new_tokens":150}}

    try:
        response = requests.post(HF_MODEL_URL, headers=headers, json=payload, timeout=20)
        response.raise_for_status()
        data = response.json()
        # Hugging Face API returns list of dicts with 'generated_text'
        text = data[0].get("generated_text", "")
        return text if text else "Sorry, no response from model."
    except Exception as e:
        return f"Error: {str(e)}"

# ------------------------------
# Button & Output
# ------------------------------
if st.button("Generate Plan"):
    if not goal.strip():
        st.warning("Please enter a goal first!")
    else:
        with st.spinner("Generating your plan..."):
            plan = get_ai_plan(goal)
            st.success("✅ Here's your plan:")
            st.text_area("AI Plan", plan, height=300)
