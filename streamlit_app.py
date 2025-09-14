from openai import OpenAI

client = OpenAI(api_key=OPENAI_API_KEY)

# Inside your button click:
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
        
