import json
from pathlib import Path

STATE_FILE = Path("evidence/lab-2-3/state.json")
REPORT_FILE = Path("reports/aws-s3-control-results.md")

REQUIRED_TAGS = ["Project", "Environment", "ManagedBy", "ComplianceScope"]


def load_state():
    with STATE_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def get_resources(state):
    root_module = state.get("values", {}).get("root_module", {})
    return root_module.get("resources", [])


def find_resource(resources, resource_type, resource_name):
    for resource in resources:
        if resource.get("type") == resource_type and resource.get("name") == resource_name:
            return resource
    return None


def pass_fail(condition):
    return "Pass" if condition else "Fail"


def evaluate_controls():
    state = load_state()
    resources = get_resources(state)

    primary_bucket = find_resource(resources, "aws_s3_bucket", "primary")
    encryption = find_resource(resources, "aws_s3_bucket_server_side_encryption_configuration", "primary")
    public_access = find_resource(resources, "aws_s3_bucket_public_access_block", "primary")
    versioning = find_resource(resources, "aws_s3_bucket_versioning", "primary")
    logging = find_resource(resources, "aws_s3_bucket_logging", "primary")
    log_bucket_encryption = find_resource(resources, "aws_s3_bucket_server_side_encryption_configuration", "log")
    log_bucket_public_access = find_resource(resources, "aws_s3_bucket_public_access_block", "log")

    results = []

    # CGE-S3-01 / SC-28 Encryption at Rest
    encryption_algorithm = "Not found"
    encryption_pass = False
    if encryption:
        rules = encryption.get("values", {}).get("rule", [])
        if rules:
            default_encryption = rules[0].get("apply_server_side_encryption_by_default", [])
            if default_encryption:
                encryption_algorithm = default_encryption[0].get("sse_algorithm", "Not found")
                encryption_pass = encryption_algorithm == "AES256"

    results.append({
        "control_id": "CGE-S3-01",
        "framework": "NIST SC-28 / ISO A.8.24 / SOC 2 CC6.1, CC6.7",
        "control": "Encryption at Rest",
        "expected": "S3 bucket uses AES256 server-side encryption",
        "actual": encryption_algorithm,
        "status": pass_fail(encryption_pass),
        "finding": "" if encryption_pass else "Primary S3 bucket encryption is missing or not AES256."
    })

    # CGE-S3-02 / AC-3 Public Access Restriction
    public_values = public_access.get("values", {}) if public_access else {}
    public_checks = {
        "block_public_acls": public_values.get("block_public_acls"),
        "ignore_public_acls": public_values.get("ignore_public_acls"),
        "block_public_policy": public_values.get("block_public_policy"),
        "restrict_public_buckets": public_values.get("restrict_public_buckets"),
    }
    public_pass = all(value is True for value in public_checks.values())

    results.append({
        "control_id": "CGE-S3-02",
        "framework": "NIST AC-3 / ISO A.5.15, A.8.3 / SOC 2 CC6.1, CC6.6, CC6.7",
        "control": "Public Access Restriction",
        "expected": "All four S3 public access block settings are true",
        "actual": ", ".join([f"{key}={value}" for key, value in public_checks.items()]),
        "status": pass_fail(public_pass),
        "finding": "" if public_pass else "One or more S3 public access block settings are not enabled."
    })

    # CGE-S3-03 / CM-6 Required Tags
    tags = primary_bucket.get("values", {}).get("tags_all", {}) if primary_bucket else {}
    missing_tags = [tag for tag in REQUIRED_TAGS if tag not in tags]
    tags_pass = len(missing_tags) == 0

    results.append({
        "control_id": "CGE-S3-03",
        "framework": "NIST CM-6 / ISO A.5.9, A.8.9 / SOC 2 CC7.1, CC8.1",
        "control": "Secure Configuration Tags",
        "expected": "Required tags are present: Project, Environment, ManagedBy, ComplianceScope",
        "actual": "Present" if tags_pass else f"Missing: {', '.join(missing_tags)}",
        "status": pass_fail(tags_pass),
        "finding": "" if tags_pass else "One or more required compliance tags are missing."
    })

    # CGE-S3-04 / CM-6 Versioning
    versioning_status = "Not found"
    versioning_pass = False
    if versioning:
        config = versioning.get("values", {}).get("versioning_configuration", [])
        if config:
            versioning_status = config[0].get("status", "Not found")
            versioning_pass = versioning_status == "Enabled"

    results.append({
        "control_id": "CGE-S3-04",
        "framework": "NIST CM-6 / ISO A.8.13, A.8.9 / SOC 2 CC7.3, A1.2",
        "control": "Versioning",
        "expected": "S3 bucket versioning is Enabled",
        "actual": versioning_status,
        "status": pass_fail(versioning_pass),
        "finding": "" if versioning_pass else "Primary S3 bucket versioning is not enabled."
    })

    # CGE-S3-05 / AU-3, AU-6 Access Logging
    logging_values = logging.get("values", {}) if logging else {}
    target_bucket = logging_values.get("target_bucket", "Not found")
    target_prefix = logging_values.get("target_prefix", "Not found")
    logging_pass = logging is not None and target_bucket != "Not found"

    results.append({
        "control_id": "CGE-S3-05",
        "framework": "NIST AU-3, AU-6 / ISO A.8.15, A.8.16 / SOC 2 CC7.2, CC7.3, CC7.4",
        "control": "Access Logging",
        "expected": "Primary S3 bucket sends access logs to a dedicated log bucket",
        "actual": f"target_bucket={target_bucket}, target_prefix={target_prefix}",
        "status": pass_fail(logging_pass),
        "finding": "" if logging_pass else "Primary S3 bucket access logging is not configured."
    })

    # CGE-S3-06 / Log Bucket Protection
    log_encryption_pass = log_bucket_encryption is not None
    log_public_values = log_bucket_public_access.get("values", {}) if log_bucket_public_access else {}
    log_public_pass = all([
        log_public_values.get("block_public_acls") is True,
        log_public_values.get("ignore_public_acls") is True,
        log_public_values.get("block_public_policy") is True,
        log_public_values.get("restrict_public_buckets") is True,
    ])
    log_bucket_pass = log_encryption_pass and log_public_pass

    results.append({
        "control_id": "CGE-S3-06",
        "framework": "NIST AU-9, SC-28, AC-3 / ISO A.8.15, A.8.24, A.5.15 / SOC 2 CC6.1, CC6.7, CC7.2",
        "control": "Log Bucket Protection",
        "expected": "Log bucket is encrypted and public access is blocked",
        "actual": f"encryption_configured={log_encryption_pass}, public_access_blocked={log_public_pass}",
        "status": pass_fail(log_bucket_pass),
        "finding": "" if log_bucket_pass else "Log bucket encryption or public access protection is incomplete."
    })

    return results


