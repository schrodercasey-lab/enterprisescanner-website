# ✅ WiFi Eyes Testing Checklist

## 🎯 Quick Test (5 Minutes)

### 1️⃣ Basic Activation
- [ ] Open `index.html` in Chrome/Edge
- [ ] Look for camera button (bottom-right, blue icon)
- [ ] Click camera button
- [ ] Browser asks for camera permission → Click "Allow"
- [ ] Full-screen overlay appears with live video
- [ ] Recording indicator (red dot) is pulsing

### 2️⃣ Camera Functionality
- [ ] Video is clear and smooth
- [ ] FPS counter shows > 0 in stats bar
- [ ] Sidebar shows 3 panels (Threats, Devices, Access)
- [ ] "Scanning environment..." appears in panels
- [ ] Flip camera button works (front ↔ back)
- [ ] Settings button shows camera config
- [ ] Close button (X) stops camera

### 3️⃣ AI Detection
- [ ] Wait 2-3 seconds for first detection
- [ ] Bounding boxes appear on video
- [ ] Device names shown above boxes
- [ ] Confidence percentages displayed (87%, 93%, etc.)
- [ ] Sidebar lists update with detected items
- [ ] Stats bar updates (Objects count > 0)
- [ ] Threat alerts appear in red/orange/green

### 4️⃣ Jupiter Integration
- [ ] 3D threat map is visible in background
- [ ] Jupiter's face is rendered
- [ ] Eyes move to follow detected objects
- [ ] Eyes glow brighter when threats detected
- [ ] Eye movement is smooth (60 FPS)

### 5️⃣ UI/UX
- [ ] Full-screen overlay looks professional
- [ ] Cyberpunk theme matches dark AI aesthetic
- [ ] Scan lines visible on video
- [ ] Glass morphism on sidebar panels
- [ ] Buttons have hover effects
- [ ] Stats bar readable at bottom

### 6️⃣ Keyboard Shortcut
- [ ] Press `Ctrl+Shift+W` to toggle camera
- [ ] Camera stops when pressed again
- [ ] Notification appears on toggle

### 7️⃣ Mobile Test (Optional)
- [ ] Resize browser to mobile size (< 768px)
- [ ] Sidebar moves to bottom
- [ ] Panels scroll horizontally
- [ ] Buttons are touch-friendly (48px)
- [ ] Everything still functional

### 8️⃣ Console Check
- [ ] Open Developer Console (F12)
- [ ] No red errors
- [ ] WiFi Eyes initialization message appears
- [ ] Run: `console.log(window.jupiterWiFiEyes)`
- [ ] Object is defined and has methods

---

## 🐛 Common Issues & Fixes

### Issue: Camera won't start
- **Check**: Are you using Chrome or Edge? (Firefox may need extra permissions)
- **Check**: Did you click "Allow" for camera permission?
- **Fix**: Reload page, try again

### Issue: No detections appearing
- **Note**: Demo mode simulates detections randomly
- **Wait**: Give it 2-5 seconds for first detection
- **Check**: FPS > 0 in stats bar means it's working

### Issue: Jupiter's eyes not moving
- **Check**: Is 3D threat map visible?
- **Try**: Scroll down to see threat map, then activate WiFi Eyes
- **Console**: Type `window.jupiterFaceMorph` - should be defined

### Issue: Blurry video
- **Try**: Flip to back camera (usually higher resolution)
- **Note**: Front cameras are often lower quality

### Issue: Button not visible
- **Check**: Scroll down slightly (button is bottom-right)
- **Try**: Press `Ctrl+Shift+W` keyboard shortcut

---

## ✅ Success Criteria

### All Tests Pass = Ready for Deployment! 🚀

If all checkboxes above are checked, WiFi Eyes is **production ready**.

### Next Step After Testing

**Task 3: Production Deployment**
- Upload files to server
- Test on live domain
- Launch to Fortune 500 prospects

---

## 🎯 Expected Results

### What You Should See

**When Working Correctly**:
1. Camera button appears (blue, bottom-right)
2. Click → Permission prompt → Allow
3. Full-screen camera opens immediately
4. Video is clear and smooth
5. Detections appear within 2-5 seconds
6. Bounding boxes drawn on video
7. Sidebar lists populate with items
8. Jupiter's eyes track objects
9. Stats update in real-time
10. Close button stops camera cleanly

**Detections**:
- Devices: "Router (87%)", "Laptop (93%)", etc.
- Threats: "Unsecured WiFi", "Open Port", severity badges
- Faces: Green box if authorized, red if not
- Counts: Objects: 3-5, Threats: 0-2

---

## 📝 Test Results

Record your results:

```
Date: ___________
Browser: ___________
Device: ___________

✅ Camera Activated: YES / NO
✅ Video Clear: YES / NO
✅ Detections Working: YES / NO
✅ Jupiter Eyes Tracking: YES / NO
✅ UI Professional: YES / NO
✅ No Console Errors: YES / NO

Overall Result: PASS / FAIL

Notes:
_________________________________
_________________________________
_________________________________
```

---

**Ready to test? Let's go!** 🚀
