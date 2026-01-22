# setup_ffmpeg.ps1
Write-Host "Downloading FFmpeg for Windows..."

$url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
$zipPath = "ffmpeg.zip"
$extractPath = "ffmpeg_temp"

# Download
Invoke-WebRequest -Uri $url -OutFile $zipPath
Write-Host "Download complete. Extracting..."

# Extract
Expand-Archive -Path $zipPath -DestinationPath $extractPath -Force

# Move binaries
$binDir = "bin"
if (-not (Test-Path $binDir)) {
    New-Item -ItemType Directory -Force -Path $binDir
}

# Find the exe files (they are usually in a nested bin folder)
$ffmpegExe = Get-ChildItem -Path $extractPath -Recurse -Filter "ffmpeg.exe" | Select-Object -First 1
$ffprobeExe = Get-ChildItem -Path $extractPath -Recurse -Filter "ffprobe.exe" | Select-Object -First 1

if ($ffmpegExe -and $ffprobeExe) {
    Move-Item -Path $ffmpegExe.FullName -Destination $binDir -Force
    Move-Item -Path $ffprobeExe.FullName -Destination $binDir -Force
    Write-Host "FFmpeg binaries installed to $binDir successfully!"
} else {
    Write-Error "Could not find ffmpeg.exe or ffprobe.exe in the downloaded archive."
}

# Cleanup
Remove-Item $zipPath -Force
Remove-Item $extractPath -Recurse -Force
