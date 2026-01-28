# Windows 11 Bloatware Removal Tool - Usage Examples

## Quick Start

### 1. Test First (Dry Run)
Before making any changes, always test in dry-run mode to see what would be changed:

```powershell
python bloatware_cleaner.py --dry-run
```

This will show you all operations that would be performed without actually making any changes.

### 2. Run the Cleanup
To actually clean your Windows 11 Pro system, run with administrator privileges:

```powershell
# Right-click PowerShell, select "Run as Administrator", then:
python bloatware_cleaner.py
```

### 3. Review the Results
After completion, check the generated logs and reports:

```powershell
# View the log directory
dir logs

# Open the latest log file
notepad logs\bloatware_removal_YYYYMMDD_HHMMSS.log

# Open the JSON report
notepad logs\report_YYYYMMDD_HHMMSS.json
```

## What Gets Removed

### Microsoft Apps (40+ apps)
- **Teams**: MicrosoftTeams, Microsoft.Teams
- **Office**: OneNote, Sway, Office Hub
- **OneDrive**: Complete removal including sync
- **Xbox**: All gaming apps and services
- **Bing Apps**: News, Weather, Finance, Sports
- **Entertainment**: Zune Music, Zune Video
- **Utilities**: Maps, 3D Viewer, Paint 3D
- **Social**: Skype, People, Your Phone
- **Other**: Cortana, Feedback Hub, Solitaire, Alarms, etc.

### Third-Party Bloatware
- Candy Crush Saga
- Candy Crush Soda Saga
- Spotify
- Disney+
- Clipchamp

### Services Disabled
- DiagTrack (Telemetry)
- dmwappushservice
- SysMain (Superfetch)
- WSearch (Windows Search)
- All Xbox services

### Privacy Protections
- Telemetry disabled via registry
- Advertising ID disabled
- Cortana disabled
- 40+ telemetry domains blocked in hosts file
- Scheduled telemetry tasks disabled
- Windows Consumer Features disabled (prevents app reinstall)

## Production Server Deployment

For deploying to multiple production AV servers:

### Option 1: Manual Deployment
```powershell
# On each server:
# 1. Copy the script
Copy-Item bloatware_cleaner.py C:\Admin\

# 2. Run as administrator
cd C:\Admin
python bloatware_cleaner.py

# 3. Restart
Restart-Computer -Force
```

### Option 2: Group Policy Deployment
1. Create a PowerShell script wrapper:
```powershell
# deploy_bloatware_cleaner.ps1
$scriptPath = "\\server\share\bloatware_cleaner.py"
python $scriptPath
if ($LASTEXITCODE -eq 0) {
    Write-Host "Cleanup successful"
} else {
    Write-Host "Cleanup failed"
    exit 1
}
```

2. Deploy via Group Policy startup script
3. Schedule automatic restart

### Option 3: Remote Execution
```powershell
# Execute on remote computers
$computers = @("SERVER1", "SERVER2", "SERVER3")

foreach ($computer in $computers) {
    Invoke-Command -ComputerName $computer -ScriptBlock {
        python C:\Admin\bloatware_cleaner.py
    }
}
```

## Automation Examples

### Scheduled Task for New Servers
Create a scheduled task that runs on first boot:

```powershell
$action = New-ScheduledTaskAction -Execute 'python' -Argument 'C:\Admin\bloatware_cleaner.py'
$trigger = New-ScheduledTaskTrigger -AtStartup
$principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest
Register-ScheduledTask -TaskName "BloatwareCleanup" -Action $action -Trigger $trigger -Principal $principal
```

### Post-Windows Update Cleanup
Since Windows Updates can reinstall some apps, create a task to run after updates:

```powershell
# Run after Windows Update
$action = New-ScheduledTaskAction -Execute 'python' -Argument 'C:\Admin\bloatware_cleaner.py'
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At 3am
$principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest
Register-ScheduledTask -TaskName "WeeklyBloatwareCleanup" -Action $action -Trigger $trigger -Principal $principal
```

## Monitoring and Verification

### Check What Apps Remain
```powershell
# List all installed AppX packages
Get-AppxPackage | Select Name, Version | Sort Name

# Check for specific bloatware
Get-AppxPackage | Where-Object {$_.Name -like "*Teams*" -or $_.Name -like "*Xbox*"}
```

### Verify Services Are Disabled
```powershell
# Check service status
Get-Service DiagTrack, dmwappushservice, SysMain | Format-Table Name, Status, StartType

# Check Xbox services
Get-Service Xbl* | Format-Table Name, Status, StartType
```

