import requests
import argparse
from threading import Thread, Lock
import queue
import os

print_lock = Lock()

def download_wordlist(git_url, destination):
    response = requests.get(git_url)
    if response.status_code == 200:
        with open(destination, 'wb') as file:
            file.write(response.content)
        print(f"[+] Wordlist downloaded from {git_url} and saved to {destination}")
        return destination
    else:
        print(f"[!] Failed to download wordlist from {git_url}")
        return None

def scan_url(url, wordlist, extensions=None, headers=None, user_agent=None, threads=10):
    q = queue.Queue()
    headers = headers if headers else {}
    if user_agent:
        headers['User-Agent'] = user_agent

    # Check if the wordlist exists locally; if not, try to download
    if not os.path.exists(wordlist):
        git_url = "https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/common.txt"
        print(f"[!] Wordlist not found locally. Attempting to download from {git_url}")
        wordlist = download_wordlist(git_url, 'common.txt')
        if not wordlist:
            return

    with open(wordlist, 'r') as file:
        for line in file:
            path = line.strip()
            if extensions:
                for ext in extensions:
                    q.put(f"{path}.{ext}")
            else:
                q.put(path)

    def worker():
        while not q.empty():
            path = q.get()
            full_url = f"{url}/{path}"
            try:
                response = requests.get(full_url, headers=headers)
                if response.status_code == 200:
                    with print_lock:
                        print(f"[+] Found: {full_url} (Status: 200)")
                elif response.status_code == 403:
                    with print_lock:
                        print(f"[-] Forbidden: {full_url} (Status: 403)")
                q.task_done()
            except requests.exceptions.RequestException as e:
                with print_lock:
                    print(f"[!] Error: {full_url} - {e}")

    for _ in range(threads):
        t = Thread(target=worker)
        t.daemon = True
        t.start()

    q.join()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Web Directory and File Enumerator with Extension Support")
    parser.add_argument("url", help="Target URL (e.g., http://example.com)")  # Users input any domain here.
    parser.add_argument("wordlist", help="Path to the wordlist file or download from GitHub if not found")
    parser.add_argument("--extensions", "-e", nargs='*', help="File extensions to append (e.g., php, html, js)")
    parser.add_argument("--threads", type=int, default=10, help="Number of threads (default: 10)")
    parser.add_argument("--headers", nargs='*', help="Custom headers in 'Key:Value' format")
    parser.add_argument("--user-agent", help="Custom User-Agent string")

    args = parser.parse_args()

    headers = {}
    if args.headers:
        for header in args.headers:
            key, value = header.split(':')
            headers[key.strip()] = value.strip()

    scan_url(args.url, args.wordlist, extensions=args.extensions, headers=headers, user_agent=args.user_agent, threads=args.threads)
