import streamlit as st
from pypdf import PdfReader
from dotenv import load_dotenv
import os
from google import genai
import json
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from io import BytesIO


# ============================================================
# CONFIGURATION
# ============================================================

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

st.set_page_config(
    page_title="AI Resume Analyser",
    page_icon="📄",
    layout="wide"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .main {
        padding-top: 2rem;
    }

    .hero {
        text-align: center;
        padding: 1rem 0 2rem 0;
    }

    .hero h1 {
        font-size: 2.7rem;
        margin-bottom: 0.4rem;
    }

    .hero p {
        font-size: 1.1rem;
        color: #666;
    }

    .score-card {
        text-align: center;
        padding: 1.5rem;
        border-radius: 15px;
        border: 1px solid #ddd;
        margin: 1rem 0;
    }

    .score {
        font-size: 3.5rem;
        font-weight: 700;
        margin: 0;
    }

    .score-label {
        font-size: 1rem;
        color: #666;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# PDF GENERATOR
# ============================================================

def create_pdf(analysis):

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=45,
        leftMargin=45,
        topMargin=45,
        bottomMargin=45
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "Title",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=22,
        spaceAfter=12
    )

    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styles["Normal"],
        alignment=TA_CENTER,
        fontSize=10,
        textColor=colors.grey,
        spaceAfter=20
    )

    heading_style = ParagraphStyle(
        "Heading",
        parent=styles["Heading2"],
        fontSize=14,
        spaceBefore=15,
        spaceAfter=8
    )

    body_style = ParagraphStyle(
        "Body",
        parent=styles["BodyText"],
        fontSize=10,
        leading=15,
        spaceAfter=6
    )

    small_style = ParagraphStyle(
        "Small",
        parent=styles["BodyText"],
        fontSize=8,
        textColor=colors.grey,
        leading=11
    )

    story = []

    # --------------------------------------------------------
    # Title
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "AI Resume & Job Match Analysis",
            title_style
        )
    )

    story.append(
        Paragraph(
            "AI-powered resume and job compatibility report",
            subtitle_style
        )
    )

    # --------------------------------------------------------
    # Match Score
    # --------------------------------------------------------

    score = analysis.get(
        "match_score",
        0
    )

    story.append(
        Paragraph(
            "Overall Match Score",
            heading_style
        )
    )

    score_table = Table(
        [
            [
                Paragraph(
                    f"<b>{score}%</b>",
                    ParagraphStyle(
                        "Score",
                        fontSize=28,
                        alignment=TA_CENTER
                    )
                )
            ]
        ],
        colWidths=[450]
    )

    score_table.setStyle(
        TableStyle(
            [
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    1,
                    colors.lightgrey
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE"
                ),
                (
                    "ALIGN",
                    (0, 0),
                    (-1, -1),
                    "CENTER"
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    15
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    15
                )
            ]
        )
    )

    story.append(score_table)

    story.append(Spacer(1, 10))

    story.append(
        Paragraph(
            analysis.get(
                "match_explanation",
                ""
            ),
            body_style
        )
    )

    # --------------------------------------------------------
    # Matching Skills
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "Matching Skills",
            heading_style
        )
    )

    matching_skills = analysis.get(
        "matching_skills",
        []
    )

    for skill in matching_skills:

        story.append(
            Paragraph(
                f"• {skill}",
                body_style
            )
        )

    # --------------------------------------------------------
    # Skill Gaps
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "Skill Gaps",
            heading_style
        )
    )

    missing_skills = analysis.get(
        "missing_skills",
        []
    )

    for skill in missing_skills:

        story.append(
            Paragraph(
                f"• {skill}",
                body_style
            )
        )

    # --------------------------------------------------------
    # Experience Gaps
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "Experience Gaps",
            heading_style
        )
    )

    experience_gaps = analysis.get(
        "experience_gaps",
        []
    )

    for gap in experience_gaps:

        story.append(
            Paragraph(
                f"• {gap}",
                body_style
            )
        )

    # --------------------------------------------------------
    # Resume Evidence
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "Resume Evidence",
            heading_style
        )
    )

    evidence = analysis.get(
        "evidence",
        []
    )

    for item in evidence:

        story.append(
            Paragraph(
                f"• {item}",
                body_style
            )
        )

    # --------------------------------------------------------
    # Resume Suggestions
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "Resume Improvement Suggestions",
            heading_style
        )
    )

    suggestions = analysis.get(
        "resume_suggestions",
        []
    )

    for i, suggestion in enumerate(
        suggestions,
        start=1
    ):

        story.append(
            Paragraph(
                f"<b>{i}.</b> {suggestion}",
                body_style
            )
        )

    # --------------------------------------------------------
    # Interview Questions
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "Likely Interview Questions",
            heading_style
        )
    )

    questions = analysis.get(
        "interview_questions",
        []
    )

    for i, question in enumerate(
        questions,
        start=1
    ):

        story.append(
            Paragraph(
                f"<b>{i}.</b> {question}",
                body_style
            )
        )

    # --------------------------------------------------------
    # Recommendation
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "Overall Recommendation",
            heading_style
        )
    )

    recommendation = analysis.get(
        "recommendation",
        ""
    )

    story.append(
        Paragraph(
            recommendation,
            body_style
        )
    )

    story.append(Spacer(1, 20))

    story.append(
        Paragraph(
            "This report was generated using AI and should be "
            "used as a supporting tool when evaluating job fit.",
            small_style
        )
    )

    # --------------------------------------------------------
    # Build PDF
    # --------------------------------------------------------

    document.build(story)

    buffer.seek(0)

    return buffer.getvalue()


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
    <div class="hero">
        <h1>📄 AI Resume & Job Match Analyser</h1>
        <p>
            Understand how well your resume matches a job,
            identify skill gaps, and prepare for interviews.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

