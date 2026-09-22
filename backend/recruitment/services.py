import io
import re
import warnings
from html import unescape

from django.conf import settings
from django.core.mail import send_mail
from django.template import Context, Template
from django.utils import timezone

from recruitment.models import (
    Application,
    CandidateEmailLog,
    CVScore,
    EmailTemplate,
    JobPosting,
)

try:
    from docx import Document as DocxDocument
except ImportError:  # pragma: no cover
    DocxDocument = None

try:
    from pypdf import PdfReader
except ImportError:  # pragma: no cover
    PdfReader = None

SKILL_ALIASES = {
    "c#": "c#",
    "csharp": "c#",
    "c++": "c++",
    "cpp": "c++",
    "python": "python",
    "py": "python",
    "django": "django",
    "drf": "django rest framework",
    "postgresql": "postgresql",
    "postgres": "postgresql",
    "psql": "postgresql",
    "sql": "sql",
    "mysql": "mysql",
    "mongodb": "mongodb",
    "redis": "redis",
    "javascript": "javascript",
    "js": "javascript",
    "typescript": "typescript",
    "ts": "typescript",
    "react": "react",
    "reactjs": "react",
    "node": "node.js",
    "nodejs": "node.js",
    "node.js": "node.js",
    "express": "express",
    "aws": "aws",
    "azure": "azure",
    "gcp": "google cloud",
    "google cloud": "google cloud",
    "docker": "docker",
    "kubernetes": "kubernetes",
    "terraform": "terraform",
    "java": "java",
    "spring": "spring",
    "dotnet": ".net",
    "net": ".net",
    ".net": ".net",
    "html": "html",
    "css": "css",
    "tailwind": "tailwind",
    "figma": "figma",
    "ux": "ux",
    "ui": "ui",
    "excel": "excel",
    "powerbi": "power bi",
    "power bi": "power bi",
    "tableau": "tableau",
    "pandas": "pandas",
    "numpy": "numpy",
    "machine learning": "machine learning",
    "ml": "machine learning",
    "ai": "artificial intelligence",
    "artificial intelligence": "artificial intelligence",
    "data analysis": "data analysis",
    "etl": "etl",
    "api": "api",
    "rest": "rest api",
    "rest api": "rest api",
    "microservices": "microservices",
    "agile": "agile",
    "scrum": "scrum",
}


def normalize_bool(value):
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    return str(value).strip().lower() in {"1", "true", "yes", "y", "on"}


