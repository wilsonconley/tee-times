from __future__ import annotations

import typing as t
from datetime import datetime
from pathlib import Path

import selenium.webdriver.support.expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException

DRIVER_PATH = Path(__file__).parent / "chromedriver"

month_mapping = {
    "01": "January",
    "02": "February",
    "03": "March",
    "04": "April",
    "05": "May",
    "06": "June",
    "07": "July",
    "08": "August",
    "09": "September",
    "10": "October",
    "11": "November",
    "12": "December",
}


class WebCrawler:
    driver: webdriver.Chrome

    def __init__(self) -> None:
        self.driver = webdriver.Chrome(executable_path=DRIVER_PATH)

    def __enter__(self) -> WebCrawler:
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.driver.quit()

    def go_to_page(self, webpage: str) -> None:
        self.driver.get(webpage)

    def ensure_clickable(
        self, by: str, identifier: str, timeout: float = 20.0
    ) -> WebElement:
        element = WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable((by, identifier))
        )
        return element


def get_credentials() -> t.Tuple[str, str]:
    path = Path(__file__).parent.resolve()
    credentials_file = path / ".credentials"
    if not credentials_file.exists():
        username = input("Input username: ")
        password = input("Input password: ")
        with open(credentials_file, "w", encoding="utf-8") as file:
            file.writelines([username, "\n", password])
    else:
        with open(credentials_file, "r", encoding="utf-8") as file:
            username, password = [line.strip() for line in file.readlines()]
    return username, password


def main() -> None:
    year = "2023"
    month = "04"
    day = "05"
    time = "07:45 AM"

    now = datetime.now()

    username, password = get_credentials()

    month_str = month_mapping[month]

    tee_times_page = "https://web1.myvscloud.com/wbwsc/sccharlestonwt.wsc/search.html?module=GR&search=no"

    with WebCrawler() as webcrawler:
        # Go to tee times page
        webcrawler.go_to_page(tee_times_page)

        # Log in
        webcrawler.ensure_clickable(By.CLASS_NAME, "login-link").click()

        # Set username
        webcrawler.ensure_clickable(By.ID, "weblogin_username").send_keys(username)

        # Set password
        webcrawler.ensure_clickable(By.ID, "weblogin_password").send_keys(password)

        # Click login
        webcrawler.ensure_clickable(By.ID, "weblogin_buttonlogin").click()

        # Sometimes you have to continue with login
        try:
            webcrawler.ensure_clickable(
                By.ID, "websessionalert_buttoncontinue", timeout=5.0
            ).click()
        except TimeoutException:
            pass

        # Navigate back to tee times
        webcrawler.go_to_page(tee_times_page)

        # Open date menu
        webcrawler.ensure_clickable(By.ID, "begindate").click()

        # Select year
        year_ = webcrawler.ensure_clickable(By.CLASS_NAME, "picker__select--year")
        for option in year_.find_elements(By.TAG_NAME, "option"):
            if option.text == year:
                option.click()
                break

        # Select month
        month_ = webcrawler.ensure_clickable(By.CLASS_NAME, "picker__select--month")
        for option in month_.find_elements(By.TAG_NAME, "option"):
            if option.text == month_str:
                option.click()
                break

        # Select day
        table = webcrawler.ensure_clickable(By.ID, "begindate_table")
        table.click()
        for option in table.find_elements(By.CLASS_NAME, "picker__day"):
            if int(option.accessible_name[0:2]) == int(month) and int(
                option.text
            ) == int(day):
                option.click()
                break

        # Select time
        webcrawler.ensure_clickable(By.ID, "begintime").click()
        webcrawler.ensure_clickable(By.CLASS_NAME, "picker__list-item").click()
        for option in webcrawler.driver.find_elements(
            By.CLASS_NAME, "picker__list-item"
        ):
            if option.text == time:
                option.click()
                break

        # Search
        webcrawler.ensure_clickable(By.ID, "grwebsearch_buttonsearch").click()

        # Get first available tee time
        webcrawler.ensure_clickable(By.CLASS_NAME, "button-cell--cart")
        webcrawler.driver.find_elements(By.CLASS_NAME, "button-cell--cart")[0].click()

        # Click to book
        # webcrawler.ensure_clickable(By.ID, "golfmemberselection_buttononeclicktofinish").click()

    print("done!")


if __name__ == "__main__":
    main()
