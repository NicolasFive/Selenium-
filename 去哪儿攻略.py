# https://www.zhihu.com/search?q=%E4%BA%94%E4%B8%80&time_interval=a_month&type=content&sort=upvoted_count
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from threading import Event
from urllib.parse import quote
import pandas as pd
from selenium.common.exceptions import NoSuchElementException, TimeoutException


def run(endEvent=Event()):
    options = webdriver.ChromeOptions()
    options.add_argument(
        '--user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"'
    )
    options.add_argument("--headless")  # 添加Headless选项
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Chrome(options=options)
    driver.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {
            "source": 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'
        },
    )
    place = "云南"
    driver.get(
        "https://travel.qunar.com/travelbook/list/{place}/hot_heat/1.htm".format(
            place=quote(place)
        )
    )
    reclusiveFinding(driver)
    print("完成爬取")
    endEvent.wait()


def reclusiveFinding(driver):
    nodes = WebDriverWait(driver, 5, 0.5).until(
        expected_conditions.presence_of_all_elements_located(
            (
                By.CLASS_NAME,
                "list_item",
            )
        )
    )

    result = list(
        map(
            lambda n: {
                "标题": elementText(n, By.CLASS_NAME, "tit", ""),
                "日期": elementText(n, By.CLASS_NAME, "date", ""),
                "天数": elementText(n, By.CLASS_NAME, "days", ""),
                "照片数量": elementText(n, By.CLASS_NAME, "photo_nums", ""),
                "费用": elementText(n, By.CLASS_NAME, "fee", ""),
                "人数": elementText(n, By.CLASS_NAME, "people", ""),
                "标签": elementText(n, By.CLASS_NAME, "trip", ""),
                "路线": elementText(n, By.CLASS_NAME, "places", ""),
            },
            nodes,
        )
    )
    exportData = {k: [node[k] for node in result] for k in result[0].keys()}

    exportToExcel(exportData, "去哪儿攻略.xlsx")

    def jumpNext():
        try:
            nextPage = driver.find_element(
                By.XPATH,
                "//div[@class='b_paging']/a[@data-beacon='click_result_nextpage']",
            )
            nextPage.click()
            print("下一页")
            reclusiveFinding(driver)
        except NoSuchElementException:
            return
        except TimeoutException:
            return
        except:
            jumpNext()

    jumpNext()


def elementText(driver, by: str, value: str, default: str = None):
    try:
        elem = driver.find_element(by, value)
        return elem.text.strip()
    except NoSuchElementException:
        return default
    except TimeoutException:
        return default


maxRow = 1


def exportToExcel(data: dict = {}, fileName: str = "output.xlsx"):
    global maxRow
    df = pd.DataFrame(data)
    try:
        with pd.ExcelWriter(fileName, mode="a", if_sheet_exists="overlay") as writer:
            df.to_excel(writer, index=False, header=False, startrow=maxRow)
            maxRow += len(df)
    except FileNotFoundError:
        with pd.ExcelWriter(fileName, mode="w") as writer:
            df_header = pd.DataFrame({k: [] for k in data.keys()})
            df_header.to_excel(writer, index=False, header=True)
        exportToExcel(data, fileName)


if __name__ == "__main__":
    endEvent = Event()
    run(endEvent)