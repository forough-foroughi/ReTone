resource "kubernetes_namespace" "ns" {
  metadata { name = var.namespace }
}

resource "helm_release" "retone" {
  name = "retone"
  namespace = kubernetes_namespace.ns.metadata[0].name
  chart = var.chart_path

  set = [ 
    {
        name = "image.repository"
        value = var.image_repo
    }, 
    {
        name = "image.tag"
        value = var.image_tag
    },
    {
        name = "service.port"       
        value = var.service_port
    },
    {
        name = "service.targetPort"
        value = var.service_targetPort
    },
    {
        name = "secretEnv.OPENROUTER_API_KEY.secretName"
        value = var.secret_name
    },
    {
        name = "secretEnv.OPENROUTER_API_KEY.key"
        value = "OPENROUTER_API_KEY"
    },
    {
        name = "ingress.enabled"
        value = "true"
    },
    {
        name = "ingress.className"
        value = var.ingress_classname
    },
    {
        name = "ingress.hosts[0].host"
        value = var.host
    },
    {
        name = "ingress.hosts[0].paths[0].path"
        value = "/"
    },
    {
        name = "ingress.hosts[0].paths[0].pathType"
        value = "Prefix"
    },
    {
        name = "serviceMonitor.enabled"
        value = "true"
    },
    {
        name = "serviceMonitor.releaseLabel"
        value = "kps"
    },
    {
        name = "serviceMonitor.path"
        value = "/metrics"
    },
    {
        name = "serviceMonitor.interval"
        value = "30s"
    }
  ]
}


resource "kubernetes_config_map" "retone_graghana_dashboard" {
  metadata {
    name      = "retone-dashboard"
    namespace = "monitoring"                 # kube-prom-stack namespace
    labels = {
      "grafana_dashboard" = "1"              # matches sidecar.dashboards.label
    }
  }

  data = {
    "retone-dashboard.json" = file("${path.module}/${var.grafana_dashboard_config_path}")
  }
}



 

