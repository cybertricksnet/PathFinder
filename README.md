
## PathFinder

**PathFinder** is a lightweight Python tool for web directory and file enumeration using multithreading for faster scanning. It is ideal for penetration testing, security assessments, and discovering hidden directories and files.

### Installation & Usage
### Requirements:
- Python 3.7 or higher

### Installation

- **Clone the repository using Git**:
   ```bash
   git clone https://github.com/cybertricksnet/PathFinder.git
   ```

- **Navigate to the directory**:
   ```bash
   cd PathFinder
   ```

- **Install dependencies (if necessary)**:
   Install the required Python modules by running:
   ```bash
   pip install -r requirements.txt
   ```

### Example Usage

**Basic scan**:
```bash
python3 PathFinder.py https://example.com /usr/share/wordlists/dirb/common.txt --threads 100
```
- This will scan the domain `https://example.com` using the wordlist `common.txt` and 50 threads.
***
**With extensions** (e.g., checking for `.php`, `.html`, and `.js` files):
```bash
python3 PathFinder.py https://example.com /usr/share/wordlists/dirb/common.txt -e php html js --threads 100
```

- This will attempt to find directories or files with `.php`, `.html`, and `.js` extensions.
***
**Example with Custom Headers & User-Agent**:
```bash
python3 PathFinder.py https://example.com /usr/share/wordlists/dirb/common.txt --headers "Authorization: Bearer token" --user-agent "Mozilla/5.0" --threads 100
```
***
**Using a larger wordlist**:
To conduct a more thorough scan with a bigger wordlist, you can use the SecLists repository. Here's how:

- Download SecLists:
   ```bash
   git clone https://github.com/danielmiessler/SecLists.git
   ```

- Use the larger wordlist for scanning:
   ```bash
   python3 PathFinder.py https://example.com /path/to/SecLists/Discovery/Web-Content/big.txt --threads 100
   ```

This will use a larger wordlist (`big.txt`) from SecLists for a more comprehensive scan.
***
### Wordlist Reference

The default wordlist used in examples comes from the **DirBuster** wordlist collection, commonly available on Kali Linux systems under `/usr/share/wordlists/dirb/`.

For more extensive scans, use wordlists from the **SecLists** repository, which contains various discovery wordlists for web content:
- **SecLists** repository: [https://github.com/danielmiessler/SecLists](https://github.com/danielmiessler/SecLists)
***
### Key Features

- **Multithreading**: Supports concurrent requests for faster enumeration.
- **Supports file extensions**: You can specify file extensions such as `.php`, `.html`, and more.
***
### Additional Notes

- You can adjust the number of threads for faster or slower scanning based on system resources.
- Larger wordlists will take more time, but will be more thorough in finding hidden files and directories.
