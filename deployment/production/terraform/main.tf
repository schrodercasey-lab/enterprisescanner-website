
provider "aws" {
  region = var.aws_region
}

variable "aws_region" {
  default = "us-east-1"
}

variable "domain_name" {
  default = "enterprisescanner.com"
}

# VPC Configuration
resource "aws_vpc" "enterprise_vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true
  
  tags = {
    Name = "Enterprise-Scanner-VPC"
    Environment = "Production"
  }
}

# Internet Gateway
resource "aws_internet_gateway" "enterprise_igw" {
  vpc_id = aws_vpc.enterprise_vpc.id
  
  tags = {
    Name = "Enterprise-Scanner-IGW"
  }
}

# Public Subnets
resource "aws_subnet" "public_subnet_a" {
  vpc_id                  = aws_vpc.enterprise_vpc.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "${var.aws_region}a"
  map_public_ip_on_launch = true
  
  tags = {
    Name = "Enterprise-Public-A"
  }
}

resource "aws_subnet" "public_subnet_b" {
  vpc_id                  = aws_vpc.enterprise_vpc.id
  cidr_block              = "10.0.2.0/24"
  availability_zone       = "${var.aws_region}b"
  map_public_ip_on_launch = true
  
  tags = {
    Name = "Enterprise-Public-B"
  }
}

# Security Groups
resource "aws_security_group" "web_sg" {
  name_prefix = "enterprise-web-"
  vpc_id      = aws_vpc.enterprise_vpc.id
  
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/16"]
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = {
    Name = "Enterprise-Web-SG"
  }
}

# Application Load Balancer
resource "aws_lb" "enterprise_alb" {
  name               = "enterprise-scanner-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.web_sg.id]
  subnets           = [aws_subnet.public_subnet_a.id, aws_subnet.public_subnet_b.id]
  
  enable_deletion_protection = false
  
  tags = {
    Name = "Enterprise-Scanner-ALB"
  }
}

# EC2 Instances
resource "aws_instance" "enterprise_app" {
  count           = 2
  ami             = "ami-0c02fb55956c7d316"  # Amazon Linux 2
  instance_type   = "t3.large"
  key_name        = aws_key_pair.enterprise_key.key_name
  subnet_id       = count.index == 0 ? aws_subnet.public_subnet_a.id : aws_subnet.public_subnet_b.id
  security_groups = [aws_security_group.web_sg.id]
  
  user_data = base64encode(templatefile("${path.module}/user_data.sh", {
    domain_name = var.domain_name
  }))
  
  tags = {
    Name = "Enterprise-Scanner-App-${count.index + 1}"
    Environment = "Production"
  }
}

# RDS Database
resource "aws_db_subnet_group" "enterprise_db_subnet" {
  name       = "enterprise-db-subnet"
  subnet_ids = [aws_subnet.public_subnet_a.id, aws_subnet.public_subnet_b.id]
  
  tags = {
    Name = "Enterprise DB Subnet Group"
  }
}

resource "aws_db_instance" "enterprise_db" {
  identifier = "enterprise-scanner-db"
  
  engine         = "postgres"
  engine_version = "15.7"
  instance_class = "db.t3.medium"
  
  allocated_storage     = 100
  max_allocated_storage = 1000
  storage_type          = "gp2"
  storage_encrypted     = true
  
  db_name  = "enterprise_scanner"
  username = "postgres"
  password = "SecurePassword123!"
  
  vpc_security_group_ids = [aws_security_group.db_sg.id]
  db_subnet_group_name   = aws_db_subnet_group.enterprise_db_subnet.name
  
  backup_retention_period = 30
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"
  
  skip_final_snapshot = true
  deletion_protection = false
  
  tags = {
    Name = "Enterprise-Scanner-DB"
  }
}

# Database Security Group
resource "aws_security_group" "db_sg" {
  name_prefix = "enterprise-db-"
  vpc_id      = aws_vpc.enterprise_vpc.id
  
  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.web_sg.id]
  }
  
  tags = {
    Name = "Enterprise-DB-SG"
  }
}

# Route Table
resource "aws_route_table" "public_rt" {
  vpc_id = aws_vpc.enterprise_vpc.id
  
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.enterprise_igw.id
  }
  
  tags = {
    Name = "Enterprise-Public-RT"
  }
}

resource "aws_route_table_association" "public_rta_a" {
  subnet_id      = aws_subnet.public_subnet_a.id
  route_table_id = aws_route_table.public_rt.id
}

resource "aws_route_table_association" "public_rta_b" {
  subnet_id      = aws_subnet.public_subnet_b.id
  route_table_id = aws_route_table.public_rt.id
}

# Key Pair (you'll need to provide the public key)
resource "aws_key_pair" "enterprise_key" {
  key_name   = "enterprise-scanner-key"
  public_key = file("~/.ssh/id_rsa.pub")  # Update this path
}

# Outputs
output "load_balancer_dns" {
  value = aws_lb.enterprise_alb.dns_name
}

output "database_endpoint" {
  value = aws_db_instance.enterprise_db.endpoint
}

output "instance_ips" {
  value = aws_instance.enterprise_app[*].public_ip
}
