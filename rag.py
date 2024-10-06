import asyncio
from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
from summar_text import remove_duplicates


def get_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver



def execute_js_with_selenium(url):
    driver = get_driver()
    try:
        driver.get(url)
        time.sleep(5)
        js_code = '''
                return Array.from(document.querySelectorAll('p, h1, h2, h3, span')).map(element => element.innerText).join(' ');
                '''
        page_text = driver.execute_script(js_code)
        cleaned_text = remove_duplicates(page_text)


        return cleaned_text
    finally:
        driver.quit()


async def execute_js_with_selenium_async(url):
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as pool:
        result = await loop.run_in_executor(pool, execute_js_with_selenium, url)
    return result


