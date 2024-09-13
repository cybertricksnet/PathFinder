
# PathFinder

**PathFinder** is a Python tool for discovering hidden directories and files on web servers. It uses multithreading for faster scanning, making it useful for penetration testing and security assessments.

## Requirements
- Python 3.7 or higher

## Installation

- **Clone this repository**:
   ```bash
   git clone https://github.com/cybertricksnet/PathFinder.git
   ```

- **Change to the directory**:
   ```bash
   cd PathFinder
   ```

- **Install necessary libraries**:
   Install any missing Python libraries by running:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### **Basic scan**:
```bash
python3 PathFinder.py https://example.com /usr/share/wordlists/dirb/common.txt --threads 100
```
This will scan the domain `https://example.com` using the wordlist `common.txt` and 100 threads.

### **With file extensions** (e.g., `.php`, `.html`, `.js`):
```bash
python3 PathFinder.py https://example.com /usr/share/wordlists/dirb/common.txt -e php html js --threads 100
```
This will attempt to find directories or files with `.php`, `.html`, and `.js` extensions.

### **Using a larger wordlist**:
You can use a larger wordlist from **SecLists** for more comprehensive scanning. To download SecLists:
   ```bash
   git clone https://github.com/danielmiessler/SecLists.git
   ```

Then use a larger wordlist like this:
   ```bash
   python3 PathFinder.py https://example.com /path/to/SecLists/Discovery/Web-Content/big.txt --threads 100
   ```

### Wordlist Reference

The default wordlist comes from **DirBuster**, typically found on Kali Linux under `/usr/share/wordlists/dirb/`. Alternatively, you can use wordlists from **SecLists**:

- **SecLists** repository: [https://github.com/danielmiessler/SecLists](https://github.com/danielmiessler/SecLists)

## Features

- **Multithreading**: Scan multiple directories and files at once for faster results.
- **Supports file extensions**: You can check for specific file extensions like `.php`, `.html`, and `.js`.
- **Custom headers and user agents**: Add headers and user-agent strings for advanced use cases.

## Notes

- You can adjust the number of threads depending on your machine's resources.
- Larger wordlists may take more time but can discover more hidden files and directories.

## Licensing

- This project is licensed under <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/license-MIT_License-blue" alt="MIT License" style="vertical-align: middle;"></a>