def normalize_tokens(value):
    if not value:
        return []
    text = unescape(str(value)).lower()
    text = text.replace("&nbsp;", " ")
    text = re.sub(r"[\r\n\t]+", " ", text)
    text = re.sub(r"[^a-z0-9+#.\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    return re.findall(r"[a-z0-9+#.]+", text)


def canonicalize_skill_token(token):
    if not token:
        return None
    cleaned = token.strip().lower()
    cleaned = cleaned.replace("-", " ").replace("_", " ")
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    if cleaned in SKILL_ALIASES:
        return SKILL_ALIASES[cleaned]
    return cleaned


def build_skill_variants(skill):
    variants = set()
    if not skill:
        return variants
    normalized = canonicalize_skill_token(skill)
    if not normalized:
        return variants
    raw_variants = [
        normalized,
        normalized.replace(" ", ""),
        normalized.replace(" ", "-"),
        normalized.replace(" ", "_"),
        normalized.replace(" ", ""),
        normalized.replace("/", " "),
        normalized.replace(".", " "),
    ]
    for value in raw_variants:
        value = re.sub(r"\s+", " ", str(value).lower()).strip()
        if value:
            variants.add(value)
        if value and " " in value:
            variants.add(value.replace(" ", ""))
    return variants


def extract_skill_matches(required_skills, candidate_text):
    if not required_skills:
        return []
    text = " ".join(
        chunk for chunk in [candidate_text or "", " ".join(normalize_tokens(candidate_text or ""))] if chunk
    ).lower()
    text = re.sub(r"[^a-z0-9+#.\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []

    matches = []
    for skill in required_skills:
        variants = build_skill_variants(skill)
        if not variants:
            continue
        if any(variant in text for variant in variants):
            matches.append(skill)
    return sorted(set(matches))


def decode_file_bytes(raw_bytes):
    if not raw_bytes:
        return ""
    for encoding in ("utf-8", "utf-8-sig", "cp1252", "latin-1"):
        try:
            return raw_bytes.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw_bytes.decode("utf-8", errors="replace")


def extract_text_from_pdf_bytes(file_bytes):
    if PdfReader is None:
        return ""
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            reader = PdfReader(io.BytesIO(file_bytes))
            pages = []
            for page in reader.pages:
                text = page.extract_text() or ""
                pages.append(text)
            return "\n".join(pages)
    except Exception:
        return ""


def extract_text_from_docx_bytes(file_bytes):
    if DocxDocument is None:
        return ""
    try:
        doc = DocxDocument(io.BytesIO(file_bytes))
        paragraphs = [
            p.text for p in doc.paragraphs if p.text and p.text.strip()]
        return "\n".join(paragraphs)
    except Exception:
        return ""


def extract_text_from_uploaded_cv(file_obj):
    if file_obj is None:
        return ""

    try:
        if hasattr(file_obj, "file") and file_obj.file is not None:
            source = file_obj.file
            try:
                source.seek(0)
            except Exception:
                pass
            file_bytes = source.read()
        elif hasattr(file_obj, "read"):
            try:
                file_obj.seek(0)
            except Exception:
                pass
            file_bytes = file_obj.read()
        elif isinstance(file_obj, (bytes, bytearray)):
            file_bytes = bytes(file_obj)
        else:
            file_bytes = b""
    except Exception:
        return ""

    file_name = getattr(file_obj, "name", "") or ""
    lower_name = file_name.lower()

    if lower_name.endswith(".pdf"):
        return extract_text_from_pdf_bytes(file_bytes)
    if lower_name.endswith(".docx") or lower_name.endswith(".doc"):
        return extract_text_from_docx_bytes(file_bytes)
    if lower_name.endswith((".txt", ".md", ".csv", ".rtf")):
        return decode_file_bytes(file_bytes)

    if file_bytes.startswith(b"%PDF"):
        return extract_text_from_pdf_bytes(file_bytes)
    if file_bytes.startswith(b"PK"):
        return extract_text_from_docx_bytes(file_bytes)

    return decode_file_bytes(file_bytes)


def extract_years(value):
    if not value:
        return 0
    matches = re.findall(r"(\d+)\+?\s*(?:years?|yrs?)", str(value).lower())
    if matches:
        return int(matches[0])
    matches = re.findall(r"(\d+)\+?\s*(?:months?)", str(value).lower())
    if matches:
        return round(int(matches[0]) / 12, 1)
    return 0


def score_application(application):
    job = application.job_posting
    candidate = application.candidate

    cv_text = extract_text_from_uploaded_cv(application.attached_cv)
    candidate_profile_text = " ".join(
        chunk for chunk in [
            candidate.about,
            candidate.candidate_skills,
            candidate.candidate_name,
            cv_text,
            job.job_description,
            job.required_skills,
        ] if chunk
    )

    required_skills = [canonicalize_skill_token(token)
                       for token in normalize_tokens(job.required_skills)]
    required_skills = sorted({skill for skill in required_skills if skill})

    candidate_skill_surface = " ".join([
        candidate.about or "",
        candidate.candidate_skills or "",
        cv_text or "",
        job.job_description or "",
    ])
    candidate_skill_tokens = [
        canonicalize_skill_token(token)
        for token in normalize_tokens(candidate_skill_surface)
    ]
    candidate_skill_tokens = sorted(
        {skill for skill in candidate_skill_tokens if skill})

    skill_matches = extract_skill_matches(
        required_skills, candidate_skill_surface)
    if not skill_matches:
        skill_matches = sorted(
            set(required_skills).intersection(candidate_skill_tokens))
    skill_score = 0
    if required_skills:
        skill_score = round((len(skill_matches) / len(required_skills)) * 100)
    skill_score = max(0, min(100, skill_score))

    experience_text = " ".join([
        candidate.about or "",
        cv_text or "",
        job.required_experience or "",
    ])
    required_experience = extract_years(job.required_experience)
    candidate_experience = extract_years(experience_text)
    if required_experience:
        experience_score = min(100, round(
            (candidate_experience / required_experience) * 100)) if candidate_experience else 35
    else:
        experience_score = 75 if candidate_experience else 50

    education_keywords = [
        "bachelor",
        "bsc",
        "ba",
        "master",
        "msc",
        "mba",
        "phd",
        "degree",
        "diploma",
        "certificate",
        "certification",
    ]

    profile_text = (candidate_profile_text or "").lower()
    education_score = 100 if any(
        keyword in profile_text for keyword in education_keywords) else 50
    if candidate_profile_text and not any(keyword in profile_text for keyword in education_keywords):
        education_score = 60

    overall_score = int(round((skill_score * 0.5) +
                              (experience_score * 0.3) + (education_score * 0.2)))
    overall_score = max(0, min(100, overall_score))

    notes = [
        f"Skills matched {len(skill_matches)} of {len(required_skills) or 1} required skill keywords extracted from the CV and profile.",
        f"Experience assessment based on {candidate_experience or 0} years against the role requirement of {required_experience or 0} years.",
        f"Education signal: {'found in candidate profile or CV' if education_score >= 75 else 'minimal/unclear from candidate profile or CV'}.",
    ]
    breakdown = {
        "overall_score": overall_score,
        "skills_score": skill_score,
        "experience_score": experience_score,
        "education_score": education_score,
        "breakdown_notes": " | ".join(notes),
    }

    application.ats_score = overall_score
    application.score_reasons = breakdown
    application.is_priority = overall_score >= job.cv_score_threshold
    application.save(
        update_fields=["ats_score", "score_reasons", "is_priority", "updated_at"])

    cv_score, _ = CVScore.objects.update_or_create(
        application=application,
        defaults={
            "overall_score": overall_score,
            "skills_score": skill_score,
            "experience_score": experience_score,
            "education_score": education_score,
            "breakdown_notes": breakdown["breakdown_notes"],
        },
    )

    return {
        "overall_score": overall_score,
        "skills_score": skill_score,
        "experience_score": experience_score,
        "education_score": education_score,
        "breakdown_notes": breakdown["breakdown_notes"],
        "is_priority": application.is_priority,
        "cv_score_id": cv_score.id,
    }


STAGE_EMAIL_TEMPLATE_TYPES = {
    Application.Stage.REJECTED: EmailTemplate.TemplateType.REJECTION,
    Application.Stage.SHORTLISTED: EmailTemplate.TemplateType.SHORTLISTED,
    Application.Stage.TEST_SENT: EmailTemplate.TemplateType.TEST_INVITATION,
    Application.Stage.INTERVIEW: EmailTemplate.TemplateType.INTERVIEW_INVITATION,
    Application.Stage.OFFER: EmailTemplate.TemplateType.OFFER,
    Application.Stage.HIRED: EmailTemplate.TemplateType.HIRED,
}

STAGE_FALLBACK_EMAILS = {
    Application.Stage.REJECTED: {
        "subject": "Update on your application",
        "body": "Hi {{candidate_name}},\n\nThank you for your interest in the {{job_title}} role. After careful review, we have decided not to move forward with your application. We appreciate your time and encourage you to apply for future opportunities.\n\nKind regards,\n{{company_name}}",
    },
    Application.Stage.SHORTLISTED: {
        "subject": "You have been shortlisted",
        "body": "Hi {{candidate_name}},\n\nWe are pleased to let you know that your application for {{job_title}} has progressed to the shortlist stage. Our team will be in touch with the next steps soon.\n\nKind regards,\n{{company_name}}",
    },
    Application.Stage.TEST_SENT: {
        "subject": "Assessment invitation",
        "body": "Hi {{candidate_name}},\n\nYou have been invited to complete the assessment for the {{job_title}} role. Please review the instructions and return your submission within the stated deadline.\n\nKind regards,\n{{company_name}}",
    },
    Application.Stage.INTERVIEW: {
        "subject": "Interview invitation",
        "body": "Hi {{candidate_name}},\n\nWe would like to invite you to interview for the {{job_title}} position. Our team will reach out with the scheduling details shortly.\n\nKind regards,\n{{company_name}}",
    },
    Application.Stage.OFFER: {
        "subject": "Offer update",
        "body": "Hi {{candidate_name}},\n\nWe are pleased to share an offer for the {{job_title}} role. Our team will follow up with the formal details and next steps shortly.\n\nKind regards,\n{{company_name}}",
    },
    Application.Stage.HIRED: {
        "subject": "Welcome to the team",
        "body": "Hi {{candidate_name}},\n\nWe are delighted to confirm your appointment for the {{job_title}} role. Welcome to the team, and we look forward to working with you.\n\nKind regards,\n{{company_name}}",
    },
}


def render_email_template(template_text, context):
    return Template(template_text).render(Context(context))


def send_stage_email(application, new_stage, sent_by=None):
    if new_stage not in STAGE_EMAIL_TEMPLATE_TYPES:
        return None

    candidate = application.candidate
    if not candidate.email:
        return None

    template = EmailTemplate.objects.filter(
        is_active=True,
        template_type=STAGE_EMAIL_TEMPLATE_TYPES[new_stage],
    ).order_by("-created_at").first()

    context = {
        "candidate_name": candidate.candidate_name,
        "job_title": application.job_posting.job_title,
        "company_name": "HR-CSS",
        "email": candidate.email,
        "phone": candidate.phone_number or "",
        "stage_label": application.get_stage_display(),
    }

    fallback = STAGE_FALLBACK_EMAILS[new_stage]
    subject = render_email_template(
        template.subject, context) if template else fallback["subject"]
    body = render_email_template(
        template.body, context) if template else render_email_template(fallback["body"], context)

    try:
        send_mail(
            subject=subject,
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[candidate.email],
            fail_silently=False,
        )
        status = CandidateEmailLog.EmailStatus.SUCCESS
        is_sent_successfully = True
        error_message = ""
    except Exception as exc:
        status = CandidateEmailLog.EmailStatus.FAILED
        is_sent_successfully = False
        error_message = str(exc)

    return CandidateEmailLog.objects.create(
        candidate=candidate,
        job_posting=application.job_posting,
        template=template,
        sent_by=sent_by,
        recipient_email=candidate.email,
        subject=subject,
        body=body,
        status=status,
        is_sent_successfully=is_sent_successfully,
        error_message=error_message,
        sent_at=timezone.now(),
    )


def create_job_posting_for_hiring_request(hiring_request):
    existing_posting = hiring_request.job_postings.first()
    if existing_posting:
        return existing_posting

    job_description = (
        f"{hiring_request.reason}\n\n"
        f"Seniority: {hiring_request.seniority}\n"
        f"Required experience: {hiring_request.required_experience}\n"
        f"Required qualifications: {hiring_request.required_qualifications}"
    )

    return JobPosting.objects.create(
        hiring_request=hiring_request,
        department=hiring_request.department,
        job_title=hiring_request.request_title,
        job_description=job_description,
        required_skills=hiring_request.required_qualifications,
        required_experience=hiring_request.required_experience,
        closing_date=None,
        cv_score_threshold=70,
        status=JobPosting.JobStatus.DRAFT,
    )
