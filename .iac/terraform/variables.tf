variable "domain" {
  type        = string
  description = "Domain name. Use only lowercase letters and numbers"
  default     = "cloudsync"
}

variable "cocktails_domain" {
  type        = string
  description = "Domain name. Use only lowercase letters and numbers"
  default     = "cocktails"
}


variable "cocktails_shortdomain" {
  type        = string
  description = "Short domain name. Use only lowercase letters and numbers"
  default     = "cockti"
}

variable "owner" {
  type    = string
  default = "cloudsync.api"
}

variable "product" {
  type    = string
  default = "cezzis"
}

variable "environment" {
  type        = string
  description = "Environment name, e.g. 'dev' or 'stage' or 'prod'"
}

variable "cloud_environment" {
  type        = string
  description = "Environment name, e.g. 'dev' or 'stage' or 'prod'"
}

variable "region" {
  type    = string
  default = "eus"
}

variable "sub" {
  type        = string
  description = "Subscription short identitifer to be used in resource naming"
  default     = "vec"
}

variable "sequence" {
  type        = string
  description = "The sequence number of the resource typically starting with 001"
  default     = "001"
}
variable "short_sequence" {
  type        = string
  description = "The short sequence number of the resource typically starting with 1"
  default     = "1"
}

variable "global_environment" {
  type        = string
  description = "The global environment name"
  default     = "glo"
}

variable "global_domain" {
  type        = string
  description = "The global domain name"
  default     = "shared"
}