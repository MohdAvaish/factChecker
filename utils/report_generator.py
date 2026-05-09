"""
report_generator.py – Generate CSV, JSON, and PDF reports.
"""

import json
import io
import pandas as pd

from typing import List, Dict, Any

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus.flowables import HRFlowable


# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────

def _flatten_result(result: Dict[str, Any]) -> Dict[str, Any]:

    sources = result.get("sources", [])

    return {
        "claim_index":
            result.get("index", "") + 1
            if isinstance(result.get("index"), int)
            else "",

        "claim": result.get("claim", ""),

        "verdict": result.get("status", ""),

        "correct_fact": result.get("correct_fact", ""),

        "explanation": result.get("explanation", ""),

        "source_1":
            sources[0] if len(sources) > 0 else "",

        "source_2":
            sources[1] if len(sources) > 1 else "",

        "source_3":
            sources[2] if len(sources) > 2 else "",
    }


# ─────────────────────────────────────────────────────────────
# CSV
# ─────────────────────────────────────────────────────────────

def generate_csv(results: List[Dict[str, Any]]) -> bytes:

    rows = [_flatten_result(r) for r in results]

    df = pd.DataFrame(rows)

    output = io.BytesIO()

    df.to_csv(
        output,
        index=False,
        encoding="utf-8"
    )

    return output.getvalue()


# ─────────────────────────────────────────────────────────────
# JSON
# ─────────────────────────────────────────────────────────────

def generate_json(results: List[Dict[str, Any]]) -> str:

    export = []

    for r in results:

        export.append(
            {
                "claim_index":
                    r.get("index", 0) + 1
                    if isinstance(r.get("index"), int)
                    else 0,

                "claim":
                    r.get("claim", ""),

                "verdict":
                    r.get("status", ""),

                "correct_fact":
                    r.get("correct_fact", ""),

                "explanation":
                    r.get("explanation", ""),

                "sources":
                    r.get("sources", []),
            }
        )

    return json.dumps(
        export,
        indent=2,
        ensure_ascii=False
    )


# ─────────────────────────────────────────────────────────────
# PDF REPORT
# ─────────────────────────────────────────────────────────────

def generate_pdf(results: List[Dict[str, Any]]) -> bytes:
    """
    Generate an attractive PDF report.
    """

    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=50,
        bottomMargin=40,
    )

    styles = getSampleStyleSheet()

    elements = []

    # ── Title ─────────────────────────

    title = Paragraph(
        "<font size=24><b>Fact-Check Report</b></font>",
        styles["Title"]
    )

    subtitle = Paragraph(
        "AI-Powered Automated Verification Results",
        styles["Heading2"]
    )

    elements.extend([
        title,
        Spacer(1, 10),
        subtitle,
        Spacer(1, 20),
    ])

    # ── Summary Stats ─────────────────

    counts = {
        "Verified": 0,
        "Inaccurate": 0,
        "False": 0,
        "Not Enough Evidence": 0
    }

    for r in results:
        status = r.get("status", "Not Enough Evidence")
        counts[status] = counts.get(status, 0) + 1

    summary_data = [
        ["Category", "Count"],
        ["Verified", counts["Verified"]],
        ["Inaccurate", counts["Inaccurate"]],
        ["False", counts["False"]],
        ["Not Enough Evidence", counts["Not Enough Evidence"]],
        ["Total Claims", len(results)],
    ]

    summary_table = Table(
        summary_data,
        colWidths=[250, 120]
    )

    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#222222")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 1, colors.grey),
        ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
    ]))

    elements.append(summary_table)

    elements.append(Spacer(1, 25))

    # ── Detailed Claims ───────────────

    for i, r in enumerate(results, 1):

        status = r.get("status", "Unknown")

        # Verdict color
        if status == "Verified":
            verdict_color = "#15803d"

        elif status == "Inaccurate":
            verdict_color = "#b45309"

        elif status == "False":
            verdict_color = "#b91c1c"

        else:
            verdict_color = "#1d4ed8"

        header = Paragraph(
            f"""
            <font size=16>
            <b>Claim {i}</b>
            </font>
            """,
            styles["Heading2"]
        )

        claim = Paragraph(
            f"""
            <b>Claim:</b><br/>
            {r.get("claim", "")}
            """,
            styles["BodyText"]
        )

        verdict = Paragraph(
            f"""
            <b>Verdict:</b>
            <font color="{verdict_color}">
            {status}
            </font>
            """,
            styles["BodyText"]
        )

        correct_fact = Paragraph(
            f"""
            <b>Correct Fact:</b><br/>
            {r.get("correct_fact", "")}
            """,
            styles["BodyText"]
        )

        explanation = Paragraph(
            f"""
            <b>Explanation:</b><br/>
            {r.get("explanation", "")}
            """,
            styles["BodyText"]
        )

        sources_html = "<br/>".join(
            r.get("sources", [])
        )

        sources = Paragraph(
            f"""
            <b>Sources:</b><br/>
            {sources_html}
            """,
            styles["BodyText"]
        )

        elements.extend([
            header,
            Spacer(1, 6),
            claim,
            Spacer(1, 6),
            verdict,
            Spacer(1, 6),
            correct_fact,
            Spacer(1, 6),
            explanation,
            Spacer(1, 6),
            sources,
            Spacer(1, 12),
            HRFlowable(width="100%"),
            Spacer(1, 14),
        ])

    # ── Footer ────────────────────────

    footer = Paragraph(
        """
        <font size=9 color="#666666">
        Generated by Fact-Check Agent using DeepSeek + Tavily + Streamlit
        </font>
        """,
        styles["BodyText"]
    )

    elements.append(Spacer(1, 20))
    elements.append(footer)

    doc.build(elements)

    pdf = buffer.getvalue()

    buffer.close()

    return pdf