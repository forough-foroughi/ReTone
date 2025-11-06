variable "kubeconfig_path" {
    type = string
    default = "~/.kube/config"
}

variable "kube_context" {
    type = string
    default = null                      # set if you have many contexts
}

variable "namespace" {
    type = string
    default = "retone"
}

variable "chart_path" { 
    type = string  
    default = "../charts/retone" 
}

variable "image_repo" { 
    type = string  
    default = "242242/retone" 
}

variable "image_tag" { 
    type = string  
    default = "v0.2" 
}

variable "secret_name" { 
    type = string  
    default = "retone-secrets" 
}

variable "host" {                       #ingress config
    type = string  
    default = "retone.forough-foroughi.com" 
}

variable "ingress_classname" {
    type = string
    default = "traefik"
  
}

variable "service_port" { 
    type = string  
    default = "80" 
}

variable "service_targetPort" { 
    type = string  
    default = "5000" 
}
