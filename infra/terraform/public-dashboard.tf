resource "aws_eip" "dashboard" {
  count = var.enable_public_dashboard ? 1 : 0

  domain = "vpc"

  depends_on = [aws_internet_gateway.robotek]

  tags = {
    Name = "${local.name}-dashboard"
  }
}

resource "aws_eip_association" "dashboard" {
  count = var.enable_public_dashboard ? 1 : 0

  allocation_id = aws_eip.dashboard[0].id
  instance_id   = aws_instance.k3s.id
}

locals {
  dashboard_public_ip = var.enable_public_dashboard ? aws_eip.dashboard[0].public_ip : null
  dashboard_hostname = var.enable_public_dashboard ? format(
    "%s.nip.io",
    replace(aws_eip.dashboard[0].public_ip, ".", "-")
  ) : ""
}
