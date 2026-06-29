# GRC Engineering Portfolio

This repository contains hands-on compliance-as-code projects that translate security and compliance controls into cloud infrastructure, Terraform implementation, automated control evaluation, and machine-readable evidence.

The goal of this portfolio is to demonstrate how GRC, audit, and security engineering practices can work together through:

* Infrastructure as code
* Controls as code
* Evidence as code
* Automated control evaluation
* Framework mapping across NIST 800-53, ISO/IEC 27001:2022, and SOC 2 Trust Services Criteria

## Projects

| Project                            | Description                                                                                                                                              | Framework Mapping                      | Evidence / Report                                        |
| ---------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------- | -------------------------------------------------------- |
| Compliant AWS S3 Control Primitive | Terraform-based AWS S3 security baseline with encryption, public access blocking, versioning, logging, compliance tags, and automated control evaluation | NIST 800-53, ISO/IEC 27001:2022, SOC 2 | `evidence/lab-2-3/`, `reports/aws-s3-control-results.md` |

## Repository Structure

```text
repository-root/
├── evidence/
│   └── lab-2-3/
│       ├── plan.json
│       ├── state.json
│       ├── plan.pretty.json
│       └── state.pretty.json
├── reports/
│   └── aws-s3-control-results.md
├── scripts/
│   └── evaluate_s3_controls.py
├── terraform/
│   └── primitives/
│       └── compliant-s3/
│           ├── main.tf
│           ├── variables.tf
│           ├── outputs.tf
│           ├── terraform.tfvars.example
│           └── README.md
└── .gitignore
```

## Current Project: Compliant AWS S3 Control Primitive

This project provisions a compliant AWS S3 bucket baseline using Terraform and evaluates the resulting Terraform evidence against defined control expectations.

Implemented capabilities include:

| Capability                     | Control Purpose                                  |
| ------------------------------ | ------------------------------------------------ |
| AES-256 server-side encryption | Protect data at rest                             |
| S3 public access block         | Restrict unauthorized public access              |
| Required compliance tags       | Support secure configuration and asset ownership |
| S3 versioning                  | Support recovery and configuration integrity     |
| S3 server access logging       | Generate audit records for review and monitoring |
| Automated evidence evaluation  | Produce a concise pass/fail control report       |

## Evidence

Evidence is captured using Terraform JSON outputs:

```bash
terraform plan -out=tfplan
terraform show -json tfplan > evidence/plan.json
terraform show -json > evidence/state.json
```

The raw JSON files are machine-readable evidence. Pretty-formatted versions are included for easier review, and the control evaluation report summarizes the results in a human-readable pass/fail format.

## Portfolio Focus

This repository is focused on GRC engineering: converting compliance requirements into deployable cloud controls, generating reusable evidence, evaluating control results, and mapping technical implementation to audit frameworks.

