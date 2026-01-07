from typing import List
from datetime import datetime, timedelta
import sqlite3
import os
import logging
import tempfile
import shutil

from core.artifact import Artifact, Evidence

class ChromeHistoryParser(Artifact):
    def __init__(self, history_path: str):
        self.history_path = history_path
        self._name = "Chrome/Edge History"
        self._description = "Parses web history from Chrome/Edge SQLite databases."

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    def _webkit_timestamp_to_datetime(self, webkit_ts: int) -> datetime:
        """Converts WebKit timestamp (microseconds since 1601-01-01) to datetime."""
        if not webkit_ts:
            return datetime.min
        
        # WebKit epoch start
        epoch_start = datetime(1601, 1, 1)
        delta = timedelta(microseconds=webkit_ts)
        return epoch_start + delta

    def extract(self) -> List[Evidence]:
        evidence_list = []
        if not os.path.exists(self.history_path):
            logging.warning(f"Browser history file not found: {self.history_path}")
            return []

        # Create a temp copy to avoid lock issues
        temp_dir = tempfile.mkdtemp()
        temp_db = os.path.join(temp_dir, "History_tmp")
        try:
            shutil.copy2(self.history_path, temp_db)
            
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            
            # Query urls table
            query = """
            SELECT url, title, visit_count, last_visit_time
            FROM urls
            WHERE last_visit_time > 0
            """
            
            cursor.execute(query)
            for row in cursor.fetchall():
                url, title, visit_count, last_visit_time = row
                
                dt = self._webkit_timestamp_to_datetime(last_visit_time)
                
                evidence = Evidence(
                    source_path=self.history_path,
                    artifact_type="Browser History",
                    data={
                        "url": url,
                        "title": title,
                        "visit_count": visit_count
                    },
                    timestamp=dt
                )
                evidence_list.append(evidence)
                
            conn.close()
            
        except Exception as e:
            logging.error(f"Failed to parse browser history {self.history_path}: {e}")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
        return evidence_list


class ChromeCookiesParser(Artifact):
    def __init__(self, cookies_path: str):
        self.cookies_path = cookies_path
        self._name = "Chrome/Edge Cookies"
        self._description = "Parses cookies from Chrome/Edge SQLite databases."

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    def _webkit_timestamp_to_datetime(self, webkit_ts: int) -> datetime:
        if not webkit_ts:
            return datetime.min
        epoch_start = datetime(1601, 1, 1)
        delta = timedelta(microseconds=webkit_ts)
        return epoch_start + delta

    def extract(self) -> List[Evidence]:
        evidence_list = []
        if not os.path.exists(self.cookies_path):
            return []
        temp_dir = tempfile.mkdtemp()
        temp_db = os.path.join(temp_dir, "Cookies_tmp")
        try:
            shutil.copy2(self.cookies_path, temp_db)
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            # Chromium stores both 'value' (plain) and 'encrypted_value'
            query = "SELECT host_key, name, value, encrypted_value, path, creation_utc FROM cookies"
            cursor.execute(query)
            for row in cursor.fetchall():
                host, name, value, enc_value, path, creation = row
                
                # If value is empty but enc_value exists, mark as encrypted
                display_value = value
                if not value and enc_value:
                    display_value = "[Encrypted]"
                
                dt = self._webkit_timestamp_to_datetime(creation)
                evidence = Evidence(
                    source_path=self.cookies_path,
                    artifact_type="Browser Cookie",
                    data={"host": host, "name": name, "path": path, "value": display_value},
                    timestamp=dt
                )
                evidence_list.append(evidence)
            conn.close()
        except Exception:
            pass
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
        return evidence_list

class FirefoxHistoryParser(Artifact):
    def __init__(self, history_path: str):
        self.history_path = history_path
        self._name = "Firefox History"
        self._description = "Parses web history from Firefox places.sqlite database."

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    def extract(self) -> List[Evidence]:
        evidence_list = []
        if not os.path.exists(self.history_path):
            logging.warning(f"Browser history file not found: {self.history_path}")
            return []

        # Create a temp copy to avoid lock issues
        temp_dir = tempfile.mkdtemp()
        temp_db = os.path.join(temp_dir, "places_tmp.sqlite")
        try:
            shutil.copy2(self.history_path, temp_db)
            
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            
            # Query moz_places table
            # Firefox stores history in moz_places and moz_historyvisits
            # For simplicity, we query moz_places which has url, title, visit_count, last_visit_date
            query = """
            SELECT url, title, visit_count, last_visit_date
            FROM moz_places
            WHERE last_visit_date > 0
            """
            
            try:
                cursor.execute(query)
                for row in cursor.fetchall():
                    url, title, visit_count, last_visit_date = row
                    
                    # Firefox uses microseconds since EPOCH (Unix)
                    if last_visit_date:
                        dt = datetime.fromtimestamp(last_visit_date / 1000000)
                    else:
                        dt = datetime.min

                    evidence = Evidence(
                        source_path=self.history_path,
                        artifact_type="Firefox History",
                        data={
                            "url": url,
                            "title": title,
                            "visit_count": visit_count
                        },
                        timestamp=dt
                    )
                    evidence_list.append(evidence)
            except sqlite3.OperationalError:
                # Might be locked or corrupted
                logging.error(f"SQLite error parsing {self.history_path}")

            conn.close()
            
        except Exception as e:
            logging.error(f"Failed to parse firefox history {self.history_path}: {e}")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
            
        return evidence_list


class FirefoxCookiesParser(Artifact):
    def __init__(self, cookies_path: str):
        self.cookies_path = cookies_path
        self._name = "Firefox Cookies"
        self._description = "Parses cookies from Firefox cookies.sqlite database."

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    def extract(self) -> List[Evidence]:
        evidence_list = []
        if not os.path.exists(self.cookies_path):
            return []

        temp_dir = tempfile.mkdtemp()
        temp_db = os.path.join(temp_dir, "cookies_tmp.sqlite")
        try:
            shutil.copy2(self.cookies_path, temp_db)
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            
            query = "SELECT baseDomain, name, value, path, creationTime FROM moz_cookies"
            cursor.execute(query)
            for row in cursor.fetchall():
                domain, name, value, path, creation = row
                # Firefox creationTime is microseconds since epoch
                dt = datetime.fromtimestamp(creation / 1000000)
                
                evidence = Evidence(
                    source_path=self.cookies_path,
                    artifact_type="Firefox Cookie",
                    data={"domain": domain, "name": name, "path": path},
                    timestamp=dt
                )
                evidence_list.append(evidence)
            conn.close()
        except Exception:
            pass
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
        return evidence_list
