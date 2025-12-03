import streamlit as st
from openai import OpenAI
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import landscape
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
import tempfile
import os

# ============================================
# INIT OPENAI CLIENT
# ============================================
client = OpenAI()

# ============================================
# STREAMLIT PAGE SETUP
# ============================================
st.set_page_config(page_title="NexGen Job Post Generator", layout="wide")

st.title("🚀 NexGen Job Posting + Carousel Generator")

st.markdown(
"""
Use this tool to instantly create:
- A **LinkedIn-optimized job post**
- A **6-slide PDF carousel** (LinkedIn-ready)
  
Choose the country, enter job details, paste your JD — done.
"""
)

# ============================================
# INPUT SIDEBAR
# ============================================
st.sidebar.header("Job Details")

country = st.sidebar.selectbox(
    "Where is this position based?",
    ["India", "Japan"]
)

role_title = st.sidebar.text_input(
    "Role Title (10–12 words)",
    placeholder="Example: Senior Full Stack Engineer – Java + React"
)

client_context = st.sidebar.text_input(
    "Optional: Add non-sensitive client context (10–12 words)",
    placeholder="Example: working with a global automotive leader"
)

st.sidebar.markdown("---")

st.sidebar.markdown("### Paste the Existing LinkedIn JD Below 👇")

# MAIN INPUT
jd_input = st.text_area(
    "Paste your current JD (up to ~1000 characters)",
    height=250,
    placeholder="Copy–paste the JD here…"
)

generate_btn = st.button("✨ Generate Job Post + Carousel PDF")


# ============================================
# FUNCTION: CALL OPENAI
# ============================================
def generate_job_post(country, role_title, client_context, jd):
    """
    Generates the LinkedIn job post + slide text content using OpenAI.
    """

    # Conditional messaging
    if country == "India":
        why_join = (
            "Work closely with top Japanese clients, gain international exposure, "
            "and explore future opportunities to collaborate or travel to Japan."
        )
    else:
        # Japan
        why_join = (
            "Opportunity to work with major Japanese enterprises, including global "
            "leaders in manufacturing and consumer services (without naming clients)."
        )

    # Build system prompt
    system_prompt = f"""
You are an expert HR content creator specialising in LinkedIn job postings.

Your task:
1. Create a **high-visibility**, **viral**, **SEO-rich** LinkedIn job post.
2. Every line MUST be **max 25 words**.
3. Highlight the **top 4–5 required skills** clearly.
4. Add **3–4 compelling lines** explaining why candidates should join NexGen
   — tailored for the country: {country}.
5. Include: “Know someone who fits? Tag them!”
6. Create a **6-slide carousel outline**:
   • Slide 1: Eye-catching title (max 25–30 words)  
   • Slide 2: About the role  
   • Slide 3: Key responsibilities (3–4 bullets, 10–12 words each)  
   • Slide 4: Required skills (3–4 bullets, 10–12 words each)  
   • Slide 5: Why join NexGen (3–4 bullets, 10–12 words each)  
   • Slide 6: Call to action + tag someone note  
7. If country = Japan, slides must contain **Japanese on top**, **English below**.
8. If country = India, slides must be **English only**.
9. Use the job title: "{role_title}".
10. Include client context subtly if provided: "{client_context}".

Return your answer in this JSON style:

{
  "linkedin_post": "....",
  "slide1": "....",
  "slide2": "....",
  "slide3": "....",
  "slide4": "....",
  "slide5": "....",
  "slide6": "...."
}

Do not break JSON format.
"""

    user_prompt = f"""
Here is the JD to rewrite and enhance:

{jd}

Generate LinkedIn post + 6 slides now.
"""

    response = client.chat.completions.create(
        model="gpt-4.1",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )

    return response.choices[0].message.parsed


# ============================================
# FUNCTION: CREATE PDF CAROUSEL
# ============================================
def create_carousel_pdf(slides):
    """
    Creates a 6-slide PDF with branding using ReportLab.
    LinkedIn carousel recommended size = landscape A4.
    """
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    doc = SimpleDocTemplate(tmp_file.name, pagesize=landscape(A4))

    story = []
    styles = getSampleStyleSheet()
    body = ParagraphStyle(
        "body",
        parent=styles["Normal"],
        fontSize=22,
        leading=28,
        spaceAfter=20
    )

    # Branding header (Nexgen.png)
    brand_image_path = "Nexgen.png"

    for i in range(1, 7):
        story.append(Image(brand_image_path, width=3.5*inch, height=0.8*inch))
        story.append(Spacer(1, 0.3*inch))
        story.append(Paragraph(slides[f"slide{i}"], body))
        story.append(Spacer(1, 0.5*inch))

        if i < 6:
            story.append(Spacer(1, 1*inch))
            story.append(Paragraph("<br/><br/>", body))

    doc.build(story)
    return tmp_file.name



# ============================================
# MAIN ACTION
# ============================================
if generate_btn:

    if not role_title or not jd_input:
        st.error("Please enter the role title and paste the JD.")
        st.stop()

    with st.spinner("Generating content using OpenAI…"):
        result = generate_job_post(country, role_title, client_context, jd_input)

    st.success("Done! Your LinkedIn post and carousel PDF are ready.")

    # SHOW LINKEDIN POST
    st.subheader("📌 Suggested LinkedIn Post")
    st.write(result["linkedin_post"])

    # BUILD PDF
    with st.spinner("Creating PDF…"):
        pdf_path = create_carousel_pdf(result)

    # DOWNLOAD PDF
    with open(pdf_path, "rb") as f:
        st.download_button(
            "📥 Download 6-Slide Carousel PDF",
            data=f,
            file_name="nexgen_job_carousel.pdf",
            mime="application/pdf"
        )

    st.markdown("---")
    st.info("Want to generate another one? Modify details on the left and click **Generate** again.")

