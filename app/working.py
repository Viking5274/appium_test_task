import time

from appium.webdriver.common.appiumby import AppiumBy
import datetime
from appium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

capabilities = dict(
    platformName="Android",
    automationName="uiautomator2",
    deviceName="9c6ceb8e",
    appPackage="com.tripadvisor.tripadvisor",
    appActivity="com.tripadvisor.android.ui.primarynavcontainer.MainActivity",
    appWaitActivity="*",
    language="en",
    locale="US",
)

appium_server_url = "http://localhost:4723/wd/hub"


class MyTest:
    full_match = '//*[@text="{}"]'
    contains_match = "//*[contains(@text, '{}')]"

    def make_swipe(self, up=False):
        size = self.driver.get_window_size()

        if not up:
            start_y = int(size["height"] * 0.6)
            end_y = int(size["height"] * 0.4)
        else:
            start_y = int(size["height"] * 0.3)
            end_y = int(size["height"] * 0.1)

        start_x = size["width"] // 2
        self.driver.swipe(start_x=start_x, start_y=start_y, end_x=start_x, end_y=end_y)

    def select_one(self, text, contains=False):
        if contains:
            return self.driver.find_element(
                by=AppiumBy.XPATH, value=self.contains_match.format(text)
            )
        else:
            return self.driver.find_element(
                by=AppiumBy.XPATH, value=self.full_match.format(text)
            )

    def select_many(self, text, contains=False):
        if contains:
            return self.driver.find_elements(
                by=AppiumBy.XPATH, value=self.contains_match.format(text)
            )
        else:
            return self.driver.find_elements(
                by=AppiumBy.XPATH, value=self.full_match.format(text)
            )

    def click_on_btn(self, btn_name):
        button = self.select_one(btn_name)
        self.wait.until(EC.element_to_be_clickable(button))
        self.make_click(button)

    @staticmethod
    def make_click(el):
        el.click()

    def full_calendar_up(self):
        self.driver.find_element(
            AppiumBy.ANDROID_UIAUTOMATOR,
            "new UiScrollable(new UiSelector().scrollable(true).instance(0)).scrollToBeginning(8);",
        )

    def select_date(self, desired_date):
        date_object = datetime.datetime.strptime(desired_date, "%m-%d-%Y")
        day = date_object.day
        year = date_object.year
        month = date_object.strftime("%B")
        month_year = f"{str(month)} {str(year)}"

        calendar_button = self.driver.find_element(
            by=AppiumBy.ID, value="com.tripadvisor.tripadvisor:id/txtDate"
        )
        self.wait.until(EC.element_to_be_clickable(calendar_button))
        calendar_button.click()

        self.full_calendar_up()

        for _ in range(100):
            try:
                month = self.select_one(month_year, True)
                desired_field_location = month.location

                # Get the screen size
                screen_size = self.driver.get_window_size()
                screen_height = screen_size["height"]

                if abs(desired_field_location["y"] - screen_height // 2) >= 100:
                    self.make_swipe()
                break
            except:
                self.make_swipe()

        self.click_on_btn(day)
        self.click_on_btn("Apply")

    def get_provider_price_data(self):
        info_dict = {}
        for _ in range(5):
            offers = self.driver.find_elements(
                by=AppiumBy.ID, value="com.tripadvisor.tripadvisor:id/cardHotelOffer"
            )
            for element in offers:
                try:
                    provider = element.find_element(
                        by=AppiumBy.ID,
                        value="com.tripadvisor.tripadvisor:id/txtProviderName",
                    ).text
                except NoSuchElementException:
                    try:
                        provider = element.find_element(
                            by=AppiumBy.ID,
                            value="com.tripadvisor.tripadvisor:id/imgProviderLogo",
                        ).get_attribute("content-desc")
                    except NoSuchElementException:
                        provider = None
                try:
                    price = element.find_element(
                        by=AppiumBy.ID,
                        value="com.tripadvisor.tripadvisor:id/txtPriceTopDeal",
                    ).text
                except NoSuchElementException:
                    price = None
                if price and provider:
                    info_dict[provider] = price
            self.make_swipe()

        return info_dict

    def select_hotel(self, hotel_name):
        for _ in range(50):
            try:
                hotel = self.select_many(hotel_name, True)
                self.make_click(hotel[1])
                break
            except:
                self.make_swipe()

    def setUp(self) -> None:
        self.driver = webdriver.Remote(appium_server_url, capabilities)
        self.wait = WebDriverWait(self.driver, 10)
        time.sleep(3)

    def tearDown(self) -> None:
        if self.driver:
            self.driver.quit()

    def get_prices(self, hotel_data) -> dict:
        self.setUp()
        dict_data = {}.items()

        for hotel_name, dates_list in hotel_data.items():

            # dict_data[hotel_name] = {}
            self.click_on_btn("Search")
            self.click_on_btn("Where to?")
            self.click_on_btn("Where to?")

            where_to = self.select_one("Where to?")
            where_to.send_keys(hotel_name)

            self.driver.keyevent(66)
            self.wait.until_not(EC.element_to_be_clickable(where_to))

            self.select_hotel(hotel_name)

            for date_in_hotel in dates_list:
                try:
                    self.select_date(date_in_hotel)

                    view_all_button = self.select_one("View all", True)
                    self.make_click(view_all_button)
                    self.wait.until_not(EC.element_to_be_clickable(view_all_button))

                    dict_data[hotel_name][
                        date_in_hotel
                    ] = self.get_provider_price_data()
                    self.driver.back()
                except NoSuchElementException | NoSuchElementException as e:
                    print(
                        f"Exception occured while processing data at hotel :{hotel_name}, date: {date_in_hotel} exception: {e}"
                    )

        self.tearDown()

        return dict_data


# if __name__ == "__main__":
#     a = MyTest()
#     a.get_prices({"New York Hilton Midtown": ["06-10-2023", "06-12-2023"]})
