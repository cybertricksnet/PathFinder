import requests
import argparse
from threading import Thread, Lock
import queue
from tqdm import tqdm
from colorama import Fore, Style, init
import signal
import sys
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
init(autoreset=True)

print_lock = Lock()
found_endpoints_200 = set()
found_endpoints_403 = set()

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
    'addons', 'extensions', 'plugins', 'theme', 'themes', 'templates', 'store', 'shop', 'products', 'solutions'
]

def check_for_false_positive(url, home_page_content):
    try:
        response = requests.get(url, verify=False, timeout=3)
        if response.status_code == 200:
            return len(response.content) != len(home_page_content)
        else:
            return False
    except requests.exceptions.RequestException:
        return False

def scan_url(url, wordlist, extensions=None, headers=None, user_agent=None, threads=50):
    session = requests.Session()
    session.headers.update(headers if headers else {})
    if user_agent:
        session.headers['User-Agent'] = user_agent

    q = queue.Queue()

    try:
        home_page_response = session.get(url, verify=False, timeout=3)
        home_page_content = home_page_response.content
    except requests.exceptions.RequestException:
        return

    paths = []
    with open(wordlist, 'r') as file:
        for line in file:
            path = line.strip()
            if extensions:
                for ext in extensions:
                    full_path = f"{path}.{ext}"
                    if full_path not in popular_dirs:
                        paths.append(full_path)
            else:
                if path not in popular_dirs:
                    paths.append(path)

    for dir_name in popular_dirs:
        q.put(dir_name)

    for path in paths:
        q.put(path)

    total_paths = len(popular_dirs) + len(paths)
    progress_bar = tqdm(total=total_paths, desc="Scan", ncols=70, bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt}')

    def worker():
        while not q.empty():
            path = q.get()
            full_url = f"{url}/{path}"
            try:
                response = session.get(full_url, verify=False, timeout=3)
                status_code = response.status_code
                if status_code == 200:
                    if check_for_false_positive(full_url, home_page_content):
                        with print_lock:
                            if full_url not in found_endpoints_200:
                                found_endpoints_200.add(full_url)
                                print(f"{Fore.GREEN}[200 OK] Found: {full_url}{Style.RESET_ALL}")
                elif status_code == 403:
                    with print_lock:
                        if full_url not in found_endpoints_403:
                            found_endpoints_403.add(full_url)
                            print(f"{Fore.RED}[403 Forbidden] {full_url}")
                progress_bar.update(1)
                q.task_done()
            except requests.exceptions.RequestException:
                progress_bar.update(1)

    threads_list = []
    for _ in range(threads):
        t = Thread(target=worker)
        t.daemon = True
        t.start()
        threads_list.append(t)

    q.join()

    for t in threads_list:
        t.join()

    progress_bar.close()
    show_summary()

def show_summary():
    print(f"\n{Fore.GREEN}Summary of Found Endpoints:{Style.RESET_ALL}")
    if found_endpoints_200 or found_endpoints_403:
        if found_endpoints_200:
            print(f"\n{Fore.GREEN}200 OK Endpoints:{Style.RESET_ALL}")
            for endpoint in found_endpoints_200:
                print(f"{Fore.GREEN}[+] {endpoint}{Style.RESET_ALL}")
        if found_endpoints_403:
            print(f"\n{Fore.RED}403 Forbidden Endpoints:{Style.RESET_ALL}")
            for endpoint in found_endpoints_403:
                print(f"{Fore.RED}[403] {endpoint}{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}[!] No valid endpoints (200 OK or 403 Forbidden) found.{Style.RESET_ALL}")

def signal_handler(sig, frame):
    print("\n\n[!] Scan interrupted by user.")
    show_summary()
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)

    parser = argparse.ArgumentParser(description="Web Directory and File Enumerator")
    parser.add_argument("url", help="Target URL (e.g., http://example.com)")
    parser.add_argument("wordlist", help="Path to the wordlist file")
    parser.add_argument("--extensions", "-e", nargs='*', help="File extensions (e.g., php, html, js)")
    parser.add_argument("--threads", type=int, default=50, help="Number of threads (default: 50 for faster scans)")
    parser.add_argument("--headers", nargs='*', help="Custom headers 'Key:Value'")
    parser.add_argument("--user-agent", help="Custom User-Agent string")

    args = parser.parse_args()

    headers = {}
    if args.headers:
        for header in args.headers:
            key, value = header.split(':')
            headers[key.strip()] = value.strip()

    scan_url(args.url, args.wordlist, extensions=args.extensions, headers=headers, user_agent=args.user_agent, threads=args.threads)
