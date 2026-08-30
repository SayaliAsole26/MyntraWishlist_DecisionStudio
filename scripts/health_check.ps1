# Pre-deploy health smoke test (PowerShell).
# Usage: .\scripts\health_check.ps1
#        .\scripts\health_check.ps1 -BaseUrl http://127.0.0.1:8002

param(
    [string]$BaseUrl = "http://127.0.0.1:8002"
)

$ErrorActionPreference = "Stop"

Write-Host "Checking $BaseUrl/health ..."
$health = Invoke-RestMethod "$BaseUrl/health"
$health | ConvertTo-Json -Compress

if ($health.status -ne "ok") {
    throw "Health status is not ok: $($health | ConvertTo-Json -Compress)"
}

# New health payload (Railway-ready)
if ($null -ne $health.PSObject.Properties["catalog_ready"]) {
    if (-not $health.catalog_ready) {
        throw "Catalog not ready"
    }
    if ($health.product_count -le 0) {
        throw "No products in catalog"
    }
    Write-Host "Health OK - $($health.product_count) products"
} else {
    Write-Host "Health OK (legacy payload - restart backend for catalog_ready fields)"
}

Write-Host "Checking categories ..."
$categories = Invoke-RestMethod "$BaseUrl/api/products/categories/list"
Write-Host "Categories: $($categories.Count)"

Write-Host "Checking products ..."
$products = Invoke-RestMethod "$BaseUrl/api/products"
Write-Host "Products: $($products.products.Count)"

Write-Host "All checks passed."
