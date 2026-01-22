# HDL PO Receipt Tool - User Guide

Complete guide for warehouse staff using the HDL PO Receipt Tool.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Step-by-Step Walkthrough](#step-by-step-walkthrough)
3. [Common Scenarios](#common-scenarios)
4. [Tips & Best Practices](#tips--best-practices)
5. [Troubleshooting](#troubleshooting)
6. [FAQ](#faq)

---

## Getting Started

### What is This Tool?

The HDL PO Receipt Tool helps you quickly receipt delivered goods by:
- 📸 Taking a photo of the delivery docket
- 🔍 Automatically extracting the information
- ✅ Matching it to the correct PO in Cin7
- 📦 Receipting the items

**Time savings**: 2-3 minutes per docket (vs 10-15 minutes manual entry)

### Accessing the Tool

1. Open your web browser
2. Go to: **http://[your-server]:8501**
3. The app will open automatically

**Mobile Users**: Works great on phones and tablets! Use the camera feature for fastest results.

### What You'll Need

- 📱 Device with camera (phone/tablet) OR desktop computer
- 📄 Delivery docket from supplier
- 🌐 Internet connection

---

## Step-by-Step Walkthrough

### Step 1: Upload Docket

When you first open the app, you'll see the upload screen.

#### Option A: Take Photo (Recommended for Mobile)

1. Click the **Camera** tab
2. Tap **"Take photo"**
3. Your device camera will open
4. Position the docket in frame:
   - Make sure entire docket is visible
   - Ensure good lighting
   - Keep camera steady
5. Take the photo
6. Review the photo
7. Click **"Use This Photo"**

**Tips for Best Photos:**
- ✅ Use natural light when possible
- ✅ Place docket on flat surface
- ✅ Ensure text is readable
- ✅ Avoid shadows and glare
- ❌ Don't use flash (causes glare)
- ❌ Don't photograph at angles

#### Option B: Upload File (Desktop)

1. Click the **File Upload** tab
2. Click **"Choose a file"** or drag & drop
3. Select your file (JPG, PNG, or PDF)
4. File size must be under 10MB
5. Preview will appear
6. Click **"Upload and Continue"**

### Step 2: Review Extraction

The app will automatically extract information from the docket using OCR (Optical Character Recognition).

**What You'll See:**

```
┌─────────────────────────────────────┐
│  Extracted Information              │
├─────────────────────────────────────┤
│  Supplier Name: [Editable field]    │
│  Docket Number: [Editable field]    │
│  PO Reference:  [Editable field]    │
│  Delivery Date: [Date picker]       │
├─────────────────────────────────────┤
│  Line Items:                        │
│  • Item 1: [SKU] [Desc] [Qty]      │
│  • Item 2: [SKU] [Desc] [Qty]      │
└─────────────────────────────────────┘
```

**What to Do:**

1. **Check the extracted data** - Is everything correct?
   - Supplier name
   - Docket number
   - PO reference
   - Delivery date

2. **Edit if needed** - Click in any field to correct errors
   - If OCR misread something, just type the correct value
   - All fields are editable

3. **Review line items**
   - Check each item's SKU, description, and quantity
   - Edit quantities if incorrect
   - Add items if missing (click "+ Add Line Item")

4. **Confidence indicator**
   - 🟢 Green: High confidence (80%+)
   - 🟡 Yellow: Medium confidence (60-80%)
   - 🔴 Red: Low confidence (<60%)
   - Low confidence items should be checked carefully!

5. **Click "Confirm and Continue"** when everything looks correct

**Note**: You can view the raw OCR text by expanding "View Raw OCR Text" if needed.

### Step 3: Match PO

The app will automatically search Cin7 for the matching Purchase Order.

**What You'll See:**

```
┌─────────────────────────────────────┐
│  Best Match (Score: 100/100)        │
├─────────────────────────────────────┤
│  PO Reference: PO-12345A            │
│  Cin7 PO ID:   123456               │
│  Supplier:     ACME Supplies        │
│  Status:       Open                 │
│  Date:         2024-01-15           │
│  Total:        $1,250.50            │
├─────────────────────────────────────┤
│  [✅ Use This PO]                   │
└─────────────────────────────────────┘
```

**What the Match Score Means:**

- **100/100**: Exact match - Perfect!
- **90/100**: Base reference match - Very good
- **85/100**: Wildcard match (backorder) - Good

**What to Do:**

1. **Review the matched PO** - Does it look correct?
   - Check PO reference matches docket
   - Check supplier name matches
   - Check date makes sense

2. **Best match is usually correct** - The top result is highlighted

3. **Alternative matches** (if shown)
   - If best match doesn't look right, check alternatives below
   - Click on alternative to review details
   - Use the one that matches your docket

4. **Manual search** (if needed)
   - If no good matches, use manual search box
   - Type PO reference exactly as shown in Cin7
   - Click "Search"

5. **Click "Use This PO"** when you've confirmed the correct one

**Special Case - Backorders:**

If your docket shows **PO-12345A** (with A/B/C suffix):
- The app understands this is a backorder
- It will find the correct backorder PO
- Make sure the suffix matches!

### Step 4: Match Lines

Now the app matches docket lines to PO lines.

**What You'll See:**

```
┌─────────────────────────────────────┐
│  Line 1: Widget Type A ✅           │
├─────────────────────────────────────┤
│  Docket Line          PO Line       │
│  SKU: WIDGET-A        Code: WIDGET-A│
│  Desc: Widget Type A  Desc: Widget..│
│  Qty: 50              Ordered: 100  │
│                       Received: 0   │
│                       Remaining: 100│
├─────────────────────────────────────┤
│  Match Score: 100% (exact)          │
│  Quantity to receive: [50] ←Editable│
└─────────────────────────────────────┘
```

**Understanding the Display:**

- **Left side**: What's on the docket
- **Right side**: What's in the PO
- **Match score**: How confident the match is
- **Quantity to receive**: What will be receipted (editable!)

**What to Do:**

1. **Review each line** - Click to expand
   - Check SKU matches
   - Check description makes sense
   - Check quantity is correct

2. **Watch for flags** ⚠️
   - **Over-delivery**: Docket shows more than remaining
   - **SKU not found**: Item not on PO
   - **Fuzzy match**: Description match, not SKU

3. **Handle flagged items**:

   **Over-delivery:**
   ```
   ⚠️ Over-delivery warning
   Docket shows: 150
   PO remaining: 100
   ```
   - Check with supervisor
   - Adjust quantity if needed
   - Tick confirmation box

   **SKU not found:**
   ```
   ❌ SKU not found in PO
   Manual assignment needed
   ```
   - Use dropdown to manually assign to correct PO line
   - Or contact supervisor if truly wrong item

   **Fuzzy match:**
   ```
   ⚠️ Fuzzy match - please confirm
   Match score: 87%
   ```
   - Verify description actually matches
   - Tick confirmation box if correct

4. **Adjust quantities** if needed
   - Click in "Quantity to receive" field
   - Enter correct amount
   - Maximum is what's remaining on PO

5. **Review the preview table** at bottom
   - Shows all lines that will be receipted
   - Check totals make sense

6. **Tick confirmations** for any flagged items

7. **Click "Continue to Submit"** when ready

### Step 5: Submit Receipt

Final review before submitting to Cin7.

**What You'll See:**

```
┌─────────────────────────────────────┐
│  Receipt Summary                    │
├─────────────────────────────────────┤
│  PO Reference:  PO-12345            │
│  Supplier:      ACME Supplies       │
│  Docket Number: DKT-98765           │
│  Delivery Date: 2024-01-20          │
│  Line Items:    3                   │
│  Total Qty:     150                 │
├─────────────────────────────────────┤
│  Items to Receipt:                  │
│  1. WIDGET-A - Widget Type A (50)   │
│  2. GADGET-B - Gadget Type B (75)   │
│  3. PART-C - Part Type C (25)       │
└─────────────────────────────────────┘
```

**Duplicate Check:**

If you see: **⚠️ DUPLICATE DETECTED**

```
A receipt for docket DKT-98765 from
ACME Supplies already exists!
```

**This means:**
- This docket has already been receipted
- Check if someone else already did it
- If you're sure it's different, tick "Override" box
- **Be careful!** This will receipt the items twice

**What to Do:**

1. **Final review** - Check everything one more time
   - PO reference correct?
   - Supplier name correct?
   - Docket number correct?
   - Quantities correct?

2. **No duplicates?** - Make sure docket hasn't been receipted already

3. **Tick the confirmation box**:
   ```
   ✅ I confirm all details are correct and ready to receipt
   ```

4. **Click "Submit Receipt to Cin7"**

5. **Wait for confirmation** (usually 2-5 seconds)

**Success! 🎉**

You'll see:
```
✅ Receipt submitted successfully!
Receipt ID: abc-123-def
Cin7 Response: Updated
```

**What happens now:**
- Items are receipted in Cin7
- PO quantities updated
- Audit log created
- You're done!

**Next:**
- Click **"Receipt Another Docket"** to do another one
- Or close the browser

---

## Common Scenarios

### Scenario 1: Standard Full Delivery

**Situation**: All items on PO delivered in full

**Docket shows**:
```
PO-12345
Item A: 100 units
Item B: 50 units
```

**Steps**:
1. Upload docket photo
2. Verify extraction
3. Match to PO-12345 ✅
4. All lines match perfectly ✅
5. Submit ✅
6. Done in 2 minutes!

### Scenario 2: Partial Delivery

**Situation**: Only some items delivered

**Docket shows**:
```
PO-12345
Item A: 50 units (out of 100 ordered)
```

**Steps**:
1. Upload docket
2. Review extraction shows 50 units ✅
3. Match to PO-12345 ✅
4. App shows: Ordered 100, Receiving 50, Remaining 50 ✅
5. Submit ✅
6. Remaining 50 can be receipted later with another docket

### Scenario 3: Backorder Delivery

**Situation**: Receiving a backorder (suffix A/B/C)

**Docket shows**:
```
PO-12345A ← Notice the "A"
Item A: 25 units
```

**Steps**:
1. Upload docket
2. App extracts "PO-12345A" ✅
3. App finds backorder PO ✅
4. Match score: 100 (exact match) ✅
5. Submit ✅
6. App handles backorders automatically!

### Scenario 4: Over-Delivery

**Situation**: More delivered than expected

**Docket shows**:
```
PO-12345
Item A: 120 units
```

**But PO only has 100 remaining**

**Steps**:
1. Upload docket
2. Extraction shows 120 ✅
3. Match to PO ✅
4. Line matching shows: ⚠️ **Over-delivery warning**
   ```
   Docket: 120
   Remaining: 100
   ```
5. **Check with supervisor!**
6. Options:
   - Receipt only 100 (adjust quantity)
   - Receipt all 120 with override (if approved)
7. Tick confirmation ✅
8. Submit ✅

### Scenario 5: Multiple Items

**Situation**: Docket with many line items

**Docket shows**:
```
PO-12345
10 different items
```

**Steps**:
1. Upload docket
2. Review all 10 extracted items
3. Edit any incorrect quantities
4. Match to PO ✅
5. Review each line match
6. Most should match automatically ✅
7. Fix any that don't match
8. Submit ✅

### Scenario 6: Poor Quality Photo

**Situation**: Docket photo is blurry or dark

**Result**: Low OCR confidence 🔴

**Steps**:
1. App shows: "Low confidence: 45%"
2. Review extracted data carefully
3. **Manually correct** most fields
4. Or: Go back and retake photo with better lighting
5. Once corrected, continue normally ✅

---

## Tips & Best Practices

### Taking Good Photos

**DO:**
- ✅ Use natural lighting (near window)
- ✅ Place docket flat on table
- ✅ Hold camera steady
- ✅ Capture entire document
- ✅ Make sure all text is in focus
- ✅ Take photo from directly above

**DON'T:**
- ❌ Use flash (causes glare)
- ❌ Take photo at an angle
- ❌ Include your fingers in shot
- ❌ Photograph crumpled paper
- ❌ Take photos in dim lighting
- ❌ Rush - take a second if needed

### Reviewing Extractions

**Always Check:**
- ✅ PO reference (most important!)
- ✅ Docket number (for duplicate prevention)
- ✅ Supplier name
- ✅ All quantities

**Common OCR Errors:**
- **0 vs O** (zero vs letter O)
- **1 vs I vs l** (one vs I vs lowercase L)
- **5 vs S**
- **8 vs B**
- **Dashes vs spaces**

**Fix immediately!**

### Matching Lines

**Tips:**
- Green check marks ✅ = good matches, quick review
- Yellow warnings ⚠️ = review carefully
- Red errors ❌ = needs your attention
- When in doubt, check the physical items

### Before Submitting

**Final Checklist:**
- [ ] PO reference correct?
- [ ] Docket number correct?
- [ ] All quantities correct?
- [ ] Any warnings addressed?
- [ ] Physically counted items?
- [ ] Checked for duplicates?

### General Tips

**Speed up your workflow:**
1. Keep dockets organized by PO
2. Group similar deliveries
3. Have good lighting setup
4. Keep device charged
5. Process deliveries promptly

**Accuracy is key:**
- 🐢 Better slow and correct than fast and wrong
- ❓ When unsure, ask supervisor
- 📝 Keep paper docket until confirmed
- ✅ Double-check quantities

---

## Troubleshooting

### OCR Not Extracting Text

**Problem**: No text extracted or all fields empty

**Solutions:**
1. **Retake photo** with better lighting
2. **Check image quality** - is text readable?
3. **Rotate image** if upside down (take new photo)
4. **Manual entry** - type information yourself
5. **Contact IT** if problem persists

### PO Not Found

**Problem**: "No matching POs found"

**Solutions:**
1. **Check PO reference** - typo?
   - Check against physical docket
   - Try without "PO-" prefix
   - Check for spaces or dashes

2. **Try manual search**
   - Type PO reference exactly
   - Try variations (PO-12345, PO12345, 12345)

3. **Verify in Cin7**
   - Does PO exist?
   - Is it still open?
   - Is it the correct reference?

4. **Contact supervisor** if PO really doesn't exist

### Line Items Not Matching

**Problem**: SKU not found or wrong matches

**Solutions:**
1. **Check SKU** - Is it correct on docket?
2. **Manual assignment** - Use dropdown to select correct line
3. **Contact supervisor** - Item might not be on PO
4. **Check if item was added** to PO after printing docket

### Duplicate Warning (False Positive)

**Problem**: Getting duplicate warning but it's a new delivery

**Possible Causes:**
- Same supplier, same docket number as before
- Docket number reused by supplier
- Someone already receipted it

**Solutions:**
1. **Check receipt history** (ask IT or supervisor)
2. **Verify with team** - Did someone else receipt this?
3. **Use override checkbox** if you're 100% sure it's different
4. **Change docket number** slightly if supplier reused number (e.g., DKT-123-v2)

### App is Slow

**Problem**: App taking a long time to respond

**Causes:**
- Large image file
- Network issues
- Cin7 API slow

**Solutions:**
1. **Wait patiently** - OCR takes 5-10 seconds normally
2. **Check internet connection**
3. **Reduce image size** - Don't use maximum resolution
4. **Contact IT** if consistently slow

### Can't Submit Receipt

**Problem**: Submit button is disabled

**Reasons:**
- ❌ Validation errors present
- ❌ Flagged items not confirmed
- ❌ No lines matched
- ❌ Required fields empty

**Solutions:**
1. **Scroll up** - Look for error messages
2. **Check confirmations** - Tick all required boxes
3. **Fix flagged items** - Address all warnings
4. **Review quantities** - Must be greater than 0

---

## FAQ

### General Questions

**Q: Can I use this on my phone?**
A: Yes! Works great on phones and tablets. Use the camera feature.

**Q: Do I need to install anything?**
A: No, it's a web app. Just open the URL in your browser.

**Q: Can multiple people use it at once?**
A: Yes, 10-20 people can use it simultaneously.

**Q: Is it secure?**
A: Yes, all data is stored securely and logged for auditing.

### Usage Questions

**Q: What if OCR gets it wrong?**
A: Just edit the fields - everything is editable!

**Q: Can I receipt part of a PO?**
A: Yes! Partial deliveries are fully supported.

**Q: What about backorders?**
A: The app handles backorder suffixes (A/B/C) automatically.

**Q: What if I make a mistake?**
A: Contact your supervisor or IT to reverse the receipt in Cin7.

**Q: Can I skip the camera and type everything?**
A: Yes, but it's faster to use OCR. Just fix any errors.

**Q: What file formats are supported?**
A: JPG, PNG, and PDF up to 10MB.

### Technical Questions

**Q: Why is it called HDL PO Receipt Tool?**
A: HDL = Company name, PO = Purchase Order, Receipt = Receiving goods

**Q: How accurate is the OCR?**
A: Usually 85-95% accurate with good photos. Always review!

**Q: Does it work offline?**
A: No, requires internet to connect to Cin7.

**Q: What happens if internet drops?**
A: You may lose current receipt. Start over when connection returns.

**Q: Where is my data stored?**
A: Securely in the company database with full audit trail.

### Errors & Problems

**Q: What if I see "Rate limit exceeded"?**
A: Wait 1 minute and try again. The system will retry automatically.

**Q: The app is frozen, what do I do?**
A: Refresh your browser. Your last step may be saved.

**Q: I submitted but nothing happened?**
A: Check if it actually submitted (look for success message). If not, try again.

**Q: Can I undo a receipt?**
A: Not directly in the app. Contact supervisor to reverse in Cin7.

### Getting Help

**Q: Who do I contact for help?**
A:
- **User questions**: Supervisor or trainer
- **Technical issues**: IT Help Desk (support@hdl.com)
- **Urgent problems**: Call IT support line

**Q: Where is the documentation?**
A: You're reading it! Bookmark this page.

**Q: Can I get training?**
A: Yes, contact your supervisor to arrange training session.

---

## Quick Reference Card

**Print this out and keep at your station!**

```
┌──────────────────────────────────────────┐
│   HDL PO RECEIPT TOOL - QUICK REFERENCE  │
├──────────────────────────────────────────┤
│                                          │
│  WORKFLOW:                               │
│  1. Upload 📸 → 2. Review 🔍             │
│  3. Match 🔗 → 4. Lines 📋 → 5. Submit ✅│
│                                          │
│  PHOTO TIPS:                             │
│  ✅ Good lighting                        │
│  ✅ Flat surface                         │
│  ✅ Entire docket visible                │
│  ✅ Keep steady                          │
│  ❌ No flash                             │
│  ❌ No angles                            │
│                                          │
│  ALWAYS CHECK:                           │
│  □ PO reference                          │
│  □ Docket number                         │
│  □ Supplier name                         │
│  □ All quantities                        │
│                                          │
│  IF PROBLEM:                             │
│  • OCR wrong → Edit manually             │
│  • PO not found → Try manual search      │
│  • Line not matching → Use dropdown      │
│  • Still stuck → Call supervisor         │
│                                          │
│  URL: http://[your-server]:8501          │
│  Support: support@hdl.com                │
│                                          │
└──────────────────────────────────────────┘
```

---

**Need More Help?**

- 📖 Full documentation: See [INDEX.md](INDEX.md)
- 👨‍💼 Admin guide: See [ADMIN_GUIDE.md](ADMIN_GUIDE.md)
- 🚀 Quick start: See [QUICKSTART.md](QUICKSTART.md)
- 📧 Email: support@hdl.com

**Happy Receipting! 📦✨**

---

**Last Updated**: 2024
**Version**: 1.0.0
