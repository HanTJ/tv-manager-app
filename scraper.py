import requests
from bs4 import BeautifulSoup
import re
import logging

logger = logging.getLogger("scraper")

def get_tv_guide_html(url):
    """지정된 URL에서 HTML 콘텐츠를 가져옴. euc-kr 인코딩 처리."""
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        response.encoding = 'euc-kr'
        return response.text
    except Exception as e:
        logger.error(f"Network error fetching {url}: {e}")
        # 예외를 상위로 전파하여 스케줄러가 실패를 감지하게 함
        raise Exception(f"URL 접속 실패: {e}")

def parse_tv_guide(html_content, day, category):
    """사용자 제공 데이터 형식에 맞춘 최종 정밀 파싱."""
    if not html_content:
        return []
    
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        results = []
        
        # 채널 목록 추출
        channels = []
        channel_div = soup.find('div', id='main_channel')
        if not channel_div:
            logger.warning("Channel list DIV not found in HTML.")
            return []

        channel_links = channel_div.find_all('a')
        for link in channel_links:
            text = link.get_text(strip=True)
            if text and text not in ['◀', '▶']:
                channels.append(text)
        
        img_labels = [
            ('live.jpg', 'LIVE'),
            ('hd.jpg', 'HD'),
            ('sub.jpg', '자막'),
            ('rebroad.jpg', '재방')
        ]
        
        result_div = soup.find('div', id='result')
        if not result_div:
            logger.warning("Schedule result DIV not found in HTML.")
            return []

        main_table = result_div.find('table')
        if not main_table:
            return []

        rows = main_table.find_all('tr', recursive=False)
        for row in rows:
            cols = row.find_all('td', recursive=False)
            if not cols:
                continue
            
            hour_text = cols[0].get_text(strip=True)
            hour_match = re.search(r'(\d+)시', hour_text)
            if not hour_match:
                continue
            hour = hour_match.group(1).zfill(2)
            
            data_cols = [td for td in cols[1:] if td.find('table')]
            
            for i, td in enumerate(data_cols):
                if i < len(channels):
                    channel_name = channels[i]
                    inner_table = td.find('table')
                    inner_rows = inner_table.find_all('tr')
                    for inner_row in inner_rows:
                        inner_cols = inner_row.find_all('td')
                        if len(inner_cols) >= 2:
                            minute_text = inner_cols[0].get_text(strip=True)
                            if not minute_text.isdigit():
                                continue
                            minute = minute_text.zfill(2)
                            
                            title_td = inner_cols[1]
                            title_text = title_td.get_text(strip=True)
                            
                            imgs = title_td.find_all('img')
                            tag_text = ""
                            for img in imgs:
                                src = img.get('src', '')
                                for filename, label in img_labels:
                                    if filename in src:
                                        if label not in tag_text:
                                            tag_text += label
                                        break
                            
                            final_title = f"{title_text} {tag_text}".strip()
                            results.append((day, category, channel_name, f"{hour}:{minute}", final_title))
                            
        return results
    except Exception as e:
        logger.error(f"Parsing error: {e}")
        raise Exception(f"HTML 파싱 중 오류 발생: {e}")
