resource "aws_key_pair" "operator" {
  count = var.enable_ssh ? 1 : 0

  key_name   = "${local.name}-operator"
  public_key = file(pathexpand(var.ssh_public_key_path))
}

resource "aws_instance" "k3s" {
  ami                         = data.aws_ami.ubuntu.id
  instance_type               = var.instance_type
  subnet_id                   = aws_subnet.public.id
  associate_public_ip_address = true
  vpc_security_group_ids      = [aws_security_group.k3s.id]
  key_name                    = var.enable_ssh ? aws_key_pair.operator[0].key_name : null
  iam_instance_profile        = var.instance_profile_name != "" ? var.instance_profile_name : null

  user_data_replace_on_change = true
  user_data = templatefile("${path.module}/../cloud-init/robotek-k3s.yaml.tftpl", {
    bootstrap_k3s_b64    = base64encode(file("${path.module}/../scripts/bootstrap-k3s.sh"))
    bootstrap_argocd_b64 = base64encode(file("${path.module}/../scripts/bootstrap-argocd.sh"))
    verify_platform_b64  = base64encode(file("${path.module}/../scripts/verify-platform.sh"))
    repository_url       = var.repository_url
    repository_revision  = var.repository_revision
    k3s_version          = var.k3s_version
    helm_version         = var.helm_version
    argocd_chart_version = var.argocd_chart_version
  })

  metadata_options {
    http_endpoint               = "enabled"
    http_tokens                 = "required"
    http_put_response_hop_limit = 1
    instance_metadata_tags      = "enabled"
  }

  root_block_device {
    encrypted   = true
    volume_type = "gp3"
    volume_size = var.root_volume_size
  }

  lifecycle {
    precondition {
      condition     = data.aws_caller_identity.current.account_id == var.expected_account_id
      error_message = "AWS account mismatch. Refresh Academy credentials and verify expected_account_id."
    }
  }

  tags = { Name = "${local.name}-k3s" }
}
