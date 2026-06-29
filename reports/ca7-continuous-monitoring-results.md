# CA-7 Continuous Monitoring & POA&M Automation Report

## Executive Summary

This report summarizes the CA-7 Continuous Monitoring & POA&M Automation project. The project demonstrates how AWS-native services can be used to detect cloud configuration noncompliance, map findings to risk scenarios, create POA&M-style remediation records, and generate audit-ready reporting artifacts.

## Control Objective

NIST SP 800-53 CA-7 focuses on continuous monitoring to support ongoing awareness of security and risk posture.

This project supports the control objective by demonstrating:

- Automated configuration monitoring
- Noncompliance detection
- Finding routing
- Risk-based enrichment
- POA&M-style remediation tracking
- Reporting and dashboard evidence generation

## Project Scope

The project deploys an AWS-native monitoring workflow using Terraform.

In scope:

- AWS Config managed rule
- EventBridge routing
- SNS notification topic
- Lambda-based POA&M creation
- DynamoDB POA&M table
- Lambda-based report generation
- S3 report storage
- JSON, CSV, and HTML dashboard outputs

## Monitoring Rule Tested

The initial monitoring rule used in this project is AWS Config ENCRYPTED_VOLUMES.

This rule checks whether attached EBS volumes are encrypted.

## Risk Mapping

The AWS Config finding is enriched with the following GRC context:

- Control ID: CA-7
- Risk ID: RISK-CLD-003
- Risk Scenario: Sensitive data exposure due to unencrypted cloud storage
- Severity: High
- Owner: Infrastructure
- Risk Response: Mitigate
- Remediation Plan: Enable encryption or migrate to encrypted volumes

## Testing Performed

An unencrypted EBS volume was created during testing.

The AWS Config ENCRYPTED_VOLUMES managed rule evaluates attached EBS volumes. Because the test volume was unattached, it did not generate a live AWS Config noncompliance finding.

To validate the downstream automation, a representative AWS Config NON_COMPLIANT event payload was used to invoke the POA&M Lambda.

The test validated:

- Event processing by Lambda
- Risk mapping logic
- DynamoDB POA&M record creation
- Report Lambda execution
- JSON report generation
- CSV report generation
- HTML dashboard generation
- S3 evidence storage

## Results

The project successfully generated a POA&M-style record and reporting artifacts.

Generated outputs included:

- ca7-poam-report.json
- ca7-poam-report.csv
- ca7-dashboard.html

## CA-7 Coverage Assessment

| CA-7 Area | Result |
|---|---|
| Continuous monitoring mechanism | Implemented using AWS Config |
| Finding detection | Demonstrated using AWS Config NON_COMPLIANT event structure |
| Finding routing | Implemented using EventBridge |
| Notification | Implemented using SNS |
| POA&M tracking | Implemented using DynamoDB |
| Risk mapping | Implemented using Lambda enrichment logic |
| Reporting | Implemented using JSON, CSV, and HTML dashboard outputs |
| Evidence generation | Implemented using S3 report storage |

## Limitations

This project supports CA-7 but does not fully satisfy the entire control by itself.

Full CA-7 operating effectiveness would also require documented continuous monitoring strategy, defined monitoring frequencies, broader control coverage, remediation SLAs, management review, closure evidence, trend analysis, risk acceptance workflow, and independent assessment or audit validation.

## Conclusion

The project demonstrates a practical GRC engineering workflow for continuous monitoring. It shows how technical cloud findings can be mapped to control and risk context, tracked as POA&M records, and reported through audit-ready artifacts.
