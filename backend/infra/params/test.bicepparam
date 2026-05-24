using '../main.bicep'

param location = 'eastus'
param environmentName = 'test'
param projectName = 'weblab'
param functionPlanSku = 'FC1'
param functionPlanTier = 'FlexConsumption'
param functionRuntimeVersion = '3.13'
param functionInstanceMemoryMb = 2048
param functionMaximumInstanceCount = 100
param deploymentContainerName = 'app-package'
param logAnalyticsRetentionDays = 30
param customAppSettings = {
  App__Environment: 'test'
}
