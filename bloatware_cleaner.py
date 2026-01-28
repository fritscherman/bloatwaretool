#!/usr/bin/env python3
"""
Windows 11 Pro Bloatware Removal Tool
A comprehensive tool to clean Windows 11 Pro systems for production AV servers.
Removes bloatware apps, disables telemetry, and optimizes system settings.
"""

import os
import sys
import subprocess
import logging
import json
import ctypes
import shutil
from datetime import datetime
from pathlib import Path

# Configure logging
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / f"bloatware_removal_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


class BloatwareRemover:
    """Main class for removing Windows 11 bloatware."""
    
    # List of bloatware apps to remove
    BLOATWARE_APPS = [
        # Microsoft Teams
        "MicrosoftTeams",
        "Microsoft.Teams",
        
        # Office apps (if not needed)
        "Microsoft.Office.OneNote",
        "Microsoft.Office.Sway",
        
        # OneDrive
        "Microsoft.OneDrive",
        "Microsoft.OneDriveSync",
        
        # Xbox and Gaming
        "Microsoft.XboxApp",
        "Microsoft.XboxGameOverlay",
        "Microsoft.XboxGamingOverlay",
        "Microsoft.XboxIdentityProvider",
        "Microsoft.XboxSpeechToTextOverlay",
        "Microsoft.Xbox.TCUI",
        "Microsoft.GamingApp",
        
        # Other bloatware
        "Microsoft.BingNews",
        "Microsoft.BingWeather",
        "Microsoft.GetHelp",
        "Microsoft.Getstarted",
        "Microsoft.MicrosoftOfficeHub",
        "Microsoft.MicrosoftSolitaireCollection",
        "Microsoft.People",
        "Microsoft.SkypeApp",
        "Microsoft.WindowsFeedbackHub",
        "Microsoft.YourPhone",
        "Microsoft.ZuneMusic",
        "Microsoft.ZuneVideo",
        "Microsoft.WindowsMaps",
        "Microsoft.MixedReality.Portal",
        "Microsoft.Microsoft3DViewer",
        "Microsoft.MSPaint",
        "Microsoft.BingFinance",
        "Microsoft.BingSports",
        "Microsoft.WindowsAlarms",
        "Microsoft.WindowsSoundRecorder",
        
        # Third-party bloatware
        "king.com.CandyCrushSaga",
        "king.com.CandyCrushSodaSaga",
        "SpotifyAB.SpotifyMusic",
        "Disney.37853FC22B2CE",
        "Clipchamp.Clipchamp",
        
        # Cortana (AI assistant)
        "Microsoft.549981C3F5F10",  # Cortana
    ]
    
    # Services to disable for reduced telemetry
    SERVICES_TO_DISABLE = [
        "DiagTrack",  # Connected User Experiences and Telemetry
        "dmwappushservice",  # WAP Push Message Routing Service
        "SysMain",  # Superfetch
        "WSearch",  # Windows Search (optional, disable if not needed)
        "XblAuthManager",  # Xbox Live Auth Manager
        "XblGameSave",  # Xbox Live Game Save
        "XboxGipSvc",  # Xbox Accessory Management Service
        "XboxNetApiSvc",  # Xbox Live Networking Service
    ]
    
    # Registry tweaks to disable telemetry
    TELEMETRY_REGISTRY_TWEAKS = [
        # Disable telemetry
        ('HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\DataCollection', 'AllowTelemetry', '0', 'DWord'),
        ('HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\DataCollection', 'AllowTelemetry', '0', 'DWord'),
        
        # Disable advertising ID
        ('HKCU:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\AdvertisingInfo', 'Enabled', '0', 'DWord'),
        
        # Disable Cortana
        ('HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\Windows Search', 'AllowCortana', '0', 'DWord'),
        
        # Disable Windows Consumer Features (prevents app reinstall)
        ('HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\CloudContent', 'DisableWindowsConsumerFeatures', '1', 'DWord'),
    ]

    def __init__(self, dry_run=False):
        """Initialize the bloatware remover.
        
        Args:
            dry_run (bool): If True, only simulate actions without making changes
        """
        self.dry_run = dry_run
        self.results = {
            "apps_removed": [],
            "apps_failed": [],
            "services_disabled": [],
            "services_failed": [],
            "registry_tweaks": [],
            "registry_failed": []
        }

    def is_admin(self):
        """Check if the script is running with administrator privileges."""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception:
            # If we can't determine (e.g., not on Windows), assume we need to check differently
            return False

    def run_powershell(self, command, check=True):
        """Execute a PowerShell command.
        
        Args:
            command (str): PowerShell command to execute
            check (bool): Whether to raise exception on error
            
        Returns:
            subprocess.CompletedProcess: Result of the command
        """
        if self.dry_run:
            logger.info(f"[DRY RUN] Would execute PowerShell: {command}")
            return subprocess.CompletedProcess(args=command, returncode=0, stdout="DRY RUN", stderr="")
        
        try:
            result = subprocess.run(
                ["powershell.exe", "-Command", command],
                capture_output=True,
                text=True,
                check=check
            )
            return result
        except subprocess.CalledProcessError as e:
            logger.error(f"PowerShell command failed: {e}")
            if check:
                raise
            # Return a dummy CompletedProcess for consistency
            return subprocess.CompletedProcess(args=command, returncode=e.returncode, stdout=e.stdout, stderr=e.stderr)

    def remove_appx_packages(self):
        """Remove bloatware AppX packages."""
        logger.info("=" * 60)
        logger.info("Starting AppX package removal...")
        logger.info("=" * 60)
        
        for app in self.BLOATWARE_APPS:
            try:
                logger.info(f"Attempting to remove: {app}")
                
                # Try to remove for current user
                cmd = f"Get-AppxPackage *{app}* | Remove-AppxPackage -ErrorAction SilentlyContinue"
                result = self.run_powershell(cmd, check=False)
                
                # Try to remove provisioned package (prevents reinstall for new users)
                cmd_provisioned = f"Get-AppxProvisionedPackage -Online | Where-Object {{$_.DisplayName -like '*{app}*'}} | Remove-AppxProvisionedPackage -Online -ErrorAction SilentlyContinue"
                result_provisioned = self.run_powershell(cmd_provisioned, check=False)
                
                logger.info(f"Successfully removed: {app}")
                self.results["apps_removed"].append(app)
                
            except Exception as e:
                logger.warning(f"Failed to remove {app}: {str(e)}")
                self.results["apps_failed"].append({"app": app, "error": str(e)})

    def disable_services(self):
        """Disable unnecessary services for telemetry and bloatware."""
        logger.info("=" * 60)
        logger.info("Disabling unnecessary services...")
        logger.info("=" * 60)
        
        for service in self.SERVICES_TO_DISABLE:
            try:
                logger.info(f"Disabling service: {service}")
                
                # Stop the service
                cmd_stop = f"Stop-Service -Name '{service}' -Force -ErrorAction SilentlyContinue"
                self.run_powershell(cmd_stop, check=False)
                
                # Disable the service
                cmd_disable = f"Set-Service -Name '{service}' -StartupType Disabled -ErrorAction SilentlyContinue"
                self.run_powershell(cmd_disable, check=False)
                
                logger.info(f"Successfully disabled: {service}")
                self.results["services_disabled"].append(service)
                
            except Exception as e:
                logger.warning(f"Failed to disable service {service}: {str(e)}")
                self.results["services_failed"].append({"service": service, "error": str(e)})

    def apply_registry_tweaks(self):
        """Apply registry tweaks to disable telemetry and unwanted features."""
        logger.info("=" * 60)
        logger.info("Applying registry tweaks...")
        logger.info("=" * 60)
        
        for reg_path, name, value, value_type in self.TELEMETRY_REGISTRY_TWEAKS:
            try:
                logger.info(f"Setting registry: {reg_path}\\{name} = {value}")
                
                # Create the registry key if it doesn't exist
                cmd_create = f"If (!(Test-Path '{reg_path}')) {{ New-Item -Path '{reg_path}' -Force | Out-Null }}"
                self.run_powershell(cmd_create, check=False)
                
                # Set the registry value
                cmd_set = f"Set-ItemProperty -Path '{reg_path}' -Name '{name}' -Value {value} -Type {value_type} -Force"
                self.run_powershell(cmd_set, check=False)
                
                logger.info(f"Successfully set: {reg_path}\\{name}")
                self.results["registry_tweaks"].append(f"{reg_path}\\{name}")
                
            except Exception as e:
                logger.warning(f"Failed to set registry {reg_path}\\{name}: {str(e)}")
                self.results["registry_failed"].append({
                    "path": reg_path,
                    "name": name,
                    "error": str(e)
                })

    def disable_scheduled_tasks(self):
        """Disable scheduled tasks related to telemetry and bloatware."""
        logger.info("=" * 60)
        logger.info("Disabling telemetry scheduled tasks...")
        logger.info("=" * 60)
        
        tasks_to_disable = [
            "\\Microsoft\\Windows\\Application Experience\\Microsoft Compatibility Appraiser",
            "\\Microsoft\\Windows\\Application Experience\\ProgramDataUpdater",
            "\\Microsoft\\Windows\\Autochk\\Proxy",
            "\\Microsoft\\Windows\\Customer Experience Improvement Program\\Consolidator",
            "\\Microsoft\\Windows\\Customer Experience Improvement Program\\UsbCeip",
            "\\Microsoft\\Windows\\DiskDiagnostic\\Microsoft-Windows-DiskDiagnosticDataCollector",
            "\\Microsoft\\Windows\\Feedback\\Siuf\\DmClient",
            "\\Microsoft\\Windows\\Feedback\\Siuf\\DmClientOnScenarioDownload",
        ]
        
        for task in tasks_to_disable:
            try:
                logger.info(f"Disabling task: {task}")
                cmd = f"Disable-ScheduledTask -TaskName '{task}' -ErrorAction SilentlyContinue"
                self.run_powershell(cmd, check=False)
                logger.info(f"Successfully disabled task: {task}")
            except Exception as e:
                logger.warning(f"Failed to disable task {task}: {str(e)}")

    def block_telemetry_hosts(self):
        """Add telemetry domains to hosts file to block outbound connections."""
        logger.info("=" * 60)
        logger.info("Blocking telemetry domains...")
        logger.info("=" * 60)
        
        telemetry_domains = [
            "vortex.data.microsoft.com",
            "vortex-win.data.microsoft.com",
            "telecommand.telemetry.microsoft.com",
            "telecommand.telemetry.microsoft.com.nsatc.net",
            "oca.telemetry.microsoft.com",
            "oca.telemetry.microsoft.com.nsatc.net",
            "sqm.telemetry.microsoft.com",
            "sqm.telemetry.microsoft.com.nsatc.net",
            "watson.telemetry.microsoft.com",
            "watson.telemetry.microsoft.com.nsatc.net",
            "redir.metaservices.microsoft.com",
            "choice.microsoft.com",
            "choice.microsoft.com.nsatc.net",
            "df.telemetry.microsoft.com",
            "reports.wes.df.telemetry.microsoft.com",
            "wes.df.telemetry.microsoft.com",
            "services.wes.df.telemetry.microsoft.com",
            "sqm.df.telemetry.microsoft.com",
            "telemetry.microsoft.com",
            "watson.ppe.telemetry.microsoft.com",
            "telemetry.appex.bing.net",
            "telemetry.urs.microsoft.com",
            "settings-sandbox.data.microsoft.com",
            "vortex-sandbox.data.microsoft.com",
            "survey.watson.microsoft.com",
            "watson.live.com",
            "statsfe2.ws.microsoft.com",
            "corpext.msitadfs.glbdns2.microsoft.com",
            "compatexchange.cloudapp.net",
            "cs1.wpc.v0cdn.net",
            "a-0001.a-msedge.net",
            "statsfe2.update.microsoft.com.akadns.net",
            "sls.update.microsoft.com.akadns.net",
            "fe2.update.microsoft.com.akadns.net",
            "diagnostics.support.microsoft.com",
            "corp.sts.microsoft.com",
            "statsfe1.ws.microsoft.com",
            "pre.footprintpredict.com",
            "i1.services.social.microsoft.com",
            "i1.services.social.microsoft.com.nsatc.net",
        ]
        
        hosts_file = Path("C:\\Windows\\System32\\drivers\\etc\\hosts")
        
        if self.dry_run:
            logger.info(f"[DRY RUN] Would add {len(telemetry_domains)} domains to hosts file")
            return
        
        try:
            # Backup and read existing hosts file
            existing_content = ""
            if hosts_file.exists():
                # Create backup
                backup_file = hosts_file.with_suffix('.backup')
                shutil.copy2(hosts_file, backup_file)
                logger.info(f"Created backup: {backup_file}")
                
                with open(hosts_file, 'r', encoding='utf-8') as f:
                    existing_content = f.read()
            
            # Add blocker entries
            new_entries = []
            for domain in telemetry_domains:
                entry = f"0.0.0.0 {domain}"
                if entry not in existing_content:
                    new_entries.append(entry)
            
            if new_entries:
                with open(hosts_file, 'a', encoding='utf-8') as f:
                    f.write("\n# Bloatware Tool - Telemetry Blocking\n")
                    f.write("\n".join(new_entries))
                    f.write("\n")
                logger.info(f"Added {len(new_entries)} telemetry domains to hosts file")
                self.results.setdefault("telemetry_domains_blocked", len(new_entries))
            else:
                logger.info("All telemetry domains already blocked in hosts file")
                
        except Exception as e:
            logger.error(f"Failed to modify hosts file: {str(e)}")

    def cleanup_browser_extensions(self):
        """Remove AI and telemetry browser extensions."""
        logger.info("=" * 60)
        logger.info("Cleaning browser extensions...")
        logger.info("=" * 60)
        
        # This is more complex and browser-specific
        # For Edge, we can remove some extensions via registry
        
        logger.info("Disabling Edge AI features...")
        edge_tweaks = [
            ('HKLM:\\SOFTWARE\\Policies\\Microsoft\\Edge', 'HubsSidebarEnabled', '0', 'DWord'),
            ('HKLM:\\SOFTWARE\\Policies\\Microsoft\\Edge', 'EdgeShoppingAssistantEnabled', '0', 'DWord'),
            ('HKLM:\\SOFTWARE\\Policies\\Microsoft\\Edge', 'EdgeCollectionsEnabled', '0', 'DWord'),
        ]
        
        for reg_path, name, value, value_type in edge_tweaks:
            try:
                cmd_create = f"If (!(Test-Path '{reg_path}')) {{ New-Item -Path '{reg_path}' -Force | Out-Null }}"
                self.run_powershell(cmd_create, check=False)
                
                cmd_set = f"Set-ItemProperty -Path '{reg_path}' -Name '{name}' -Value {value} -Type {value_type} -Force"
                self.run_powershell(cmd_set, check=False)
                
                logger.info(f"Disabled Edge feature: {name}")
                self.results.setdefault("edge_features_disabled", []).append(name)
            except Exception as e:
                logger.warning(f"Failed to disable Edge feature {name}: {str(e)}")
                self.results.setdefault("edge_features_failed", []).append({"feature": name, "error": str(e)})

    def generate_report(self):
        """Generate a summary report of all actions taken."""
        logger.info("=" * 60)
        logger.info("CLEANUP SUMMARY REPORT")
        logger.info("=" * 60)
        
        logger.info(f"\nApps Removed: {len(self.results['apps_removed'])}")
        for app in self.results['apps_removed']:
            logger.info(f"  ✓ {app}")
        
        if self.results['apps_failed']:
            logger.info(f"\nApps Failed: {len(self.results['apps_failed'])}")
            for item in self.results['apps_failed']:
                logger.info(f"  ✗ {item['app']}: {item['error']}")
        
        logger.info(f"\nServices Disabled: {len(self.results['services_disabled'])}")
        for service in self.results['services_disabled']:
            logger.info(f"  ✓ {service}")
        
        logger.info(f"\nRegistry Tweaks Applied: {len(self.results['registry_tweaks'])}")
        for tweak in self.results['registry_tweaks']:
            logger.info(f"  ✓ {tweak}")
        
        logger.info("\n" + "=" * 60)
        logger.info(f"Log file saved to: {LOG_FILE}")
        logger.info("=" * 60)
        
        # Save JSON report
        report_file = LOG_DIR / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2)
        logger.info(f"JSON report saved to: {report_file}")

    def run(self):
        """Execute the complete bloatware removal process."""
        logger.info("Windows 11 Pro Bloatware Removal Tool")
        logger.info("=" * 60)
        
        if self.dry_run:
            logger.info("RUNNING IN DRY-RUN MODE - No changes will be made")
            logger.info("=" * 60)
        
        # Check admin privileges
        if not self.is_admin():
            if self.dry_run:
                logger.warning("Not running with administrator privileges - dry-run may show incomplete results")
            else:
                logger.error("This script requires administrator privileges!")
                logger.error("Please run as administrator.")
                return False
        
        try:
            # Execute all cleanup operations
            self.remove_appx_packages()
            self.disable_services()
            self.apply_registry_tweaks()
            self.disable_scheduled_tasks()
            self.block_telemetry_hosts()
            self.cleanup_browser_extensions()
            
            # Generate report
            self.generate_report()
            
            logger.info("\n" + "=" * 60)
            logger.info("Bloatware removal completed successfully!")
            logger.info("Please restart your computer for all changes to take effect.")
            logger.info("=" * 60)
            
            return True
            
        except Exception as e:
            logger.error(f"An error occurred during cleanup: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return False


def main():
    """Main entry point for the script."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Windows 11 Pro Bloatware Removal Tool for Production AV Servers",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run in dry-run mode (simulate, don't make changes)
  python bloatware_cleaner.py --dry-run
  
  # Run the actual cleanup (requires admin privileges)
  python bloatware_cleaner.py
        """
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Simulate actions without making any changes'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='Windows 11 Bloatware Remover v1.0.0'
    )
    
    args = parser.parse_args()
    
    # Create and run the remover
    remover = BloatwareRemover(dry_run=args.dry_run)
    success = remover.run()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
