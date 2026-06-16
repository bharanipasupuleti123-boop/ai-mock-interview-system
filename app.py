import streamlit as st
from groq import Groq
from streamlit_js_eval import streamlit_js_eval

# PAGE CONFIG

st.set_page_config(
    page_title="AI Mock Interview Coach",
    layout="centered"
)

st.title("AI Mock Interview Coach")

st.markdown("""
Practice HR and technical interviews using AI.

Get realistic interview questions and personalized feedback
based on your skills, experience, and target role.
""")

# SESSION STATES

defaults = {
    "setup_complete": False,
    "user_message_count": 0,
    "feedback_shown": False,
    "chat_complete": False,
    "messages": [],
    "feedback_text": ""
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# FUNCTIONS

def complete_setup():
    st.session_state.setup_complete = True


def show_feedback():
    st.session_state.feedback_shown = True


def reset_app():
    streamlit_js_eval(
        js_expressions="parent.window.location.reload()"
    )


# SETUP SCREEN

if not st.session_state.setup_complete:

    st.subheader("Candidate Information")

    name = st.text_input(
        "Full Name",
        placeholder="Enter your name"
    )

    experience = st.text_area(
        "Experience",
        placeholder="Example: Worked on ML projects, internships..."
    )

    skills = st.text_area(
        "Skills",
        placeholder="Example: Python, SQL, Machine Learning"
    )

    st.subheader("Target Role")

    col1, col2 = st.columns(2)

    with col1:
        level = st.selectbox(
            "Experience Level",
            ["Junior", "Mid-level", "Senior"]
        )

    with col2:
        difficulty = st.selectbox(
            "Interview Difficulty",
            ["Beginner", "Intermediate", "Advanced"]
        )

    position = st.selectbox(
        "Target Position",
        [
            "Data Scientist",
            "Data Engineer",
            "ML Engineer",
            "BI Analyst",
            "Financial Analyst"
        ]
    )

    company = st.selectbox(
        "Target Company",
        [
            "Amazon",
            "Meta",
            "Spotify",
            "LinkedIn",
            "IBM",
            "Google",
            "Microsoft"
        ]
    )

    if st.button("Start Interview"):

        if not name.strip():
            st.warning("Please enter your name.")
            st.stop()

        st.session_state.name = name
        st.session_state.experience = experience
        st.session_state.skills = skills
        st.session_state.level = level
        st.session_state.position = position
        st.session_state.company = company
        st.session_state.difficulty = difficulty

        complete_setup()
        st.rerun()


# INTERVIEW SCREEN

if (
    st.session_state.setup_complete
    and not st.session_state.feedback_shown
    and not st.session_state.chat_complete
):

    st.subheader("Interview Session")

    progress = (
        st.session_state.user_message_count / 5
    )
    st.progress(progress)

    st.info(
        "Start by introducing yourself."
    )

    # Safe API key loading
    try:
        client = Groq(
            api_key=st.secrets["GROQ_API_KEY"]
        )
    except Exception:
        st.error(
            "Groq API key missing.\n\n"
            "Create `.streamlit/secrets.toml` "
            "and add your API key."
        )
        st.stop()

    # Model
    model_name = "llama-3.3-70b-versatile"

    # Initial system prompt
    if not st.session_state.messages:

        system_prompt = f"""
You are a professional HR interviewer.

Candidate Name:
{st.session_state.name}

Target Role:
{st.session_state.level}
{st.session_state.position}

Company:
{st.session_state.company}

Interview Difficulty:
{st.session_state.difficulty}

Candidate Experience:
{st.session_state.experience}

Skills:
{st.session_state.skills}

Instructions:
- Conduct a realistic interview.
- Ask one question at a time.
- Mix HR and technical questions.
- Ask role-specific questions.
- Keep tone professional.
- Do not give feedback during interview.
- Keep questions concise.
"""

        st.session_state.messages.append({
            "role": "system",
            "content": system_prompt
        })

    # Display chat history
    for message in st.session_state.messages:
        if message["role"] != "system":

            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Chat input
    if st.session_state.user_message_count < 5:

        if prompt := st.chat_input(
            "Type your response..."
        ):

            # User message
            st.session_state.messages.append({
                "role": "user",
                "content": prompt
            })

            with st.chat_message("user"):
                st.markdown(prompt)

            # Assistant response
            if st.session_state.user_message_count < 4:

                with st.chat_message("assistant"):

                    try:
                        stream = client.chat.completions.create(
                            model=model_name,
                            messages=[
                                {
                                    "role": m["role"],
                                    "content": m["content"]
                                }
                                for m in st.session_state.messages
                            ],
                            stream=True
                        )

                        response = st.write_stream(
                            chunk.choices[0].delta.content or ""
                            for chunk in stream
                        )

                    except Exception as e:
                        st.error(f"Error: {e}")
                        st.stop()

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response
                })

            st.session_state.user_message_count += 1

    # Complete interview
    if st.session_state.user_message_count >= 5:
        st.success("Interview completed!")
        st.session_state.chat_complete = True


# FEEDBACK BUTTON

if (
    st.session_state.chat_complete
    and not st.session_state.feedback_shown
):

    if st.button(
        "Get Feedback",
        type="primary"
    ):
        show_feedback()
        st.rerun()


# FEEDBACK SCREEN

if st.session_state.feedback_shown:

    st.subheader(
        "Interview Performance Report"
    )

    # Generate feedback only once
    if not st.session_state.feedback_text:

        conversation_history = "\n".join([
            f"{msg['role']}: {msg['content']}"
            for msg in st.session_state.messages
            if msg["role"] != "system"
        ])

        try:
            feedback_client = Groq(
                api_key=st.secrets[
                    "GROQ_API_KEY"
                ]
            )

            feedback_completion = (
                feedback_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {
                            "role": "system",
                            "content": """
You are an expert interview evaluator.

STRICT FORMAT:

Overall Score:
/10

Communication Skills:
<feedback>

Technical Knowledge:
<feedback>

Strengths:
<strengths>

Areas of Improvement:
<improvements>

Final Recommendation:
<recommendation>

Rules:
- Be honest and practical.
- Keep response professional.
- Do not ask questions.
"""
                        },
                        {
                            "role": "user",
                            "content":
                            f"Evaluate this interview:\n\n"
                            f"{conversation_history}"
                        }
                    ]
                )
            )

            st.session_state.feedback_text = (
                feedback_completion
                .choices[0]
                .message.content
            )

        except Exception as e:
            st.error(
                f"Error generating feedback: {e}"
            )

    st.write(st.session_state.feedback_text)

    # Download button
    st.download_button(
        label="Download Report",
        data=st.session_state.feedback_text,
        file_name="interview_feedback.txt",
        mime="text/plain"
    )

    # Restart
    if st.button(
        "Restart Interview",
        type="primary"
    ):
        reset_app()