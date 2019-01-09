resource "kubernetes_service" "app_service" {
  metadata {
    name = "api-service"
  }
  spec {
    selector {
      app = "${var.app_name}"
    }
    session_affinity = "ClientIP"
    port {
      name = "api-port"
      port = 80
      target_port = 8000
    }

    type = "NodePort"
  }
}

resource "kubernetes_deployment" "app" {
  depends_on = ["kubernetes_secret.app_secrets"]
  metadata {
    name = "${var.app_name}"
    labels {
      sha = "${var.commit_sha}"
      app = "${var.app_name}"
    }
  }

  spec {
    replicas = 1

    selector {
      match_labels {
        app = "${var.app_name}"
      }
    }

    template {
      metadata {
        labels {
          sha = "${var.commit_sha}"
          app = "${var.app_name}"
        }
      }

      spec {
        container {
          image = "${var.image}"
          name  = "${var.app_name}"

          port {
            container_port = 8000
          }

          env {
            name = "DJANGO_SECRET_KEY"
            value_from {
              secret_key_ref {
                name = "${var.app_name}"
                key = "django_secret_key"
              }
            }
          }
          env {
            name = "DB_USER"
            value = "${local.db_user}"
          }
          env {
            name = "DB_PASS"
            value_from {
              secret_key_ref {
                name = "${var.app_name}"
                key = "db_pass"
              }
            }
          }
          env {
            name = "DB_HOST"
            value = "${var.db_host}"
          }
          env {
            name = "DB_NAME"
            value = "${var.app_name}"
          }
          env {
            name = "HOST_DOMAIN"
            value = "${var.api_domain}"
          }
          env {
            name = "STATIC_ROOT"
            value = "${var.static_root}"
          }
          env {
            name = "DJANGO_SETTINGS_MODULE"
            value = "posts.settings.${var.environment}"
          }
          liveness_probe {
            http_get {
              path = "/health"
              port = 8000
              http_header {
                name  = "Host"
                value = "${var.api_domain}"
              }
            }
            initial_delay_seconds = 5
            period_seconds        = 5
          }
          readiness_probe {
            http_get {
              path = "/health"
              port = 8000
              http_header {
                name  = "Host"
                value = "${var.api_domain}"
              }
            }
            initial_delay_seconds = 5
            period_seconds        = 5
          }
        }
      }
    }
  }
}