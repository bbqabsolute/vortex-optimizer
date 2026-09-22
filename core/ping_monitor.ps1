# ============================================================
#  ping_monitor.ps1 - Fortnite Optimizer
#  Tests ping to regional Fortnite & DNS servers
# ============================================================
$servers = @(
    [PSCustomObject]@{Region="NA East";     Host="3.208.77.48"},
    [PSCustomObject]@{Region="NA West";     Host="52.88.93.104"},
    [PSCustomObject]@{Region="EU";          Host="18.184.96.48"},
    [PSCustomObject]@{Region="Asia (SG)";   Host="13.250.58.207"},
    [PSCustomObject]@{Region="Oceania";     Host="13.236.69.139"},
    [PSCustomObject]@{Region="Epic API";    Host="epicgames.com"},
    [PSCustomObject]@{Region="Cloudflare";  Host="1.1.1.1"},
    [PSCustomObject]@{Region="Google DNS";  Host="8.8.8.8"}
)

$results = @()
$bestPing = 9999
$bestRegion = ""

foreach ($s in $servers) {
    try {
        $pings = Test-Connection -ComputerName $s.Host -Count 2 -ErrorAction Stop -WarningAction SilentlyContinue
        $avg = [int]($pings.ResponseTime | Measure-Object -Average).Average
        $barLen = [math]::Min([int]($avg/5), 25)
        $bar = "#" * $barLen

        $status = if ($avg -lt 40) { "EXCELLENT" }
                  elseif ($avg -lt 70) { "GOOD" }
                  elseif ($avg -lt 110) { "AVERAGE" }
                  else { "HIGH" }

        $line = "  {0,-14} {1,4}ms  [{2}] {3}" -f $s.Region, $avg, $bar.PadRight(20), $status
        Write-Host $line

        if ($avg -lt $bestPing -and $s.Region -notmatch "Cloudflare|Google|Epic") {
            $bestPing = $avg
            $bestRegion = $s.Region
        }
        $results += [PSCustomObject]@{Region=$s.Region; Avg=$avg}
    } catch {
        Write-Host ("  {0,-14} UNREACHABLE" -f $s.Region)
    }
}

Write-Host ""
Write-Host "  ================================================"
if ($bestRegion) {
    Write-Host "  Best region: $bestRegion ($bestPing ms)"
    Write-Host "  Select '$bestRegion' in Fortnite settings!"
}
Write-Host "  ================================================"
Write-Host ""
$internetPing = ($results | Where-Object {$_.Region -eq "Cloudflare"}).Avg
if ($internetPing) {
    if ($internetPing -lt 10) { Write-Host "  Internet: excellent (<10ms base ping)" }
    elseif ($internetPing -lt 30) { Write-Host "  Internet: good (~${internetPing}ms base ping)" }
    else { Write-Host "  Internet: fair/high (~${internetPing}ms base ping)" }
}
