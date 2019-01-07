terraform {
  backend "gcs" {
  }
}

provider "google" {
    project = "${var.project_id}"
}

provider "kubernetes" {
}

# passed from outside
variable project_id {
    type = "string"
}

variable region {
    type = "string"
}

variable state_bucket {
    type = "string"
}

variable app_name {
    type = "string"
}

variable commit_sha {
    type = "string"
}

variable image {
    type = "string"
}

variable environment {
    type = "string"
}

# from vars file
variable api_domain {
    type = "string"
}

variable db_user {
    type = "string"
}