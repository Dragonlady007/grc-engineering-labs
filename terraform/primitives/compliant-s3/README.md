# Lab 2.3 — Compliant AWS S3 Terraform Primitive

This Terraform primitive provisions a compliant AWS S3 bucket baseline mapped to NIST 800-53 controls. It enforces required compliance tags for CM-6, server-side encryption for SC-28, public access blocking for AC-3, versioning for CM-6, and S3 server access logging for AU-3/AU-6. Evidence is captured as machine-readable JSON using Terraform plan and state outputs.

## Controls Implemented

| Control | Implementation |
|---|---|
| SC-28 | Enables AES-256 server-side encryption for S3 data at rest |
| AC-3 | Blocks public access using all four S3 public access block settings |
| CM-6 | Applies required compliance tags through Terraform provider default tags |
| CM-6 | Enables S3 bucket versioning as part of secure configuration baseline |
| AU-3 / AU-6 | Enables S3 server access logging to a dedicated log bucket |

## Evidence

Evidence artifacts are generated using:

```bash
terraform plan -out=tfplan
terraform show -json tfplan > evidence/plan.json
terraform show -json > evidence/state.json
```

Portfolio evidence is stored under:

```text
evidence/lab-2-3/
├── plan.json
└── state.json
```

## Verification

The deployed bucket was verified using AWS CLI checks for encryption, versioning, and public access blocking:

```bash
aws s3api get-bucket-encryption --bucket "$BUCKET" --region us-east-1
aws s3api get-bucket-versioning --bucket "$BUCKET" --region us-east-1
aws s3api get-public-access-block --bucket "$BUCKET" --region us-east-1
```

Verified results:

- Encryption algorithm: AES256
- Versioning: Enabled
- Public access block: BlockPublicAcls, IgnorePublicAcls, BlockPublicPolicy, and RestrictPublicBuckets all set to true
