terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }

    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.4"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

locals {
  account_id = data.aws_caller_identity.current.account_id
  region     = data.aws_region.current.name

  common_tags = {
    Project     = var.project_name
    Control     = "CA-7"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# ------------------------------------------------------------
# CA-7: AWS Config Logging Bucket
# ------------------------------------------------------------

resource "aws_s3_bucket" "config_logs" {
  bucket = "${var.project_name}-config-logs-${local.account_id}-${local.region}"

  tags = merge(local.common_tags, {
    Component = "AWS Config Logging"
  })
}

resource "aws_s3_bucket_public_access_block" "config_logs" {
  bucket = aws_s3_bucket.config_logs.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "config_logs" {
  bucket = aws_s3_bucket.config_logs.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_policy" "config_logs" {
  bucket = aws_s3_bucket.config_logs.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AWSConfigBucketPermissionsCheck"
        Effect = "Allow"
        Principal = {
          Service = "config.amazonaws.com"
        }
        Action   = "s3:GetBucketAcl"
        Resource = aws_s3_bucket.config_logs.arn
      },
      {
        Sid    = "AWSConfigBucketDelivery"
        Effect = "Allow"
        Principal = {
          Service = "config.amazonaws.com"
        }
        Action   = "s3:PutObject"
        Resource = "${aws_s3_bucket.config_logs.arn}/AWSLogs/${local.account_id}/Config/*"
        Condition = {
          StringEquals = {
            "s3:x-amz-acl" = "bucket-owner-full-control"
          }
        }
      }
    ]
  })

  depends_on = [
    aws_s3_bucket_public_access_block.config_logs
  ]
}

# ------------------------------------------------------------
# CA-7: AWS Config Setup
# ------------------------------------------------------------

resource "aws_iam_role" "config_role" {
  name = "${var.project_name}-config-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Service = "config.amazonaws.com"
      }
      Action = "sts:AssumeRole"
    }]
  })

  tags = merge(local.common_tags, {
    Component = "AWS Config IAM Role"
  })
}

resource "aws_iam_role_policy_attachment" "config_policy" {
  role       = aws_iam_role.config_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWS_ConfigRole"
}

resource "aws_config_configuration_recorder" "main" {
  name     = "${var.project_name}-config-recorder"
  role_arn = aws_iam_role.config_role.arn

  recording_group {
    all_supported                 = true
    include_global_resource_types = false
  }

  depends_on = [
    aws_iam_role_policy_attachment.config_policy
  ]
}

resource "aws_config_delivery_channel" "main" {
  name           = "${var.project_name}-config-delivery-channel"
  s3_bucket_name = aws_s3_bucket.config_logs.bucket

  depends_on = [
    aws_config_configuration_recorder.main,
    aws_s3_bucket_policy.config_logs
  ]
}

resource "aws_config_configuration_recorder_status" "main" {
  name       = aws_config_configuration_recorder.main.name
  is_enabled = true

  depends_on = [
    aws_config_delivery_channel.main
  ]
}

# ------------------------------------------------------------
# CA-7: AWS Config Rule
# ------------------------------------------------------------
# For the first sandbox test, we monitor unencrypted EBS volumes.
# This makes it easy to trigger a safe NON_COMPLIANT finding.

resource "aws_config_config_rule" "encrypted_volumes" {
  name        = "${var.project_name}-encrypted-volumes"
  description = "CA-7: Monitors whether attached EBS volumes are encrypted."

  source {
    owner             = "AWS"
    source_identifier = "ENCRYPTED_VOLUMES"
  }

  tags = merge(local.common_tags, {
    Component = "Continuous Monitoring Rule"
    RiskID    = "RISK-CLD-003"
  })

  depends_on = [
    aws_config_configuration_recorder_status.main
  ]
}

# ------------------------------------------------------------
# CA-7(f): SNS Notification Channel
# ------------------------------------------------------------

resource "aws_sns_topic" "conmon" {
  name = "${var.project_name}-conmon-alerts"

  tags = merge(local.common_tags, {
    Component = "Finding Notification"
  })
}

resource "aws_sns_topic_policy" "conmon" {
  arn = aws_sns_topic.conmon.arn

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Sid    = "AllowEventBridgePublish"
      Effect = "Allow"
      Principal = {
        Service = "events.amazonaws.com"
      }
      Action   = "sns:Publish"
      Resource = aws_sns_topic.conmon.arn
    }]
  })
}

resource "aws_sns_topic_subscription" "email" {
  count     = var.alert_email != "" ? 1 : 0
  topic_arn = aws_sns_topic.conmon.arn
  protocol  = "email"
  endpoint  = var.alert_email
}

# ------------------------------------------------------------
# CA-7: POAM Tracking Table
# ------------------------------------------------------------

resource "aws_dynamodb_table" "poam" {
  name         = "${var.project_name}-poam"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "finding_id"

  attribute {
    name = "finding_id"
    type = "S"
  }

  tags = merge(local.common_tags, {
    Component = "POAM Tracking"
  })
}

# ------------------------------------------------------------
# CA-7: Reporting Bucket
# ------------------------------------------------------------

resource "aws_s3_bucket" "conmon_reports" {
  bucket = "${var.project_name}-conmon-reports-${local.account_id}-${local.region}"

  tags = merge(local.common_tags, {
    Component = "ConMon Reporting"
  })
}

