# Simple Driver Setup Test

Try running one of these to see which browser you have:

```powershell
# Check if Edge is installed
Get-Command msedge -ErrorAction SilentlyContinue

# Check if Chrome is installed
Get-Command chrome -ErrorAction SilentlyContinue

# Or check program files
dir "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
dir "C:\Program Files\Google\Chrome\Application\chrome.exe"
```

Let me know which one you have and we'll configure it to work without downloading drivers!
