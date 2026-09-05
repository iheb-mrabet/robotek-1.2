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
    description = "Package, image and Git access"
    protocol    = "-1"
    from_port   = 0
    to_port     = 0
    cidr_blocks = ["0.0.0.0/0"]
  }

  lifecycle {
    create_before_destroy = true
  }

  tags = { Name = "${local.name}-admin" }
}
