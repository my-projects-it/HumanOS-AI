# app.py
import streamlit as st
import openai
import sqlite3
import datetime
import os
from typing import List, Dict

# -------------------------
# CONFIG
# -------------------------
st.set_page_config(page_title="HumanOS (Python MVP)", layout="wide")
DB_PATH = "humanos.db"

# If you want real AI, set OPENAI_API_KEY env var or paste below:
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")  # or set here directly (not recommended)

# Choose model name you have access to
OPENAI_MODEL = "gpt-4o"  # change if unavailable, or use "gpt-3.5-turbo"

# -------------------------
# DB UTILITIES
# -------------------------
def init_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        language TEXT,
        created_at TEXT
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS goals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        title TEXT,
        details TEXT,
        created_at TEXT
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS chats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        role TEXT,
        content TEXT,
        created_at TEXT
    )
    """)
    conn.commit()
    return conn

conn = init_db()

def add_user(name: str, language: str = "English") -> int:
    cur = conn.cursor()
    now = datetime.datetime.utcnow().isoformat()
    cur.execute("INSERT INTO users (name, language, created_at) VALUES (?, ?, ?)", (name, language, now))
    conn.commit()
    return cur.lastrowid

def get_user(user_id: int):
    cur = conn.cursor()
    cur.execute("SELECT id, name, language, created_at FROM users WHERE id=?", (user_id,))
    return cur.fetchone()

def add_goal(user_id: int, title: str, details: str = ""):
    cur = conn.cursor()
    now = datetime.datetime.utcnow().isoformat()
    cur.execute("INSERT INTO goals (user_id, title, details, created_at) VALUES (?, ?, ?, ?)", (user_id, title, details, now))
    conn.commit()

def get_goals(user_id: int):
    cur = conn.cursor()
    cur.execute("SELECT id, title, details, created_at FROM goals WHERE user_id=? ORDER BY id DESC", (user_id,))
    return cur.fetchall()

def add_chat(user_id: int, role: str, content: str):
    cur = conn.cursor()
    now = datetime.datetime.utcnow().isoformat()
    cur.execute("INSERT INTO chats (user_id, role, content, created_at) VALUES (?, ?, ?, ?)", (user_id, role, content, now))
    conn.commit()

def get_chats(user_id: int, limit: int = 200):
    cur = conn.cursor()
    cur.execute("SELECT role, content, created_at FROM chats WHERE user_id=? ORDER BY id DESC LIMIT ?", (user_id, limit))
    rows = cur.fetchall()
    return list(reversed(rows))

# -------------------------
# OPENAI UTIL
# -------------------------
def call_openai_system(prompt: str) -> str:
    """
    Calls OpenAI ChatCompletions. If no API key set, returns a dummy response.
    """
    if not OPENAI_API_KEY:
        # Dummy fallback
        return ("[Demo mode] AI not configured. Here's a suggested daily plan:\n\n"
                "- Morning: 30-min focused learning on topic.\n- Afternoon: Apply learning with a small task.\n- Evening: Revise & reflect.")
    try:
        openai.api_key = OPENAI_API_KEY
        # ChatCompletion (chat-based). Adjust for API you have access to.
        response = openai.ChatCompletion.create(
            model=OPENAI_MODEL,
            messages=[{"role":"system","content":"You are a helpful, concise personal AI coach."},
                      {"role":"user","content": prompt}],
            temperature=0.6,
            max_tokens=600
        )
        text = response.choices[0].message.content.strip()
        return text
    except Exception as e:
        return f"[AI error] {str(e)}"

# -------------------------
# PROMPT TEMPLATES
# -------------------------
def daily_plan_prompt(name: str, language: str, goal_title: str, goal_details: str) -> str:
    prompt = f"""
You are a concise personal coach. User name: {name}. Language preference: {language}.
User goal: "{goal_title}".
Details: {goal_details}

Create a practical, prioritized DAILY plan for today (morning/afternoon/evening), with:
- concrete 3-5 tasks
- approximate time for each task
- one quick habit to build (2-5 minutes)
- one suggested resource (free) or action
Keep it short and actionable, bullet points. End with a one-line motivational note.
"""
    return prompt.strip()

def chat_assistant_prompt(name: str, language: str, memory: List[Dict], user_message: str) -> str:
    mem_text = ""
    if memory:
        mem_text = "User memory summary:\n" + "\n".join([f"- {m}" for m in memory])
    prompt = f"""
You are a concise personal AI coach for {name}. Language: {language}.
{mem_text}

User asks: {user_message}

