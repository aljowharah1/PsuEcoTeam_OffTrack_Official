# PSU Racing Dashboard - Command Reference

Quick reference guide for running and managing the mobile dashboard during competition.

---

## 🚀 Starting the Dashboard Test

### Run Attempt1 Data Replay
```bash
py scripts/replay_attempt1.py
```
**What it does:** Broadcasts Attempt1.csv data to MQTT broker in real-time (10Hz). All phones connected to the dashboard will receive live telemetry.

### Run Attempt2 Data Replay
```bash
py scripts/replay_attempt2.py
```
**What it does:** Same as above but uses Attempt2.csv data.

---

## 🛑 Stopping the Replay

### Stop All Python Processes
```bash
taskkill //F //IM python.exe
```
**What it does:** Force terminates all running Python processes (including replay scripts).
- `//F` = Force termination
- `//IM` = Image name (process name)
- `python.exe` = The process to kill

### Stop Specific Python Process
```bash
taskkill //F //PID <process_id>
```
**What it does:** Kills a specific Python process by its Process ID.

---

## 📱 Accessing the Dashboard

### Local Access (Testing on Computer)
```
file:///C:/Users/Juju/Desktop/shell/dashboardPSU_ECOteam/app/index.html
```
**What it does:** Opens the dashboard locally in your browser.

### Online Access (Phone/Multiple Devices)
```
https://shell-mobile.vercel.app
```
**What it does:** Access the hosted dashboard from any device with internet.

---

## 🔄 Git Commands (Updating Hosted Version)

### Check Status
```bash
git status
```
**What it does:** Shows which files have been modified, added, or deleted.

### Add All Changes
```bash
git add .
```
**What it does:** Stages all modified files for commit.

### Add Specific Files
```bash
git add app/script.js app/index.html
```
**What it does:** Stages only specific files for commit.

### Commit Changes
```bash
git commit -m "Your message here"
```
**What it does:** Saves staged changes with a descriptive message.

### Push to GitHub (Auto-deploys to Vercel)
```bash
git push origin main
```
**What it does:** Uploads your commits to GitHub. Vercel automatically redeploys the dashboard with your changes.

### Quick Update (All in One)
```bash
git add . && git commit -m "Update dashboard" && git push origin main
```
**What it does:** Stages, commits, and pushes all changes in one command.

---

## 🧪 Testing Commands

### Check Python Version
```bash
py --version
```
**What it does:** Shows which Python version is installed.

### List Running Python Processes
```bash
tasklist | findstr python
```
**What it does:** Shows all running Python processes and their Process IDs.

### Test MQTT Connection
```bash
py scripts/replay_attempt1.py
```
Then check browser console (F12) for connection messages.

---

## 📊 Data Files Location

### Attempt Data
```
data/2025/Attempt/Attempt1.csv
data/2025/Attempt/Attempt2.csv
```

### Replay Scripts
```
scripts/replay_attempt1.py
scripts/replay_attempt2.py
```

### Dashboard Files
```
app/index.html    - Main HTML
app/style.css     - Styles
app/script.js     - Logic & MQTT
```

---

## 🏁 Race Day Workflow

### 1. Before the Race
```bash
# Make sure dashboard is deployed
git status
git push origin main

# Access on phone: https://shell-mobile.vercel.app
```

### 2. Testing with Old Data
```bash
# Start replay
py scripts/replay_attempt1.py

# Stop replay when done
taskkill //F //IM python.exe
```

### 3. During the Race
- Car system broadcasts to MQTT automatically
- All phones show live data
- No commands needed!

### 4. GPS Fallback Mode (If No Internet)
- Dashboard automatically switches to GPS mode
- Uses phone's GPS for speed/position
- Shows "🛰️ GPS MODE (OFFLINE)" indicator

---

## 🛠️ Troubleshooting

### Dashboard Not Updating
```bash
# Hard refresh browser
Ctrl + Shift + R (Chrome/Edge)
Cmd + Shift + R (Safari)
```

### MQTT Not Connecting
1. Check internet connection
2. Verify MQTT credentials in `app/script.js`
3. Check browser console (F12) for errors

### Replay Script Won't Start
```bash
# Stop all Python processes first
taskkill //F //IM python.exe

# Then start fresh
py scripts/replay_attempt1.py
```

### Can't Push to Git
```bash
# Pull latest changes first
git pull origin main

# Then push
git push origin main
```

### Dashboard Shows Old Data
```bash
# Clear browser cache and hard refresh
Ctrl + Shift + Delete (Clear cache)
Ctrl + Shift + R (Hard refresh)
```

---

## 📝 Quick Tips

1. **Always stop replay before starting a new one**
   ```bash
   taskkill //F //IM python.exe
   py scripts/replay_attempt1.py
   ```

2. **Update live dashboard quickly**
   ```bash
   git add . && git commit -m "Fix" && git push origin main
   ```

3. **Check if replay is running**
   ```bash
   tasklist | findstr python
   ```

4. **Dashboard URL for phones**
   - Bookmark: `https://shell-mobile.vercel.app`
   - Add to home screen for easy access

5. **Emergency GPS Mode**
   - If MQTT fails, dashboard auto-switches to GPS
   - Works offline with phone's GPS only
   - No current/efficiency data (car-only features)

---

## 🔗 Important URLs

- **Dashboard**: https://shell-mobile.vercel.app
- **GitHub Repo**: https://github.com/aljowharah1/Shell-mobile
- **Vercel Dashboard**: https://vercel.com/dashboard
- **MQTT Broker**: 8fac0c92ea0a49b8b56f39536ba2fd78.s1.eu.hivemq.cloud

---

## 📞 Quick Reference Card

```
START REPLAY:  py scripts/replay_attempt1.py
STOP REPLAY:   taskkill //F //IM python.exe
DASHBOARD URL: https://shell-mobile.vercel.app
UPDATE LIVE:   git add . && git commit -m "Update" && git push origin main
```

---

**Good luck at the competition! 🏆🏎️**