### Verify Telemetry Settings
```powershell
# Check telemetry registry settings
Get-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\DataCollection" -Name AllowTelemetry

# Check advertising ID
Get-ItemProperty -Path "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\AdvertisingInfo" -Name Enabled
```

### Check Hosts File
```powershell
# View blocked telemetry domains
Get-Content C:\Windows\System32\drivers\etc\hosts | Select-String "Bloatware Tool"
```

## Troubleshooting

### Issue: Access Denied
**Solution**: Ensure you're running as Administrator
```powershell
# Check if running as admin
[Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent() | 
    Select-Object -ExpandProperty IsInRole -ArgumentList ([Security.Principal.WindowsBuiltInRole]::Administrator)
```

### Issue: Some Apps Reinstall After Windows Update
**Solution**: This is normal Windows behavior. Re-run the tool or use the scheduled task approach.

### Issue: Can't Remove Specific App
**Solution**: Some apps are protected. Check Event Viewer for details.
```powershell
# View Event Viewer logs
Get-EventLog -LogName Application -Source "AppX*" -Newest 50
```

### Issue: Windows Search Not Working (If Needed)
**Solution**: Re-enable the WSearch service
```powershell
Set-Service -Name WSearch -StartupType Automatic
Start-Service -Name WSearch
```

## Reverting Changes

### Reinstall a Specific App
```powershell
# Via Microsoft Store or PowerShell
# For example, reinstall Calculator:
Get-AppxPackage -AllUsers Microsoft.WindowsCalculator | Foreach {Add-AppxPackage -DisableDevelopmentMode -Register "$($_.InstallLocation)\AppXManifest.xml"}
```

### Re-enable a Service
```powershell
Set-Service -Name "ServiceName" -StartupType Automatic
Start-Service -Name "ServiceName"
```

### Restore Hosts File
```powershell
# Use the backup created by the tool
Copy-Item C:\Windows\System32\drivers\etc\hosts.backup C:\Windows\System32\drivers\etc\hosts -Force
```

### Reset Telemetry Settings
```powershell
# Remove registry tweaks
Remove-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\DataCollection" -Name AllowTelemetry
Remove-ItemProperty -Path "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\AdvertisingInfo" -Name Enabled
```

## Best Practices for Production AV Servers

1. **Always Test First**: Use --dry-run on a test system before production deployment

2. **Create System Restore Points**: 
   ```powershell
   Checkpoint-Computer -Description "Before Bloatware Removal" -RestorePointType MODIFY_SETTINGS
   ```

3. **Document Changes**: Save logs to a central location
   ```powershell
   Copy-Item logs\*.log \\server\logs\$env:COMPUTERNAME\
   ```

4. **Verify AV Software Still Works**: After cleanup, test your AV server functionality

5. **Schedule Regular Cleanups**: Windows Updates may reinstall some apps

6. **Keep Backups**: Maintain backups of critical configurations

7. **Test Network Connectivity**: Ensure blocking telemetry doesn't affect needed services

## Log Analysis

The tool generates detailed logs. Here's what to look for:

### Success Indicators
```
Successfully removed: Microsoft.Teams
Successfully disabled: DiagTrack
Successfully set: HKLM:\SOFTWARE\Policies\Microsoft\Windows\DataCollection\AllowTelemetry
Added 40 telemetry domains to hosts file
```

### Warning Indicators
```
Failed to remove Microsoft.XboxApp: Access denied
Failed to disable service XblAuthManager: Service not found
```

### JSON Report Structure
```json
{
  "apps_removed": ["App1", "App2", ...],
  "apps_failed": [{"app": "AppName", "error": "Error message"}],
  "services_disabled": ["Service1", "Service2", ...],
  "services_failed": [{"service": "ServiceName", "error": "Error message"}],
  "registry_tweaks": ["Path\\Name", ...],
  "registry_failed": [{"path": "Path", "name": "Name", "error": "Error message"}],
  "telemetry_domains_blocked": 40,
  "edge_features_disabled": ["Feature1", "Feature2"],
  "edge_features_failed": []
}
```

## Security Considerations

1. **Review the Script**: Always review code before running with admin privileges
2. **Use Official Repository**: Only download from the official GitHub repository
3. **Verify No Malware**: Scan the script with your AV software before running
4. **Monitor System**: Watch for unexpected behavior after running
5. **Keep Updated**: Use the latest version for security fixes

## Support and Feedback

If you encounter issues:
1. Check the log files in the `logs/` directory
2. Review this usage guide
3. Check the README.md for additional information
4. Open an issue on GitHub with log files attached

---

**Remember**: Always test in a non-production environment first, and ensure you have proper backups before making system changes.
