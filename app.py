import streamlit as st
from datetime import datetime

st.set_page_config(page_title="DebateRef", page_icon="⚖️", layout="wide")

st.title("⚖️ DebateRef")
st.caption("Pick a topic, challenge an argument, submit rebuttals, and judge the round.")


# -----------------------------
# STARTER TOPICS + ARGUMENTS
# -----------------------------

STARTER_TOPICS = {
    "Solar Panels": [
        {
            "author": "Alex",
            "argument": "Cities should require solar panels on public buildings because it can lower long-term energy costs and reduce emissions."
        },
        {
            "author": "Jordan",
            "argument": "Solar mandates can be too expensive upfront, especially for towns with tight budgets."
        },
    ],
    "Universal Health Care": [
        {
            "author": "Casey",
            "argument": "Universal health care could make medical access more equal and reduce financial stress from unexpected illness."
        },
        {
            "author": "Taylor",
            "argument": "Universal health care could increase taxes and reduce choice depending on how it is designed."
        },
    ],
    "Voting Age": [
        {
            "author": "Morgan",
            "argument": "The voting age should be lowered because younger people are affected by policy and deserve representation."
        },
        {
            "author": "Riley",
            "argument": "The voting age should stay the same because voting requires maturity and life experience."
        },
    ],
}


# -----------------------------
# SESSION STATE
# This is Streamlit's way of remembering things
# while the app is running.
# -----------------------------

if "topics" not in st.session_state:
    st.session_state.topics = STARTER_TOPICS.copy()

if "battles" not in st.session_state:
    st.session_state.battles = []

if "active_topic" not in st.session_state:
    st.session_state.active_topic = "Solar Panels"

if "selected_argument_index" not in st.session_state:
    st.session_state.selected_argument_index = 0


# -----------------------------
# SIMPLE TEMPORARY JUDGE
# This is NOT real AI yet.
# It gives a basic score based on simple writing signals.
# Later, this can be replaced with OpenAI.
# -----------------------------

def score_text(text):
    """
    Beginner explanation:
    This function gives a rough score to a debate response.

    It looks for:
    - enough detail
    - reasoning words like because/however/therefore
    - examples or evidence words
    - respectful tone

    This is temporary until you connect the real AI judge.
    """

    score = 50
    lower = text.lower()

    if len(text.split()) > 25:
        score += 10

    if any(word in lower for word in ["because", "therefore", "since", "so"]):
        score += 10

    if any(word in lower for word in ["example", "data", "study", "evidence", "research", "cost", "impact"]):
        score += 10

    if any(word in lower for word in ["however", "but", "although", "counterpoint"]):
        score += 10

    if any(word in lower for word in ["stupid", "idiot", "dumb", "moron"]):
        score -= 20

    return max(0, min(score, 100))


def judge_battle(messages):
    """
    Beginner explanation:
    This function compares your responses against the opponent's responses.

    For now, it uses the simple scoring function above.
    Later, this is the function you would replace with OpenAI.
    """

    user_scores = []
    opponent_scores = []

    for message in messages:
        if message["side"] == "You":
            user_scores.append(score_text(message["text"]))
        else:
            opponent_scores.append(score_text(message["text"]))

    user_avg = round(sum(user_scores) / len(user_scores), 1) if user_scores else 0
    opponent_avg = round(sum(opponent_scores) / len(opponent_scores), 1) if opponent_scores else 0

    if user_avg > opponent_avg:
        winner = "You"
    elif opponent_avg > user_avg:
        winner = "Opponent"
    else:
        winner = "Tie"

    rationale = (
        "This temporary judge scores based on clarity, detail, reasoning words, evidence signals, "
        "direct counterpoints, and civility. It does not fact-check yet."
    )

    return {
        "winner": winner,
        "you_score": user_avg,
        "opponent_score": opponent_avg,
        "rationale": rationale,
    }


# -----------------------------
# APP LAYOUT
# -----------------------------

left, middle, right = st.columns([1, 1.6, 1.2])


# -----------------------------
# LEFT: TOPICS
# -----------------------------

