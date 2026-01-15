import re
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
import feedparser
from urllib.parse import urlparse, parse_qs
from typing import List,Dict

def discover_feeds(page_url: str, timeout: int = 10) -> List[str]:
    """
    page_url(웹페이지)에서 RSS/Atom 피드 링크를 발견해서 절대 URL 목록으로 반환.
    우선순위:
      1) <link rel="alternate" type="application/rss+xml|application/atom+xml"...>
      2) 본문 <a href="...rss|atom|feed|.xml"> 형태 휴리스틱
    """
    headers = {"User-Agent": "Mozilla/5.0 (RSS-Discovery/1.0)"}
    r = requests.get(page_url, headers=headers, timeout=timeout)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")
    feeds: list[str] = []

    # 1) 표준 feed discovery
    for link in soup.find_all("link", attrs={"rel": re.compile(r"\balternate\b", re.I)}):
        typ = (link.get("type") or "").lower().strip()
        href = (link.get("href") or "").strip()
        if not href:
            continue
        if typ in ("application/rss+xml", "application/atom+xml", "application/rdf+xml", "text/xml", "application/xml"):
            feeds.append(urljoin(page_url, href))

    # 2) 휴리스틱 (일부 사이트는 <a>로만 걸어둠)
    if not feeds:
        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            if not href:
                continue
            h = href.lower()
            if any(k in h for k in ("rss", "atom", "feed")) or h.endswith((".rss", ".xml")):
                feeds.append(urljoin(page_url, href))

    # 중복 제거(순서 유지)
    uniq = []
    seen = set()
    for f in feeds:
        if f not in seen:
            seen.add(f)
            uniq.append(f)
    return uniq


if __name__ == "__main__":
    pass

def url_change_html(url):
    # 가져온 url에서 RSS로 된 것 탐색
    rss_url = discover_feeds(url)
    
    # requests로 RSS 전체 페이지 요청
    response = requests.get(rss_url[0])
    
    # HTTP 상태 코드 체크
    if response.status_code // 100 != 2 :
        print("status_code : ", response.status_code)
        exit()

    # HTML 문서인지 확인
    if 'text/html' not in response.headers['Content-Type']:
        print('not html')
        exit()
    
    # HTML 파싱
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')
    return soup

def append_link(category_parse):
    """
    feedparser로 파싱한 RSS 객체에서 기사 entries을 sort_value에 추가하는 함수

    Args:
        category_parse: 카테고리별 RSS파싱 한거

    Returns:
        sort_value(list): 각 기사 entries가 담긴 리스트
    """
    sort_value = []
    for i in category_parse.entries:
        sort_value.append(i)
    return sort_value


def rss_parsing(soup):
    
    
    # input 태그 중 value가 http로 시작하는 RSS 링크만 수집
    rss_links = [a.get("value") for a in soup.select('input[value^="http"]')]
    
    

    # rss 파싱 후 카테고리별 기사 리스트 생성
    accident_list = append_link(feedparser.parse(rss_links[5]))
    policy_list = append_link(feedparser.parse(rss_links[6]))
    business_list = append_link(feedparser.parse(rss_links[7]))
    international_list = append_link(feedparser.parse(rss_links[8]))
    tech_list = append_link(feedparser.parse(rss_links[9]))



    # 카테고리별로 기사들이 있는 딕셔너리
    feeds = {
        "policy": policy_list,
        "accident": accident_list,
        "business": business_list,
        "international": international_list,
        "tech": tech_list
    }
    return feeds



def get_idx(feeds):
    """
    모든 카테고리의 기사 정보를 하나씩 리스트로 가져오는 함수.

    각 기사에서:
    - idx 추출
    - 제목, 링크 수집
    - 링크에서 날짜 파싱
    - 카테고리 정보 포함

    Returns:
        news_list[dict]: 기사 정보가 담긴 딕셔너리 리스트
    """
    news_list = [] 

    for category, feed_list in feeds.items():  
            for entry in feed_list:
                idx = pasing_idx(entry.link)
                title = entry.title
                link = entry.link
                from_date = get_date(entry.link)
                news_list.append({
                    "idx": idx,
                    "title": title,
                    "link": link,
                    "category": category,  
                    "from_date": from_date
                })

    return news_list

    


def pasing_idx(url):
    """
    기사 URL에서 idx 값을 추출하는 함수
    (parse_qs = 쿼리 문자열(링크)를 딕셔너리로 변환 하여 idx만 뽑을수있게 해줌)

    Args:
        url : 기사 URL

    Returns:
        true : idx 값
        None : None
    """
    parsed = urlparse(url)
    result = parse_qs(parsed.query)
    return result.get("idx",[None])[0]
    


def get_date(url):
    """
    기사 페이지에 접속하여 작성 날짜를 추출하는 함수
    
    Args:
        url : 기사 링크

    Returns:
        link_date : 기사 날짜 (문자열)
    """
    response = requests.get(url)
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')
    rss_links = [a.get_text(strip=True) for a in soup.select('div[id="news_util01"]')]

    result = rss_links[0]
    link_date = result[5:]
    return link_date


