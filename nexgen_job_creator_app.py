import streamlit as st
from openai import OpenAI
from io import BytesIO
from fpdf import FPDF

# =========================
#  OpenAI client
# =========================
# API key is stored in Streamlit Secrets as:
# OPENAI_API_KEY = "sk-xxxxx"
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])


# =========================
#  Helper functions
# =========================
def generate_job_post(role, location, experience, skills, extra_notes):
    """Call OpenAI to generate a job posting text."""

    user_prompt = f"""
Create a detailed LinkedIn job post for the following role.

Role: {role}
Location: {location}
Experience required: {experience}
Key skills: {skills}
Extra notes from the hiring manager: {extra_notes}

Structure the post as:
1. Strong hook line (1–2 sentences)
2. Short intro about the company and team
3. 5–8 bullet points on responsibilities
4. 5–8 bullet points on must-have & good-to-have skills
5. 3–4 lines on culture, growth, and why join us
6. Clear CTA to apply, including contact / email placeholder.

Keep tone professional, friendly and concise.
"""

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an expert recruiter and copywriter who writes high-conversion "
                    "job posts for LinkedIn. You keep things clear, structured and easy to scan."
                ),
            },
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.8,
    )

    return completion.choices[0].message.content.strip()


def job_post_to_pdf(text, title="Job_Posting"):
    """Create a simple PDF from the generated text using fpdf2."""
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_title(title)
    pdf.set_font("Arial", size=11)

    for line in text.split("\n"):
        pdf.multi_cell(0, 6, line)
        pdf.ln(1)

    pdf_bytes = pdf.output(dest="S").encode("latin-1")
    return BytesIO(pdf_bytes)


# =========================
#  Streamlit UI
# =========================
st.set_page_config(
    page_title="Nexgen Job Posting Helper",
    page_icon="🧩",
    layout="centered",
)

st.title("🧩 Nexgen Job Posting Helper")
st.write(
    "Generate a recruiter-friendly LinkedIn / job portal post, and download it as a PDF "
    "to share with your team or agencies."
)

with st.form("job_form"):
    col1, col2 = st.columns(2)

    with col1:
        role = st.text_input(
            "Role / Job Title*",
            placeholder="Bilingual L1 Support Lead (Japanese + Tamil)",
        )
        location = st.text_input("Location", placeholder="Coimbatore, Tamil Nadu")

    with col2:
        experience = st.text_input(
            "Experience range", placeholder="5+ years in L1 / Tech Support"
        )
        skills = st.text_area(
            "Key skills (comma separated)",
            placeholder=(
                "Japanese JLPT N3/N2, Tamil (native), ServiceNow, JIRA, Confluence, "
                "Java/.NET/Front-end basics"
            ),
            height=100,
        )

    extra_notes = st.text_area(
        "Extra notes / context for the role",
        placeholder="Any client specifics, work timings, culture notes, must-have behaviours, etc.",
        height=120,
    )

    submitted = st.form_submit_button("Generate job post")

if submitted:
    if not role.strip():
        st.error("Please enter at least a Role / Job Title.")
    else:
        with st.spinner("Calling OpenAI and drafting your job post..."):
            try:
                post_text = generate_job_post(
                    role, location, experience, skills, extra_notes
                )
            except Exception as e:
                st.error(
                    "There was an error talking to OpenAI. Please check the API key and logs."
                )
                st.exception(e)
            else:
                st.success("Done! Review your job post below 👇")

                st.subheader("Generated job post")
                st.write(post_text)

                # Create PDF
                pdf_buffer = job_post_to_pdf(post_text, title=role.replace(" ", "_"))
                st.download_button(
                    label="⬇️ Download as PDF",
                    data=pdf_buffer,
                    file_name=f"{role.replace(' ', '_')}_job_post.pdf",
                    mime="application/pdf",
                )

st.markdown("---")
st.caption(
    "Built for Nexgen recruiters. You can safely share this public URL with your team; "
    "the OpenAI API key is stored securely in Streamlit secrets and never exposed."
)
