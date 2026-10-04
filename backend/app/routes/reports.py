from io import BytesIO
import csv

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)

from app.database import get_db
from app.models.user import User
from app.models.incident import Incident
from app.models.alert import Alert
from app.models.security_event import SecurityEvent

from app.security.jwt import get_current_user
from app.security.rate_limit import rate_limit


router = APIRouter(
    prefix="/reports",
    tags=["Security Reports"],
    dependencies=[Depends(rate_limit)]
)


# =========================================================
# REPORT SUMMARY
# =========================================================

@router.get("/summary")
def report_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    total_events = db.query(SecurityEvent).count()
    total_incidents = db.query(Incident).count()
    total_alerts = db.query(Alert).count()

    # -------------------------
    # INCIDENT STATUS
    # -------------------------

    open_incidents = (
        db.query(Incident)
        .filter(
            Incident.status == "open"
        )
        .count()
    )

    investigating_incidents = (
        db.query(Incident)
        .filter(
            Incident.status == "investigating"
        )
        .count()
    )

    resolved_incidents = (
        db.query(Incident)
        .filter(
            Incident.status.in_(
                ["resolved", "closed"]
            )
        )
        .count()
    )

    # -------------------------
    # INCIDENT SEVERITY
    # -------------------------

    critical_incidents = (
        db.query(Incident)
        .filter(
            Incident.severity == "critical"
        )
        .count()
    )

    high_incidents = (
        db.query(Incident)
        .filter(
            Incident.severity == "high"
        )
        .count()
    )

    medium_incidents = (
        db.query(Incident)
        .filter(
            Incident.severity == "medium"
        )
        .count()
    )

    low_incidents = (
        db.query(Incident)
        .filter(
            Incident.severity == "low"
        )
        .count()
    )

    # -------------------------
    # ALERT STATUS
    # -------------------------

    new_alerts = (
        db.query(Alert)
        .filter(
            Alert.status == "new"
        )
        .count()
    )

    acknowledged_alerts = (
        db.query(Alert)
        .filter(
            Alert.status == "acknowledged"
        )
        .count()
    )

    resolved_alerts = (
        db.query(Alert)
        .filter(
            Alert.status == "resolved"
        )
        .count()
    )

    return {
        "report": "SentinelX Security Report",
        "generated_for": current_user.username,

        "total_security_events": total_events,
        "total_incidents": total_incidents,
        "total_alerts": total_alerts,

        "incident_status": {
            "open": open_incidents,
            "investigating": investigating_incidents,
            "resolved_or_closed": resolved_incidents
        },

        "incident_severity": {
            "critical": critical_incidents,
            "high": high_incidents,
            "medium": medium_incidents,
            "low": low_incidents
        },

        "alert_status": {
            "new": new_alerts,
            "acknowledged": acknowledged_alerts,
            "resolved": resolved_alerts
        }
    }


# =========================================================
# CSV REPORT
# =========================================================

