import requests
import argparse
from threading import Thread, Lock
import queue

print_lock = Lock()

def scan_url(url, wordlist, headers=None, user_agent=None, threads=10):
    q = queue.Queue()
    headers = headers if headers else {}
    if user_agent:
        headers['User-Agent'] = user_agent

    with open(wordlist, 'r') as file:
        for line in file:
            path = line.strip()
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
    parser = argparse.ArgumentParser(description="Simple Web Directory and File Enumerator")
    parser.add_argument("url", help="Target URL (e.g., http://example.com)")
    parser.add_argument("wordlist", help="Path to the wordlist file")
    parser.add_argument("--threads", type=int, default=10, help="Number of threads (default: 10)")
    parser.add_argument("--headers", nargs='*', help="Custom headers in 'Key:Value' format")
    parser.add_argument("--user-agent", help="Custom User-Agent string")

    args = parser.parse_args()

    headers = {}
    if args.headers:
        for header in args.headers:
            key, value = header.split(':')
            headers[key.strip()] = value.strip()

    scan_url(args.url, args.wordlist, headers=headers, user_agent=args.user_agent, threads=args.threads)
