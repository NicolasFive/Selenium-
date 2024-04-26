# https://www.zhihu.com/search?q=%E4%BA%94%E4%B8%80&time_interval=a_month&type=content&sort=upvoted_count
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from threading import Event
from urllib.parse import quote
import time


def run(endEvent=Event()):
    options = webdriver.ChromeOptions()
    options.add_argument(
        '--user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"'
    )
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    driver = webdriver.Chrome(options=options)
    driver.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {
            "source": 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'
        },
    )
    driver.implicitly_wait(60)  # 智能等待
    keywords = "昆明"
    driver.get(
        "https://www.zhihu.com/search?q={kw}&time_interval=a_day&type=content".format(
            kw=quote(keywords)
        )
    )
    driver.find_element(By.CLASS_NAME, "ContentItem-title")
    nodes = reclusiveFinding(driver, 0)
    for node in nodes:
        title = node.find_element(By.CLASS_NAME, "ContentItem-title")
        print(title.text.strip())
    endEvent.wait()


def reclusiveFinding(driver, prevNum):
    nodes = []
    maxRetry = 3
    curRetry = 0
    while True:
        nodes = driver.find_elements(
            By.XPATH,
            "//div[@data-za-detail-view-path-module='SearchResultList']/child::*[not(@role)]",
        )
        if len(nodes) != prevNum:
            break
        if curRetry >= maxRetry:
            return nodes
        curRetry += 1
        time.sleep(2)
    lastNode = nodes[-1]
    webdriver.ActionChains(driver).scroll_to_element(lastNode).perform()
    WebDriverWait(driver, timeout=2).until(lambda d: lastNode.is_displayed())
    print("滚动到页尾")
    return reclusiveFinding(driver, len(nodes))


if __name__ == "__main__":
    endEvent = Event()
    run(endEvent)
