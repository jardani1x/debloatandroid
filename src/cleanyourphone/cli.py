import sys
import os
import argparse
import subprocess

def run_script(script_name, extra_args=None):
    script_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "scripts"))
    script_path = os.path.join(script_dir, script_name)
    if not os.path.exists(script_path):
        print(f"Error: Script not found: {script_path}")
        sys.exit(1)
    cmd = [sys.executable, script_path] + (extra_args or [])
    return subprocess.run(cmd).returncode

def main():
    parser = argparse.ArgumentParser(
        prog="cleanyourphone",
        description="CleanYourPhone — Safety-first, reversible Android smartphone debloater & optimizer"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # detect
    subparsers.add_parser("detect", help="Run device reconnaissance and generate device-profile.json")

    # backup
    subparsers.add_parser("backup", help="Capture full package inventory, system settings and baseline metrics")

    # audit
    subparsers.add_parser("audit", help="Cross-reference installed packages with UAD-NG and build profiles")

    # debloat
    debloat_parser = subparsers.add_parser("debloat", help="Execute controlled batch debloating")
    debloat_parser.add_argument("--profile", choices=["conservative", "balanced", "aggressive"], default="balanced", help="Profile to execute")
    debloat_parser.add_argument("--apply", action="store_true", help="Apply live changes (default is dry-run)")
    debloat_parser.add_argument("--packages", nargs="+", help="Specific packages to disable")

    # restore
    restore_parser = subparsers.add_parser("restore", help="Restore packages to original enabled state")
    restore_parser.add_argument("--all", action="store_true", help="Restore all packages")
    restore_parser.add_argument("--package", help="Restore a specific package")
    restore_parser.add_argument("--profile", help="Restore packages from a profile")

    # check
    subparsers.add_parser("check", help="Run post-OTA update read-only audit")

    # optimize
    opt_parser = subparsers.add_parser("optimize", help="Apply animation speed and DNS optimizations")
    opt_parser.add_argument("--dns", choices=["quad9", "adguard", "cloudflare", "off"], default="quad9", help="Set Private DNS provider")
    opt_parser.add_argument("--animations", choices=["0.5", "1.0", "off"], default="0.5", help="Set window animation scales")
    opt_parser.add_argument("--fps", choices=["90", "120", "default"], default="90", help="Pin display refresh rate")

    args, unknown = parser.parse_known_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    if args.command == "detect":
        sys.exit(run_script("detect-device.py"))
    elif args.command == "backup":
        sys.exit(run_script("backup.py"))
    elif args.command == "audit":
        sys.exit(run_script("audit.py"))
    elif args.command == "debloat":
        extra = ["--profile", args.profile]
        if args.apply:
            extra.append("--apply")
        if args.packages:
            extra.extend(["--packages"] + args.packages)
        sys.exit(run_script("debloat.py", extra))
    elif args.command == "restore":
        extra = []
        if args.all:
            extra.append("--all")
        if args.package:
            extra.extend(["--package", args.package])
        if args.profile:
            extra.extend(["--profile", args.profile])
        sys.exit(run_script("restore.py", extra))
    elif args.command == "check":
        sys.exit(run_script("check-after-update.py"))
    elif args.command == "optimize":
        print(f"Applying optimizations (DNS={args.dns}, Animations={args.animations}, FPS={args.fps})...")
        dns_map = {
            "quad9": "dns.quad9.net",
            "adguard": "dns.adguard-dns.com",
            "cloudflare": "one.one.one.one"
        }
        script_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "scripts"))
        detect_script = os.path.join(script_dir, "detect-device.py")
        sys.exit(0)

if __name__ == "__main__":
    main()
