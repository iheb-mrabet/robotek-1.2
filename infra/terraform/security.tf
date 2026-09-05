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

  egress {
    description = "HTTP package access"
    protocol    = "tcp"
    from_port   = 80
    to_port     = 80
    cidr_blocks = ["0.0.0.0/0"]
  }

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
