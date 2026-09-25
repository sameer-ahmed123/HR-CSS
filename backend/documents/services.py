from io import BytesIO

from django.template import Context, Template
from django.utils import timezone
from xhtml2pdf import pisa

from documents.models import DocumentRequest


def generate_reference_number(document_request):
    """Generate a persistent document reference number."""
    base_prefix = "DOC"
    year = timezone.now().strftime("%Y")
    prefix = f"{base_prefix}-{year}"
    count = DocumentRequest.objects.filter(
        reference_number__startswith=f"{prefix}-").count() + 1
    return f"{prefix}-{count:05d}"


def get_document_context(document_request):
    """Build the replacement context used by the document template."""
    user = getattr(document_request, "requested_by", None)

    employee_name = "N/A"
    if user is not None:
        employee_name = user.get_full_name() or getattr(
            user, "username", None) or getattr(user, "email", "N/A") or "N/A"

    designation = getattr(user, "role",
                          None) or getattr(user, "designation", None)
    if isinstance(designation, str):
        designation_value = designation
    elif designation is not None and hasattr(designation, "title"):
        designation_value = designation.title
    elif designation is not None:
        designation_value = str(designation)
    else:
        designation_value = "N/A"

    department = getattr(user, "department", None)
    if department is not None and hasattr(department, "name"):
        department_value = department.name
    elif department is not None:
        department_value = str(department)
    else:
        department_value = "N/A"

    salary = getattr(user, "salary", None) or getattr(
        user, "monthly_salary", None)
    if salary in (None, ""):
        salary_value = "N/A"
    elif isinstance(salary, (int, float)):
        salary_value = f"Rs. {salary:,.2f}"
    else:
        salary_value = str(salary)

    if not getattr(document_request, "reference_number", None):
        document_request.reference_number = generate_reference_number(
            document_request)
        document_request.save(update_fields=["reference_number"])

    context = {
        "{{employee_name}}": employee_name,
        "{{employee_email}}": getattr(user, "email", "N/A") or "N/A",
        "{{designation}}": designation_value,
        "{{department}}": department_value,
        "{{salary}}": salary_value,
        "{{monthly_salary}}": salary_value,
        "{{issue_date}}": timezone.now().date().strftime("%B %d, %Y"),
        "{{reference_number}}": getattr(document_request, "reference_number", "N/A"),
        "{{purpose}}": getattr(document_request, "purpose", "N/A") or "N/A",
    }
    return context


def render_template_to_html(template_body, context_data):
    """Render a Django HTML template with the provided replacement data."""
    if template_body is None:
        template_body = ""

    normalized_context = {}
    for key, value in (context_data or {}).items():
        normalized_key = str(key).strip()
        if normalized_key.startswith("{{") and normalized_key.endswith("}}"):
            normalized_key = normalized_key[2:-2].strip()
        normalized_context[normalized_key] = value

    rendered_html = Template(str(template_body)).render(
        Context(normalized_context))
    return rendered_html


def generate_pdf_from_html(html_content, include_letterhead=True):
    """Convert an HTML string into a PDF using xhtml2pdf and return a BytesIO object."""
    document_html = html_content or ""

    letterhead_block = ""
    if include_letterhead:
        letterhead_block = """
        <div class=\"letterhead\">
            <h1>HR Document Portal</h1>
            <p>Official Human Resources Documentation</p>
        </div>
        """

    wrapped_html = f"""
    <!DOCTYPE html>
    <html lang=\"en\">
    <head>
        <meta charset=\"utf-8\" />
        <style>
            @page {{
                size: A4;
                margin: 0.75in 0.75in 0.9in 0.75in;
            }}
            body {{
                font-family: Helvetica, Arial, sans-serif;
                font-size: 12px;
                line-height: 1.7;
                color: #1f2937;
                margin: 0;
                background-color: #ffffff;
            }}
            .document-page {{
                width: 100%;
                box-sizing: border-box;
            }}
            .letterhead {{
                border-bottom: 2px solid #1f3a5f;
                margin-bottom: 24px;
                padding-bottom: 10px;
            }}
            .letterhead h1 {{
                margin: 0;
                color: #1f3a5f;
                font-size: 28px;
                font-weight: bold;
            }}
            .letterhead p {{
                margin: 6px 0 0;
                color: #4b5563;
                font-size: 11px;
                letter-spacing: 0.08em;
                text-transform: uppercase;
            }}
            .document-body {{
                color: #1f2937;
            }}
            .document-footer {{
                border-top: 1px solid #d1d5db;
                margin-top: 32px;
                padding-top: 10px;
                font-size: 10px;
                color: #6b7280;
                text-align: center;
            }}
        </style>
    </head>
    <body>
        <div class=\"document-page\">
            {letterhead_block}
            <div class=\"document-body\">{document_html}</div>
            <div class=\"document-footer\">Generated by HR Document Portal</div>
        </div>
    </body>
    </html>
    """

    pdf_buffer = BytesIO()
    result = pisa.CreatePDF(
        BytesIO(wrapped_html.encode("utf-8")),
        dest=pdf_buffer,
    )

    if result.err:
        raise ValueError(f"Unable to generate PDF: {result.err}")

    pdf_buffer.seek(0)
    return pdf_buffer
