
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
