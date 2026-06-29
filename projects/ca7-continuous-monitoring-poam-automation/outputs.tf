output "ca7_config_rule" {
  description = "AWS Config rule used for CA-7 continuous monitoring."
  value       = aws_config_config_rule.encrypted_volumes.name
}

output "ca7_sns_topic_arn" {
  description = "SNS topic used as the CA-7 finding notification channel."
  value       = aws_sns_topic.conmon.arn
}

output "ca7_eventbridge_rule_name" {
  description = "EventBridge rule that routes AWS Config NON_COMPLIANT findings."
  value       = aws_cloudwatch_event_rule.noncompliant.name
}

output "ca7_poam_table_name" {
  description = "DynamoDB table storing CA-7 POA&M-style findings."
  value       = aws_dynamodb_table.poam.name
}

output "ca7_report_bucket" {
  description = "S3 bucket storing CA-7 continuous monitoring reports."
  value       = aws_s3_bucket.conmon_reports.bucket
}

output "ca7_poam_lambda_name" {
  description = "Lambda function that creates CA-7 POA&M records from AWS Config findings."
  value       = aws_lambda_function.create_poam.function_name
}

output "ca7_report_lambda_name" {
  description = "Lambda function that generates CA-7 reporting artifacts."
  value       = aws_lambda_function.generate_report.function_name
}