Respond helpfully and give concrete steps, resources, and one short checklist if applicable.
"""
    return prompt.strip()

# -------------------------
# STREAMLIT UI
# -------------------------
st.title("HumanOS — Personal AI Life Coach (Python MVP)")
st.markdown("Build fast, iterate faster. **Single-file Python MVP** with AI-powered daily plans and chat. (Demo mode runs without OpenAI key.)")

# Sidebar: user setup
st.sidebar.header("User")
if "user_id" not in st.session_state:
    st.session_state.user_id = None

if st.session_state.user_id is None:
    name = st.sidebar.text_input("Enter your name", value="")
    language = st.sidebar.selectbox("Language", ["English", "हिन्दी"])
    if st.sidebar.button("Start (create profile)"):
        if not name.strip():
            st.sidebar.error("Please enter a name.")
        else:
            uid = add_user(name.strip(), language)
            st.session_state.user_id = uid
            st.experimental_rerun()
else:
    user = get_user(st.session_state.user_id)
    st.sidebar.success(f"Hello, {user[1]} ({user[2]})")
    if st.sidebar.button("Sign out"):
        st.session_state.user_id = None
        st.experimental_rerun()

# Main UI requires user
if st.session_state.user_id is None:
    st.info("Create a profile from the left panel to begin. Use demo mode if you don't have an OpenAI key.")
    st.stop()

user = get_user(st.session_state.user_id)
name = user[1]; language = user[2]

# Show goals and add new goal
st.subheader("Your Goals")
with st.form("add_goal"):
    col1, col2 = st.columns([3,1])
    title = col1.text_input("Add a new goal (e.g., Learn Python, Get job, Fitness habit)")
    details = col2.text_input("Short details (optional)")
    submitted = st.form_submit_button("Add Goal")
    if submitted:
        if title.strip():
            add_goal(st.session_state.user_id, title.strip(), details.strip())
            st.success("Goal added.")
        else:
            st.error("Enter a goal title.")

goals = get_goals(st.session_state.user_id)
if goals:
    for g in goals:
        st.markdown(f"- **{g[1]}** — {g[2]}")
else:
    st.info("No goals yet. Add one above.")

# Select goal to generate plan
st.subheader("Generate Today's Plan")
goal_select = st.selectbox("Choose a goal", options=[(g[0], g[1]) for g in goals] if goals else [], format_func=lambda x: x[1] if x else "No goals")
if goal_select:
    gid = goal_select[0]
    selected_goal = next((g for g in goals if g[0]==gid), None)
    if selected_goal:
        _, title, details, _ = selected_goal
        if st.button("Generate Daily Plan (AI)"):
            prompt = daily_plan_prompt(name, language, title, details)
            st.info("Generating plan — this may take a few seconds...")
            ai_text = call_openai_system(prompt)
            add_chat(st.session_state.user_id, "assistant", ai_text)
            st.success("Plan generated and saved in your chat history.")

# Chat interface
st.subheader("Chat with your AI Coach")
chats = get_chats(st.session_state.user_id)
for role, content, created in chats:
    if role == "assistant":
        st.markdown(f"**AI:** {content}")
    else:
        st.mark_markdown = None
        st.markdown(f"**You:** {content}")

with st.form("chat_form"):
    user_msg = st.text_input("Ask anything (e.g., 'How to prepare for interview today?')", key="user_input")
    send = st.form_submit_button("Send")
    if send and user_msg.strip():
        # collect memory (recent goals as memory)
        mem = [f"Goal: {g[1]} - {g[2]}" for g in goals]
        prompt = chat_assistant_prompt(name, language, mem, user_msg.strip())
        st.info("Getting AI response...")
        ai_response = call_openai_system(prompt)
        add_chat(st.session_state.user_id, "user", user_msg.strip())
        add_chat(st.session_state.user_id, "assistant", ai_response)
        st.experimental_rerun()

# Quick tips and OpenAI key entry
st.sidebar.header("OpenAI Key (optional)")
key_input = st.sidebar.text_input("Paste your OpenAI API key (sk-...)", value=OPENAI_API_KEY, type="password")
if key_input and key_input != OPENAI_API_KEY:
    # persist to environment for session only
    OPENAI_API_KEY = key_input
    os.environ["OPENAI_API_KEY"] = key_input
    st.sidebar.success("API key set for this session. Re-generate plan to use real AI.")

st.sidebar.markdown("---")
st.sidebar.markdown("**Developer Notes:**\n- This is an MVP. Use SQLite for local memory. \n- To scale, replace SQLite with Postgres, add auth, and move AI calls server-side with rate limiting.")
