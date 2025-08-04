import contextlib
from typing import Optional
from seleniumbase import Driver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from pyselsearch.proxy_gen import create_proxy_auth_extension


class GoogleSearch:
    def __init__(
        self,
        headless: bool = True,
        lang: Optional[str] = 'en',
        proxy: Optional[str] = None,
        desc_selector: Optional[str] = '[data-sncf]',
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

        self.driver = Driver(
            uc=True,
            driver_version="136",
            headless=headless,
            extension_dir=extension_dir
        )

        self.driver.uc_activate_cdp_mode()
        self.lang = lang
        self.DESCRIPTION_SELECTOR = desc_selector
        self.SEARCH_INPUT_SELECTOR = search_selector
        self.RESULTS_CONTAINER_SELECTOR = results_selector

    @staticmethod
    def _get_if_exists(parent, by: By, selector: str):
        with contextlib.suppress(NoSuchElementException):
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

    def search(self, query: str, sleep_time: int = 2) -> list[dict]:
        results = []
        self.driver.uc_open_with_reconnect(f"http://www.google.com/?hl={self.lang}")
        self.driver.sleep(sleep_time)

        with contextlib.suppress(Exception):
            self.driver.uc_gui_click_captcha(timeout=10)
            self.driver.sleep(sleep_time)

        self.driver.reconnect()
        search_box = self.driver.find_element(By.CSS_SELECTOR, self.SEARCH_INPUT_SELECTOR)
        search_box.send_keys(query)
        search_box.submit()
        self.driver.sleep(sleep_time)

        lister_items = self.driver.find_elements(By.CSS_SELECTOR, self.RESULTS_CONTAINER_SELECTOR)
        for item in lister_items:
            result = self._parse_item(item)
            if result:
                results.append(result)

        self.driver.quit()
        return results
