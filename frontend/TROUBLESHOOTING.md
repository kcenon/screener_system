# Frontend Troubleshooting Guide

## Blank Page Issue (Nothing Displays)

### Quick Fixes

1. **Hard Refresh Browser Cache**
   ```
   Chrome/Edge: Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (Mac)
   Firefox: Ctrl+F5 (Windows/Linux) or Cmd+Shift+R (Mac)
   Safari: Cmd+Option+R (Mac)
   ```

2. **Clear Browser Cache & Cookies**
   - Chrome: Settings → Privacy and Security → Clear browsing data
   - Select "Cached images and files" and "Cookies and other site data"
   - Time range: "All time"

3. **Check Browser Console for Errors**
   - Press F12 to open Developer Tools
   - Go to "Console" tab
   - Look for red error messages
   - Common errors:
     - `Failed to fetch` → Backend not running
     - `Module not found` → Missing dependency
     - `Unexpected token` → Syntax error in code

4. **Verify Dev Server is Running**
   ```bash
   # Check if port 5173 is in use
   lsof -ti:5173

   # If not running, start it
   cd frontend
   npm run dev
   ```

5. **Check Network Tab**
   - Open Developer Tools (F12)
   - Go to "Network" tab
   - Refresh page
   - Look for failed requests (red status codes)
   - Check if `main.tsx` loads successfully

### Common Issues

#### Issue 1: JavaScript Disabled
- Check if JavaScript is enabled in browser settings
- Try opening in incognito/private mode

#### Issue 2: CORS Errors
- Check console for CORS-related errors
- Verify backend CORS configuration
- Backend should allow: http://localhost:5173

#### Issue 3: Module Resolution Errors
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Clear Vite cache
rm -rf node_modules/.vite
npm run dev
```

#### Issue 4: Port Already in Use
```bash
# Kill process on port 5173
lsof -ti:5173 | xargs kill -9

# Restart dev server
npm run dev
```

### Diagnostic Commands

```bash
# Check if server responds
curl -I http://localhost:5173/

# Check if API backend is running
curl http://localhost:8000/api/v1/health

# View Vite dev server logs
# (Check terminal where npm run dev is running)

# Test build
npm run build

# Run type checking
npm run type-check

# Run linting
npm run lint
```

### Browser Compatibility

Minimum browser versions:
- Chrome/Edge: 90+
- Firefox: 88+
- Safari: 14+

### Still Not Working?

1. **Try different browser** (Chrome, Firefox, Edge)
2. **Disable browser extensions** (especially ad blockers, privacy tools)
3. **Check firewall/antivirus** (might be blocking localhost)
4. **Restart computer** (last resort)

### Development Server URLs

After starting `npm run dev`, the app should be available at:
- Local: http://localhost:5173/
- Network: http://192.168.x.x:5173/ (for mobile/other devices)

### Expected Console Output

When the app loads successfully, you should see:
```
React DevTools: Connected
[Vite] connected.
```

### Need More Help?

Check the browser console and share:
1. Any red error messages
2. Failed network requests
3. Warnings in console
4. What page/component you're trying to access
