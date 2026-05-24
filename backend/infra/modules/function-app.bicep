targetScope = 'resourceGroup'

@description('Azure region for all resources.')
param location string

@description('Short environment name such as test or prod.')
param environmentName string

@description('Base project name used in resource naming.')
param projectName string

@description('SKU for the Functions hosting plan.')
param functionPlanSku string

@description('Hosting plan tier for the Function App.')
param functionPlanTier string

@description('Python runtime version for the Function App runtime configuration.')
param functionRuntimeVersion string

@description('Memory allocation in MB for each Flex Consumption instance.')
param instanceMemoryMb int

@description('Maximum instance count for the Flex Consumption Function App.')
param maximumInstanceCount int

@description('Storage account name for AzureWebJobsStorage.')
param storageAccountName string

@description('Storage account resource identifier.')
param storageAccountResourceId string

@description('Deployment blob container URL for Function App packages.')
param deploymentContainerUrl string

@description('Application Insights connection string.')
param applicationInsightsConnectionString string

@description('Log Analytics workspace resource ID.')
param logAnalyticsWorkspaceResourceId string

@description('Additional app settings to add to the Function App.')
param customAppSettings object

var planName = '${projectName}-${environmentName}-plan'
var functionAppName = '${projectName}-${environmentName}-func'
var storageKeys = listKeys(storageAccountResourceId, '2023-05-01')
var storageConnectionString = 'DefaultEndpointsProtocol=https;AccountName=${storageAccountName};AccountKey=${storageKeys.keys[0].value};EndpointSuffix=${environment().suffixes.storage}'
var baseAppSettings = {
  APPLICATIONINSIGHTS_CONNECTION_STRING: applicationInsightsConnectionString
  AzureWebJobsStorage: storageConnectionString
  DEPLOYMENT_STORAGE_CONNECTION_STRING: storageConnectionString
}
var mergedAppSettings = union(baseAppSettings, customAppSettings)

resource plan 'Microsoft.Web/serverfarms@2023-12-01' = {
  name: planName
  location: location
  kind: 'functionapp'
  sku: {
    name: functionPlanSku
    tier: functionPlanTier
    size: functionPlanSku
    family: 'FC'
    capacity: 0
  }
  properties: {
    reserved: true
  }
}

resource functionApp 'Microsoft.Web/sites@2023-12-01' = {
  name: functionAppName
  location: location
  kind: 'functionapp,linux'
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    enabled: true
    httpsOnly: true
    clientAffinityEnabled: false
    publicNetworkAccess: 'Enabled'
    serverFarmId: plan.id
    functionAppConfig: {
      deployment: {
        storage: {
          type: 'blobContainer'
          value: deploymentContainerUrl
          authentication: {
            type: 'StorageAccountConnectionString'
            storageAccountConnectionStringName: 'DEPLOYMENT_STORAGE_CONNECTION_STRING'
          }
        }
      }
      runtime: {
        name: 'python'
        version: functionRuntimeVersion
      }
      scaleAndConcurrency: {
        instanceMemoryMB: instanceMemoryMb
        maximumInstanceCount: maximumInstanceCount
      }
    }
    siteConfig: {
      minTlsVersion: '1.2'
      ftpsState: 'FtpsOnly'
      use32BitWorkerProcess: false
      linuxFxVersion: ''
    }
    virtualNetworkSubnetId: null
  }
}

resource appSettingsConfig 'Microsoft.Web/sites/config@2023-12-01' = {
  name: 'appsettings'
  parent: functionApp
  properties: mergedAppSettings
}

resource diagnosticSettings 'Microsoft.Insights/diagnosticSettings@2021-05-01-preview' = {
  name: '${functionAppName}-diagnostics'
  scope: functionApp
  properties: {
    workspaceId: logAnalyticsWorkspaceResourceId
    logs: [
      {
        categoryGroup: 'allLogs'
        enabled: true
      }
    ]
    metrics: [
      {
        category: 'AllMetrics'
        enabled: true
      }
    ]
  }
}

output functionAppName string = functionApp.name
output functionAppPrincipalId string = functionApp.identity.principalId
output functionAppDefaultHostname string = functionApp.properties.defaultHostName
output planName string = plan.name
