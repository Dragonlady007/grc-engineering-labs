# GRC Engineering Portfolio

This repository contains hands-on compliance-as-code projects that translate security and compliance controls into cloud infrastructure, Terraform implementation, and machine-readable evidence.

The goal of this portfolio is to demonstrate how GRC, audit, and security engineering practices can work together through:

- Infrastructure as code
- Controls as code
- Evidence as code
- Framework mapping across NIST 800-53, ISO/IEC 27001:2022, and SOC 2 Trust Services Criteria

## Projects

| Project | Description | Framework Mapping | Evidence |
|---|---|---|---|
| Compliant AWS S3 Control Primitive | Terraform-based AWS S3 security baseline with encryption, public access blocking, versioning, logging, and compliance tags | NIST 800-53, ISO/IEC 27001:2022, SOC 2 | `evidence/lab-2-3/` |

## Repository Structure

```text
repository-root/
├── evidence/
│   └── lab-2-3/
│       ├── plan.json
│       ├── state.json
│       ├── plan.pretty.json
│       └── state.pretty.json
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
