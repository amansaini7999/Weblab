targetScope = 'resourceGroup'

@description('Azure region for all resources.')
param location string

@description('Short environment name such as test or prod.')
param environmentName string

@description('Base project name used in resource naming.')
param projectName string = 'weblab'

@description('SKU for the Functions hosting plan.')
param functionPlanSku string = 'FC1'

@description('Hosting plan tier for the Function App.')
param functionPlanTier string = 'FlexConsumption'

@description('Python runtime version for the Function App runtime configuration.')
param functionRuntimeVersion string = '3.13'

@description('Memory allocation in MB for each Flex Consumption instance.')
param functionInstanceMemoryMb int = 2048

@description('Maximum instance count for the Flex Consumption Function App.')
param functionMaximumInstanceCount int = 100

@description('Deployment blob container name for Function App packages.')
param deploymentContainerName string = 'app-package'

@description('Log Analytics retention in days.')
param logAnalyticsRetentionDays int = 30

@description('Additional app settings to add to the Function App.')
param customAppSettings object = {}

module monitoring './modules/monitoring.bicep' = {
  params: {
    location: location
    environmentName: environmentName
    projectName: projectName
    logAnalyticsRetentionDays: logAnalyticsRetentionDays
  }
}

module storage './modules/storage.bicep' = {
  params: {
    location: location
    environmentName: environmentName
    projectName: projectName
    deploymentContainerName: deploymentContainerName
  }
}

module functionApp './modules/function-app.bicep' = {
  params: {
    location: location
    environmentName: environmentName
    projectName: projectName
    functionPlanSku: functionPlanSku
    functionPlanTier: functionPlanTier
    functionRuntimeVersion: functionRuntimeVersion
    instanceMemoryMb: functionInstanceMemoryMb
    maximumInstanceCount: functionMaximumInstanceCount
    storageAccountName: storage.outputs.name
    storageAccountResourceId: storage.outputs.resourceId
    deploymentContainerUrl: storage.outputs.deploymentContainerUrl
    applicationInsightsConnectionString: monitoring.outputs.applicationInsightsConnectionString
    logAnalyticsWorkspaceResourceId: monitoring.outputs.logAnalyticsWorkspaceResourceId
    customAppSettings: customAppSettings
  }
}

output functionAppName string = functionApp.outputs.functionAppName
output functionAppPrincipalId string = functionApp.outputs.functionAppPrincipalId
output functionAppDefaultHostname string = functionApp.outputs.functionAppDefaultHostname
output storageAccountName string = storage.outputs.name
output deploymentContainerUrl string = storage.outputs.deploymentContainerUrl
output applicationInsightsName string = monitoring.outputs.applicationInsightsName
output logAnalyticsWorkspaceName string = monitoring.outputs.logAnalyticsWorkspaceName
