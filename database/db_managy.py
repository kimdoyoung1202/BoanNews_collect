import pymysql
import configparser
import logging_config as log
import logging


"""
    logger 생성
        -log.setup_logging() 은 공통된 규칙 설정
        -logger = logging.getLogger(__name__) (name)으로 파일별 파일이름으로 작성되는 로거
        - 어느 파일에서 로그가 났는지 확인이 쉽다
"""
log.setup_logging()
logger = logging.getLogger(__name__)

def connect(db_config):
    """
    DB 설정 정보를 이용해 MYSQL 데이터베이스에 연결하는 함수

    Args:
        db_config (dict): DB 접속 정보가 담긴 딕셔너리
        - host : DB 주소
        - port : 포트 번호
        - db : 데이터베이스 이름
        - user : 사용자 이름
        - password : 비밀번호
        
    Raises:
        Exception: DB 연결 실패시 로그를 남김
    """
    global mysql, cursor
    try:
        mysql = pymysql.connect(
            host=db_config["host"]
            , port=int(db_config["port"])
            , db=db_config["db"]
            , user=db_config["user"]
            , password=db_config["password"]
            , charset="utf8"
        )
    except Exception as e:
        logger.error(f"DB 연결 실패: {e}")


def db_close() :
    """
    데이터베이스 연결을 종료 시키는 함수
    
    Raises:
        Exception: DB 연결 종료 중 오류 발생 시 로그를 출력 후 프로그램 종료
    """
    try:
        mysql.close()
        
    except Exception as e:
        logger.error(f"db_close error : {e}") 
        exit()
        
def cursor_open():
    """
    Global mysql 연결 객체를 이용해 cursor를 사용하기 위한 함수
    
    Raises:
        Exception: cursor 생성 실패 시 DB연결 종료 후 프로그램 종료
    """
    global cursor
    try:
        cursor = mysql.cursor()
    except Exception as e:
        logger.error(f"cursor not open : {e}")
        db_close()
        exit()
        
def cursor_close():
    """
    현재 사용 중인 cursor를 닫는 함수

    Raises:
        Exception: 커서 종료 실패 시 프로그램 종료
    """

    try:
        cursor.close()
    except Exception as e:
        logger.error(f"cursor not close : {e}")
        exit()
        


def insert_news(idx ,title, link, from_date):
    """
    news_config 테이블에 새로운 기사를 추가하는 함수

    Args:
        idx : 기사 고유 식별코드
        title : 기사 제목
        link : 기사 링크
        from_date : 기사 날짜

    Returns:
        int: 삽입된 행의 id (auto increment 값)

    Raises:
        Exception: 삽입 실패 시 롤백 후 로그 출력
    """
    try:
        query = " insert into news_config (idx, title, link, from_date) values (%s, %s, %s, %s)"
        cursor.execute(query, (idx, title, link, from_date))
        mysql.commit()
        return cursor.lastrowid
        
    except Exception as e:
        logger.error(f"not insert rollback : {e}")
        mysql.rollback()


def find_news_config(idx):
    """
    idx를 기준으로 news_config 테이블에서 중복 기사를 조회하는 함수

    Args:
        idx : 기사 고유 식별코드

    Returns:
        true(존재) : id
        None(없음) : None

    Raises:
        Exception: 조회 실패 시 로그 출력
    """
    try:
        cursor.execute("select id from news_config where idx=%s",(idx,))
        row = cursor.fetchone()
        if row :
            return row
        else:
            return None
    except Exception as e:
        logger.error(f"idx로 찾기 실패 : {e}")




def insert_news_category(news_id, category_name):
    """
    news_config(id)와 category(name)을 연결지어 news_category 테이블에 저장하는 함수

    Args:
        news_id : news_config 테이블의 기사 id
        category_name : category 테이블의 카테고리 이름

    Raises:
        Exception: 삽입 실패 시 롤백 후 로그 출력
    """
    try:
        sql = "insert into news_category (news_id, category_id) select %s,id from category where name = %s"
        cursor.execute(sql, (news_id,category_name))
        mysql.commit()

    except Exception as e:
        mysql.rollback()
        logger.error(f"news_category 실패 : {e}")




