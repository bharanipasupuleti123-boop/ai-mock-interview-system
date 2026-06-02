import streamlit as st
from groq import Groq
from streamlit_js_eval import streamlit_js_eval

# Setting up the Streamlit page configuration
st.set_page_config(
    page_title="StreamlitChatMessageHistory",
    page_icon="💬"
)

st.title("Chatbot")

# Initialize session state variables
if "setup_complete" not in st.session_state:
    st.session_state.setup_complete = False

if "user_message_count" not in st.session_state:
    st.session_state.user_message_count = 0

if "feedback_shown" not in st.session_state:
    st.session_state.feedback_shown = False

if "chat_complete" not in st.session_state:
    st.session_state.chat_complete = False

if "messages" not in st.session_state:
    st.session_state.messages = []


# Helper functions
def complete_setup():
    st.session_state.setup_complete = True


def show_feedback():
    st.session_state.feedback_shown = True


# Setup stage for collecting user details
if not st.session_state.setup_complete:

    st.subheader("Personal Information")

    # Initialize session state for personal information
    if "name" not in st.session_state:
        st.session_state["name"] = ""

    if "experience" not in st.session_state:
        st.session_state["experience"] = ""

    if "skills" not in st.session_state:
        st.session_state["skills"] = ""

    # Get personal information input
    st.session_state["name"] = st.text_input(
        label="Name",
        value=st.session_state["name"],
        placeholder="Enter your name",
        max_chars=40
    )

    st.session_state["experience"] = st.text_area(
        label="Experience",
        value=st.session_state["experience"],
        placeholder="Describe your experience",
        max_chars=200
    )

    st.session_state["skills"] = st.text_area(
        label="Skills",
        value=st.session_state["skills"],
        placeholder="List your skills",
        max_chars=200
    )

    # Company and Position Section
    st.subheader("Company and Position")

    # Initialize defaults
    if "level" not in st.session_state:
        st.session_state["level"] = "Junior"

    if "position" not in st.session_state:
        st.session_state["position"] = "Data Scientist"

    if "company" not in st.session_state:
        st.session_state["company"] = "Amazon"

    col1, col2 = st.columns(2)

    with col1:
        levels = ["Junior", "Mid-level", "Senior"]

        st.session_state["level"] = st.radio(
            "Choose level",
            options=levels,
            index=levels.index(
                st.session_state["level"]
            )
        )

    with col2:
        positions = [
            "Data Scientist",
            "Data Engineer",
            "ML Engineer",
            "BI Analyst",
            "Financial Analyst"
        ]

        st.session_state["position"] = st.selectbox(
            "Choose a position",
            positions,
            index=positions.index(
                st.session_state["position"]
            )
        )

    companies = [
        "Amazon",
        "Meta",
        "Udemy",
        "365 Company",
        "Nestle",
        "LinkedIn",
        "Spotify"
    ]

    st.session_state["company"] = st.selectbox(
        "Select a Company",
        companies,
        index=companies.index(
            st.session_state["company"]
        )
    )

    # Button to complete setup
    if st.button("Start Interview"):
        complete_setup()
        st.rerun()


# Interview phase
if (
    st.session_state.setup_complete
    and not st.session_state.feedback_shown
    and not st.session_state.chat_complete
):

    st.info(
        "Start by introducing yourself",
        icon="👋"
    )

    # Initialize Groq client
    client = Groq(
        api_key=st.secrets["GROQ_API_KEY"]
    )

    # Set Groq model
    if "groq_model" not in st.session_state:
        st.session_state["groq_model"] = (
            "llama-3.3-70b-versatile"
        )

    # System prompt
    if not st.session_state.messages:
        st.session_state.messages = [{
            "role": "system",
            "content": (
                f"You are an HR executive interviewing "
                f"{st.session_state['name']} "
                f"for the role of "
                f"{st.session_state['level']} "
                f"{st.session_state['position']} "
                f"at {st.session_state['company']}. "

                f"The candidate has experience in "
                f"{st.session_state['experience']} "
                f"and skills in "
                f"{st.session_state['skills']}. "

                "Ask professional interview questions "
                "one at a time. Keep responses formal "
                "and realistic like a real HR interview."
            )
        }]

    # Display chat messages
    for message in st.session_state.messages:
        if message["role"] != "system":
            with st.chat_message(
                message["role"]
            ):
                st.markdown(
                    message["content"]
                )

    # Handle user input
    if st.session_state.user_message_count < 5:

        if prompt := st.chat_input(
            "Your response",
            max_chars=1000
        ):

            st.session_state.messages.append({
                "role": "user",
                "content": prompt
            })

            with st.chat_message("user"):
                st.markdown(prompt)

            # Assistant response
            if (
                st.session_state.user_message_count
                < 4
            ):

                with st.chat_message(
                    "assistant"
                ):

                    stream = (
                        client.chat.completions.create(
                            model=st.session_state[
                                "groq_model"
                            ],
                            messages=[
                                {
                                    "role": m["role"],
                                    "content": m["content"]
                                }
                                for m in
                                st.session_state.messages
                            ],
                            stream=True,
                        )
                    )

                    response = st.write_stream(
                        chunk.choices[0]
                        .delta.content or ""
                        for chunk in stream
                    )

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response
                })

            # Increment counter
            st.session_state.user_message_count += 1

    # End interview after 5 responses
    if (
        st.session_state.user_message_count
        >= 5
    ):
        st.session_state.chat_complete = True


# Show Get Feedback button
if (
    st.session_state.chat_complete
    and not st.session_state.feedback_shown
):

    if st.button("Get Feedback"):
        show_feedback()
        st.rerun()


# Feedback screen
if st.session_state.feedback_shown:

    st.subheader("Feedback")

    conversation_history = "\n".join([
        f"{msg['role']}: "
        f"{msg['content']}"
        for msg in
        st.session_state.messages
    ])

    # Feedback client
    feedback_client = Groq(
        api_key=st.secrets["GROQ_API_KEY"]
    )

    # Generate feedback
    feedback_completion = (
        feedback_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": """
You are a professional interview evaluator.

Evaluate the interviewee's performance.

STRICT FORMAT:

Overall Score:
<score>/10

Feedback:
<feedback>

Rules:
- Put Overall Score and Feedback on separate lines.
- Give practical and honest feedback.
- Mention strengths and areas of improvement.
- Do not ask additional questions.
"""
                },
                {
                    "role": "user",
                    "content": (
                        "Evaluate this interview:\n\n"
                        f"{conversation_history}"
                    )
                }
            ]
        )
    )

    st.write(
        feedback_completion
        .choices[0]
        .message.content
    )

    # Restart interview
    if st.button(
        "Restart Interview",
        type="primary"
    ):
        streamlit_js_eval(
            js_expressions=(
                "parent.window.location.reload()"
            )
        )