def write_report(results):
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)

    total = len(results)
    passed = sum(1 for result in results if result["status"] == "Pass")
    failed = total - passed

    lines = [
        "# AWS S3 Control Evaluation Report",
        "",
        "This report summarizes automated control evaluation results from the Terraform state evidence file.",
        "",
        "## Summary",
        "",
        f"- Total controls evaluated: {total}",
        f"- Passed: {passed}",
        f"- Failed: {failed}",
        "",
        "## Control Results",
        "",
        "| Control ID | Framework Mapping | Control | Expected | Actual | Status |",
        "|---|---|---|---|---|---|",
    ]

    for result in results:
        lines.append(
            f"| {result['control_id']} | {result['framework']} | {result['control']} | "
            f"{result['expected']} | {result['actual']} | {result['status']} |"
        )

    findings = [result for result in results if result["status"] == "Fail"]

    lines.extend(["", "## Findings", ""])

    if not findings:
        lines.append("No findings identified. All evaluated controls passed.")
    else:
        for finding in findings:
            lines.extend([
                f"### {finding['control_id']} — {finding['control']}",
                "",
                f"**Finding:** {finding['finding']}",
                "",
                f"**Expected:** {finding['expected']}",
                "",
                f"**Actual:** {finding['actual']}",
                "",
            ])

    REPORT_FILE.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    control_results = evaluate_controls()
    write_report(control_results)
    print(f"Report written to {REPORT_FILE}")
