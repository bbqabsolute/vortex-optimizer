# ============================================================
#  fortnite_ini.ps1 - Fortnite Optimizer
#  Deep INI tweaks for Engine.ini and GameUserSettings.ini
# ============================================================
$fnCfg = "$env:LOCALAPPDATA\FortniteGame\Saved\Config\WindowsClient"
if (!(Test-Path $fnCfg)) {
    Write-Host "[INI] ! Fortnite config folder not found"
    exit 0
}

function Set-IniValue($lines, $section, $key, $val) {
    $secIdx = -1; $keyFound = $false
    for ($i=0; $i -lt $lines.Count; $i++) {
        if ($lines[$i] -match "^\[$section\]") { $secIdx = $i }
        if ($secIdx -ge 0 -and $lines[$i] -match "^$key=") {
            $lines[$i] = "$key=$val"; $keyFound = $true; break
        }
    }
    if (-not $keyFound) {
        if ($secIdx -ge 0) { $lines = $lines[0..$secIdx] + "$key=$val" + $lines[($secIdx+1)..($lines.Count-1)] }
        else { $lines += "[$section]"; $lines += "$key=$val" }
    }
    return $lines
}

# 1. Engine.ini
$engineFile = "$fnCfg\Engine.ini"
if (Test-Path $engineFile) {
    if (!(Test-Path "$engineFile.backup")) { Copy-Item $engineFile "$engineFile.backup" -Force }
    $content = Get-Content $engineFile

    $tweaks = @{
        "SystemSettings" = @{
            "r.BloomQuality" = "0"
            "r.DepthOfFieldQuality" = "0"
            "r.LensFlareQuality" = "0"
            "r.RefractionQuality" = "0"
            "r.SSR.Quality" = "0"
            "r.AmbientOcclusionLevels" = "0"
            "r.VolumetricFog" = "0"
            "r.MaxAnisotropy" = "0"
            "r.TranslucencyLightingVolumeDim" = "1"
            "r.ContactShadows" = "0"
            "r.CapsuleShadows" = "0"
            "r.DBuffer" = "0"
            "r.DistanceFieldAO" = "0"
            "r.SceneColorFringeQuality" = "0"
            "r.SubsurfaceQuality" = "0"
            "r.Streaming.LimitPoolSizeToVRAM" = "0"
            "r.Streaming.PoolSize" = "0"
            "foliage.DitheredLOD" = "0"
            "grass.DensityScale" = "0"
        }
        "Core.System" = @{
            "AsyncLoadingThreadEnabled" = "True"
            "WarnIfPackageLoaded" = "False"
        }
        "/Script/Engine.GarbageCollectionSettings" = @{
            "gc.MaxObjectsInGame" = "2162688"
        }
    }

    foreach ($section in $tweaks.Keys) {
        foreach ($key in $tweaks[$section].Keys) {
            $content = Set-IniValue $content $section $key $tweaks[$section][$key]
        }
    }
    Set-Content -Path $engineFile -Value $content -Encoding UTF8
    Write-Host "[INI] + Engine.ini optimized"
}

# 2. GameUserSettings.ini
$gusFile = "$fnCfg\GameUserSettings.ini"
if (Test-Path $gusFile) {
    if (!(Test-Path "$gusFile.backup")) { Copy-Item $gusFile "$gusFile.backup" -Force }
    $c = Get-Content $gusFile -Raw
    $c = $c -replace 'bUseVSync=True', 'bUseVSync=False'
    $c = $c -replace 'bUseVSync=true', 'bUseVSync=False'
    $c = $c -replace 'FrameRateLimit=\d+(\.\d+)?', 'FrameRateLimit=0.000000'
    $c = $c -replace 'bShowGrass=True', 'bShowGrass=False'
    $c = $c -replace 'EffectsQuality=\d', 'EffectsQuality=0'
    $c = $c -replace 'PostProcessQuality=\d', 'PostProcessQuality=0'
    Set-Content $gusFile $c -Encoding UTF8
    Write-Host "[INI] + GameUserSettings.ini updated"
}
