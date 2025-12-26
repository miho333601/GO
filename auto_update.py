import asyncio
import os
import sys
from playwright.async_api import async_playwright
from github import Github

# 讀取 yml 傳過來的變數
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN") 
GITHUB_USER = "miho333601"
REPO_NAME = "GO"
DESTINATION_PATH = "schedule.png"
TARGET_URL = "https://www.cingkang.com/schedule_auo.php"

async def capture_schedule():
    print("--- 步驟 1: 開始擷取網頁 ---")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1280, 'height': 800})
        page = await context.new_page()
        try:
            await page.goto(TARGET_URL, wait_until="networkidle", timeout=60000)
            calendar = page.locator(".calendar-body")
            if await calendar.count() > 0:
                await calendar.screenshot(path="schedule.png")
                print("✅ 截圖成功")
                return True
            else:
                print("❌ 找不到 calendar-body")
                return False
        except Exception as e:
            print(f"❌ 擷取異常: {e}")
            return False
        finally:
            await browser.close()

def upload_to_github():
    print("--- 步驟 2: 上傳至 GitHub ---")
    if not GITHUB_TOKEN:
        print("❌ 錯誤：找不到 GITHUB_TOKEN")
        sys.exit(1)
    try:
        g = Github(GITHUB_TOKEN)
        repo = g.get_user(GITHUB_USER).get_repo(REPO_NAME)
        with open("schedule.png", 'rb') as file:
            content = file.read()
        try:
            contents = repo.get_contents(DESTINATION_PATH)
            repo.update_file(contents.path, "Update schedule", content, contents.sha)
        except:
            repo.create_file(DESTINATION_PATH, "Initial upload", content)
        print("✅ 上傳成功")
    except Exception as e:
        print(f"❌ 上傳失敗: {e}")
        sys.exit(1)

async def main():
    if await capture_schedule():
        upload_to_github()

if __name__ == "__main__":
    asyncio.run(main())
