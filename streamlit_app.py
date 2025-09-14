import streamlit as st
import os
from openai import OpenAI

st.set_page_config(page_title="HumanOS Public AI", layout="centered")
st.title("🤖 HumanOS – Free AI Coach for Everyone")

# --- Step 1: Load API Key ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
if not OPENAI_API_KEY:
    st.error("⚠️ AI service not configured. (Admin: please set OPENAI_API_KEY in Streamlit Secrets)")
    st.stop()

# --- Step 2: Create OpenAI Client ---
client = OpenAI(api_key=OPENAI_API_KEY)

# --- Step 3: Simple Input ---
st.subheader("Your Goal")
goal = st.text_input("What do you want to achieve today? (e.g. Learn Python, Prepare for Interview)")

if st.button("Generate Daily Plan"):
    if not goal:
        st.error("⚠️ Please enter a goal first.")
    else:
        with st.spinner("Generating your plan..."):
            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful, concise personal coach."},
                        {"role": "user", "content": f"Create a short, actionable daily plan for: {goal}"}
                    ],
                    max_tokens=300
                )
                ai_text = response.choices[0].message.content.strip()
            except Exception as e:
                ai_text = f"⚠️ API Error: {str(e)}"
        st.markdown(f"### 📅 Your Plan\n{ai_text}")
