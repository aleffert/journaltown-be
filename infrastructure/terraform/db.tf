locals {
  db_instance_name = "${var.app_name}-app-db"
  db_user = "${var.app_name}"
}

 resource "google_sql_database" "app" {
   name      = "${var.app_name}"
   instance  = "${local.db_instance_name}"
 }

 resource "google_sql_user" "app" {
   name     = "${local.db_user}"
   password = "${var.db_pass}"
   instance  = "${local.db_instance_name}"
 }