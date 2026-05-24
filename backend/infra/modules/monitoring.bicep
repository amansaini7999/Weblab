targetScope = 'resourceGroup'

@description('Azure region for all resources.')
param location string

@description('Short environment name such as test or prod.')
param environmentName string

@description('Base project name used in resource naming.')
param projectName string

@description('Log Analytics retention in days.')
param logAnalyticsRetentionDays int

var workspaceName = '${projectName}-${environmentName}-log'
var applicationInsightsName = '${projectName}-${environmentName}-appi'

resource workspace 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: workspaceName
  location: location
  properties: {
    retentionInDays: logAnalyticsRetentionDays
    features: {
      searchVersion: 1
      legacy: 0
      enableLogAccessUsingOnlyResourcePermissions: true
    }
    sku: {
      name: 'PerGB2018'
    }
  }
}

resource applicationInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: applicationInsightsName
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: workspace.id
    publicNetworkAccessForIngestion: 'Enabled'
    publicNetworkAccessForQuery: 'Enabled'
    RetentionInDays: logAnalyticsRetentionDays
    IngestionMode: 'LogAnalytics'
    DisableIpMasking: false
    Request_Source: 'rest'
  }
}

output applicationInsightsName string = applicationInsights.name
output applicationInsightsConnectionString string = applicationInsights.properties.ConnectionString
output applicationInsightsInstrumentationKey string = applicationInsights.properties.InstrumentationKey
output logAnalyticsWorkspaceName string = workspace.name
output logAnalyticsWorkspaceResourceId string = workspace.id