resource "aws_s3_bucket_public_access_block" "conmon_reports" {
  bucket = aws_s3_bucket.conmon_reports.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "conmon_reports" {
  bucket = aws_s3_bucket.conmon_reports.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# ------------------------------------------------------------
# CA-7: Lambda IAM Role
# ------------------------------------------------------------

resource "aws_iam_role" "ca7_lambda_role" {
  name = "${var.project_name}-ca7-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
      Action = "sts:AssumeRole"
    }]
  })

  tags = merge(local.common_tags, {
    Component = "Lambda Execution Role"
  })
}

resource "aws_iam_role_policy" "ca7_lambda_policy" {
  name = "${var.project_name}-ca7-lambda-policy"
  role = aws_iam_role.ca7_lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AllowPOAMTableAccess"
        Effect = "Allow"
        Action = [
          "dynamodb:PutItem",
          "dynamodb:GetItem",
          "dynamodb:UpdateItem",
          "dynamodb:Scan"
        ]
        Resource = aws_dynamodb_table.poam.arn
      },
      {
        Sid    = "AllowReportBucketAccess"
        Effect = "Allow"
        Action = [
          "s3:PutObject",
          "s3:GetObject"
        ]
        Resource = "${aws_s3_bucket.conmon_reports.arn}/*"
      },
      {
        Sid    = "AllowLambdaLogging"
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "*"
      }
    ]
  })
}

# ------------------------------------------------------------
# CA-7: Lambda Function - Create POA&M Record
# ------------------------------------------------------------

data "archive_file" "poam_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/lambda/create_poam.py"
  output_path = "${path.module}/lambda/create_poam.zip"
}

resource "aws_lambda_function" "create_poam" {
  function_name = "${var.project_name}-create-poam"
  role          = aws_iam_role.ca7_lambda_role.arn
  handler       = "create_poam.lambda_handler"
  runtime       = "python3.12"
  timeout       = 30

  filename         = data.archive_file.poam_lambda_zip.output_path
  source_code_hash = data.archive_file.poam_lambda_zip.output_base64sha256

  environment {
    variables = {
      POAM_TABLE = aws_dynamodb_table.poam.name
    }
  }

  tags = merge(local.common_tags, {
    Component = "POAM Automation"
  })

  depends_on = [
    aws_iam_role_policy.ca7_lambda_policy
  ]
}

# ------------------------------------------------------------
# CA-7: Lambda Function - Generate Report
# ------------------------------------------------------------

data "archive_file" "report_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/lambda/generate_report.py"
  output_path = "${path.module}/lambda/generate_report.zip"
}

resource "aws_lambda_function" "generate_report" {
  function_name = "${var.project_name}-generate-report"
  role          = aws_iam_role.ca7_lambda_role.arn
  handler       = "generate_report.lambda_handler"
  runtime       = "python3.12"
  timeout       = 30

  filename         = data.archive_file.report_lambda_zip.output_path
  source_code_hash = data.archive_file.report_lambda_zip.output_base64sha256

  environment {
    variables = {
      POAM_TABLE    = aws_dynamodb_table.poam.name
      REPORT_BUCKET = aws_s3_bucket.conmon_reports.bucket
    }
  }

  tags = merge(local.common_tags, {
    Component = "ConMon Reporting"
  })

  depends_on = [
    aws_iam_role_policy.ca7_lambda_policy
  ]
}

# ------------------------------------------------------------
# CA-7: EventBridge Rule for NON_COMPLIANT Findings
# ------------------------------------------------------------

resource "aws_cloudwatch_event_rule" "noncompliant" {
  name        = "${var.project_name}-config-noncompliant"
  description = "CA-7: Routes AWS Config NON_COMPLIANT findings to notification and POA&M automation."

  event_pattern = jsonencode({
    source        = ["aws.config"]
    "detail-type" = ["Config Rules Compliance Change"]
    detail = {
      newEvaluationResult = {
        complianceType = ["NON_COMPLIANT"]
      }
    }
  })

  tags = merge(local.common_tags, {
    Component = "Event Routing"
  })
}

resource "aws_cloudwatch_event_target" "to_sns" {
  rule      = aws_cloudwatch_event_rule.noncompliant.name
  target_id = "ca7-sns-notification"
  arn       = aws_sns_topic.conmon.arn
}

resource "aws_cloudwatch_event_target" "to_poam_lambda" {
  rule      = aws_cloudwatch_event_rule.noncompliant.name
  target_id = "ca7-poam-lambda"
  arn       = aws_lambda_function.create_poam.arn
}

resource "aws_lambda_permission" "allow_eventbridge_poam" {
  statement_id  = "AllowExecutionFromEventBridgeForPOAM"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.create_poam.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.noncompliant.arn
}

# ------------------------------------------------------------
# CA-7: Monthly Reporting Schedule
# ------------------------------------------------------------

resource "aws_cloudwatch_event_rule" "monthly_ca7_report" {
  name                = "${var.project_name}-monthly-ca7-report"
  description         = "CA-7: Monthly continuous monitoring POA&M reporting."
  schedule_expression = "cron(0 13 1 * ? *)"

  tags = merge(local.common_tags, {
    Component = "Scheduled Reporting"
  })
}

resource "aws_cloudwatch_event_target" "monthly_report_lambda" {
  rule      = aws_cloudwatch_event_rule.monthly_ca7_report.name
  target_id = "ca7-report-lambda"
  arn       = aws_lambda_function.generate_report.arn
}

resource "aws_lambda_permission" "allow_eventbridge_report" {
  statement_id  = "AllowExecutionFromEventBridgeForReport"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.generate_report.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.monthly_ca7_report.arn
}
