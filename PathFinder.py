import requests
import argparse
from threading import Thread, Lock
import queue
from tqdm import tqdm
import os
from colorama import Fore, Style, init
import signal
import sys

init(autoreset=True)  # Automatically reset colors after each print

print_lock = Lock()
found_endpoints = []  # List to store found endpoints

# Popular directory names
popular_dirs = [
    'about', 'about-us', 'services', 'contact', 'home', 'products', 'blog', 'login', 'admin', 'dashboard',
    'account', 'help', 'faq', 'privacy', 'terms', 'tos', 'careers', 'jobs', 'support', 'signup', 'register',
    'signin', 'subscribe', 'unsubscribe', 'profile', 'settings', 'feedback', 'news', 'events', 'press', 'media',
    'partners', 'team', 'portfolio', 'projects', 'solutions', 'clients', 'reviews', 'testimonials', 'gallery',
    'videos', 'downloads', 'pricing', 'plans', 'features', 'offers', 'discounts', 'promotions', 'coupons', 'deals',
    'specials', 'store', 'shop', 'cart', 'checkout', 'orders', 'billing', 'payment', 'shipping', 'track', 'tracking',
    'wishlist', 'terms-of-service', 'privacy-policy', 'legal', 'disclaimer', 'cookies', 'cookie-policy', 'security',
    'sitemap', 'resources', 'documentation', 'docs', 'api', 'developers', 'partners', 'affiliates', 'referrals',
    'community', 'forum', 'forums', 'discussion', 'chat', 'contact-us', 'get-in-touch', 'social', 'social-media',
    'follow', 'subscribe-us', 'unsubscribe', 'status', 'outage', 'maintenance', 'upgrade', 'terms-conditions',
    'terms-of-use', 'how-it-works', 'our-team', 'meet-the-team', 'leadership', 'staff', 'board', 'management',
    'founders', 'our-history', 'history', 'mission', 'values', 'vision', 'our-work', 'what-we-do', 'company',
    'corporate', 'business', 'solutions', 'industries', 'verticals', 'team', 'why-us', 'our-story', 'who-we-are',
    'about-us', 'contact-us', 'get-started', 'start-here', 'how-it-works', 'our-process', 'our-clients',
    'customer-stories', 'success-stories', 'case-studies', 'testimonials', 'reviews', 'faqs', 'help-center',
    'support-center', 'knowledge-base', 'support', 'live-chat', 'contact-form', 'careers', 'work-with-us', 'jobs',
    'job-openings', 'opportunities', 'apply', 'hiring', 'internships', 'volunteer', 'join-us', 'get-involved',
    'donate', 'contribute', 'fundraise', 'sponsor', 'media-center', 'press-releases', 'news', 'events', 'webinars',
    'conferences', 'press', 'media', 'announcements', 'newsletter', 'subscribe', 'unsubscribe', 'privacy-policy',
    'terms-of-use', 'terms-and-conditions', 'site-map', 'sitemap', 'legal', 'disclaimer', 'disclosures', 'cookie-policy',
    'terms', 'resources', 'support', 'documentation', 'guides', 'tutorials', 'api-docs', 'dev', 'developers', 'integrations',
    'addons', 'extensions', 'plugins', 'theme', 'themes', 'templates', 'store', 'shop', 'products', 'solutions',
    'industries', 'ecommerce', 'product', 'solutions', 'pricing', 'plans', 'subscription', 'billing', 'payments',
    'checkout', 'payment', 'billing', 'invoices', 'orders', 'order-history', 'subscriptions', 'account', 'profile',
    'settings', 'manage', 'upgrade', 'features', 'free-trial', 'demo', 'trial', 'trial-account', 'signup', 'register',
    'join', 'create-account', 'login', 'signin', 'account-login', 'user', 'users', 'admin', 'admin-dashboard',
    'control-panel', 'cms', 'backend'
]

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

