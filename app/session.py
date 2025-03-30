from playwright.async_api import async_playwright

async def save_session():
    user_data_dir = "user_data"
    async with async_playwright() as p:
        browser = await p.chromium.launch_persistent_context(user_data_dir, headless=False)
        page = browser.pages[0] if browser.pages else await browser.new_page()
        await page.goto("https://web.whatsapp.com")
        input("Нажмите Enter после входа в аккаунт...")
        await browser.close()