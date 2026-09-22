# ============================================================
#  msi_mode.ps1 - Fortnite Optimizer
#  Enables Message Signaled Interrupts (MSI) for GPU and NIC
# ============================================================
$count = 0
$gpuCount = 0
$nicCount = 0
$pciPath = "HKLM:\SYSTEM\CurrentControlSet\Enum\PCI"

try {
    $devs = Get-ChildItem $pciPath -ErrorAction SilentlyContinue
    foreach ($dev in $devs) {
        $insts = Get-ChildItem $dev.PSPath -ErrorAction SilentlyContinue
        foreach ($inst in $insts) {
            $props = Get-ItemProperty $inst.PSPath -ErrorAction SilentlyContinue
            $class = $props.Class
            if ($class -eq "Display" -or $class -eq "Net") {
                $msiPath = "$($inst.PSPath)\Device Parameters\Interrupt Management\MessageSignaledInterruptProperties"
                $affPath = "$($inst.PSPath)\Device Parameters\Interrupt Management\Affinity Policy"
                if (!(Test-Path $msiPath)) { New-Item -Path $msiPath -Force | Out-Null }
                Set-ItemProperty -Path $msiPath -Name "MSISupported" -Value 1 -Type DWord -Force
                if (!(Test-Path $affPath)) { New-Item -Path $affPath -Force | Out-Null }
                Set-ItemProperty -Path $affPath -Name "DevicePriority" -Value 3 -Type DWord -Force
                $count++
                $devName = $props.FriendlyName
                if ($class -eq "Display") { $gpuCount++; Write-Host "  [MSI] GPU: $devName" }
                if ($class -eq "Net") { $nicCount++; Write-Host "  [MSI] NIC: $devName" }
            }
        }
    }
    Write-Host "[MSI] + MSI enabled for $count devices (GPU: $gpuCount, NIC: $nicCount)"
} catch {
    Write-Host "[MSI] ! Warning during MSI configuration: $_"
}
