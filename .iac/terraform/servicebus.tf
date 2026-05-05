# ----------------------------------------
# Cocktail Updates Scheduled On-Prem Queue (sbq-)
# Subscription on the cloudsync topic forwards
# matching messages here. On-prem consumer reads from
# this queue (infra owned here, consumer is same as sender).
# ----------------------------------------
module "cloudsync_servicebus_cocktail_updates_scheduled_onprem_queue" {
  source = "git::ssh://git@github.com/mtnvencenzo/Terraform-Modules.git//modules/servicebus-queue"

  namespace_id        = data.azurerm_servicebus_namespace.servicebus_namespace.id
  name_discriminator  = "updates-sched-onprem"
  sub                 = var.sub
  region              = var.region
  environment         = var.environment
  domain              = var.domain
  resource_group_name = data.azurerm_resource_group.cocktails_resource_group.name
  location            = data.azurerm_resource_group.cocktails_resource_group.location

  providers = {
    azurerm = azurerm
  }

  tags = local.tags
}

# ----------------------------------------
# SAS Policy — Listen-only on the on-prem sync queue
# External on-prem consumer uses this key to read messages
# ----------------------------------------
resource "azurerm_servicebus_queue_authorization_rule" "cloudsync_servicebus_cocktail_updates_scheduled_onprem_listen" {
  name     = "listen"
  queue_id = module.cloudsync_servicebus_cocktail_updates_scheduled_onprem_queue.id
  listen   = true
  send     = false
  manage   = false
}

# ----------------------------------------
# On-prem sync queue Listen SAS primary key
# External consumer uses this to read messages
# ----------------------------------------
resource "azurerm_key_vault_secret" "cocktails_updates_sync_scheduled_onprem_listen_primary_key" {
  name         = "cocktails-updates-sync-scheduled-onprem-queue-listen-primary-key"
  value        = azurerm_servicebus_queue_authorization_rule.cloudsync_servicebus_cocktail_updates_scheduled_onprem_listen.primary_key
  key_vault_id = data.azurerm_key_vault.cocktails_onprem_keyvault.id
  tags         = local.tags
}

resource "azurerm_key_vault_secret" "cocktails_updates_sync_scheduled_onprem_listen_secondary_key" {
  name         = "cocktails-updates-sync-scheduled-onprem-queue-listen-secondary-key"
  value        = azurerm_servicebus_queue_authorization_rule.cloudsync_servicebus_cocktail_updates_scheduled_onprem_listen.secondary_key
  key_vault_id = data.azurerm_key_vault.cocktails_onprem_keyvault.id
  tags         = local.tags
}

# ----------------------------------------
# Subscription on cocktail-updates topic → forwards to on-prem queue
# ----------------------------------------
module "cloudsync_servicebus_cocktail_updates_scheduled_onprem_subscription" {
  source = "git::ssh://git@github.com/mtnvencenzo/Terraform-Modules.git//modules/servicebus-subscription"

  topic_id            = data.azurerm_servicebus_topic.onprem_cloudsync_topic.id
  forward_to          = module.cloudsync_servicebus_cocktail_updates_scheduled_onprem_queue.name
  name_discriminator  = "updates-sched-onprem"
  sub                 = var.sub
  region              = var.region
  environment         = var.environment
  domain              = var.domain
  resource_group_name = data.azurerm_resource_group.cocktails_resource_group.name
  location            = data.azurerm_resource_group.cocktails_resource_group.location

  providers = {
    azurerm = azurerm
  }

  tags = local.tags
}

# ----------------------------------------
# Subscription rule — only forward messages with
# correlation filter label "cocktail.data.updated-scheduled"
# ----------------------------------------
module "cloudsync_servicebus_cocktail_updates_scheduled_onprem_subscription_rule" {
  source = "git::ssh://git@github.com/mtnvencenzo/Terraform-Modules.git//modules/servicebus-subscription-rule-correlation"

  subscription_id          = module.cloudsync_servicebus_cocktail_updates_scheduled_onprem_subscription.id
  correlation_filter_label = "cocktail.data.updated-scheduled"

  providers = {
    azurerm = azurerm
  }
}