@router.get("/csv")
def export_csv(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    incidents = (
        db.query(Incident)
        .order_by(
            Incident.created_at.desc()
        )
        .all()
    )

    string_buffer = BytesIO()

    header = [
        "Incident ID",
        "Title",
        "Incident Type",
        "Detection Rule",
        "Source IP",
        "IOC Type",
        "IOC Value",
        "Event ID",
        "Username",
        "Severity",
        "Risk Score",
        "Status",
        "Assigned To",
        "Created At",
        "Updated At"
    ]

    # csv.writer needs a text stream,
    # so create the CSV using StringIO.
    import io

    text_buffer = io.StringIO()

    writer = csv.writer(
        text_buffer
    )

    writer.writerow(header)

    for incident in incidents:

        writer.writerow([
            incident.id,
            incident.title or "",
            incident.incident_type or "",
            incident.detection_rule or "",
            incident.source_ip or "",
            incident.ioc_type or "",
            incident.ioc_value or "",
            incident.event_id or "",
            incident.username or "",
            incident.severity or "",
            incident.risk_score or 0,
            incident.status or "",
            incident.assigned_to or "",
            (
                incident.created_at.isoformat()
                if incident.created_at
                else ""
            ),
            (
                incident.updated_at.isoformat()
                if incident.updated_at
                else ""
            )
        ])

    csv_data = (
        text_buffer
        .getvalue()
        .encode("utf-8")
    )

    string_buffer.write(
        csv_data
    )

    string_buffer.seek(0)

    return StreamingResponse(
        string_buffer,
        media_type="text/csv",
        headers={
            "Content-Disposition":
                "attachment; "
                "filename=sentinelx_security_report.csv"
        }
    )


# =========================================================
# PDF REPORT
# =========================================================

@router.get("/pdf")
def export_pdf(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    incidents = (
        db.query(Incident)
        .order_by(
            Incident.created_at.desc()
        )
        .all()
    )

    total_events = (
        db.query(SecurityEvent).count()
    )

    total_incidents = (
        db.query(Incident).count()
    )

    total_alerts = (
        db.query(Alert).count()
    )

    critical_incidents = (
        db.query(Incident)
        .filter(
            Incident.severity == "critical"
        )
        .count()
    )

    high_incidents = (
        db.query(Incident)
        .filter(
            Incident.severity == "high"
        )
        .count()
    )

    medium_incidents = (
        db.query(Incident)
        .filter(
            Incident.severity == "medium"
        )
        .count()
    )

    low_incidents = (
        db.query(Incident)
        .filter(
            Incident.severity == "low"
        )
        .count()
    )

    open_incidents = (
        db.query(Incident)
        .filter(
            Incident.status == "open"
        )
        .count()
    )

    investigating_incidents = (
        db.query(Incident)
        .filter(
            Incident.status == "investigating"
        )
        .count()
    )

    resolved_incidents = (
        db.query(Incident)
        .filter(
            Incident.status.in_(
                ["resolved", "closed"]
            )
        )
        .count()
    )

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=15 * mm,
        leftMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm
    )

    styles = getSampleStyleSheet()

    title_style = styles["Title"]
    heading_style = styles["Heading2"]
    normal_style = styles["BodyText"]

    story = []

    # -------------------------
    # TITLE
    # -------------------------

    story.append(
        Paragraph(
            "SentinelX Security Report",
            title_style
        )
    )

    story.append(
        Spacer(1, 8)
    )

    story.append(
        Paragraph(
            f"Generated for: "
            f"{current_user.username}",
            normal_style
        )
    )

    story.append(
        Spacer(1, 15)
    )

    # -------------------------
    # SECURITY SUMMARY
    # -------------------------

    story.append(
        Paragraph(
            "Security Summary",
            heading_style
        )
    )

    summary_data = [
        ["Metric", "Count"],
        [
            "Security Events",
            str(total_events)
        ],
        [
            "Incidents",
            str(total_incidents)
        ],
        [
            "Alerts",
            str(total_alerts)
        ],
        [
            "High/Critical Incidents",
            str(
                high_incidents
                + critical_incidents
            )
        ]
    ]

    summary_table = Table(
        summary_data,
        colWidths=[
            90 * mm,
            40 * mm
        ]
    )

    summary_table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.grey
            ),
            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.white
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.black
            ),
            (
                "ALIGN",
                (1, 1),
                (-1, -1),
                "CENTER"
            ),
            (
                "PADDING",
                (0, 0),
                (-1, -1),
                6
            )
        ])
    )

    story.append(
        summary_table
    )

    story.append(
        Spacer(1, 15)
    )

    # -------------------------
    # INCIDENT STATUS
    # -------------------------

    story.append(
        Paragraph(
            "Incident Status",
            heading_style
        )
    )

    status_data = [
        ["Status", "Count"],
        ["Open", str(open_incidents)],
        [
            "Investigating",
            str(investigating_incidents)
        ],
        [
            "Resolved / Closed",
            str(resolved_incidents)
        ]
    ]

    status_table = Table(
        status_data,
        colWidths=[
            90 * mm,
            40 * mm
        ]
    )

    status_table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.grey
            ),
            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.white
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.black
            ),
            (
                "ALIGN",
                (1, 1),
                (-1, -1),
                "CENTER"
            ),
            (
                "PADDING",
                (0, 0),
                (-1, -1),
                6
            )
        ])
    )

    story.append(
        status_table
    )

    story.append(
        Spacer(1, 15)
    )

    # -------------------------
    # INCIDENT SEVERITY
    # -------------------------

    story.append(
        Paragraph(
            "Incident Severity",
            heading_style
        )
    )

    severity_data = [
        ["Severity", "Count"],
        [
            "Critical",
            str(critical_incidents)
        ],
        [
            "High",
            str(high_incidents)
        ],
        [
            "Medium",
            str(medium_incidents)
        ],
        [
            "Low",
            str(low_incidents)
        ]
    ]

    severity_table = Table(
        severity_data,
        colWidths=[
            90 * mm,
            40 * mm
        ]
    )

    severity_table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.grey
            ),
            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.white
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.black
            ),
            (
                "ALIGN",
                (1, 1),
                (-1, -1),
                "CENTER"
            ),
            (
                "PADDING",
                (0, 0),
                (-1, -1),
                6
            )
        ])
    )

    story.append(
        severity_table
    )

    story.append(
        Spacer(1, 15)
    )

    # -------------------------
    # INCIDENT DETAILS
    # -------------------------

    story.append(
        Paragraph(
            "Incident Details",
            heading_style
        )
    )

    data = [
        [
            "ID",
            "Title",
            "Rule",
            "Severity",
            "Risk",
            "Status"
        ]
    ]

    for incident in incidents:

        title = (
            incident.title
            or "-"
        )

        title = title[:30]

        data.append([
            str(incident.id),
            title,
            (
                incident.detection_rule
                or "-"
            ),
            (
                incident.severity
                or "-"
            ),
            str(
                incident.risk_score
                or 0
            ),
            (
                incident.status
                or "-"
            )
        ])

    incident_table = Table(
        data,
        colWidths=[
            12 * mm,
            55 * mm,
            38 * mm,
            22 * mm,
            15 * mm,
            25 * mm
        ],
        repeatRows=1
    )

    incident_table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.grey
            ),
            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.white
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.4,
                colors.black
            ),
            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                7
            ),
            (
                "PADDING",
                (0, 0),
                (-1, -1),
                4
            ),
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "TOP"
            )
        ])
    )

    story.append(
        incident_table
    )

    story.append(
        Spacer(1, 15)
    )

    story.append(
        Paragraph(
            "Report generated by SentinelX "
            "Security Monitoring Platform.",
            normal_style
        )
    )

    document.build(
        story
    )

    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
                "attachment; "
                "filename=sentinelx_security_report.pdf"
        }
    )