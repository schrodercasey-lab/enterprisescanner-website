
# Homepage Deployment Verification Script

Write-Host "🔍 Verifying Homepage Deployment..." -ForegroundColor Cyan
Write-Host ""

# Test domain
try {
    $response = Invoke-WebRequest -Uri "http://enterprisescanner.com" -TimeoutSec 10
    $content_length = $response.Content.Length
    
    if ($content_length -gt 30000) {
        Write-Host "✅ Homepage deployed successfully!" -ForegroundColor Green
        Write-Host "📊 Content size: $content_length bytes" -ForegroundColor Green
        Write-Host "🌐 Site: http://enterprisescanner.com" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Homepage may not be fully deployed" -ForegroundColor Yellow
        Write-Host "📊 Content size: $content_length bytes (expected >30KB)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Unable to verify deployment: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "🔧 If verification fails, homepage upload may still be needed."
