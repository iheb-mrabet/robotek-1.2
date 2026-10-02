data "aws_ec2_managed_prefix_list" "instance_connect" {
  count = var.enable_ssh ? 1 : 0

  filter {
    name   = "prefix-list-name"
    values = ["com.amazonaws.${var.aws_region}.ec2-instance-connect"]
  }
}

resource "aws_security_group" "k3s" {
  name_prefix = "${local.name}-"
  description = "Robotek administration only; application UIs stay behind a tunnel"
  vpc_id      = aws_vpc.robotek.id

  dynamic "ingress" {
    for_each = var.enable_ssh ? [1] : []
    content {
      description = "SSH from the current operator IPv4 only"
      protocol    = "tcp"
      from_port   = 22
      to_port     = 22
      cidr_blocks = [var.admin_cidr]
    }
  }

  dynamic "ingress" {
    for_each = var.enable_ssh ? [1] : []
    content {
      description     = "SSH from the regional EC2 Instance Connect service"
      protocol        = "tcp"
      from_port       = 22
      to_port         = 22
      prefix_list_ids = [data.aws_ec2_managed_prefix_list.instance_connect[0].id]
    }
  }

  # The dashboard is intentionally public and terminates trusted HTTPS in Caddy.
  # HTTP remains open for the existing systemd forwarder and explicit health checks.
  #trivy:ignore:AVD-AWS-0107:exp:2026-11-30
  dynamic "ingress" {
    for_each = var.enable_public_dashboard ? {
      http  = 80
      https = 443
    } : {}

    content {
      description = "Public Robotek dashboard ${ingress.key}"
      protocol    = "tcp"
      from_port   = ingress.value
      to_port     = ingress.value
      cidr_blocks = ["0.0.0.0/0"]
    }
  }

  # The Academy host must reach changing Ubuntu mirror addresses over HTTP.
  # Reassess whether a managed proxy is available before this exception expires.
  #trivy:ignore:AVD-AWS-0104:exp:2026-11-30
  egress {
    description = "HTTP package access"
    protocol    = "tcp"
    from_port   = 80
    to_port     = 80
    cidr_blocks = ["0.0.0.0/0"]
  }

  # GitHub, Helm, Docker Hub and container registries use changing HTTPS endpoints.
  # Reassess whether a managed proxy is available before this exception expires.
  #trivy:ignore:AVD-AWS-0104:exp:2026-11-30
  egress {
    description = "HTTPS package, image, chart and Git access"
    protocol    = "tcp"
    from_port   = 443
    to_port     = 443
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    description = "Amazon Time Sync Service"
    protocol    = "udp"
    from_port   = 123
    to_port     = 123
    cidr_blocks = ["169.254.169.123/32"]
  }

  lifecycle {
    create_before_destroy = true
  }

  tags = { Name = "${local.name}-admin" }
}
