# AWS S3 Control Evaluation Report

This report summarizes control evaluation results from the Terraform state evidence file.

## Summary

- Total controls evaluated: 6
- Passed: 6
- Failed: 0

## Control Results

| Control ID | Framework Mapping | Control | Expected | Actual | Status |
|---|---|---|---|---|---|
| CGE-S3-01 | NIST SC-28 / ISO A.8.24 / SOC 2 CC6.1, CC6.7 | Encryption at Rest | S3 bucket uses AES256 server-side encryption | AES256 | Pass |
| CGE-S3-02 | NIST AC-3 / ISO A.5.15, A.8.3 / SOC 2 CC6.1, CC6.6, CC6.7 | Public Access Restriction | All four S3 public access block settings are true | block_public_acls=true, ignore_public_acls=true, block_public_policy=true, restrict_public_buckets=true | Pass |
| CGE-S3-03 | NIST CM-6 / ISO A.5.9, A.8.9 / SOC 2 CC7.1, CC8.1 | Secure Configuration Tags | Required tags are present: Project, Environment, ManagedBy, ComplianceScope | Present | Pass |
| CGE-S3-04 | NIST CM-6 / ISO A.8.13, A.8.9 / SOC 2 CC7.3, A1.2 | Versioning | S3 bucket versioning is Enabled | Enabled | Pass |
| CGE-S3-05 | NIST AU-3, AU-6 / ISO A.8.15, A.8.16 / SOC 2 CC7.2, CC7.3, CC7.4 | Access Logging | Primary S3 bucket sends access logs to a dedicated log bucket | target_bucket=grclab-dev-logs-560fdfdf, target_prefix=access-logs/ | Pass |
| CGE-S3-06 | NIST AU-9, SC-28, AC-3 / ISO A.8.15, A.8.24, A.5.15 / SOC 2 CC6.1, CC6.7, CC7.2 | Log Bucket Protection | Log bucket is encrypted and public access is blocked | encryption_configured=true, public_access_blocked=true | Pass |

## Findings

No findings identified. All evaluated controls passed.

## Evidence Sources

| Evidence Source | Purpose |
|---|---|
| `evidence/lab-2-3/state.json` | Terraform deployed-state evidence |
| `evidence/lab-2-3/plan.json` | Terraform plan evidence |
| `terraform/primitives/compliant-s3/main.tf` | Terraform implementation |
| `terraform/primitives/compliant-s3/outputs.tf` | Terraform output evidence |
