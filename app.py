# app.py

# Streamlit creates the web app interface.
import streamlit as st

# JSON helps us read structured AI results.
import json

# dotenv lets Python read your secret API key from the .env file.
from dotenv import load_dotenv

# os lets Python access environment variables.
import os

# OpenAI lets this app talk to the AI model.
from openai import OpenAI


# Load secret values from the .env file.
load_dotenv()

# Create the OpenAI client.
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# -----------------------------
# APP SETUP
# -----------------------------

st.set_page_config(
    page_title="DebateRef",
    page_icon="⚖️",
    layout="wide"
)

st.title("⚖️ DebateRef")
st.caption("AI debate evaluator with scoring, clarity review, and fact-checking support.")


# -----------------------------
# DEFAULT DATA
# -----------------------------

# These are the judging categories your original prototype used.
JUDGING_CRITERIA = [
    "Evidence Quality",
    "Logic",
    "Direct Responses",
    "Accuracy",
    "Clarity",
    "Consistency",
    "Civility"
]

# This creates saved messages the first time the app loads.
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "side": "Mike",
            "text": "Cities should put solar on public buildings because schools, libraries, and town halls use electricity every day. Even partial offset lowers operating costs over time."
        },
        {
            "side": "Opponent",
            "text": "The upfront cost is huge. Towns already struggle with budgets, and solar output drops in cloudy winters."
        }
    ]

# This stores the latest AI judgment.
if "result" not in st.session_state:
    st.session_state.result = None


# -----------------------------
# AI JUDGE FUNCTION
# -----------------------------

def judge_debate(topic, messages):
    """
    This function sends the debate to OpenAI and asks it to judge the debate.

    The AI is asked to return JSON so the app can display the result neatly.
    """

    debate_text = "\n".join(
        [f"{message['side']}: {message['text']}" for message in messages]
    )

    prompt = f"""
You are DebateRef, a neutral AI debate judge.

Your job:
1. Read the debate topic.
2. Read both sides of the debate.
3. Evaluate who argued better.
4. Check factual claims when possible.
5. Do not reward a side just because you personally agree with them.
6. Reward better reasoning, evidence, direct responses, accuracy, clarity, consistency, and civility.

Use these judging categories:
{", ".join(JUDGING_CRITERIA)}

Return ONLY valid JSON in this exact structure:

{{
  "winner": "Mike, Opponent, or Tie",
  "summary": "Short explanation of why they won.",
  "scores": [
    {{
      "category": "Evidence Quality",
      "mike": 0,
      "opponent": 0,
      "reason": "Beginner-friendly explanation of the score."
    }}
  ],
  "fact_checks": [
    {{
      "claim": "Specific claim being checked.",
      "verdict": "True / Mostly true / Mixed / Mostly false / False / Not enough evidence",
      "explanation": "Short explanation."
    }}
  ],
  "improvement_notes": [
    "One practical way a debater could improve."
  ]
}}

Debate topic:
{topic}

Debate messages:
{debate_text}
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        tools=[{"type": "web_search_preview"}],
        input=prompt
    )

    # Convert the AI's text response into Python data.
    return json.loads(response.output_text)


# -----------------------------
# LAYOUT
# -----------------------------

left_col, middle_col, right_col = st.columns([1, 2, 1.3])


# -----------------------------
# LEFT SIDE: DEBATE SETTINGS
# -----------------------------

with left_col:
    st.subheader("Debate Setup")

    topic = st.text_area(
        "Debate topic",
        value="Should cities require solar panels on public buildings?",
        height=100
    )

    side = st.radio(
        "Who is speaking?",
        ["Mike", "Opponent"]
    )

    new_message = st.text_area(
        "New debate point",
        placeholder="Type a debate point here...",
        height=130
    )

    if st.button("Add Point", use_container_width=True):
        if new_message.strip():
            st.session_state.messages.append(
                {
                    "side": side,
                    "text": new_message.strip()
                }
            )

            # Clear old result because the debate changed.
            st.session_state.result = None

            st.rerun()
        else:
            st.warning("Type a message before adding it.")

    if st.button("Clear Debate", use_container_width=True):
        st.session_state.messages = []
        st.session_state.result = None
        st.rerun()


# -----------------------------
# MIDDLE: DEBATE CHAT
# -----------------------------

with middle_col:
    st.subheader("Debate")

    if not st.session_state.messages:
        st.info("No debate points yet. Add one on the left.")
    else:
        for message in st.session_state.messages:
            if message["side"] == "Mike":
                st.chat_message("user").write(f"**Mike:** {message['text']}")
            else:
                st.chat_message("assistant").write(f"**Opponent:** {message['text']}")

    st.divider()

    if st.button("✨ Judge Debate", type="primary", use_container_width=True):
        if len(st.session_state.messages) < 2:
            st.warning("Add at least two debate points before judging.")
        else:
            with st.spinner("AI is judging the debate and checking factual claims..."):
                try:
                    st.session_state.result = judge_debate(
                        topic,
                        st.session_state.messages
                    )
                    st.success("Debate judged.")
                except Exception as error:
                    st.error("Something went wrong while judging the debate.")
                    st.write(error)


# -----------------------------
# RIGHT SIDE: AI VERDICT
# -----------------------------

with right_col:
    st.subheader("AI Verdict")

    result = st.session_state.result

    if result is None:
        st.info("Click **Judge Debate** to see the AI verdict.")
    else:
        st.metric("Winner", result.get("winner", "Unknown"))

        st.write(result.get("summary", "No summary provided."))

        st.divider()

        st.subheader("Scores")

        for score in result.get("scores", []):
            st.write(f"**{score.get('category', 'Category')}**")

            mike_score = score.get("mike", 0)
            opponent_score = score.get("opponent", 0)

            st.write(f"Mike: {mike_score}/100")
            st.progress(mike_score / 100)

            st.write(f"Opponent: {opponent_score}/100")
            st.progress(opponent_score / 100)

            st.caption(score.get("reason", ""))

        st.divider()

        st.subheader("Fact Checks")

        fact_checks = result.get("fact_checks", [])

        if not fact_checks:
            st.caption("No specific factual claims were checked.")
        else:
            for fact in fact_checks:
                st.write(f"**Claim:** {fact.get('claim', '')}")
                st.write(f"**Verdict:** {fact.get('verdict', '')}")
                st.caption(fact.get("explanation", ""))

        st.divider()

        st.subheader("Improvement Notes")

        for note in result.get("improvement_notes", []):
            st.write(f"- {note}")
