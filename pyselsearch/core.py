import contextlib
import json
from typing import Optional
from seleniumbase import Driver
import seleniumbase.config as sb_config
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from pyselsearch.proxy_gen import create_proxy_auth_extension


class GoogleSearch:
    def __init__(
        self,
        headless: bool = False,
        lang: Optional[str] = 'en',
        proxy: Optional[str] = None,
        window_size: Optional[str] = None,
        window_position: Optional[str] = None,
        desc_selector: Optional[str] = '[data-sncf]',
        ai_search_button: Optional[str] = 'button[role="link"]',
        ai_result_selector: Optional[str] = '//div[@data-container-id="main-col"]',
        ai_button_retries: int = 3,
        search_selector: Optional[str] = 'textarea[name="q"]',
        results_selector: Optional[str] = '#search div[data-rpos]'
    ):
        extension_dir = None

        if proxy:
            # proxy format: username:password@host:port
            if "@" not in proxy or ":" not in proxy:
                raise ValueError("Proxy format must be username:password@host:port")
            creds, address = proxy.split("@")
            username, password = creds.split(":")
            host, port = address.split(":")
            extension_dir = create_proxy_auth_extension(proxy_user=username,
                                                        proxy_pass=password,
                                                        proxy_host=host,
                                                        proxy_port=port)

        sb_config.binary_location = "cft"
        self.driver = Driver(
            uc=True,
            binary_location="cft",
            browser="chrome",
            headless=headless,
            extension_dir=extension_dir,
            window_size=window_size,
            window_position=window_position,
        )
        self.lang = lang
        self.DESCRIPTION_SELECTOR = desc_selector
        self.SEARCH_INPUT_SELECTOR = search_selector
        self.AI_BUTTON_SELECTOR = ai_search_button
        self.AI_RESULTS_SELECTOR = ai_result_selector
        self.AI_BUTTON_RETRIES = ai_button_retries
        self.RESULTS_CONTAINER_SELECTOR = results_selector

    @staticmethod
    def _get_if_exists(parent, by: By, selector: str):
        with contextlib.suppress(NoSuchElementException, AttributeError):
            return parent.find_element(by, selector)

    @staticmethod
    def _safe_get_text(element, attribute: Optional[str] = None) -> Optional[str]:
        if not element:
            return None
        with contextlib.suppress(Exception):
            if attribute:
                return (element.get_attribute(attribute) or '').strip() or None
            return element.text.strip() or None

    def _parse_item(self, item) -> Optional[dict]:
        link_element = self._get_if_exists(item, By.TAG_NAME, "a")
        link = self._safe_get_text(link_element, "href")
        title_element = self._get_if_exists(link_element, By.TAG_NAME, "h3")
        title = self._safe_get_text(title_element)

        if not link or not title:
            return None

        desc_parts = item.find_elements(By.CSS_SELECTOR, self.DESCRIPTION_SELECTOR)
        description = " ".join(self._safe_get_text(el) for el in desc_parts if self._safe_get_text(el)).strip() or None

        return {
            "url": link,
            "title": title,
            "description": description,
        }

    @staticmethod
    def _parse_ai_item(item) -> Optional[dict]:
        text = item.text.strip()
        start = text.find("{")
        end = text.rfind("}") + 1
        if start == -1 or end == 0:
            return {}
        try:
            return json.loads(text[start:end])
        except json.JSONDecodeError:
            return {}

    def _click_ai_button_with_retries(self, sleep_time: int) -> None:
        for attempt in range(self.AI_BUTTON_RETRIES):
            buttons = self.driver.cdp.find_elements(self.AI_BUTTON_SELECTOR)
            if len(buttons) > 0:
                self.driver.cdp.gui_click_element(self.AI_BUTTON_SELECTOR)
                return
            if attempt < self.AI_BUTTON_RETRIES - 1:
                self.driver.uc_activate_cdp_mode(f"https://www.google.com/?hl={self.lang}")
                self.driver.sleep(sleep_time)
        raise NoSuchElementException(f"AI search button not found: {self.AI_BUTTON_SELECTOR}")

    def search(self, query: str, sleep_time: int = 2, ai_mode=False) -> list[dict]:
        results = []
        self.driver.sleep(int(sleep_time/2))
        self.driver.uc_activate_cdp_mode(f"https://www.google.com/?hl={self.lang}")
        self.driver.sleep(int(sleep_time/2))
        if ai_mode:
            self._click_ai_button_with_retries(sleep_time)
        else:
            self.driver.cdp.gui_click_element(self.SEARCH_INPUT_SELECTOR)
        self.driver.sleep(sleep_time)
        self.driver.connect()
        self.driver.press_keys(self.SEARCH_INPUT_SELECTOR, query + "\n")
        self.driver.sleep(sleep_time)
        with contextlib.suppress(Exception):
            self.driver.disconnect()
            self.driver.sleep(sleep_time)
            self.driver.uc_gui_click_captcha()
            # TODO: need to figure out later how to solve this re-captcha
            self.driver.connect()
        self.driver.sleep(sleep_time)
        if ai_mode:
            lister_items = self.driver.find_elements(By.XPATH, self.AI_RESULTS_SELECTOR)
            parser = self._parse_ai_item
        else:
            lister_items = self.driver.find_elements(By.CSS_SELECTOR, self.RESULTS_CONTAINER_SELECTOR)
            parser = self._parse_item

        for item in lister_items:
            result = parser(item)
            if result:
                results.append(result)

        self.driver.quit()
        return results
