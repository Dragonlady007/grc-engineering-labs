# GRC Engineering Portfolio

This repository contains hands-on GRC engineering projects that translate security and compliance requirements into cloud infrastructure, automation, control evidence, and audit-ready reporting.

The goal of this portfolio is to demonstrate how GRC, audit, cloud security, and security engineering practices can work together through:

- Infrastructure as code
- Controls as code
- Evidence as code
- Risk-based control monitoring
- POA&M-style remediation tracking
- Framework mapping across NIST 800-53, ISO/IEC 27001:2022, and SOC 2 Trust Services Criteria

## Projects

| Project | Focus Area | Description | Framework Mapping |
|---|---|---|---|
| Compliant AWS S3 Control Primitive | Cloud control baseline | Terraform-based AWS S3 security baseline with encryption, public access blocking, versioning, logging, and compliance tags | NIST 800-53, ISO/IEC 27001:2022, SOC 2 |
| CA-7 Continuous Monitoring & POA&M Automation | Continuous monitoring / GRC automation | AWS-native monitoring workflow that maps cloud configuration findings to risk scenarios, creates POA&M-style records, and generates JSON, CSV, and HTML dashboard reporting | NIST 800-53 CA-7, CA-5, RA-5, SI-4; ISO/IEC 27001:2022 monitoring and corrective action concepts; SOC 2 CC7 / CC4 concepts |

## Repository Structure

- `evidence/` — generated evidence artifacts
- `reports/` — reporting outputs
- `scripts/` — helper scripts
- `terraform/primitives/compliant-s3/` — reusable S3 control primitive
- `projects/ca7-continuous-monitoring-poam-automation/` — CA-7 continuous monitoring and POA&M automation project

## Portfolio Focus

This portfolio is designed to show practical experience with:

- Translating compliance requirements into technical cloud controls
- Building Terraform-based security baselines
- Generating machine-readable evidence
- Mapping technical findings to control IDs and risk scenarios
- Creating audit-ready reporting artifacts
- Connecting cloud security monitoring to GRC workflows
