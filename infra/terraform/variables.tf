variable "project_name" {
  description = "Project tag/name prefix."
  type        = string
  default     = "robotek"
}

variable "environment" {
  description = "Environment name."
  type        = string
  default     = "staging"
}

variable "aws_region" {
  description = "AWS Academy region allowed for the current lab."
  type        = string
  default     = "us-east-1"
}

variable "expected_account_id" {
  description = "Fresh AWS account ID. Terraform refuses to continue when it differs."
  type        = string

  validation {
    condition     = can(regex("^[0-9]{12}$", var.expected_account_id))
    error_message = "expected_account_id must be a 12-digit AWS account ID."
  }
}

variable "vpc_cidr" {
  type    = string
  default = "10.42.0.0/16"
}

variable "public_subnet_cidr" {
  type    = string
  default = "10.42.10.0/24"
}

variable "availability_zone" {
  description = "Optional explicit AZ. The first available AZ is used when null."
  type        = string
  default     = null
}

variable "instance_type" {
  description = "K3s node size. t3.large is the historical baseline."
  type        = string
  default     = "t3.large"
}

variable "root_volume_size" {
  description = "Encrypted gp3 root volume size in GiB."
  type        = number
  default     = 60

  validation {
    condition     = var.root_volume_size >= 50 && var.root_volume_size <= 100
    error_message = "root_volume_size must be between 50 and 100 GiB."
  }
}

variable "enable_ssh" {
  description = "Open SSH only to admin_cidr. Disable when Session Manager is available."
  type        = bool
  default     = true
}

variable "enable_public_dashboard" {
  description = "Allocate a stable Elastic IP and publish the Robotek dashboard over trusted HTTPS."
  type        = bool
  default     = true
}

variable "caddy_version" {
  description = "Pinned Caddy release used for the permanent HTTPS endpoint."
  type        = string
  default     = "v2.11.4"

  validation {
    condition     = can(regex("^v[0-9]+\\.[0-9]+\\.[0-9]+$", var.caddy_version))
    error_message = "caddy_version must be a full semantic version prefixed with v."
  }
}

variable "caddy_sha512" {
  description = "Official SHA-512 digest for the pinned linux_amd64 Caddy archive."
  type        = string
  default     = "8220d1f013b6f27510247b2360c9e0ca9f018feebd82515f07635318b34ff9777ccc8fd0b6e6f2486ce3a33fe389fbb7db12d05baa474f4587509fb4f5ebf1c9"

  validation {
    condition     = can(regex("^[0-9a-f]{128}$", var.caddy_sha512))
    error_message = "caddy_sha512 must be a lowercase SHA-512 digest."
  }
}

variable "admin_cidr" {
  description = "Current operator public IPv4 as a /32. Never use 0.0.0.0/0."
  type        = string
  default     = ""

  validation {
    condition = var.admin_cidr == "" || (
      can(cidrhost(var.admin_cidr, 0)) && endswith(var.admin_cidr, "/32") && var.admin_cidr != "0.0.0.0/0"
    )
    error_message = "admin_cidr must be empty or a valid IPv4 /32, never 0.0.0.0/0."
  }
}

variable "ssh_public_key_path" {
  description = "Path to a local public key. The private key never enters Terraform."
  type        = string
  default     = ""
}

variable "instance_profile_name" {
  description = "Optional pre-existing Academy instance profile for SSM, such as LabInstanceProfile."
  type        = string
  default     = ""
}

variable "repository_url" {
  type    = string
  default = "https://github.com/iheb-mrabet/robotek-1.2.git"
}

variable "repository_revision" {
  type    = string
  default = "main"
}

variable "k3s_version" {
  description = "Pinned K3s version."
  type        = string
  default     = "v1.34.1+k3s1"
}

variable "helm_version" {
  description = "Pinned Helm version."
  type        = string
  default     = "v3.21.1"
}

variable "argocd_chart_version" {
  description = "Pinned argo-cd Helm chart version."
  type        = string
  default     = "8.5.7"
}