with left:
    st.subheader("1. Pick or Add Topic")

    topic_names = list(st.session_state.topics.keys())

    selected_topic = st.selectbox(
        "Choose an existing topic",
        topic_names,
        index=topic_names.index(st.session_state.active_topic)
    )

    st.session_state.active_topic = selected_topic

    new_topic = st.text_input("Add a new topic")

    if st.button("Add Topic", use_container_width=True):
        if new_topic.strip():
            st.session_state.topics[new_topic.strip()] = []
            st.session_state.active_topic = new_topic.strip()
            st.rerun()
        else:
            st.warning("Type a topic first.")

    st.divider()

    st.subheader("2. Add Argument to Topic")

    new_author = st.text_input("Argument author", value="New User")
    new_argument = st.text_area("Argument", height=120)

    if st.button("Add Argument", use_container_width=True):
        if new_argument.strip():
            st.session_state.topics[st.session_state.active_topic].append(
                {
                    "author": new_author.strip() or "Anonymous",
                    "argument": new_argument.strip(),
                }
            )
            st.rerun()
        else:
            st.warning("Type an argument first.")


# -----------------------------
# MIDDLE: ARGUMENTS + START BATTLE
# -----------------------------

with middle:
    st.subheader(f"Arguments: {st.session_state.active_topic}")

    arguments = st.session_state.topics[st.session_state.active_topic]

    if not arguments:
        st.info("No arguments yet. Add one from the left.")
    else:
        for i, item in enumerate(arguments):
            with st.container(border=True):
                st.write(f"**{item['author']} says:**")
                st.write(item["argument"])

                if st.button("Submit a Rebuttal", key=f"rebuttal_{i}", use_container_width=True):
                    st.session_state.selected_argument_index = i
                    st.session_state.show_rebuttal_box = True

    if st.session_state.get("show_rebuttal_box", False) and arguments:
        selected = arguments[st.session_state.selected_argument_index]

        st.divider()
        st.subheader("Start Battle")

        st.write("You are rebutting:")
        st.info(selected["argument"])

        opening_rebuttal = st.text_area(
            "Your rebuttal",
            placeholder="Write your response to start the battle...",
            height=150
        )

        if st.button("Start Battle", type="primary", use_container_width=True):
            if opening_rebuttal.strip():
                new_battle = {
                    "id": len(st.session_state.battles) + 1,
                    "topic": st.session_state.active_topic,
                    "opponent": selected["author"],
                    "original_argument": selected["argument"],
                    "created": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "messages": [
                        {
                            "side": "Opponent",
                            "text": selected["argument"],
                        },
                        {
                            "side": "You",
                            "text": opening_rebuttal.strip(),
                        },
                    ],
                    "result": None,
                }

                st.session_state.battles.append(new_battle)
                st.session_state.show_rebuttal_box = False
                st.rerun()
            else:
                st.warning("Write your rebuttal first.")


# -----------------------------
# RIGHT: ACTIVE BATTLE
# -----------------------------

with right:
    st.subheader("Battle Threads")

    if not st.session_state.battles:
        st.info("No battles yet. Submit a rebuttal to start one.")
    else:
        battle_options = [
            f"Battle {battle['id']} — {battle['topic']} vs {battle['opponent']}"
            for battle in st.session_state.battles
        ]

        selected_battle_label = st.selectbox("Choose battle", battle_options)
        selected_index = battle_options.index(selected_battle_label)
        battle = st.session_state.battles[selected_index]

        st.write(f"**Topic:** {battle['topic']}")
        st.caption(f"Started: {battle['created']}")

        st.divider()

        for msg in battle["messages"]:
            if msg["side"] == "You":
                st.chat_message("user").write(f"**You:** {msg['text']}")
            else:
                st.chat_message("assistant").write(f"**Opponent:** {msg['text']}")

        st.divider()

        next_side = st.radio(
            "Add next response as:",
            ["You", "Opponent"],
            horizontal=True
        )

        next_response = st.text_area(
            "Next response",
            placeholder="Continue the debate...",
            height=100
        )

        if st.button("Add Response", use_container_width=True):
            if next_response.strip():
                battle["messages"].append(
                    {
                        "side": next_side,
                        "text": next_response.strip(),
                    }
                )
                battle["result"] = None
                st.rerun()
            else:
                st.warning("Type a response first.")

        if st.button("Judge Round", type="primary", use_container_width=True):
            battle["result"] = judge_battle(battle["messages"])
            st.rerun()

        if battle["result"]:
            st.divider()
            st.subheader("Round Result")

            st.metric("Winner", battle["result"]["winner"])

            st.write(f"**Your Score:** {battle['result']['you_score']}/100")
            st.progress(battle["result"]["you_score"] / 100)

            st.write(f"**Opponent Score:** {battle['result']['opponent_score']}/100")
            st.progress(battle["result"]["opponent_score"] / 100)

            st.caption(battle["result"]["rationale"])
