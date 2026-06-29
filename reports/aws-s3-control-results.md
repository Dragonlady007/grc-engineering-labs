# AWS S3 Control Evaluation Report

This report summarizes control evaluation results from the Terraform state evidence file for the Compliant AWS S3 Control Primitive.

## Summary

* Total controls evaluated: 6
* Passed: 6
* Failed: 0

## Control ID Naming

The `CGE-S3` control IDs are internal portfolio control identifiers created for this project.

They are used to organize the compliance-as-code implementation and evidence mapping for the AWS S3 control primitive. These IDs are not official NIST, ISO, or SOC 2 control IDs.

Each internal control ID maps to one or more external framework requirements.

| Internal Control ID | Meaning                                     | External Framework Mapping                                                          |
| ------------------- | ------------------------------------------- | ----------------------------------------------------------------------------------- |
| CGE-S3-01           | AWS S3 encryption at rest control           | NIST SC-28, ISO A.8.24, SOC 2 CC6.1 / CC6.7                                         |
| CGE-S3-02           | AWS S3 public access restriction control    | NIST AC-3, ISO A.5.15 / A.8.3, SOC 2 CC6.1 / CC6.6 / CC6.7                          |
| CGE-S3-03           | AWS S3 secure configuration tagging control | NIST CM-6, ISO A.5.9 / A.8.9, SOC 2 CC7.1 / CC8.1                                   |
| CGE-S3-04           | AWS S3 versioning control                   | NIST CM-6, ISO A.8.13 / A.8.9, SOC 2 CC7.3 / A1.2                                   |
| CGE-S3-05           | AWS S3 access logging control               | NIST AU-3 / AU-6, ISO A.8.15 / A.8.16, SOC 2 CC7.2 / CC7.3 / CC7.4                  |
| CGE-S3-06           | AWS S3 log bucket protection control        | NIST AU-9 / SC-28 / AC-3, ISO A.8.15 / A.8.24 / A.5.15, SOC 2 CC6.1 / CC6.7 / CC7.2 |

## Control Results

| Control ID | Control Status | Framework Mapping                                                               | Control                   | Expected                                                                    | Actual                                                                                                  |
| ---------- | -------------- | ------------------------------------------------------------------------------- | ------------------------- | --------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| CGE-S3-01  | Pass           | NIST SC-28 / ISO A.8.24 / SOC 2 CC6.1, CC6.7                                    | Encryption at Rest        | S3 bucket uses AES256 server-side encryption                                | AES256                                                                                                  |
| CGE-S3-02  | Pass           | NIST AC-3 / ISO A.5.15, A.8.3 / SOC 2 CC6.1, CC6.6, CC6.7                       | Public Access Restriction | All four S3 public access block settings are true                           | block_public_acls=true, ignore_public_acls=true, block_public_policy=true, restrict_public_buckets=true |
| CGE-S3-03  | Pass           | NIST CM-6 / ISO A.5.9, A.8.9 / SOC 2 CC7.1, CC8.1                               | Secure Configuration Tags | Required tags are present: Project, Environment, ManagedBy, ComplianceScope | Present                                                                                                 |
| CGE-S3-04  | Pass           | NIST CM-6 / ISO A.8.13, A.8.9 / SOC 2 CC7.3, A1.2                               | Versioning                | S3 bucket versioning is Enabled                                             | Enabled                                                                                                 |
| CGE-S3-05  | Pass           | NIST AU-3, AU-6 / ISO A.8.15, A.8.16 / SOC 2 CC7.2, CC7.3, CC7.4                | Access Logging            | Primary S3 bucket sends access logs to a dedicated log bucket               | target_bucket=grclab-dev-logs-560fdfdf, target_prefix=access-logs/                                      |
| CGE-S3-06  | Pass           | NIST AU-9, SC-28, AC-3 / ISO A.8.15, A.8.24, A.5.15 / SOC 2 CC6.1, CC6.7, CC7.2 | Log Bucket Protection     | Log bucket is encrypted and public access is blocked                        | encryption_configured=true, public_access_blocked=true                                                  |

## Findings

No findings identified. All evaluated controls passed.

## Evidence Sources

| Evidence Source                                | Purpose                           |
| ---------------------------------------------- | --------------------------------- |
| `evidence/lab-2-3/state.json`                  | Terraform deployed-state evidence |
| `evidence/lab-2-3/plan.json`                   | Terraform plan evidence           |
| `terraform/primitives/compliant-s3/main.tf`    | Terraform implementation          |
| `terraform/primitives/compliant-s3/outputs.tf` | Terraform output evidence         |

## Evaluation Notes

This report is based on the Terraform evidence captured during project execution. The JSON evidence provides the machine-readable source of truth, while this report summarizes the control evaluation results in a human-readable format for portfolio and audit-readiness review.
