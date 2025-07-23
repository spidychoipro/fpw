# FPW - Folder Password Wrapper

🔐 Simple command-line tool for password-protecting folders in Linux/Unix systems.

## Features

- **Password Protection**: Set passwords for any folder
- **Interactive Shell**: Access protected folders through a secure shell session
- **Session Management**: Stay authenticated for 1 hour without re-entering passwords
- **Multiple Folders**: Protect multiple folders with different passwords
- **Secure Storage**: Passwords are hashed and stored securely in `~/.config/fpw/`

## Installation

1. Clone the repository:
```bash
git clone https://github.com/spidychoipro/fpw.git
cd fpw
```

2. Make the script executable:
```bash
chmod +x access_folder.sh
```

3. (Optional) Add to PATH for global access:
```bash
# Add to your ~/.bashrc or ~/.zshrc
export PATH="$PATH:/path/to/fpw"
# Or create a symlink
sudo ln -s /path/to/fpw/access_folder.sh /usr/local/bin/fpw
```

## Usage

### Set Password for a Folder
```bash
fpw set /path/to/folder
```
- First time: Sets a new password
- Existing protection: Requires current password to change

### Enter Protected Folder
```bash
fpw enter /path/to/folder
```
- Prompts for password (3 attempts allowed)
- Opens an interactive shell in the protected folder
- Shell prompt shows `[fpw:foldername] $`
- Type `exit` or press `Ctrl+D` to leave and lock the folder

### List Protected Folders
```bash
fpw list
```
Shows all protected folders and their session status:
- 🔓 Active session
- 🔒 Locked

### Remove Password Protection
```bash
fpw remove /path/to/folder
```
Requires current password to remove protection.

## Examples

```bash
# Protect a sensitive project folder
fpw set ~/Documents/private-project

# Enter the protected folder
fpw enter ~/Documents/private-project
# [fpw:private-project] $ ls
# [fpw:private-project] $ vim secret-file.txt
# [fpw:private-project] $ exit

# Check which folders are protected
fpw list

# Remove protection when no longer needed
fpw remove ~/Documents/private-project
```

## Security Features

- **Hashed Passwords**: Passwords are SHA-256 hashed with folder path as salt
- **Secure File Permissions**: Configuration files are readable only by the user (600)
- **Session Timeout**: Sessions expire after 1 hour of inactivity
- **Failed Attempt Protection**: Access blocked after 3 wrong password attempts

## File Structure

```
~/.config/fpw/
├── .shadow    # Encrypted password storage
└── .sessions  # Active session tracking
```

## Requirements

- Python 3.x
- Linux/Unix system with bash
- Standard Python libraries (os, sys, getpass, hashlib, json, subprocess, signal, time)

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This tool provides basic folder access control and is intended for personal use. It should not be considered a replacement for proper system-level security measures or encryption for highly sensitive data.
