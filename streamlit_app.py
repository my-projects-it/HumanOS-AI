import streamlit as st
import os
import requests

# ------------------------------
# Page Config
# ------------------------------
st.set_page_config(
    page_title="AI Planner",
    page_icon="🤖",
    layout="wide"
)

# ------------------------------
# Title
# ------------------------------
st.title("🌟 AI Goal Planner")
st.write("Enter your goal and get a personalized plan!")

# ------------------------------
# Input
# ------------------------------
goal = st.text_input("Type your goal here:")

# ------------------------------
# Hugging Face Token
# ------------------------------
HF_API_TOKEN = os.getenv("HF_API_TOKEN", "")

# ------------------------------
# Function to get AI plan from Hugging Face
# ------------------------------
def get_ai_plan_from_hf(goal: str):
    if not HF_API_TOKEN:
        return f"[Demo Mode] Plan for '{goal}':\n- Morning: Learn basics\n- Afternoon: Practice\n- Evening: Reflect"
    
    url = "https://api-inference.huggingface.co/models/gpt2"  # Example model, replace with your preferred one
    headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
    payload = {
        "inputs": f"Create a simple daily plan for the goal: {goal}",
        "parameters": {"max_new_tokens": 150}
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        # Hugging Face API response parsing
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
            plan = get_ai_plan_from_hf(goal)
            st.success("✅ Here's your plan:")
            st.text_area("AI Plan", plan, height=300)
