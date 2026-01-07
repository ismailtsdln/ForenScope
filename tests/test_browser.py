import os
import sqlite3
import tempfile
import shutil
from artifacts.browser import ChromeHistoryParser, FirefoxHistoryParser, ChromeCookiesParser

def test_chrome_history_extraction():
    # Create a dummy Chrome history database
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "History")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE urls (url TEXT, title TEXT, visit_count INTEGER, last_visit_time INTEGER)")
    # Webkit timestamp: 1601-01-01 + microseconds
    # 13253952000000000 is approx 2021-01-01
    cursor.execute("INSERT INTO urls VALUES ('http://test.com', 'Test Title', 5, 13253952000000000)")
    conn.commit()
    conn.close()

    parser = ChromeHistoryParser(db_path)
    results = parser.extract()

    assert len(results) == 1
    assert results[0].data["url"] == "http://test.com"
    assert results[0].data["visit_count"] == 5
    
    shutil.rmtree(temp_dir)

def test_chrome_cookies_extraction():
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "Cookies")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE cookies (host_key TEXT, name TEXT, value TEXT, encrypted_value BLOB, path TEXT, creation_utc INTEGER)")
    cursor.execute("INSERT INTO cookies VALUES ('.google.com', 'SID', 'abc123', NULL, '/', 13253952000000000)")
    conn.commit()
    conn.close()

    parser = ChromeCookiesParser(db_path)
    results = parser.extract()

    assert len(results) == 1
    assert results[0].data["host"] == ".google.com"
    
    shutil.rmtree(temp_dir)
