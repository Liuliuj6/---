"""
头条爬虫核心模块
"""
import traceback
import requests
import re
import logging
from typing import Dict, List, Optional, Any
from urllib.parse import urlencode
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
import urllib.parse
import datetime
logger = logging.getLogger(__name__)



service = Service('/usr/local/bin/msedgedriver')
service.start()
driver = webdriver.Remote(service.service_url)
class ToutiaoSpider:
    """微博爬虫类"""

    def search_toutiao(self, keyword: str, page: int = 0) -> List[Dict[str, Any]]:
        """搜索微博数据"""
        try:
            # 构建搜索URL
            params = {
                'dvpf': 'pc',
                'source': 'pagination',
                'keyword': keyword,
                'pd': 'synthesis',
                'action_type': 'pagination',
                'page_num': page,
            }

            search_url = f"https://so.toutiao.com/search?{urlencode(params)}"
            print(search_url)

            # 发送请求
            driver.get(url=search_url)
            try:
                # 等待页面加载完成，最长等待20秒
                WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, 's-result-list')))
                page_source = BeautifulSoup(driver.page_source, 'html.parser')


                # 添加调试日志：记录响应信息
                logger.info(f"[调试] 搜索请求成功")

                # 检查是否被重定向到登录页面
                if 'login' in driver.current_url:
                    logger.warning("[调试] 检测到被重定向到登录页面")

                # 检查是否包含反爬虫提示
                if '验证码' in driver.page_source:
                    logger.warning("[调试] 检测到验证码或反爬虫机制")

                # 解析搜索结果
                toutiao_list = self._parse_search_results(page_source, keyword)
            except Exception as e:
                logger.error(f"webdriver搜索头条失败: {e}")
                return []
            return toutiao_list
            
        except Exception as e:
            logger.error(f"搜索头条失败: {e}")
            return []

    def _parse_search_results(self, html, keyword: str) -> List[Dict[str, Any]]:
        """解析搜索结果页面"""
        toutiao_list = []

        try:
            # 添加调试日志：检查页面结构
            logger.info(f"[调试] 开始解析HTML，长度: {len(html)} 字符")

            cards = html.find_all('div', class_='cs-view cs-view-block cs-card-content')
            for card in cards:
                if not card.find('div', class_='flex-1 text-default text-m text-regular') and not card.find('div', class_='flex-1 text-darker text-l text-regular'):
                    cards.remove(card)
            if not cards:
                logger.info("[错误] 未找到card")

            for card in cards:
                try:
                    toutiao_data = self._extract_toutiao_from_card(card, keyword)
                    if toutiao_data:
                        toutiao_list.append(toutiao_data)
                except Exception as e:
                    logger.warning(f"解析头条卡片失败: {e}")
                    traceback.print_exc()
                    continue

            logger.info(f"解析到 {len(toutiao_list)} 条头条数据")

        except Exception as e:
            logger.error(f"解析搜索结果失败: {e}")

        return toutiao_list


    def _extract_toutiao_from_card(self, card, keyword: str) -> Optional[Dict[str, Any]]:
        """从网页卡片中提取头条数据"""
        try:
            isLongText = False
            title = '无'
            ip_location = '无'
            # 提取基本信息
            content_elem1 = card.find('div', class_='flex-1 text-darker text-l text-regular')
            if content_elem1:
                is_official = False
                content_elem = content_elem1.find('span', class_='text-underline-hover') if content_elem1 else None
                content = content_elem.get_text(strip=True)
            else:
                is_official = True
                content_elem1 = card.find('div', class_='flex-1 text-default text-m text-regular')
                content_elem = content_elem1.find('span', class_='text-underline-hover') if content_elem1 else None
                content = content_elem.get_text(strip=True) if content_elem else None
            if content and len(content) >= 140:
                isLongText = True
            if is_official:
                title_elem = card.find('div', class_='flex-1 text-darker text-xl text-medium d-flex align-items-center overflow-hidden')
                title_a = title_elem.find('a') if title_elem else None
                title = title_a.get_text(strip=True) if title_a else ''
            # 提取用户信息
            user_elem1 = card.find('div', class_='flex-1 text-darker text-m text-medium')
            if user_elem1:
                user_elem = user_elem1.find('span', class_='text-underline-hover')
                user_name = user_elem.get_text(strip=True) if user_elem else ''
            else:
                user_elem1 = card.find('div', class_='cs-view cs-view-flex align-items-center flex-row cs-source-content')
                user_elem = user_elem1.find('span', class_='text-ellipsis') if user_elem1 else None
                user_name = user_elem.get_text(strip=True) if user_elem else ''

            # 提取时间
            if is_official:
                time_elem1 = card.find('div', class_='cs-view cs-view-flex align-items-center flex-row cs-source-content')
                time_elem = time_elem1.find_all('span', class_='text-ellipsis') if time_elem1 else None
                created_at = time_elem[-1].get_text(strip=True) if time_elem else None
            else:
                time_elem1 = card.find('div', class_='cs-view cs-view-flex align-items-center flex-row cs-text-split text-light text-s')
                created_at = time_elem1.find('span').get_text(strip=True) if time_elem1 else None
            if created_at:
                if not "月" in created_at:
                    created_at = "无数据"
            else:
                created_at = "无数据"
            
            # 提取互动数据
            action_elem = card.find('div', class_='cs-view cs-view-flex align-items-center flex-row cs-text-split margin-bottom-8 text-light text-m')
            reposts_count = 0
            comments_count = 0
            attitudes_count = 0

            if action_elem:
                action_links = action_elem.find_all('span')
                for link in action_links:
                    text = link.get_text(strip=True)
                    if '转发' in text:
                        reposts_count = self._extract_count(text)
                    elif '评论' in text:
                        comments_count = self._extract_count(text)
                    elif '赞' in text:
                        attitudes_count = self._extract_count(text)

            # 获取用户头像url
            url = card.find('img', class_='object-cover radius-circle')
            #print(url['src'])
            # 获取用户id
            user_id = '无'
            user_id_elem = card.find('a', class_='cs-view margin-bottom-4 cs-view-block')
            if user_id_elem and 'href' in user_id_elem.attrs and not is_official:
                href_value = user_id_elem['href']
                parsed_url = urllib.parse.urlparse(href_value)
                query_params = urllib.parse.parse_qs(parsed_url.query)
                target_url = urllib.parse.unquote(query_params['url'][0]) if query_params else None
                match = re.search(r'/user/(\d+)/', target_url)
                if match:
                    user_id = match.group(1)
            # 获取微博id
            mblog_id = '无'
            if not is_official:
                mblog_id_elem1 = card.find('div', class_='cs-view margin-bottom-4 cs-view-block')
                mblog_id_elem = mblog_id_elem1.find('a', class_='cs-view margin-bottom-4 cs-view-block') if mblog_id_elem1 else '无'
                if mblog_id_elem and 'href' in mblog_id_elem.attrs:
                    href_value = mblog_id_elem['href']
                    if href_value:
                        parsed_url = urllib.parse.urlparse(href_value)
                        query_params = urllib.parse.parse_qs(parsed_url.query)
                        urllib.quote(query_params.encode('utf-8'))
                        match = re.search(r'/a(\d+)/', target_url)
                        mblog_id = match.group(1)
            else:
                mblog_id_elem = card.find('a', class_='text-ellipsis text-underline-hover')
                if mblog_id_elem and 'href' in mblog_id_elem.attrs:
                    href_value = mblog_id_elem['href']
                    if href_value:
                        parsed_url = urllib.parse.urlparse(href_value)
                        query_params = urllib.parse.parse_qs(parsed_url.query)
                        target_url = urllib.parse.unquote(query_params['url'][0])
                        mblog_id = f"other_link:{target_url}"

            # 提取图片url和数量
            images = card.find_all('img', class_='object-cover')
            image_urls = []
            for img in images:
                if 'src' in img.attrs:
                    image_urls.append(img['src'])
            image_count = len(image_urls)

            # 提取用户ip
            if not is_official:
                link_tag = card.find('a')
                if link_tag and 'href' in link_tag.attrs:
                    href_value = link_tag['href']
                    parsed_url = urllib.parse.urlparse(href_value)
                    query_params = urllib.parse.parse_qs(parsed_url.query)
                    target_url = urllib.parse.unquote(query_params['url'][0])
                    driver1 = webdriver.Remote(service.service_url)
                    try:
                        driver1.get(url=target_url)
                        WebDriverWait(driver1, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'profile-container')))
                        button = driver1.find_element(By.CLASS_NAME, "more-info")
                        button.click()
                        WebDriverWait(driver1, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'address')))
                        user_page_source = BeautifulSoup(driver1.page_source, 'html.parser')
                        ip_location1 = user_page_source.find('p', class_='address') if user_page_source else None
                        ip_location = ip_location1.get_text(strip=True) if ip_location1 else '无'
                        ip_location.replace('IP属地：', '', 1)
                    finally:
                        driver1.quit()
                else:
                    logger.warning("未找到用户主页url")

            if content:
                return {
                    '_id': mblog_id,
                    'is_official': is_official,
                    'created_at': created_at,
                    'geo:detail:title': title,
                    'reposts_count': reposts_count,
                    'comments_count': comments_count,
                    'attitudes_count': attitudes_count,
                    'content': content,
                    'isLongText': isLongText,
                    'user_nick_name': user_name,
                    'keyword': keyword,
                    'ip_location': ip_location,
                    'user:avatar_hd': url['src'] if url else '无',
                    'user: _id': user_id,
                    'crawl_time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'pic_urls': image_urls,
                    'pic_count': image_count,
                }
            else:
                return None

        except Exception as e:
            print(f"提取头条数据失败: ")
            traceback.print_exc()
            return None
    def _extract_count(self, text: str) -> int:
        """从文本中提取数字"""
        try:
            # 提取数字
            numbers = re.findall(r'\d+', text)
            if numbers:
                return int(numbers[0])
            return 0
        except:
            return 0
    def driver_quit(self):
        driver.quit()
