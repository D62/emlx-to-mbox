#!/usr/bin/env python3

# === IMPORTS ===
import mailbox
import os
import sys
import time
from datetime import datetime
from email import policy
from email.parser import BytesParser
from email.utils import parseaddr, parsedate_tz, mktime_tz

# === USER INPUT ===
source_folder = input("📁 Enter the path to your Apple Mail folder (a mailbox or any parent folder): ").strip()
output_mbox   = input("📦 Enter the path for the output .mbox file: ").strip()

# === CONSTANTS ===
timestamp = datetime.now().strftime("%Y%m%d")

# === HELPERS ===
def read_emlx_bytes(path: str) -> bytes:
    """Read an Apple .emlx file, handling the optional leading byte-count line."""
    with open(path, "rb") as f:
        first = f.readline()
        if first.strip().isdigit():
            size = int(first.strip())
            data = f.read(size)
            if len(data) < size:  # fallback if misreported
                f.seek(0)
                return f.read()
            return data
        f.seek(0)
        return f.read()

def unixfrom_for(msg) -> str:
    """Build a proper 'From ' line for mbox format using From/Date headers."""
    from_addr = parseaddr(msg.get('From', 'MAILER-DAEMON'))[1] or 'MAILER-DAEMON'
    tt = parsedate_tz(msg.get('Date', ''))
    if tt is not None:
        ts = mktime_tz(tt)
        datestr = time.asctime(time.localtime(ts))
    else:
        datestr = time.asctime()
    return f"From {from_addr} {datestr}"

def collect_emlx_paths(root: str):
    """
    Yield all .emlx files under the given folder recursively.
    Prunes Apple Mail "Attachments" folders (not needed for mbox).
    """
    root = os.path.abspath(root)
    for dirpath, dirnames, filenames in os.walk(root):
        # Prune attachment caches (e.g., "Attachments" or "Attachments.noindex")
        dirnames[:] = [d for d in dirnames if not d.lower().startswith("attachments")]
        for fn in filenames:
            if fn.lower().endswith(".emlx"):
                yield os.path.join(dirpath, fn)

# === NORMALIZE & VALIDATE INPUT ===
def normalize(p: str) -> str:
    # Expand ~ and $HOME, then absolutize and resolve symlinks
    return os.path.realpath(os.path.abspath(os.path.expanduser(os.path.expandvars(p))))

src_abs = normalize(source_folder)
out_abs = normalize(output_mbox)

print(f"🔎 Scanning under: {src_abs}")

if not os.path.exists(src_abs):
    print(f"❌ Source folder not found: {src_abs}")
    print("💡 Tip: use a full path or start with ~/, which I now expand automatically.")
    sys.exit(1)

# === DISCOVER FILES ===
all_files = sorted(collect_emlx_paths(src_abs))
if not all_files:
    print("⚠️ No .emlx files found. Typical Apple Mail locations include:")
    print("   ~/Library/Mail/V*/Mailboxes/<YourMailbox>.mbox")
    print("   ~/Library/Mail/V*/<Account Folders>/*.mbox/Messages/")
    sys.exit(0)
print(f"📄 Found {len(all_files)} message file(s).")

# === CREATE MBOX ===
mbox = mailbox.mbox(out_abs, create=True)
mbox.lock()

# === CONVERT ===
print(f"🛠️ Converting and writing to: {out_abs}")
success = 0
failed = 0

try:
    for i, path in enumerate(all_files, 1):
        try:
            raw = read_emlx_bytes(path)
            msg = BytesParser(policy=policy.default).parsebytes(raw)
            msg.set_unixfrom(unixfrom_for(msg))
            mbox.add(msg)
            success += 1
        except Exception as e:
            failed += 1
            print(f"❌ Error converting message #{i} ({path}): {e}")
finally:
    mbox.flush()
    mbox.close()

# === FINAL STATS ===
print("\n✅ Conversion complete.")
print(f"✔️ Converted: {success} message(s)")
print(f"⚠️ Failed:    {failed} message(s)")
print(f"📦 Output MBOX: {out_abs}")
