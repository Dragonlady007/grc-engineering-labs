# CA-7 Continuous Monitoring with Risk-Based POA&M and Reporting

## Overview

This project demonstrates a GRC engineering implementation of NIST SP 800-53 CA-7 Continuous Monitoring using Terraform and AWS-native services.

The project shows how a cloud configuration finding can move through a continuous monitoring workflow:

Monitoring -> Finding Detection -> Risk Mapping -> POA&M Tracking -> Reporting -> Dashboard

## What This Lab Builds

This project deploys:

- AWS Config rule for continuous monitoring
- EventBridge rule for NON_COMPLIANT findings
- SNS topic for finding notification
- Lambda function to create POA&M-style records
- DynamoDB table to store findings
- Lambda function to generate reports
- S3 bucket to store JSON, CSV, and HTML dashboard reports

## Architecture

AWS Config Managed Rule
-> AWS Config NON_COMPLIANT Event
-> EventBridge Rule
-> SNS Notification Channel
-> Lambda: Create POA&M Record
-> DynamoDB POA&M Table
-> Lambda: Generate Report
-> S3 Report Bucket
-> JSON / CSV / HTML Dashboard

## AWS Services Used

- Terraform: deploys the project infrastructure
- AWS Config: monitors AWS resource compliance
- EventBridge: routes NON_COMPLIANT events
- SNS: provides finding notification
- Lambda: creates POA&M records and generates reports
- DynamoDB: stores POA&M-style findings
- S3: stores reporting and evidence artifacts

## Monitoring Rule

The initial lab uses the AWS Config managed rule ENCRYPTED_VOLUMES.

This rule checks whether attached EBS volumes are encrypted.

## Risk Mapping

AWS Config produces a technical finding. The POA&M Lambda adds GRC context by mapping the finding to a risk scenario.

For this project:

- Control ID: CA-7
- Risk ID: RISK-CLD-003
- Risk Scenario: Sensitive data exposure due to unencrypted cloud storage
- Severity: High
- Owner: Infrastructure
- Risk Response: Mitigate
- Remediation Plan: Enable encryption or migrate to encrypted volumes

## POA&M Tracking

The create_poam Lambda creates a DynamoDB record with:

- Finding ID
- Control ID
- Risk ID
- Risk scenario
- Resource type
- Resource ID
- Severity
- Owner
- Status
- Due date
- Remediation plan

## Reporting and Dashboard

The generate_report Lambda creates three reporting artifacts in S3:

- ca7-poam-report.json: machine-readable evidence report
- ca7-poam-report.csv: spreadsheet-friendly POA&M report
- ca7-dashboard.html: human-readable dashboard

The dashboard summarizes total findings, open findings, closed findings, overdue findings, findings by risk, findings by severity, findings by owner, findings by status, and POA&M details.

## Testing Approach

The AWS Config rule was deployed successfully.

During testing, an unencrypted EBS volume was created. The AWS Config ENCRYPTED_VOLUMES rule evaluates attached EBS volumes, so the unattached test volume did not produce a live Config finding.

To validate the downstream workflow, a representative AWS Config NON_COMPLIANT event payload was used to invoke the POA&M Lambda.

This validated:

- Lambda processing
- Risk mapping
- DynamoDB POA&M record creation
- JSON report generation
- CSV report generation
- HTML dashboard generation
- S3 evidence storage

## CA-7 Coverage

This project demonstrates:

- Continuous monitoring
- Finding detection
- Finding routing
- Notification
- POA&M tracking
- Risk linkage
- Reporting
- Evidence generation

## Limitations

This project supports CA-7 but does not fully satisfy the entire control by itself.

Full CA-7 implementation would also require a documented continuous monitoring strategy, defined monitoring frequencies, broader control coverage, remediation SLAs, management review, closure evidence, trend analysis, risk acceptance workflow, and independent assessment or audit validation.

## Portfolio Summary

Built a risk-based CA-7 continuous monitoring project using Terraform, AWS Config, EventBridge, SNS, Lambda, DynamoDB, and S3. The project demonstrates how cloud configuration findings can be mapped to risk scenarios, tracked as POA&M records, and reported through JSON, CSV, and HTML dashboard artifacts.
