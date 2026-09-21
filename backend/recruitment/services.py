import re

from django.template import Context, Template

from recruitment.models import CVScore, JobPosting


def normalize_bool(value):
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    return str(value).strip().lower() in {"1", "true", "yes", "y", "on"}


def normalize_tokens(value):
    if not value:
        return []
    return re.findall(r"[a-zA-Z0-9+#.]+", str(value).lower())


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

    required_skills = normalize_tokens(job.required_skills)
    candidate_skills = normalize_tokens(candidate.candidate_skills)
    candidate_profile_text = normalize_tokens(
        f"{candidate.about} {candidate.candidate_name}")
    skill_matches = sorted(
        {token for token in required_skills if token in candidate_skills or token in candidate_profile_text}
    )
    skill_score = 0
    if required_skills:
        skill_score = round((len(skill_matches) / len(required_skills)) * 100)
    skill_score = max(0, min(100, skill_score))

    required_experience = extract_years(job.required_experience)
    candidate_experience = extract_years(candidate.about)
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
    profile_text = (candidate.about or "").lower()
    education_score = 100 if any(
        keyword in profile_text for keyword in education_keywords) else 50
    if candidate.about and not any(keyword in profile_text for keyword in education_keywords):
        education_score = 60

    overall_score = int(round((skill_score * 0.5) +
                              (experience_score * 0.3) + (education_score * 0.2)))
    overall_score = max(0, min(100, overall_score))

    notes = [
        f"Skills matched {len(skill_matches)} of {len(required_skills) or 1} required skill keywords.",
        f"Experience assessment based on {candidate_experience or 0} years against the role requirement of {required_experience or 0} years.",
        f"Education signal: {'found in candidate profile' if education_score >= 75 else 'minimal/unclear from candidate profile'}.",
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


def render_email_template(template_text, context):
    return Template(template_text).render(Context(context))


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
