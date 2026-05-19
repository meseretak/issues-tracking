$file = "c:\Users\meseretak\Desktop\devops execrices\issues tracking\frontend\app.js"
$content = [System.IO.File]::ReadAllText($file, [System.Text.Encoding]::UTF8)

# Find the FIRST occurrence of the bootstrap listener close and truncate there
$marker = "// If no token, login-page is visible by default (no display:none in HTML)`r`n});"
$idx = $content.IndexOf($marker)
if ($idx -ge 0) {
    $cleanContent = $content.Substring(0, $idx + $marker.Length) + "`r`n"
    [System.IO.File]::WriteAllText($file, $cleanContent, [System.Text.Encoding]::UTF8)
    Write-Host "SUCCESS: File trimmed at index $idx. New length: $($cleanContent.Length) chars"
} else {
    # Try LF-only version
    $marker2 = "// If no token, login-page is visible by default (no display:none in HTML)`n});"
    $idx2 = $content.IndexOf($marker2)
    if ($idx2 -ge 0) {
        $cleanContent = $content.Substring(0, $idx2 + $marker2.Length) + "`n"
        [System.IO.File]::WriteAllText($file, $cleanContent, [System.Text.Encoding]::UTF8)
        Write-Host "SUCCESS (LF): File trimmed at index $idx2. New length: $($cleanContent.Length) chars"
    } else {
        Write-Host "ERROR: Marker not found. Content snippet around 2350:"
        $lines = $content -split "`n"
        $lines[2345..2355] | ForEach-Object { Write-Host $_ }
    }
}
