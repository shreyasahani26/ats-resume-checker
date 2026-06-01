import streamlit as st
import PyPDF2
import re
import json

st.set_page_config(page_title="Simple ATS Checker")

def extract_text_from_pdf(uploaded_file):
    pdf_reader = PyPDF2.PdfReader(uploaded_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() or ""
    return text

def calculate_ats_score(resume_text, jd_text):
    resume_words = set(re.findall(r'\b\w+\b', resume_text.lower()))
    jd_words = set(re.findall(r'\b\w+\b', jd_text.lower()))

    stop_words = {
        "and", "the", "to", "of", "in", "for", "with",
        "a", "an", "is", "on", "that", "by"
    }

    jd_keywords = jd_words - stop_words
    matched = jd_keywords.intersection(resume_words)

    score = 0
    if len(jd_keywords) > 0:
        score = round((len(matched) / len(jd_keywords)) * 100)

    missing = list(jd_keywords - matched)

    return score, matched, missing
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:

    st.title("🔐 ATS Resume Checker")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Continue"):

        if email and password:
            st.session_state.logged_in = True
            st.session_state.user_email = email
            st.rerun()
        else:
            st.error("Enter Email and Password")

    st.stop()

    st.title(" ATS Resume Checker")

    option = st.radio(
        "Choose",
        ["Login", "Sign Up"]
    )

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if option == "Sign Up":

        if st.button("Create Account"):

            with open("users.json", "r") as f:
                users = json.load(f)

            users[email] = password

            with open("users.json", "w") as f:
                json.dump(users, f)

            st.success("Account Created Successfully!")

    else:

        if st.button("Login"):

            with open("users.json", "r") as f:
                users = json.load(f)

            if email in users and users[email] == password:
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Invalid Email or Password")

    st.stop()
st.title(" ATS Resume Checker")

job_description = st.text_area(
    "Paste Job Description",
    height=200
)

uploaded_file = st.file_uploader(
    "Upload Resume (PDF)",
    type=["pdf"]
)

if st.button("Analyze Resume"):

    if not uploaded_file or not job_description:
        st.error("Please upload a resume and enter a job description.")
    else:
        resume_text = extract_text_from_pdf(uploaded_file)

        score, matched, missing = calculate_ats_score(
            resume_text,
            job_description
        )

        st.success(f"ATS Score: {score}%")

        st.subheader("Matched Keywords")
        st.write(", ".join(list(matched)[:20]))

        st.subheader("Missing Keywords")
        st.write(", ".join(missing[:20]))