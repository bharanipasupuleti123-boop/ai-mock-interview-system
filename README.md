# AI Mock Interview System

An AI-powered mock interview platform built using **Streamlit**, **Groq API**, and **Llama 3.3** that helps students and job seekers prepare for interviews through realistic HR and technical interview simulations with personalized feedback.

## Features

* Personalized interview questions based on:

  * Skills
  * Experience
  * Target role
  * Difficulty level
* Interactive HR and technical interview sessions
* AI-generated performance feedback
* Communication and technical skill evaluation
* Downloadable interview feedback report
* User-friendly web interface

## Technologies Used

* **Python**
* **Streamlit**
* **Groq API**
* **Llama 3.3 70B Versatile**
* **Streamlit JS Eval**

## Project Workflow

1. User enters profile details and target role.
2. AI generates personalized interview questions.
3. Candidate answers interview questions.
4. AI evaluates responses.
5. Detailed feedback report is generated.

## Installation

Clone the repository:

```bash
git clone https://github.com/yourusername/AI-Mock-Interview-System.git
cd AI-Mock-Interview-System
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Add your Groq API key in `.streamlit/secrets.toml`

```toml
GROQ_API_KEY = "your_groq_api_key"
```

Run the application:

```bash
streamlit run app.py
```

## Project Structure

```text
AI-Mock-Interview-System/
│── app.py
│── requirements.txt
│── README.md
│── .gitignore
│── .streamlit/
│   └── secrets.toml
```

## Future Enhancements

* Voice-based interview support
* Resume-based question generation
* Multilingual interview support
* Real-time performance tracking
* Advanced AI analytics

## Conclusion

The AI Mock Interview System helps candidates improve interview preparation through realistic practice sessions and personalized AI feedback, enhancing confidence and interview performance.

## Author

**Pasupuleti Bharani Kumar**
Vardhaman College of Engineering
