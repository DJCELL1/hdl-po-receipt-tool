# Railway CLI Setup Script
# Hardware Direct PO Receipt Tool

Write-Host "🚂 Railway Deployment Setup" -ForegroundColor Green
Write-Host "================================`n" -ForegroundColor Green

# Check if Railway CLI is installed
Write-Host "Checking for Railway CLI..." -ForegroundColor Yellow
$railwayExists = Get-Command railway -ErrorAction SilentlyContinue

if (-not $railwayExists) {
    Write-Host "❌ Railway CLI not found.`n" -ForegroundColor Red
    Write-Host "Install it with:" -ForegroundColor Cyan
    Write-Host "npm install -g @railway/cli`n" -ForegroundColor White

    $install = Read-Host "Install Railway CLI now? (y/n)"
    if ($install -eq 'y') {
        Write-Host "`nInstalling Railway CLI..." -ForegroundColor Yellow
        npm install -g @railway/cli
    } else {
        Write-Host "`nPlease install Railway CLI and run this script again." -ForegroundColor Yellow
        exit
    }
}

Write-Host "✅ Railway CLI found!`n" -ForegroundColor Green

# Login to Railway
Write-Host "Step 1: Login to Railway" -ForegroundColor Cyan
Write-Host "This will open your browser..." -ForegroundColor Yellow
railway login

# Initialize project
Write-Host "`nStep 2: Initialize Railway project" -ForegroundColor Cyan
railway init

# Add PostgreSQL
Write-Host "`nStep 3: Add PostgreSQL database" -ForegroundColor Cyan
$addDb = Read-Host "Add PostgreSQL database? (y/n)"
if ($addDb -eq 'y') {
    railway add --database postgres
    Write-Host "✅ PostgreSQL added!" -ForegroundColor Green
}

# Set environment variables
Write-Host "`nStep 4: Set environment variables" -ForegroundColor Cyan
Write-Host "You'll need to enter your Cin7 credentials.`n" -ForegroundColor Yellow

$cin7Key = Read-Host "Enter your CIN7_API_KEY (Cin7 api_username)"
$cin7Secret = Read-Host "Enter your CIN7_API_SECRET (Cin7 api_key)" -AsSecureString
$cin7SecretPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
    [Runtime.InteropServices.Marshal]::SecureStringToBSTR($cin7Secret)
)

Write-Host "`nSetting environment variables..." -ForegroundColor Yellow
railway variables set CIN7_API_KEY="$cin7Key"
railway variables set CIN7_API_SECRET="$cin7SecretPlain"
railway variables set JWT_SECRET="hdl-$(Get-Random)-$(Get-Date -Format 'yyyyMMddHHmmss')"
railway variables set NODE_ENV="production"
railway variables set PORT="3001"

Write-Host "✅ Environment variables set!" -ForegroundColor Green

# Deploy
Write-Host "`nStep 5: Deploy to Railway" -ForegroundColor Cyan
$deploy = Read-Host "Deploy now? (y/n)"
if ($deploy -eq 'y') {
    Write-Host "`nDeploying to Railway..." -ForegroundColor Yellow
    Write-Host "This will take 2-3 minutes...`n" -ForegroundColor Yellow
    railway up

    Write-Host "`n✅ Deployment complete!" -ForegroundColor Green
    Write-Host "`nYour app is live! Check the Railway dashboard for the URL.`n" -ForegroundColor Green
} else {
    Write-Host "`nYou can deploy later with: railway up`n" -ForegroundColor Yellow
}

Write-Host "🎉 Setup complete!" -ForegroundColor Green
Write-Host "`nNext steps:" -ForegroundColor Cyan
Write-Host "1. Go to https://railway.app/dashboard" -ForegroundColor White
Write-Host "2. Check your deployment status" -ForegroundColor White
Write-Host "3. Get your app URL from the dashboard" -ForegroundColor White
Write-Host "4. Share the URL with your team!`n" -ForegroundColor White
