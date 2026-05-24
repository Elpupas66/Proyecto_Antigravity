[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$body = @{
    action = "COMPRAR"
    symbol = "BTCUSD"
    volume = 0.01
    order_type = "MERCADO"
    price = 0
    sl = 10000
    tp = 100000
    justification = "Porque el precio está retrocediendo en una clara tendencia bajista."
} | ConvertTo-Json -Depth 10

# Asegurar que el body se envíe como UTF-8
$bodyBytes = [System.Text.Encoding]::UTF8.GetBytes($body)

$headers = @{
    "Content-Type" = "application/json"
    "X-API-Key" = "antigravity-secure-key-2024"
}

Write-Host "=== TEST LOCAL /validate ===" -ForegroundColor Cyan
$response = Invoke-RestMethod -Uri "http://localhost:8000/validate" -Method POST -Body $bodyBytes -ContentType "application/json; charset=utf-8" -Headers $headers
Write-Host ($response | ConvertTo-Json) -ForegroundColor Green

Write-Host "`n=== TEST CLOUDFLARE /validate ===" -ForegroundColor Cyan
$response2 = Invoke-RestMethod -Uri "https://gatekeeper.jmbv-trader.org/validate" -Method POST -Body $bodyBytes -ContentType "application/json; charset=utf-8" -Headers $headers
Write-Host ($response2 | ConvertTo-Json) -ForegroundColor Green
