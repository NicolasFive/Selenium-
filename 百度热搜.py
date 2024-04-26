from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from threading import Event


def run(endEvent=Event()):
    options = webdriver.ChromeOptions()
    options.add_argument(
        '--user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.31"'
    )
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(5)  # 智能等待
    driver.get("https://www.baidu.com")

    # 等待热搜加载（hotsearch-item）
    # 使用显性等待， 等待元素id="TANGRAM__PSP_11__changeSmsCodeItem"加载到dom树中，等待上限是10s,每0.8秒去验证一下条件是否成立.
    WebDriverWait(driver, 10, 0.8).until(
        EC.presence_of_element_located((By.CLASS_NAME, "hotsearch-item"))
    )

    # 获取刷新按钮（智能等待5s）
    refreshBtn = driver.find_element(By.ID, "hotsearch-refresh-btn")
    hotdict = dict()
    maxLen = 1000
    try:
        while len(hotdict) < maxLen:
            # 获取热搜标题
            contents = driver.find_elements(By.CLASS_NAME, "title-content")
            for c in contents:
                index = c.find_element(
                    By.CLASS_NAME, "title-content-index"
                ).text.strip()
                title = c.find_element(
                    By.CLASS_NAME, "title-content-title"
                ).text.strip()
                indexInt = int(index) if bool(index) else -1
                if indexInt in hotdict:
                    raise StopIteration
                hotdict[indexInt] = title
                if len(hotdict) >= maxLen:
                    raise StopIteration
            refreshBtn.click()
    except StopIteration:
        pass
    sortedKeys = sorted(hotdict.keys())
    for k in sortedKeys:
        print("{0:3d} {1}".format(k, hotdict[k]))
    endEvent.wait()


if __name__ == "__main__":
    endEvent = Event()
    run(endEvent)
