targetScope = 'resourceGroup'

@description('Azure region for all resources.')
param location string

@description('Short environment name such as test or prod.')
param environmentName string

@description('Base project name used in resource naming.')
param projectName string

@description('PostgreSQL administrator login name.')
param administratorLogin string

@description('PostgreSQL administrator password.')
@secure()
param administratorPassword string

@description('PostgreSQL SKU name.')
param skuName string

@description('PostgreSQL storage size in GiB.')
param storageSizeGb int

@description('PostgreSQL backup retention days.')
param backupRetentionDays int

@description('Database name for the application.')
param databaseName string

var serverName = 'psql-${projectName}-${environmentName}'

resource server 'Microsoft.DBforPostgreSQL/flexibleServers@2023-12-01-preview' = {
  name: serverName
  location: location
  sku: {
    name: skuName
    tier: 'Burstable'
  }
  properties: {
    administratorLogin: administratorLogin
    administratorLoginPassword: administratorPassword
    version: '16'
    availabilityZone: '1'
    createMode: 'Create'
    storage: {
      storageSizeGB: storageSizeGb
      autoGrow: 'Enabled'
      tier: 'P4'
    }
    backup: {
      backupRetentionDays: backupRetentionDays
      geoRedundantBackup: 'Disabled'
    }
    highAvailability: {
      mode: 'Disabled'
    }
    network: {
      publicNetworkAccess: 'Enabled'
    }
    maintenanceWindow: {
      customWindow: 'Disabled'
      dayOfWeek: 0
      startHour: 0
      startMinute: 0
    }
    authConfig: {
      activeDirectoryAuth: 'Disabled'
      passwordAuth: 'Enabled'
      tenantId: subscription().tenantId
    }
  }
}

resource database 'Microsoft.DBforPostgreSQL/flexibleServers/databases@2023-12-01-preview' = {
  name: databaseName
  parent: server
  properties: {
    charset: 'UTF8'
    collation: 'en_US.utf8'
  }
}

output serverName string = server.name
output databaseName string = database.name
output fullyQualifiedDomainName string = server.properties.fullyQualifiedDomainName
output resourceId string = server.id
