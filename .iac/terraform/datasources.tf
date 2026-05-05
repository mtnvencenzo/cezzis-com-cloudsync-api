data "azurerm_client_config" "current" {}

data "azurerm_resource_group" "cocktails_resource_group" {
  name = "rg-${var.sub}-${var.region}-${var.cloud_environment}-${var.cocktails_domain}-${var.sequence}"
}

data "azurerm_resource_group" "global_shared_resource_group" {
  name = "rg-${var.sub}-${var.region}-${var.global_environment}-shared-${var.sequence}"
}

data "azurerm_servicebus_namespace" "servicebus_namespace" {
  resource_group_name = data.azurerm_resource_group.global_shared_resource_group.name
  name                = "sb-${var.sub}-${var.region}-${var.global_environment}-shared-${var.sequence}"
}

data "azurerm_servicebus_topic" "onprem_cloudsync_topic" {
  name         = "sbt-${var.sub}-${var.region}-${var.environment}-${var.cocktails_domain}-cloud-sync-${var.sequence}"
  namespace_id = data.azurerm_servicebus_namespace.servicebus_namespace.id
}

data "azurerm_key_vault" "cocktails_onprem_keyvault" {
  name                = "kv-${var.sub}-${var.region}-prm-${var.cocktails_shortdomain}-${var.short_sequence}"
  resource_group_name = data.azurerm_resource_group.cocktails_resource_group.name
}

