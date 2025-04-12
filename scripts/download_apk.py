import argparse
import re
import requests
from playwright.sync_api import sync_playwright
import sys


parser = argparse.ArgumentParser()
parser.add_argument('-s', '--server', choices=['cn', 'en'], default='cn')
parser.add_argument('-ou', '--old-url')
args = parser.parse_args()

user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1938.81"


def get_apk_url(server):
    retries = 5
    for attempt in range(retries):
        try:
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(headless=True)
                context = browser.new_context(user_agent=user_agent)
                page = context.new_page()

                if server == 'cn':
                    page.goto("https://www.biligame.com/detail/?id=101772", wait_until="networkidle", timeout=90000)
                    content = page.content()
                    matches = re.findall(r'<a href="https://pkg\.bili[^"]+\.apk', content)
                    download_url = re.sub(r'^.*href="', '', matches[0])
                    return download_url

                elif server == 'en':
                    with page.expect_download(timeout=90000) as download_info:
                        try:
                            page.goto("https://d.apkpure.com/b/XAPK/com.YoStarEN.Arknights?version=latest", timeout=90000)
                        except Exception as e:
                            if (not "Page.goto: net::ERR_ABORTED at" in str(e)):
                                raise e
                    download = download_info.value
                    return download.url

                browser.close()
                break
        except Exception as e:
            print(f'URL attempt {attempt + 1} failed: {e}', file=sys.stderr)
            if attempt == retries - 1:
                print(f'Failed to get APK url after {retries} attempts.', file=sys.stderr)
                exit(1)


def download_apk(server, url):
    retries = 5
    for attempt in range(retries):
        try:
            headers = {'User-Agent': user_agent}
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            with open(f'{server}.apk', 'wb') as f:
                f.write(response.content)
            break
        except requests.exceptions.RequestException as e:
            print(f'Download attempt {attempt + 1} failed: {e}', file=sys.stderr)
            if attempt == retries - 1:
                print(f'Failed to download APK after {retries} attempts.', file=sys.stderr)
                exit(1)


if __name__ == "__main__":
    apk_url = get_apk_url(args.server)
    if args.old_url:
        if apk_url == args.old_url:
            print('Up to date.', file=sys.stdout)
            exit()
    print(apk_url, file=sys.stdout)
    download_apk(args.server, apk_url)
    exit()
