"""crawling_browser 패키지

undetected-chromedriver를 사용한 웹 크롤링 라이브러리

Example:
    >>> from crawling_browser import Browser
    >>> browser = Browser(session_id="main")
    >>> browser.goto("https://example.com")
    >>> element = browser.element("//h1")
    >>> print(element.text)
    >>> browser.close()
"""

from .browser import Browser
from .element import Element
from .config import CHROME_VERSION

__version__ = "0.1.2"
__all__ = ["Browser", "Element", "CHROME_VERSION"]