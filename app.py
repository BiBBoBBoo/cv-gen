from __future__ import annotations
from src.utils.validation import validate_cv
from src.utils.formatting import render_cv_html
from src.services.storage import draft_json, load_draft_json, save_local_draft
from src.services.cv_generator import generate_cv
from src.models.cv import CVData, Education, Experience, GeneratedCV

import sys
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

ROOT = Path(__file__).parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


st.set_page_config(page_title="Career Canvas", layout="centered")

STEPS = ["Personal", "Profile", "Experience",
         "Skills", "Education", "Additional"]


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        :root { --ink:#172033; --muted:#5f6b7a; --accent:#2563eb; --line:#d9dee7; --soft:#eff6ff; }
        .stApp { background:#f7f8fa; color:var(--ink); }
        .block-container { max-width: 860px; padding: 5rem 1.25rem 4rem; }
        h1, h2, h3 { color:var(--ink); letter-spacing:-.02em; }
        h1 { font-size:1.65rem; font-weight:700; margin-bottom:.25rem; }
        h2 { font-size:1.25rem; font-weight:700; }
        h3 { font-size:1rem; }
        .app-header { border-bottom:1px solid var(--line); margin-bottom:1.5rem; padding-bottom:1rem; }
        .app-name { color:var(--ink); font-size:1.1rem; font-weight:700; margin:0; }
        .app-subtitle { color:var(--muted); font-size:.9rem; margin:.25rem 0 0; }
        .section-label { color:var(--muted); font-size:.78rem; font-weight:600; letter-spacing:.04em; margin:0 0 .75rem; }
        .helper-text { color:var(--muted); font-size:.85rem; line-height:1.5; margin:.25rem 0 1.25rem; }
        .status-pill { background:var(--soft); border:1px solid #bfdbfe; color:#1d4ed8; display:inline-block; font-size:.75rem; padding:4px 8px; }
        .stTextInput label, .stTextArea label, .stSelectbox label, .stCheckbox label, .stRadio label { color:var(--ink)!important; font-weight:600!important; }
        [data-testid="stTextInput"], [data-testid="stTextArea"], [data-testid="stSelectbox"] { background:#fff; border:1px solid var(--line); border-radius:4px; padding:.45rem .7rem .25rem; margin-bottom:.8rem; }
        [data-testid="stTextInput"] input, [data-testid="stTextArea"] textarea, [data-testid="stSelectbox"] div[data-baseweb="select"] { background:#fff !important; border:1px solid #aeb8c6 !important; border-radius:4px !important; color:var(--ink) !important; -webkit-text-fill-color:var(--ink); }
        [data-testid="stTextInput"] input, [data-testid="stSelectbox"] div[data-baseweb="select"] { min-height:2.55rem; }
        [data-testid="stTextArea"] textarea { min-height:6rem; }
        .stTextInput input::placeholder, .stTextArea textarea::placeholder { color:#7a8492 !important; opacity:1; -webkit-text-fill-color:#7a8492; }
        [data-baseweb="select"] > div, [data-baseweb="select"] span { background:#fff !important; color:var(--ink) !important; -webkit-text-fill-color:var(--ink); }
        [data-baseweb="popover"] { background:#fff !important; color:var(--ink) !important; }
        [role="option"] { background:#fff !important; color:var(--ink) !important; }
        [role="option"][aria-selected="true"], [role="option"]:hover { background:var(--soft) !important; color:var(--ink) !important; }
        [data-testid="stTextInput"] input:focus, [data-testid="stTextArea"] textarea:focus, [data-testid="stSelectbox"] div[data-baseweb="select"]:focus-within { border-color:var(--accent) !important; box-shadow:0 0 0 1px var(--accent); }
        .stButton > button, .stDownloadButton > button { background:#fff; border:1px solid var(--line); border-radius:4px; color:var(--ink); min-height:2.35rem; }
        .stButton > button:hover, .stDownloadButton > button:hover { border-color:var(--accent); color:var(--accent); }
        .stButton > button[kind="primary"] { background:var(--accent); border-color:var(--accent); color:#fff; }
        [data-testid="stExpander"] { background:#fff !important; border:1px solid var(--line); border-radius:4px; box-shadow:none; margin-bottom:.75rem; }
        [data-testid="stExpander"] summary, [data-testid="stExpander"] summary p { background:#fff !important; color:var(--ink) !important; font-weight:600; }
        [data-testid="stFileUploader"] section { background:#fff !important; border-color:var(--line) !important; }
        [data-testid="stFileUploader"] label, [data-testid="stFileUploader"] small, [data-testid="stFileUploader"] span { color:var(--muted) !important; }
        [data-testid="stFileUploader"] button { background:#fff !important; border:1px solid var(--line) !important; color:var(--ink) !important; }
        [data-testid="stRadio"] > div { gap:.35rem; }
        [data-testid="stRadio"] label { border:1px solid transparent; border-radius:4px; padding:.2rem .35rem; }
        .options-note { color:var(--muted); font-size:.8rem; margin:.25rem 0 .75rem; }
        .preview-status { color:var(--muted); font-size:.85rem; margin:.5rem 0 1.25rem; }
        @media (max-width: 640px) { .block-container { padding:4.25rem .85rem 3rem; } .stColumns { display:block; } }
        @media print { [data-testid="stSidebar"], header, footer, .stButton, .stDownloadButton, [data-testid="stExpander"] { display:none!important; } .stApp { background:#fff; } }
        </style>
        """,
        unsafe_allow_html=True,
    )


def reset_widget_state() -> None:
    prefixes = ("personal_", "profile_", "job_",
                "skills_", "education_", "additional_")
    for key in list(st.session_state):
        if key.startswith(prefixes):
            del st.session_state[key]


def start_state() -> None:
    if "data" not in st.session_state:
        st.session_state.data = CVData()
        st.session_state.step = 0
        st.session_state.generated = None
        st.session_state.use_ai = False
        st.session_state.loaded_upload = None


def text_field(label: str, value: str, key: str, **kwargs) -> str:
    if key not in st.session_state:
        st.session_state[key] = value
    return st.text_input(label, key=key, **kwargs)


def text_area(label: str, value: str, key: str, **kwargs) -> str:
    if key not in st.session_state:
        st.session_state[key] = value
    return st.text_area(label, key=key, **kwargs)


def clear_data() -> None:
    reset_widget_state()
    st.session_state.data = CVData()
    st.session_state.generated = None
    st.session_state.step = 0
    st.session_state.notice = "All data cleared"


def render_personal(data: CVData) -> None:
    personal = data.personal
    left, right = st.columns(2)
    with left:
        personal.full_name = text_field(
            "Full name", personal.full_name, "personal_full_name", placeholder="e.g. Your Name")
        personal.phone = text_field(
            "Phone", personal.phone, "personal_phone", placeholder="+91 98765 43210")
        personal.location = text_field(
            "Location", personal.location, "personal_location", placeholder="City, Country")
    with right:
        personal.target_job_title = text_field("Target job title", personal.target_job_title,
                                               "personal_target_job_title", placeholder="e.g. Senior Financial Accounting Manager")
        personal.email = text_field(
            "Email", personal.email, "personal_email", placeholder="you@example.com")
        personal.linkedin = text_field(
            "LinkedIn", personal.linkedin, "personal_linkedin", placeholder="linkedin.com/in/your-name")
    personal.employment_preference = st.selectbox("Employment preference", ["Full-time", "Part-time", "Contract", "Consulting"], index=["Full-time", "Part-time", "Contract", "Consulting"].index(
        personal.employment_preference) if personal.employment_preference in ["Full-time", "Part-time", "Contract", "Consulting"] else 0, key="personal_preference")


def render_profile(data: CVData) -> None:
    profile = data.profile
    left, right = st.columns(2)
    with left:
        profile.years = text_field(
            "Total years of experience", profile.years, "profile_years", placeholder="e.g. 32")
        profile.profession = text_field(
            "Profession", profile.profession, "profile_profession", placeholder="e.g. Senior accounting professional")
    with right:
        profile.industry = text_field(
            "Industry / domain", profile.industry, "profile_industry", placeholder="e.g. Insurance")
        profile.specializations = text_field(
            "Areas of specialization", profile.specializations, "profile_specializations", placeholder="Separate areas with commas")
    st.info("Don't worry about professional wording. Describe your experience naturally; the application will refine it.")
    profile.description = text_area("Career description", profile.description, "profile_description",
                                    placeholder="Tell us what you have done in your own words...", height=130)
    profile.target_roles = text_field(
        "Target roles", profile.target_roles, "profile_target_roles", placeholder="Roles separated by commas")


def render_experience(data: CVData) -> None:
    for index, job in enumerate(data.experiences):
        with st.expander(f"{index + 1:02d}  {job.designation or 'Untitled role'}", expanded=index == 0):
            left, right = st.columns(2)
            with left:
                job.company = text_field(
                    "Company", job.company, f"job_{job.id}_company", placeholder="Company name")
                job.designation = text_field(
                    "Designation", job.designation, f"job_{job.id}_designation", placeholder="Job title")
                job.location = text_field(
                    "Location", job.location, f"job_{job.id}_location", placeholder="City, Country")
                job.start_year = text_field(
                    "Start year", job.start_year, f"job_{job.id}_start", placeholder="YYYY")
            with right:
                job.industry = text_field(
                    "Industry / domain", job.industry, f"job_{job.id}_industry", placeholder="e.g. Insurance")
                job.end_year = text_field(
                    "End year", job.end_year, f"job_{job.id}_end", placeholder="YYYY")
                job.current = st.checkbox(
                    "Current role", value=job.current, key=f"job_{job.id}_current")
                job.software = text_field("Software / systems used", job.software,
                                          f"job_{job.id}_software", placeholder="e.g. Excel, ERP system")
            st.caption("Enter one responsibility or achievement per line.")
            job.responsibilities = [line.strip() for line in text_area("Responsibilities", "\n".join(
                job.responsibilities), f"job_{job.id}_responsibilities", height=120).splitlines()]
            job.achievements = [line.strip() for line in text_area("Achievements", "\n".join(
                job.achievements), f"job_{job.id}_achievements", height=100).splitlines()]
            job.processes = text_area(
                "Processes handled", job.processes, f"job_{job.id}_processes", height=80)
            job.team_management = text_area(
                "Team management", job.team_management, f"job_{job.id}_team", height=80)
            if len(data.experiences) > 1 and st.button("Remove this role", key=f"remove_job_{job.id}"):
                data.experiences.pop(index)
                reset_widget_state()
                st.rerun()
    if st.button("+ Add another role"):
        data.experiences.append(Experience())
        st.rerun()


def render_skills(data: CVData) -> None:
    skills = data.skills
    skills.functional = text_area("Accounting / functional skills", skills.functional,
                                  "skills_functional", placeholder="Separate skills with commas", height=100)
    skills.industry = text_area("Industry / domain skills", skills.industry,
                                "skills_industry", placeholder="Separate skills with commas", height=100)
    skills.software = text_area("Software / tools", skills.software,
                                "skills_software", placeholder="Separate tools with commas", height=100)
    skills.custom = text_area("Custom skills", skills.custom, "skills_custom",
                              placeholder="Anything else relevant", height=100)
    st.caption(
        "Skills are kept as supplied and arranged into ATS-friendly groups. No keywords are added.")


def render_education(data: CVData) -> None:
    for index, item in enumerate(data.education):
        with st.expander(f"{index + 1:02d}  {item.qualification or 'Untitled qualification'}", expanded=index == 0):
            left, right = st.columns(2)
            with left:
                item.qualification = text_field(
                    "Qualification", item.qualification, f"education_{item.id}_qualification", placeholder="e.g. Bachelor of Commerce")
                item.specialization = text_field(
                    "Specialization", item.specialization, f"education_{item.id}_specialization", placeholder="e.g. Accounting")
                item.institution = text_field(
                    "Institution", item.institution, f"education_{item.id}_institution", placeholder="Institution name")
            with right:
                item.year = text_field(
                    "Year", item.year, f"education_{item.id}_year", placeholder="YYYY")
                item.certification = text_field(
                    "Certification", item.certification, f"education_{item.id}_certification", placeholder="Optional certification")
            if len(data.education) > 1 and st.button("Remove this entry", key=f"remove_education_{item.id}"):
                data.education.pop(index)
                reset_widget_state()
                st.rerun()
    if st.button("+ Add another education or certification"):
        data.education.append(Education())
        st.rerun()


def render_additional(data: CVData) -> None:
    additional = data.additional
    additional.languages = text_field(
        "Languages", additional.languages, "additional_languages", placeholder="e.g. English, Hindi")
    additional.availability = text_field("Availability", additional.availability,
                                         "additional_availability", placeholder="e.g. Available from June 2026")
    additional.awards = text_area(
        "Awards", additional.awards, "additional_awards", height=80)
    additional.memberships = text_area(
        "Professional memberships", additional.memberships, "additional_memberships", height=80)
    additional.training = text_area(
        "Training", additional.training, "additional_training", height=80)


def render_builder() -> None:
    data: CVData = st.session_state.data
    st.markdown('<div class="app-header"><p class="app-name">Career Canvas</p><p class="app-subtitle">Build a professional CV from your experience.</p></div>', unsafe_allow_html=True)
    if st.session_state.get("notice"):
        st.success(st.session_state.pop("notice"))
    st.markdown('<p class="section-label">CV information</p>',
                unsafe_allow_html=True)
    selected = st.radio("CV sections", STEPS,
                        index=st.session_state.step, horizontal=True)
    st.session_state.step = STEPS.index(selected)
    st.subheader(selected)
    if selected == "Personal":
        render_personal(data)
    elif selected == "Profile":
        render_profile(data)
    elif selected == "Experience":
        render_experience(data)
    elif selected == "Skills":
        render_skills(data)
    elif selected == "Education":
        render_education(data)
    else:
        render_additional(data)
    st.markdown('<p class="helper-text">Your progress is kept in this session. Use Options below for draft files.</p>', unsafe_allow_html=True)
    back, _, forward = st.columns([1, 2, 1])
    with back:
        if st.button("Back", disabled=st.session_state.step == 0):
            st.session_state.step -= 1
            st.rerun()
    with forward:
        if st.session_state.step < len(STEPS) - 1:
            if st.button("Next", type="primary"):
                st.session_state.step += 1
                st.rerun()
        else:
            st.session_state.use_ai = st.checkbox(
                "Use AI refinement", value=st.session_state.use_ai)
            if st.session_state.use_ai:
                st.caption(
                    "AI refinement sends your CV content to the configured OpenAI provider. It falls back to local refinement if unavailable.")
            if st.button("Generate CV", type="primary"):
                warnings = validate_cv(data)
                if warnings:
                    for warning in warnings:
                        st.warning(warning)
                st.session_state.generated = generate_cv(
                    data, st.session_state.use_ai)
                st.rerun()


def render_options() -> None:
    with st.expander("Options"):
        st.markdown(
            '<p class="options-note">Less frequently used actions for draft files.</p>', unsafe_allow_html=True)
        option_left, option_right = st.columns(2)
        with option_left:
            if st.button("Save draft locally"):
                save_local_draft(st.session_state.data)
                st.success("Draft saved as cv_draft.json")
            st.download_button("Download draft", data=draft_json(
                st.session_state.data), file_name="career-canvas-draft.json", mime="application/json")
        with option_right:
            upload = st.file_uploader("Load draft", type="json")
            if upload is not None and upload.name != st.session_state.get("loaded_upload"):
                try:
                    st.session_state.data = load_draft_json(upload.getvalue())
                    reset_widget_state()
                    st.session_state.loaded_upload = upload.name
                    st.session_state.generated = None
                    st.success("Draft loaded")
                    st.rerun()
                except (ValueError, TypeError):
                    st.error("That draft file could not be read.")
            if st.button("Clear all data"):
                clear_data()
                st.rerun()
        st.caption(
            "Local rewriting keeps your CV in this application. AI is optional and falls back locally if unavailable.")


def update_generated_bullets(generated: GeneratedCV, job: Experience, index: int, value: str, achievements: bool) -> None:
    target = job.achievements if achievements else job.responsibilities
    if index < len(target):
        target[index] = value


def render_preview() -> None:
    generated: GeneratedCV = st.session_state.generated
    st.markdown('<div class="app-header"><p class="app-name">Career Canvas</p><p class="app-subtitle">Review your CV and make any final edits.</p></div>', unsafe_allow_html=True)
    st.subheader("CV preview")
    st.markdown(
        f'<p class="preview-status"><span class="status-pill">{generated.status}</span> Your information stays under your control.</p>', unsafe_allow_html=True)
    if st.button("Edit CV"):
        st.session_state.generated = None
        st.rerun()
    with st.expander("Edit generated content", expanded=True):
        generated.summary = st.text_area(
            "Professional summary", generated.summary, key="generated_summary", height=120)
        competencies = st.text_area("Core competencies", ", ".join(
            generated.competencies), key="generated_competencies", height=90)
        generated.competencies = [
            item.strip() for item in competencies.split(",") if item.strip()]
        for job in generated.experience:
            st.markdown(
                f"**{job.designation or 'Role'} · {job.company or 'Company'}**")
            responsibilities = st.text_area("Responsibilities", "\n".join(
                job.responsibilities), key=f"generated_resp_{job.id}", height=100)
            achievements = st.text_area("Achievements", "\n".join(
                job.achievements), key=f"generated_ach_{job.id}", height=90)
            job.responsibilities = [
                item.strip() for item in responsibilities.splitlines() if item.strip()]
            job.achievements = [
                item.strip() for item in achievements.splitlines() if item.strip()]
        for item in generated.data.education:
            with st.container(border=True):
                item.qualification = text_field(
                    "Qualification", item.qualification, f"preview_education_{item.id}_qualification")
                item.specialization = text_field(
                    "Specialization", item.specialization, f"preview_education_{item.id}_specialization")
                item.institution = text_field(
                    "Institution", item.institution, f"preview_education_{item.id}_institution")
                item.year = text_field(
                    "Year", item.year, f"preview_education_{item.id}_year")
                item.certification = text_field(
                    "Certification", item.certification, f"preview_education_{item.id}_certification")
        for label, attr in (("Languages", "languages"), ("Awards", "awards"), ("Professional memberships", "memberships"), ("Training", "training"), ("Availability", "availability")):
            setattr(generated.data.additional, attr, text_area(label, getattr(
                generated.data.additional, attr), f"preview_additional_{attr}", height=65))
    html = render_cv_html(generated)
    components.html(html, height=1250, scrolling=True)
    st.download_button("Download CV HTML", data=html,
                       file_name="career-canvas-cv.html", mime="text/html")
    st.caption("For a clean PDF, turn off browser headers and footers in the print dialog. This removes the date, URL, and page number added by the browser.")


def main() -> None:
    start_state()
    inject_styles()
    if st.session_state.generated is None:
        render_builder()
        render_options()
    else:
        render_preview()


if __name__ == "__main__":
    main()
