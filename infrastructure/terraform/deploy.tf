resource "kubernetes_service" "app_service" {
  metadata {
    name = "${var.app_name}-port"
  }
  spec {
    selector {
      app = "${var.app_name}"
    }
    session_affinity = "ClientIP"
    port {
      port = 80
      target_port = 80
    }

    type = "NodePort"
  }
}

resource "kubernetes_deployment" "app" {
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
        }
      }
    }
  }
}