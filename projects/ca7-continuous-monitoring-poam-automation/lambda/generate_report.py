import os
import json
import csv
import io
from datetime import datetime, timezone, date
from html import escape

import boto3

dynamodb = boto3.resource("dynamodb")
s3 = boto3.client("s3")

table = dynamodb.Table(os.environ["POAM_TABLE"])
bucket = os.environ["REPORT_BUCKET"]


def is_overdue(item, today):
    due_date_value = item.get("due_date")
    if not due_date_value:
        return False

    try:
        due_date = date.fromisoformat(due_date_value)
    except ValueError:
        return False

    return item.get("status") == "Open" and due_date < today


def increment_count(dictionary, key):
    if key not in dictionary:
        dictionary[key] = 0
    dictionary[key] += 1


def build_count_list(counts):
    if not counts:
        return "<li>No data</li>"

    rows = ""
    for key, value in sorted(counts.items()):
        rows += f"<li><strong>{escape(str(key))}</strong>: {value}</li>"
    return rows


def build_findings_rows(items):
    if not items:
        return """
        <tr>
            <td colspan="10">No findings available.</td>
        </tr>
        """

    rows = ""
    for item in items:
        rows += f"""
        <tr>
            <td>{escape(str(item.get("finding_id", "")))}</td>
            <td>{escape(str(item.get("control_id", "")))}</td>
            <td>{escape(str(item.get("risk_id", "")))}</td>
            <td>{escape(str(item.get("risk_scenario", "")))}</td>
            <td>{escape(str(item.get("resource_type", "")))}</td>
            <td>{escape(str(item.get("resource_id", "")))}</td>
            <td>{escape(str(item.get("severity", "")))}</td>
            <td>{escape(str(item.get("owner", "")))}</td>
            <td>{escape(str(item.get("status", "")))}</td>
            <td>{escape(str(item.get("due_date", "")))}</td>
        </tr>
        """
    return rows


