terraform {
  backend "gcs" {
  }
}

provider "google" {
    project = "${var.project_id}"
}

# passed from outside
variable project_id {
    type = "string"
}

variable state_bucket {
    type = "string"
}

variable app_name {
    type = "string"
}


# internal
variable domain_name {
    type = "string"
}