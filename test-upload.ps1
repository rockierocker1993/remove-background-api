# Test script untuk upload image
$imagePath = "C:\Users\ThinkPad\Downloads\Gemini_Generated_Image_btmouabtmouabtmo.png"
$url = "http://localhost:8000/api/v1/remove-bg-icon"

# Check if file exists
if (-not (Test-Path $imagePath)) {
    Write-Host "File not found: $imagePath" -ForegroundColor Red
    exit
}

Write-Host "Uploading image..." -ForegroundColor Green

# Upload using Invoke-RestMethod
try {
    $response = Invoke-RestMethod -Uri $url -Method Post -InFile $imagePath -ContentType "multipart/form-data" -OutFile "result.png"
    Write-Host "Success! Image saved to result.png" -ForegroundColor Green
} catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host $_.Exception.Response
}
