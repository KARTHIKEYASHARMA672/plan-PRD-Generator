# prd_and_plan_generator.py
import streamlit as st
import os
import google.generativeai as genai
from dotenv import load_dotenv
from datetime import datetime

# -------------------------------
# Load API Key
# -------------------------------
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    st.error("❌ GOOGLE_API_KEY not set in .env file.")
else:
    genai.configure(api_key=API_KEY)

# -------------------------------
# Helper Functions
# -------------------------------
def generate_prd(app_name, app_idea, app_type, language):
    prompt = f"""
    You are an expert product manager. Create a **Product Requirements Document (PRD)** 
    for the following app idea. The PRD should be clear, structured, and tailored 
    to the app type and description provided.

    App Name: {app_name}
    App Type: {app_type}
    Description: {app_idea}

    Structure the PRD with these sections:
    1. Overview
    2. Essential Core Features
    3. Tech Stack
    4. Design Preferences
    5. All Screens/Pages
    6. App Menu and Navigation Structure
    7. User Flow
    8. Monetization Strategy
    9. Risks & Challenges
    10. Roadmap (MVP → Future Releases)

    Language: {language}
    """
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    return response.text if response else "⚠️ No response from Gemini."


def generate_plan(prd_text, language):
    prompt = f"""
    You are a senior software architect. Carefully read the PRD below and 
    generate a **unique, PRD-specific step-by-step implementation plan**.

    --- PRD START ---
    {prd_text}
    --- PRD END ---

    Rules for the implementation plan:
    - Break the plan into logical phases (e.g., Frontend, Backend, AI Integration, Authentication, Testing, Deployment, Optimization). 
      Only include phases that are relevant to THIS PRD.
    - For each phase, provide:
      • Objectives  
      • Detailed Tasks (must reference actual features, APIs, and technologies mentioned in the PRD)  
      • Deliverables  
    - Do NOT create generic filler tasks. All tasks must map directly to the PRD.
    - If the PRD specifies unique tools (e.g., Supabase, Firebase, OCR API, OpenAI), mention them explicitly in tasks.
    - If the PRD is lightweight, reduce the number of phases but go deeper into tasks.
    - Ensure the final roadmap looks like a professional execution plan tailored to this project.

    Language: {language}
    """
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    return response.text if response else "⚠️ No response from Gemini."

# -------------------------------
# Streamlit UI
# -------------------------------
st.set_page_config(page_title="PRD & Plan Generator", layout="wide")

st.title("📄 PRD & 🚀 Implementation Plan Generator")

tab1, tab2 = st.tabs(["📄 Generate PRD", "🚀 Generate Implementation Plan"])

# -------------------------------
# Tab 1: PRD Generator
# -------------------------------
with tab1:
    st.subheader("📄 Generate Product Requirements Document (PRD)")

    app_name = st.text_input("App Name", placeholder="e.g., PRD Forge")
    app_idea = st.text_area("Describe your app idea", placeholder="Enter a short description...")
    app_type = st.selectbox("App Type", ["Web App", "Mobile App", "Hybrid", "AI Tool", "IoT App"])
    language = st.selectbox("Output Language", ["English", "Hindi", "Telugu"])
    export_format = st.radio("Export Format", ["Markdown", "Text"])

    if st.button("🚀 Generate PRD"):
        if not app_idea or not app_name:
            st.warning("⚠️ Please enter both App Name and Description.")
        else:
            with st.spinner("Generating PRD... ⏳"):
                prd_output = generate_prd(app_name, app_idea, app_type, language)

            st.subheader("📑 Generated PRD")
            st.markdown(prd_output)

            # Save for Tab 2 use
            st.session_state["last_prd"] = prd_output

            # Export
            file_name = f"{app_name.replace(' ', '_')}_PRD_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            file_content = prd_output.encode("utf-8")
            if export_format == "Markdown":
                st.download_button("⬇️ Download PRD (Markdown)", data=file_content, file_name=f"{file_name}.md", mime="text/markdown")
            else:
                st.download_button("⬇️ Download PRD (Text)", data=file_content, file_name=f"{file_name}.txt", mime="text/plain")

# -------------------------------
# Tab 2: Implementation Plan Generator
# -------------------------------
with tab2:
    st.subheader("🚀 Generate Project Implementation Plan")

    st.write("Paste a PRD below or use the one you just generated in Tab 1.")

    prd_input = st.text_area("PRD Input", st.session_state.get("last_prd", ""), height=400)
    plan_language = st.selectbox("Plan Language", ["English", "Hindi", "Telugu"], key="plan_lang")

    if st.button("⚡ Generate Implementation Plan"):
        if not prd_input.strip():
            st.warning("⚠️ Please provide a PRD to generate a plan.")
        else:
            with st.spinner("Generating Implementation Plan... ⏳"):
                plan_output = generate_plan(prd_input, plan_language)

            st.subheader("📊 Generated Implementation Plan")
            st.markdown(plan_output)

            # Export
            file_name = f"ImplementationPlan_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            file_content = plan_output.encode("utf-8")
            st.download_button("⬇️ Download Plan (Markdown)", data=file_content, file_name=f"{file_name}.md", mime="text/markdown")
