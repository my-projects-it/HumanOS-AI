import streamlit as st
import openai
import os

st.set_page_config(page_title="HumanOS Public AI", layout="centered")
st.title("🤖 HumanOS – Free AI Coach for Everyone")

# --- Auto Load Key (from secrets or env) ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
if not OPENAI_API_KEY:
    st.error("⚠️ AI service temporarily unavailable. (Admin: please set OPENAI_API_KEY in Streamlit Secrets)")
    st.stop()

openai.api_key = OPENAI_API_KEY

# --- Simple Goal Input ---
st.subheader("Your Goal")
goal = st.text_input("What do you want to achieve today? (e.g. Learn Python, Prepare for Interview)")

if st.button("Generate Daily Plan"):
    if not goal:
        st.error("⚠️ Please enter a goal first.")
    else:
        with st.spinner("Generating your plan..."):
            try:
                response = openai.ChatCompletion.create(
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
    
