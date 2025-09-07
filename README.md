# Apple Mail to MBOX Converter

A Python script to convert Apple Mail `.emlx` message files into a single `.mbox` archive for use in other email clients.

## Requirements

- Python 3.8+
- Access to your Apple Mail folder (e.g. `~/Library/Mail/V*/` on macOS)

## Installation

1. Clone the repository:
```
git clone https://github.com/yourname/applemail-to-mbox.git
```
2. Navigate to its root:
```
cd applemail-to-mbox
```
3. Run the script:
```
python emlx_to_mbox.py
```
## Usage

When prompted:

1. Enter the path to your Apple Mail folder (mailbox or parent folder).  
2. Enter the desired path for the output `.mbox` file.

Example:
```
📁 ~/Library/Mail/V10
📦 /Users/you/Desktop/AppleMail-archive.mbox
```
## Importing the `.mbox`

You can import the resulting `.mbox` into Gmail using [MBOX to Gmail Importer](https://github.com/D62/mbox-to-gmail) or into clients like Thunderbird and Apple Mail via their “Import Mailbox” options.

## Notes

- Folder hierarchy is not preserved; all messages go into one `.mbox`.  
- Some messages may fail conversion, but the script reports them at the end.  
