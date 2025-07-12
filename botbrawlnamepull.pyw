from playwright.sync_api import sync_playwright

pages = [
    {
        "url": "https://botbrawl.appspot.com/InBoxRed.html",
        "file_name": r"C:\BotBrawl\automation\inboxredholder.txt"
    },
    {
        "url": "https://botbrawl.appspot.com/InBoxWhite.html",
        "file_name": r"C:\BotBrawl\automation\inboxwhiteholder.txt"
    },
    {
        "url": "https://botbrawl.appspot.com/OnDeckRed.html",
        "file_name": r"C:\BotBrawl\automation\ondeckredholder.txt"
    },
    {
        "url": "https://botbrawl.appspot.com/OnDeckWhite.html",
        "file_name": r"C:\BotBrawl\automation\ondeckwhiteholder.txt"
    }
]

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    for item in pages:
        url = item["url"]
        file_name = item["file_name"]

        page.goto(url)
        # Wait until #root is visible (like your Selenium wait)
        page.wait_for_selector("#root", timeout=5000)
        text = page.inner_text("#root").strip()

        with open(file_name, 'w', encoding='utf-8') as f:
            f.write(text)

        print(f"✅ Saved {file_name}: {text}")

    browser.close()
