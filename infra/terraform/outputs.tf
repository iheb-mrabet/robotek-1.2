output "account_id" {
  value = data.aws_caller_identity.current.account_id
}

output "region" {
  value = var.aws_region
}

output "instance_id" {
  value = aws_instance.k3s.id
}

output "public_ip" {
  value = aws_instance.k3s.public_ip
}

output "private_ip" {
  value = aws_instance.k3s.private_ip
}

output "ssh_command" {
  value = var.enable_ssh ? "ssh ubuntu@${aws_instance.k3s.public_ip}" : "SSH disabled; use Session Manager"
}

output "dashboard_tunnel_command" {
  value = var.enable_ssh ? "ssh -L 30080:127.0.0.1:30080 -L 8080:127.0.0.1:8080 -L 9090:127.0.0.1:9090 -L 3000:127.0.0.1:3000 ubuntu@${aws_instance.k3s.public_ip}" : "Use Session Manager port forwarding"
}