def check_for_false_positive(url, home_page_content):
    try:
        response = requests.get(url, verify=False)
        if response.status_code == 200:
            # Compare content length with the homepage to check for false positives
            if len(response.content) == len(home_page_content):
                return False  # Likely a false positive if the content length matches
            else:
                return True
        else:
            return False
    except requests.exceptions.RequestException as e:
        return False

def scan_url(url, wordlist, extensions=None, headers=None, user_agent=None, threads=10):
    q = queue.Queue()
    headers = headers if headers else {}
    if user_agent:
        headers['User-Agent'] = user_agent

    # Get homepage content length for false positive detection
    try:
        home_page_response = requests.get(url, headers=headers, verify=False)
        home_page_content = home_page_response.content
    except requests.exceptions.RequestException as e:
        print(f"[!] Error: Could not get homepage of {url}: {e}")
        return

    # Check if the wordlist exists locally; if not, try to download
    if not os.path.exists(wordlist):
        git_url = "https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/common.txt"
        print(f"[!] Wordlist not found locally. Attempting to download from {git_url}")
        wordlist = download_wordlist(git_url, 'common.txt')
        if not wordlist:
            return

    # Read the wordlist and remove duplicates with popular directories
    paths = []
    with open(wordlist, 'r') as file:
        for line in file:
            path = line.strip()
            if extensions:
                for ext in extensions:
                    full_path = f"{path}.{ext}"
                    if full_path not in popular_dirs:  # Prevent duplicates
                        paths.append(full_path)
            else:
                if path not in popular_dirs:  # Prevent duplicates
                    paths.append(path)

    # Add common directories to the queue first
    for dir_name in popular_dirs:
        q.put(dir_name)

    # Add remaining paths from the wordlist
    for path in paths:
        q.put(path)

    total_paths = len(popular_dirs) + len(paths)  # Total number of paths to scan

    # Create a progress bar using tqdm
    progress_bar = tqdm(total=total_paths, desc="Scanning Progress", ncols=100)

    def worker():
        while not q.empty():
            path = q.get()
            full_url = f"{url}/{path}"
            try:
                response = requests.get(full_url, headers=headers, verify=False)
                if response.status_code == 200:
                    if check_for_false_positive(full_url, home_page_content):
                        with print_lock:
                            print(f"{Fore.GREEN}[+] Found: {full_url} (Status: 200){Style.RESET_ALL}")
                        found_endpoints.append(full_url)  # Add to found list
                    else:
                        with print_lock:
                            print(f"{Fore.YELLOW}[!] False Positive: {full_url} (Status: 200 but matches homepage content)")
                elif response.status_code == 403:
                    with print_lock:
                        print(f"[-] Forbidden: {full_url} (Status: 403)")
                progress_bar.update(1)  # Update the progress bar
                q.task_done()
            except requests.exceptions.RequestException as e:
                with print_lock:
                    print(f"[!] Error: {full_url} - {e}")
                progress_bar.update(1)  # Update the progress bar

    # Start the threads
    for _ in range(threads):
        t = Thread(target=worker)
        t.daemon = True
        t.start()

    q.join()
    progress_bar.close()  # Close the progress bar once the scanning is done

    # Print the summary
    show_summary()

def show_summary():
    """ Display a summary of found endpoints in green """
    print(f"\n{Fore.GREEN}Summary of Found Endpoints:{Style.RESET_ALL}")
    if found_endpoints:
        for endpoint in found_endpoints:
            print(f"{Fore.GREEN}[+] {endpoint}{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}[!] No endpoints found.{Style.RESET_ALL}")

def signal_handler(sig, frame):
    """ Handle Ctrl+C to show summary before exit """
    print("\n\n[!] Scan interrupted by user.")
    show_summary()  # Show the summary of found endpoints
    sys.exit(0)

if __name__ == "__main__":
    # Catch Ctrl+C interrupt
    signal.signal(signal.SIGINT, signal_handler)

    parser = argparse.ArgumentParser(description="Web Directory and File Enumerator with Extension Support")
    parser.add_argument("url", help="Target URL (e.g., http://example.com)")
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
