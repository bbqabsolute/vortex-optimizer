# ============================================================
#  pagefile_optimize.ps1 - Fortnite Optimizer
#  Configures optimal fixed size pagefile
# ============================================================
try {
    $cs = Get-CimInstance Win32_ComputerSystem
    $ramMB = [int]($cs.TotalPhysicalMemory / 1MB)
    if ($ramMB -le 0) { $ramMB = 8192 }
    Write-Host "[PGF] Detected RAM: $ramMB MB"

    if ($ramMB -le 8192) {
        $minPF = $ramMB
        $maxPF = $ramMB * 2
    } else {
        $minPF = 4096
        $maxPF = [int]($ramMB * 1.25)
    }
    Write-Host "[PGF] Pagefile sizing: $minPF MB (min) / $maxPF MB (max)"

    $sysDrive = $env:SystemDrive

    try {
        $disk = Get-PhysicalDisk | Where-Object {
            $part = Get-Partition -DriveLetter ($sysDrive[0]) -ErrorAction SilentlyContinue
            if ($part) { $part.DiskNumber -eq $_.DeviceId }
        } | Select-Object -First 1
        if ($disk -and ($disk.MediaType -eq "SSD" -or $disk.MediaType -eq "NVMe")) {
            Write-Host "[PGF] Drive: SSD/NVMe - optimal for pagefile"
        } else {
            Write-Host "[PGF] Drive: HDD - SSD recommended for pagefile"
        }
    } catch { }

    Set-CimInstance -InputObject $cs -Property @{AutomaticManagedPagefile = $false} -ErrorAction SilentlyContinue | Out-Null

    $pf = Get-CimInstance -ClassName Win32_PageFileSetting -Filter "Name='$sysDrive\\pagefile.sys'" -ErrorAction SilentlyContinue
    if (!$pf) {
        New-CimInstance -ClassName Win32_PageFileSetting -Property @{
            Name = "$sysDrive\pagefile.sys"
            InitialSize = $minPF
            MaximumSize = $maxPF
        } -ErrorAction SilentlyContinue | Out-Null
    } else {
        Set-CimInstance -InputObject $pf -Property @{
            InitialSize = $minPF
            MaximumSize = $maxPF
        } -ErrorAction SilentlyContinue | Out-Null
    }

    Write-Host "[PGF] + Pagefile set: ${minPF}MB - ${maxPF}MB"
    Write-Host "[PGF] + Location: $sysDrive\pagefile.sys"
    Write-Host "[PGF] ! Changes take effect after REBOOT"
} catch {
    Write-Host "[PGF] ! Note: Run as Administrator to apply pagefile changes"
}
