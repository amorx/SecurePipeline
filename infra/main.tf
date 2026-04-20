# 1. Define the Cloud Provider
provider "aws" {
  region = "ap-southeast-2" # Sydney region
}

# 2. Create a Private Network (VPC)
# So the vault is not accessible directly from the open internet
resource "aws_vpc" "vault_vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true

  tags = {
    Name = "secure-vault-network"
  }
}

# 3. Secure Security Group (The Firewall)
resource "aws_security_group" "vault_sg" {
  name        = "vault-security-group"
  description = "Allow restricted access to the secure vault"
  vpc_id      = aws_vpc.vault_vpc.id

  # Only allow HTTPS traffic on 443
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["1.2.3.4/32"] # Replace with your specific IP
  }

  # Allow the vault to talk to the internet for updates
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
