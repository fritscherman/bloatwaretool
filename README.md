# Windows 11 Pro Bloatware Removal Tool

A comprehensive Python tool designed to clean Windows 11 Pro systems of bloatware for production-ready AV (Audio/Video) servers.

## Features

This tool removes or disables:

### 🗑️ Bloatware Applications
- **Microsoft Teams** - Removes the pre-installed Teams app
- **Office Apps** - OneNote, Sway, and Office Hub
- **OneDrive** - Complete removal of OneDrive sync client
- **Xbox & Gaming Apps** - All Xbox-related apps and services
- **Entertainment Apps** - Spotify, Candy Crush, Disney+, etc.
- **Other Pre-installed Apps** - Bing apps, Feedback Hub, Your Phone, Maps, 3D Viewer, etc.
- **AI Assistants** - Cortana and related AI features

### 🔒 Privacy & Telemetry
- Disables Windows telemetry and data collection
- Blocks telemetry domains via hosts file
- Disables diagnostic services
- Removes scheduled telemetry tasks
- Disables advertising ID

### 🌐 Browser Cleanup
- Disables Edge AI features (Shopping Assistant, Collections, etc.)
- Removes AI browser extensions and features

### ⚙️ System Optimization
- Disables unnecessary services (Xbox, Superfetch, Windows Search)
- Applies registry tweaks for privacy
- Prevents automatic reinstallation of bloatware apps

## Requirements

- **Operating System**: Windows 11 Pro
- **Python Version**: Python 3.8 or higher
- **Privileges**: Administrator/Elevated privileges required

## Installation

1. Clone this repository:
```bash
git clone https://github.com/fritscherman/bloatwaretool.git
cd bloatwaretool
```

2. Verify Python is installed:
```bash
python --version
```

No additional dependencies are required - the tool uses only Python standard library modules.

## Usage

### ⚠️ Important: Administrator Privileges Required

This tool **must** be run with administrator privileges to make system changes.

### Dry Run Mode (Recommended First)

Test what the tool would do without making any changes:

```bash
python bloatware_cleaner.py --dry-run
```

This will show you all the actions that would be performed without actually modifying your system.

### Production Run

To actually clean your system:

1. **Open PowerShell or Command Prompt as Administrator**:
   - Right-click on PowerShell/CMD
   - Select "Run as Administrator"

2. Navigate to the tool directory:
```bash
cd path\to\bloatwaretool
```

3. Run the tool:
```bash
python bloatware_cleaner.py
```

4. **Restart your computer** after the tool completes for all changes to take effect.

## What Gets Removed/Disabled

### Applications Removed
- Microsoft Teams
- Microsoft Office OneNote, Sway, Hub
- OneDrive
- Xbox apps (App, Game Overlay, Identity Provider, TCUI, Gaming App)
- Bing News, Weather, Finance, Sports
- Skype, Your Phone
- Zune Music & Video
- Windows Maps, Feedback Hub
- Mixed Reality Portal
- 3D Viewer, Paint 3D
- Cortana
- Third-party bloatware (Candy Crush, Spotify, Disney+, etc.)

### Services Disabled
- DiagTrack (Connected User Experiences and Telemetry)
- dmwappushservice (WAP Push Message Routing)
- SysMain (Superfetch)
- WSearch (Windows Search - optional)
- Xbox services (Auth Manager, Game Save, Accessory Management, Live Networking)

### Registry Tweaks Applied
- Disables telemetry collection
- Disables advertising ID
- Disables Cortana
- Prevents Windows Consumer Features (stops app reinstallation)

### Scheduled Tasks Disabled
- Application Experience tasks
- Customer Experience Improvement Program tasks
- Disk Diagnostic Data Collector
- Feedback and diagnostics tasks

### Hosts File Entries
Blocks 40+ Microsoft telemetry domains to prevent outbound data collection.

## Logging

The tool creates detailed logs for every run:

- **Log Directory**: `./logs/`
- **Log File**: `bloatware_removal_YYYYMMDD_HHMMSS.log`
- **JSON Report**: `report_YYYYMMDD_HHMMSS.json`

Logs include:
- Timestamp of each action
- Success/failure status for each operation
- Detailed error messages if any operation fails
- Summary report of all changes made

## Safety Features

1. **Dry-run mode** - Test before making changes
2. **Comprehensive logging** - Track all changes made
3. **Admin check** - Prevents running without proper privileges
4. **Error handling** - Continues operation even if individual items fail
5. **Non-destructive** - Doesn't remove system-critical components

## Command-Line Options

```
usage: bloatware_cleaner.py [-h] [--dry-run] [--version]

Windows 11 Pro Bloatware Removal Tool for Production AV Servers

options:
  -h, --help     show this help message and exit
  --dry-run      Simulate actions without making any changes
  --version      show program's version number and exit

Examples:
  # Run in dry-run mode (simulate, don't make changes)
  python bloatware_cleaner.py --dry-run
  
  # Run the actual cleanup (requires admin privileges)
  python bloatware_cleaner.py
```

## Production AV Server Considerations

This tool is specifically designed for production AV servers where:
- Minimal bloatware reduces system overhead
- Telemetry and data collection must be minimized
- Only essential services should run
- System resources are dedicated to AV processing
- Network traffic should be optimized and controlled

## Reverting Changes

While this tool doesn't include an automatic undo feature, you can:

1. **Reinstall apps**: Use Microsoft Store or PowerShell
2. **Re-enable services**: 
   ```powershell
   Set-Service -Name "ServiceName" -StartupType Automatic
   Start-Service -Name "ServiceName"
   ```
3. **Registry changes**: Can be manually reverted via Registry Editor
4. **Hosts file**: Edit `C:\Windows\System32\drivers\etc\hosts` to remove entries

## Troubleshooting

### "Access Denied" Errors
- Ensure you're running PowerShell/CMD as Administrator
- Some operations may require disabling Windows Defender temporarily

### Some Apps Reinstall After Windows Update
- This is a known Windows behavior
- Re-run the tool after major Windows updates
- The registry tweaks help prevent this

### Service Won't Disable
- Some services are protected by Windows
- Check Event Viewer for detailed error messages
- May require Group Policy changes for certain services

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## License

This project is provided as-is for use in preparing production Windows 11 Pro systems.

## Disclaimer

⚠️ **Use at your own risk**. This tool makes significant changes to your Windows installation. While designed to be safe for production AV servers:

- Always test in a non-production environment first
- Create a system restore point before running
- Review the dry-run output before actual execution
- Some removed apps may be needed for your specific use case
- Ensure you have backups before making system changes

The authors are not responsible for any issues arising from the use of this tool.

## Support

For issues, questions, or feature requests, please open an issue on the GitHub repository.

---

**Version**: 1.0.0  
**Last Updated**: January 2026  
**Tested On**: Windows 11 Pro (Build 22000+)