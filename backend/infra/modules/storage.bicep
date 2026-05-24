targetScope = 'resourceGroup'

@description('Azure region for all resources.')
param location string

@description('Short environment name such as test or prod.')
param environmentName string

@description('Base project name used in resource naming.')
param projectName string

@description('Blob container used by Flex Consumption deployment packages.')
param deploymentContainerName string = 'app-package'

var storageName = toLower('${take(projectName, 3)}${environmentName}${take(uniqueString(resourceGroup().id, projectName, environmentName), 12)}st')

resource storageAccount 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: storageName
  location: location
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  properties: {
    accessTier: 'Hot'
    allowBlobPublicAccess: false
    minimumTlsVersion: 'TLS1_2'
    supportsHttpsTrafficOnly: true
    allowSharedKeyAccess: true
    networkAcls: {
      defaultAction: 'Allow'
      bypass: 'AzureServices'
    }
  }
}

resource blobService 'Microsoft.Storage/storageAccounts/blobServices@2023-05-01' = {
  name: 'default'
  parent: storageAccount
}

resource deploymentContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-05-01' = {
  name: deploymentContainerName
  parent: blobService
  properties: {
    publicAccess: 'None'
  }
}

output name string = storageAccount.name
output resourceId string = storageAccount.id
output deploymentContainerName string = deploymentContainer.name
output deploymentContainerUrl string = 'https://${storageAccount.name}.blob.${environment().suffixes.storage}/${deploymentContainer.name}'
