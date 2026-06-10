# get-computer-id.ps1 - Get computer's unique ID (MAC address)
# Works on Windows PowerShell

$adapter = Get-NetAdapter | Where-Object { $_.Status -eq 'Up' } | Select-Object -First 1
if ($adapter) {
    $mac = $adapter.MacAddress -replace '-', '' -replace ':', ''
    Write-Output $mac.ToLower()
} else {
    Write-Error "No active network adapter found"
    exit 1
}
