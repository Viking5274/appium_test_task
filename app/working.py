import time
from appium.webdriver.common.appiumby import AppiumBy
import datetime
from appium import webdriver
from selenium.common import NoSuchElementException

capabilities = dict(
    platformName="Android",
    automationName="uiautomator2",
    deviceName="Android",
    appPackage="com.tripadvisor.tripadvisor",
    appActivity="com.tripadvisor.android.ui.primarynavcontainer.MainActivity",
    language="en",
    locale="US",
)

appium_server_url = "http://localhost:4723"


class MyTest:
    full_match = '//*[@text="{}"]'
    contains_match = "//*[contains(@text, '{}')]"

    def make_swipe(self, up=False):
        size = self.driver.get_window_size()

        if not up:
            start_x = size["width"] // 2
            start_y = int(size["height"] * 0.6)
            end_y = int(size["height"] * 0.4)
        else:
            start_x = size["width"] // 2
            start_y = int(size["height"] * 0.3)
            end_y = int(size["height"] * 0.1)

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

    @staticmethod
    def make_click(el):
        el.click()

    def full_calendar_up(self):
        self.driver.find_element(
            AppiumBy.ANDROID_UIAUTOMATOR,
            f"new UiScrollable(new UiSelector().scrollable(true).instance(0)).scrollToBeginning(8);",
        )
        time.sleep(1)

    def select_date(self, desired_date):
        date_object = datetime.datetime.strptime(desired_date, "%m-%d-%Y")
        day = date_object.day
        year = date_object.year
        month = date_object.strftime("%B")
        month_year = str(month) + " " + str(year)

        calendar_button = self.driver.find_element(
            by=AppiumBy.ID, value="com.tripadvisor.tripadvisor:id/txtDate"
        )

        calendar_button.click()
        time.sleep(3)

        self.full_calendar_up()
        time.sleep(3)

        for _ in range(100):
            try:
                month = self.select_one(month_year, True)
                desired_field_location = month.location

                # Get the screen size
                screen_size = self.driver.get_window_size()
                screen_height = screen_size["height"]

                if abs(desired_field_location["y"] - screen_height // 2) < 100:
                    break
                else:
                    self.make_swipe()
                    break
            except:
                self.make_swipe()

        date_button = self.select_one(day)
        self.make_click(date_button)

        apply_button = self.select_one("Apply")
        self.make_click(apply_button)
        time.sleep(10)

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
                time.sleep(1)
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
                time.sleep(1)

    def setUp(self) -> None:
        self.driver = webdriver.Remote(appium_server_url, capabilities)
        time.sleep(3)

    def tearDown(self) -> None:
        if self.driver:
            self.driver.quit()

    def get_prices(self, hotel_data) -> dict:
        self.setUp()
        dict_data = {}

        for hotel_name, dates_list in hotel_data.items():
            try:
                dict_data[hotel_name] = {}
                search_button = self.select_one("Search")
                self.make_click(search_button)

                time.sleep(3)

                where_to = self.select_one("Where to?")
                self.make_click(where_to)
                time.sleep(3)

                where_to = self.select_one("Where to?")
                where_to.send_keys(hotel_name)
                self.driver.keyevent(66)
                time.sleep(5)

                self.select_hotel(hotel_name)
                time.sleep(3)

                for date_in_hotel in dates_list:
                    try:
                        self.select_date(date_in_hotel)

                        view_all_button = self.select_one("View all", True)
                        self.make_click(view_all_button)
                        time.sleep(10)

                        dict_data[hotel_name][
                            date_in_hotel
                        ] = self.get_provider_price_data()
                        self.driver.back()
                    except NoSuchElementException | NoSuchElementException as e:
                        print(
                            f"Exception occured while processing data at hotel :{hotel_name}, date: {date_in_hotel} exception: {e}"
                        )
                        continue
            except Exception as e:
                print(
                    f"Exception occured while processing data at hotel :{hotel_name}, exception: {e}"
                )

        self.tearDown()

        return dict_data
