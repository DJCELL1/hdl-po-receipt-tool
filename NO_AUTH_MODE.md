# No Authentication Mode - Enabled

The app has been configured to run **without requiring login**.

## What Changed

✅ **Authentication Disabled** - Go straight to the dashboard
✅ **No Login/Register Pages** - Direct access to all features
✅ **Mock User** - Backend uses a default user (ID: 1)

## How to Use

1. **Start the app:**
   ```powershell
   docker-compose up -d
   ```

2. **Open browser:**
   ```
   http://localhost:3000
   ```

3. **You're in!** - No login needed, straight to the dashboard

## Features Available

- ✅ Scan/upload dockets
- ✅ OCR extraction
- ✅ PO matching
- ✅ Line matching
- ✅ Create receipts
- ✅ View receipt history

All features work exactly the same, just without authentication.

## Notes

- All receipts are associated with user ID 1
- No multi-user support in this mode
- Perfect for single-user/warehouse setup
- To re-enable auth, restore the original App.tsx and route files

---

**Ready to use!** Just run `docker-compose up -d` and open http://localhost:3000
