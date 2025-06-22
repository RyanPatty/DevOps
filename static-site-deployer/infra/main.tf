terraform {
  required_version = ">= 1.5"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
  profile = "ryan_dev_home"
}

# Variables
variable "bucket_name" {
  description = "Name of the S3 bucket for static site hosting"
  type        = string
}

variable "github_repo" {
  description = "GitHub repository name (e.g., username/repo)"
  type        = string
}

# S3 bucket for static site hosting
resource "aws_s3_bucket" "static_site" {
  bucket = var.bucket_name

  tags = {
    Name        = "Static Site Bucket"
    Environment = "production"
    Project     = "static-site-deployer"
  }
}

# Enable versioning
resource "aws_s3_bucket_versioning" "static_site" {
  bucket = aws_s3_bucket.static_site.id
  versioning_configuration {
    status = "Enabled"
  }
}

# Configure static website hosting
resource "aws_s3_bucket_website_configuration" "static_site" {
  bucket = aws_s3_bucket.static_site.id

  index_document {
    suffix = "index.html"
  }

  error_document {
    key = "index.html"
  }
}

# Block public access (CloudFront will access via Origin Access Control)
resource "aws_s3_bucket_public_access_block" "static_site" {
  bucket = aws_s3_bucket.static_site.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Origin Access Control for CloudFront
resource "aws_cloudfront_origin_access_control" "static_site" {
  name                              = "static-site-oac"
  description                       = "Origin Access Control for Static Site"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}

# CloudFront distribution
resource "aws_cloudfront_distribution" "static_site" {
  enabled             = true
  is_ipv6_enabled     = true
  default_root_object = "index.html"
  price_class         = "PriceClass_100" # Use only North America and Europe

  origin {
    domain_name              = aws_s3_bucket.static_site.bucket_regional_domain_name
    origin_access_control_id = aws_cloudfront_origin_access_control.static_site.id
    origin_id                = "S3-${aws_s3_bucket.static_site.bucket}"
  }

  default_cache_behavior {
    allowed_methods        = ["GET", "HEAD"]
    cached_methods         = ["GET", "HEAD"]
    target_origin_id       = "S3-${aws_s3_bucket.static_site.bucket}"
    viewer_protocol_policy = "redirect-to-https"
    compress               = true

    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }

    min_ttl     = 0
    default_ttl = 3600
    max_ttl     = 86400
  }

  # Handle SPA routing - redirect 404s to index.html
  custom_error_response {
    error_code         = 404
    response_code      = "200"
    response_page_path = "/index.html"
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    cloudfront_default_certificate = true
    minimum_protocol_version       = "TLSv1.2_2021"
  }

  tags = {
    Name        = "Static Site Distribution"
    Environment = "production"
    Project     = "static-site-deployer"
  }
}

# Outputs
output "bucket_name" {
  description = "Name of the S3 bucket"
  value       = aws_s3_bucket.static_site.bucket
}

output "cloudfront_distribution_id" {
  description = "ID of the CloudFront distribution"
  value       = aws_cloudfront_distribution.static_site.id
}

output "cloudfront_url" {
  description = "URL of the CloudFront distribution"
  value       = "https://${aws_cloudfront_distribution.static_site.domain_name}"
}

output "s3_website_url" {
  description = "S3 website URL (for reference only - CloudFront is the main URL)"
  value       = aws_s3_bucket_website_configuration.static_site.website_endpoint
}