st.divider()


# ============================================================
# INPUT SECTION
# ============================================================

col1, col2 = st.columns(2)

resume_text = ""

with col1:

    st.subheader("📄 Your Resume")

    resume = st.file_uploader(
        "Upload your resume",
        type=["pdf"],
        label_visibility="collapsed"
    )

    if resume:

        try:

            reader = PdfReader(resume)

            for page in reader.pages:

                text = page.extract_text()

                if text:
                    resume_text += text

            st.success(
                "Resume uploaded successfully!"
            )

        except Exception as e:

            st.error(
                f"Could not read the PDF: {e}"
            )


with col2:

    st.subheader("💼 Job Description")

    job_description = st.text_area(
        "Paste the job description",
        height=230,
        placeholder="Paste the job description here...",
        label_visibility="collapsed"
    )


st.divider()


# ============================================================
# ANALYZE BUTTON
# ============================================================

if st.button(
    "🔍 Analyze Resume",
    use_container_width=True,
    type="primary"
):

    if not resume:

        st.warning(
            "Please upload your resume first."
        )

    elif not resume_text:

        st.warning(
            "Could not extract text from the uploaded resume."
        )

    elif not job_description.strip():

        st.warning(
            "Please paste a job description first."
        )

    else:

        with st.spinner(
            "🤖 AI is analyzing your resume..."
        ):

            prompt = f"""
You are an AI career assistant helping a candidate evaluate their fit for a job.

Analyze the candidate's resume against the job description carefully.

CANDIDATE RESUME — THIS IS THE ONLY SOURCE OF TRUTH:
{resume_text}

JOB DESCRIPTION — USE THIS ONLY TO IDENTIFY JOB REQUIREMENTS:
{job_description}

CRITICAL RULES:

1. Treat the candidate resume above as the complete and only source
   of information about the candidate.

2. Never assume the candidate has worked on a project, technology,
   tool, internship, certification, or achievement unless it is
   explicitly present in the resume.

3. Do not use information from previous conversations, previous
   analyses, or outside knowledge about the candidate.

4. If something is not present in the resume, treat it as unknown.

5. Never invent projects, skills, experience, achievements,
   certifications, or numbers.

6. Clearly distinguish technical skill gaps from professional
   experience gaps.

7. Do not heavily penalize a fresher simply because a job asks for
   professional experience. Mention this separately under
   experience_gaps.

8. Interview questions must be based strictly on the resume and
   job description.

Return ONLY valid JSON.

Do not include markdown.
Do not include ```json.
Do not include any explanation outside the JSON.

Use EXACTLY this structure:

{{
    "match_score": 0,
    "match_explanation": "",
    "matching_skills": [],
    "missing_skills": [],
    "experience_gaps": [],
    "evidence": [],
    "resume_suggestions": [],
    "interview_questions": [],
    "recommendation": ""
}}

Rules:

- match_score must be an integer from 0 to 100.

- match_explanation should briefly explain the score.

- matching_skills should contain important skills from the job
  description that are explicitly present in the resume.

- missing_skills should contain important technical skills from
  the job description that are not present in the resume.

- experience_gaps should contain requirements related to years of
  experience, production experience, seniority, deployment
  experience, or similar requirements that the candidate does
  not currently demonstrate.

- evidence should provide evidence from the resume supporting
  the match assessment.

- Never invent evidence.

- resume_suggestions should contain 3 to 5 specific suggestions
  based only on genuine information in the resume.

- interview_questions should contain exactly 5 realistic questions.

- Never mention a project or technology that is not explicitly
  present in the resume.

- recommendation should classify the candidate as:
  Strong Match, Moderate Match, or Weak Match.
"""

            try:

                response = client.models.generate_content(
                    model="gemini-3.5-flash-lite",
                    contents=prompt
                )

                analysis_text = response.text.strip()

                if analysis_text.startswith("```json"):
                    analysis_text = analysis_text[7:]

                if analysis_text.startswith("```"):
                    analysis_text = analysis_text[3:]

                if analysis_text.endswith("```"):
                    analysis_text = analysis_text[:-3]

                analysis_text = analysis_text.strip()

                analysis = json.loads(
                    analysis_text
                )

                st.success(
                    "Analysis completed!"
                )

                st.divider()

                # ====================================================
                # MATCH SCORE
                # ====================================================

                score = analysis.get(
                    "match_score",
                    0
                )

                st.subheader(
                    "🎯 Overall Match"
                )

                st.markdown(
                    f"""
                    <div class="score-card">
                        <div class="score">
                            {score}%
                        </div>
                        <div class="score-label">
                            Resume Match Score
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                st.progress(
                    max(0, min(score, 100)) / 100
                )

                st.write(
                    analysis.get(
                        "match_explanation",
                        ""
                    )
                )

                # ====================================================
                # SKILLS
                # ====================================================

                skill_col1, skill_col2 = st.columns(2)

                with skill_col1:

                    st.subheader(
                        "✅ Matching Skills"
                    )

                    matching_skills = analysis.get(
                        "matching_skills",
                        []
                    )

                    if matching_skills:

                        for skill in matching_skills:

                            st.markdown(
                                f"• **{skill}**"
                            )

                    else:

                        st.write(
                            "No major matching skills identified."
                        )

                with skill_col2:

                    st.subheader(
                        "⚠️ Skill Gaps"
                    )

                    missing_skills = analysis.get(
                        "missing_skills",
                        []
                    )

                    if missing_skills:

                        for skill in missing_skills:

                            st.markdown(
                                f"• **{skill}**"
                            )

                    else:

                        st.write(
                            "No major skill gaps identified."
                        )

                st.divider()

                # ====================================================
                # EXPERIENCE GAPS
                # ====================================================

                st.subheader(
                    "📌 Experience Gaps"
                )

                experience_gaps = analysis.get(
                    "experience_gaps",
                    []
                )

                if experience_gaps:

                    for gap in experience_gaps:

                        st.write(
                            f"• {gap}"
                        )

                else:

                    st.write(
                        "No major experience gaps identified."
                    )

                # ====================================================
                # EVIDENCE
                # ====================================================

                st.subheader(
                    "🔎 Resume Evidence"
                )

                evidence = analysis.get(
                    "evidence",
                    []
                )

                if evidence:

                    for item in evidence:

                        st.write(
                            f"• {item}"
                        )

                else:

                    st.write(
                        "No supporting evidence identified."
                    )

                st.divider()

                # ====================================================
                # RESUME SUGGESTIONS
                # ====================================================

                st.subheader(
                    "💡 Resume Improvement Suggestions"
                )

                suggestions = analysis.get(
                    "resume_suggestions",
                    []
                )

                for i, suggestion in enumerate(
                    suggestions,
                    start=1
                ):

                    st.write(
                        f"**{i}.** {suggestion}"
                    )

                st.divider()

                # ====================================================
                # INTERVIEW QUESTIONS
                # ====================================================

                st.subheader(
                    "🎯 Likely Interview Questions"
                )

                questions = analysis.get(
                    "interview_questions",
                    []
                )

                for i, question in enumerate(
                    questions,
                    start=1
                ):

                    st.write(
                        f"**{i}.** {question}"
                    )

                st.divider()

                # ====================================================
                # RECOMMENDATION
                # ====================================================

                st.subheader(
                    "📌 Overall Recommendation"
                )

                recommendation = analysis.get(
                    "recommendation",
                    ""
                )

                st.info(
                    recommendation
                )

                st.divider()

                # ====================================================
                # PDF DOWNLOAD
                # ====================================================

                pdf_data = create_pdf(
                    analysis
                )

                st.download_button(
                    label="📥 Download PDF Report",
                    data=pdf_data,
                    file_name="resume_job_analysis.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

                st.caption(
                    "AI-generated analysis. "
                    "Use this as a supporting tool when evaluating job fit."
                )

            except json.JSONDecodeError:

                st.error(
                    "The AI returned an unexpected format. "
                    "Please try the analysis again."
                )

                with st.expander(
                    "View AI Response"
                ):

                    st.write(
                        analysis_text
                    )

            except Exception as e:

                st.error(
                    f"AI Error: {e}"
                )