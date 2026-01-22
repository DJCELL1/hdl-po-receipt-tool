# Cin7 Docket Receiver - Quick Start Guide

Get up and running in 5 minutes!

## Prerequisites

- Docker Desktop installed
- Cin7 Omni API credentials

## Step 1: Download & Extract

Download and extract the project files to a directory of your choice.

## Step 2: Configure

1. Copy the example environment file:
```bash
copy .env.example .env
```

2. Edit `.env` and add your Cin7 credentials:
```env
CIN7_API_KEY=your-api-key-here
CIN7_API_SECRET=your-api-secret-here
JWT_SECRET=your-random-secret-at-least-32-characters
```

**To get Cin7 API credentials:**
- Log into Cin7 Omni
- Go to Settings > API
- Click "Generate API Key"
- Copy both the key and secret

**To generate JWT_SECRET:**
```bash
# Windows PowerShell
[Convert]::ToBase64String((1..32 | ForEach-Object { Get-Random -Maximum 256 }))

# Linux/Mac
openssl rand -base64 32
```

## Step 3: Start the Application

Open a terminal in the project directory and run:

```bash
docker-compose up -d
```

Wait 30-60 seconds for all services to start.

## Step 4: Access the Application

Open your web browser and navigate to:

**http://localhost:3000**

## Step 5: Create Your Account

1. Click "Register"
2. Enter your email, password, and name
3. Click "Register"

You'll be automatically logged in!

## Step 6: Scan Your First Docket

1. Click "Scan New Docket"
2. Take a photo of a delivery docket or upload an image
3. Review the extracted information
4. Match to Purchase Order
5. Confirm line items
6. Submit receipt to Cin7!

## Troubleshooting

### Can't access http://localhost:3000

Check if containers are running:
```bash
docker-compose ps
```

All three services (postgres, backend, frontend) should show "Up".

If not running:
```bash
docker-compose logs
```

### "Database connection failed"

The database might still be starting. Wait 30 more seconds and try again.

### "Invalid Cin7 API credentials"

Double-check your `.env` file:
- API Key and Secret are correct
- No extra spaces
- Values are not wrapped in quotes

### Frontend shows blank page

Hard refresh your browser (Ctrl+Shift+R on Windows, Cmd+Shift+R on Mac)

## Next Steps

- Read the [README.md](README.md) for full documentation
- Read the [ADMIN_GUIDE.md](ADMIN_GUIDE.md) for deployment and maintenance
- Check out the receipt history to see all processed dockets

## Stopping the Application

```bash
docker-compose down
```

## Restarting the Application

```bash
docker-compose up -d
```

## Getting Help

Check the logs:
```bash
docker-compose logs -f backend
```

Still stuck? Review the ADMIN_GUIDE.md troubleshooting section.

---

**Need more help?** Contact your system administrator.
