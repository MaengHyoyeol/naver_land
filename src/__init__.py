"""
네이버 부동산 데이터 수집 프로젝트
undetected_chromedriver 기반 실제 작동 크롤러
"""

__version__ = "2.1.1"
__author__ = "Your Name"

from .naver_crawler import NaverRealEstateCrawler
from .data_parser import DataParser
from .display import DataDisplay

__all__ = ['NaverRealEstateCrawler', 'DataParser', 'DataDisplay']


