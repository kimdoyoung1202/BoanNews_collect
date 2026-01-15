import os
import logging
from logging.handlers import TimedRotatingFileHandler

def setup_logging(log_path: str=os.path.dirname(__file__)+"/logs/app.log") -> None :
    """로깅 설정
        매개 변수로 로그파일 경로가 주어지면 주어진 경로로,
        주어지지 않으면 logs/app.log 에 로깅 하도록 설정.
        - 매일 자정 새로운 로그파일 생성 (전날 로그는 app.log.yyyymmdd 파일로 저장 됨)
        - 14일 경과한 파일은 자동 삭제

    Args:
        log_path (str, optional): _description_. Defaults to "logs/app.log".
    """

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    
    if root.handlers :
        return
    
    handler = TimedRotatingFileHandler(
        log_path,
        when = "midnight",
        interval = 1,
        backupCount = 14,
        encoding = "utf-8",
        utc = False
    )
    
    fmt = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s : %(lineno)d - %(message)s"
    )
    
    handler.setFormatter(fmt)
    root.addHandler(handler)