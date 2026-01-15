from rss import rss_fetcher as rs
import pymysql
import configparser
import config
from database import db_managy as db
import logging_config as log
import logging
from typing import List,Dict

def main():
    """
        RSS로 수집한 뉴스 데이터를 DB에 저장하는 함수
        
        동작 순서:
        1. 로깅 설정 및 로거 생성
        2. RSS로 가져온 기사 목록들을 news_list에 추가
        3. DB연결에 관련된 설정을 ini파일에서 가져오기
        4. DB연결
        5. 기사 idx를 비교하여 중복 검사 후 신규 기사만 저장(insert_news)
        6. 같은 기사더라도 카테고리가 다르면 news_category 테이블에 추가
        7. DB 연결 종료
        
        Raises:
            Exception: DB연결 또는 처리 중에 오류 발생 시 로그를 남기고 프로그램 종료
    """
    log.setup_logging()
    logger = logging.getLogger(__name__)
    soup = rs.url_change_html("https://www.boannews.com/")
    feeds = rs.rss_parsing(soup)
    news_list = rs.get_idx(feeds)

    try:
        config = configparser.ConfigParser()
        config.read('/home/ktech/my_project/config/db.ini', encoding='utf-8')
        db_config = config['database']
    except Exception as e :
        logger.critical("설정파일을 읽어 오지 못함 : {e}", exc_info= True)

    try:
        db.connect(db_config)
        logger.info("DB CONNECT")
    except Exception as e :
        logger.error(f"DB 연결 중 오류 발생 : {e}", exc_info= True)
        logger.critical("DB연결 실패로 프로그램 종료")
        exit()
    
    
    for news in news_list:
        idx = news["idx"]
        title = news["title"]
        link = news["link"]
        from_date = news["from_date"]
        category_name = news["category"]
    
        db.cursor_open()
        
        is_exist = db.find_news_config(idx)
        if is_exist:
            logger.info(f"중복 기사 : {title}")
            continue
        else:
            news_id = db.insert_news(idx, title, link, from_date)
            logger.info(f"기사 저장 완료: {title}")
        
        db.insert_news_category(news_id,category_name)
        logger.info("news_category 추가 완료")
        db.cursor_close()
                
    db.db_close()
    logger.info("DB연결 종료")

    
if __name__ == "__main__" :
    main()