def build_dashboard_html(
    report_date,
    items,
    open_items,
    closed_items,
    overdue_items,
    findings_by_risk,
    findings_by_severity,
    findings_by_owner,
    findings_by_status
):
    findings_rows = build_findings_rows(items)

    risk_list = build_count_list(findings_by_risk)
    severity_list = build_count_list(findings_by_severity)
    owner_list = build_count_list(findings_by_owner)
    status_list = build_count_list(findings_by_status)

    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>CA-7 Continuous Monitoring Dashboard</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 40px;
            color: #1f2937;
            background: #ffffff;
        }}
        h1 {{
            margin-bottom: 4px;
        }}
        .subtitle {{
            color: #6b7280;
            margin-top: 0;
            margin-bottom: 30px;
        }}
        .cards {{
            display: flex;
            gap: 16px;
            flex-wrap: wrap;
            margin-bottom: 30px;
        }}
        .card {{
            border: 1px solid #d1d5db;
            border-radius: 10px;
            padding: 16px;
            min-width: 170px;
            background: #f9fafb;
        }}
        .card .number {{
            font-size: 32px;
            font-weight: bold;
            margin-bottom: 4px;
        }}
        .card .label {{
            color: #4b5563;
            font-size: 14px;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(2, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .panel {{
            border: 1px solid #d1d5db;
            border-radius: 10px;
            padding: 16px;
            background: #ffffff;
        }}
        .panel h2 {{
            margin-top: 0;
            font-size: 18px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 12px;
        }}
        th, td {{
            border: 1px solid #d1d5db;
            padding: 8px;
            text-align: left;
            font-size: 12px;
            vertical-align: top;
        }}
        th {{
            background: #f3f4f6;
        }}
        .note {{
            margin-top: 30px;
            padding: 14px;
            border-left: 4px solid #9ca3af;
            background: #f9fafb;
            color: #4b5563;
            font-size: 14px;
        }}
        .footer {{
            margin-top: 30px;
            color: #6b7280;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <h1>CA-7 Continuous Monitoring Dashboard</h1>
    <p class="subtitle">Risk-based POA&M reporting generated from DynamoDB records. Report date: <strong>{report_date}</strong></p>

    <div class="cards">
        <div class="card">
            <div class="number">{len(items)}</div>
            <div class="label">Total Findings</div>
        </div>
        <div class="card">
            <div class="number">{len(open_items)}</div>
            <div class="label">Open Findings</div>
        </div>
        <div class="card">
            <div class="number">{len(closed_items)}</div>
            <div class="label">Closed Findings</div>
        </div>
        <div class="card">
            <div class="number">{len(overdue_items)}</div>
            <div class="label">Overdue Findings</div>
        </div>
    </div>

    <div class="grid">
        <div class="panel">
            <h2>Findings by Risk</h2>
            <ul>{risk_list}</ul>
        </div>
        <div class="panel">
            <h2>Findings by Severity</h2>
            <ul>{severity_list}</ul>
        </div>
        <div class="panel">
            <h2>Findings by Owner</h2>
            <ul>{owner_list}</ul>
        </div>
        <div class="panel">
            <h2>Findings by Status</h2>
            <ul>{status_list}</ul>
        </div>
    </div>

    <h2>POA&M Findings</h2>
    <table>
        <tr>
            <th>Finding ID</th>
            <th>Control</th>
            <th>Risk ID</th>
            <th>Risk Scenario</th>
            <th>Resource Type</th>
            <th>Resource ID</th>
            <th>Severity</th>
            <th>Owner</th>
            <th>Status</th>
            <th>Due Date</th>
        </tr>
        {findings_rows}
    </table>

    <div class="note">
        <strong>Control context:</strong> This dashboard supports CA-7 continuous monitoring by summarizing detected findings,
        mapped risk scenarios, POA&M ownership, remediation status, and reporting evidence.
    </div>

    <div class="footer">
        Generated by the CA-7 reporting Lambda. Source: DynamoDB POA&M table.
    </div>
</body>
</html>
"""


def lambda_handler(event, context):
    now = datetime.now(timezone.utc)
    today = now.date()
    report_date = today.isoformat()

    response = table.scan()
    items = response.get("Items", [])

    while "LastEvaluatedKey" in response:
        response = table.scan(ExclusiveStartKey=response["LastEvaluatedKey"])
        items.extend(response.get("Items", []))

    open_items = []
    closed_items = []
    overdue_items = []

    findings_by_risk = {}
    findings_by_severity = {}
    findings_by_owner = {}
    findings_by_status = {}

    for item in items:
        status = item.get("status", "Unknown")
        risk_id = item.get("risk_id", "Unknown")
        severity = item.get("severity", "Unknown")
        owner = item.get("owner", "Unknown")

        increment_count(findings_by_risk, risk_id)
        increment_count(findings_by_severity, severity)
        increment_count(findings_by_owner, owner)
        increment_count(findings_by_status, status)

        if status == "Open":
            open_items.append(item)

        if status == "Closed":
            closed_items.append(item)

        if is_overdue(item, today):
            overdue_items.append(item)

    summary = {
        "control_id": "CA-7",
        "report_date": report_date,
        "total_findings": len(items),
        "open_findings": len(open_items),
        "closed_findings": len(closed_items),
        "overdue_findings": len(overdue_items),
        "findings_by_risk": findings_by_risk,
        "findings_by_severity": findings_by_severity,
        "findings_by_owner": findings_by_owner,
        "findings_by_status": findings_by_status,
        "findings": items
    }

    json_key = f"ca7/reports/{report_date}/ca7-poam-report.json"
    csv_key = f"ca7/reports/{report_date}/ca7-poam-report.csv"
    html_key = f"ca7/reports/{report_date}/ca7-dashboard.html"

    s3.put_object(
        Bucket=bucket,
        Key=json_key,
        Body=json.dumps(summary, indent=2, default=str),
        ContentType="application/json"
    )

    csv_buffer = io.StringIO()
    fieldnames = [
        "finding_id",
        "control_id",
        "risk_id",
        "risk_scenario",
        "source",
        "config_rule_name",
        "resource_type",
        "resource_id",
        "severity",
        "likelihood",
        "impact",
        "inherent_risk",
        "residual_risk",
        "risk_response",
        "owner",
        "status",
        "poam_status",
        "detected_date",
        "due_date",
        "last_updated",
        "remediation_plan"
    ]

    writer = csv.DictWriter(csv_buffer, fieldnames=fieldnames)
    writer.writeheader()

    for item in items:
        writer.writerow({field: item.get(field, "") for field in fieldnames})

    s3.put_object(
        Bucket=bucket,
        Key=csv_key,
        Body=csv_buffer.getvalue(),
        ContentType="text/csv"
    )

    html = build_dashboard_html(
        report_date,
        items,
        open_items,
        closed_items,
        overdue_items,
        findings_by_risk,
        findings_by_severity,
        findings_by_owner,
        findings_by_status
    )

    s3.put_object(
        Bucket=bucket,
        Key=html_key,
        Body=html,
        ContentType="text/html"
    )

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "CA-7 report and dashboard generated",
            "json_report": json_key,
            "csv_report": csv_key,
            "html_dashboard": html_key,
            "total_findings": len(items),
            "open_findings": len(open_items),
            "closed_findings": len(closed_items),
            "overdue_findings": len(overdue_items)
        })
    }
