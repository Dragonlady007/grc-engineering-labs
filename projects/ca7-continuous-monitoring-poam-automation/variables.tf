variable "aws_region" {
  description = "AWS region for the CA-7 continuous monitoring lab."
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Name prefix for CA-7 continuous monitoring resources."
  type        = string
  default     = "grc-ca7-lab"
}

variable "environment" {
  description = "Environment name for tagging and evidence."
  type        = string
  default     = "lab"
}

variable "alert_email" {
  description = "Optional email address for SNS alerts. Leave blank to skip email subscription."
  type        = string
  default     = ""
}
