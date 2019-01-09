variable django_secret_key {
    type = "string"
}

variable db_pass {
    type = "string"
}

variable mailgun_api_key {
  type = "string"
}

resource "kubernetes_secret" "app_secrets" {
  metadata {
    name = "${var.app_name}"
  }

  data {
    django_secret_key = "${var.django_secret_key}"
    db_pass = "${var.db_pass}"
    mailgun_api_key = "${var.mailgun_api_key}"
  }

}