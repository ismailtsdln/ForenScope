from typing import List
from datetime import datetime
import os
import logging
import mmap
import contextlib
import xml.etree.ElementTree as ET

from Evtx.Evtx import Evtx
from Evtx.Views import evtx_file_xml_view

from core.artifact import Artifact, Evidence

class EvtxParser(Artifact):
    def __init__(self, evtx_path: str, target_event_ids: List[int] = None):
        self.evtx_path = evtx_path
        self._name = "Windows Event Logs"
        self._description = "Parses Windows EVTX logs for specific Event IDs."
        self.target_event_ids = target_event_ids or [4624, 4625] # Logon Success/Failure

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    def extract(self) -> List[Evidence]:
        evidence_list = []
        if not os.path.exists(self.evtx_path):
            logging.warning(f"EVTX file not found: {self.evtx_path}")
            return []

        try:
            with Evtx(self.evtx_path) as evtx:
                for record in evtx.records():
                    try:
                        xml_content = record.xml()
                        root = ET.fromstring(xml_content)
                        
                        # Namespaces in EVTX XML are annoying, usually:
                        # {http://schemas.microsoft.com/win/2004/08/events/event}
                        # We will strip namespaces or handle them
                        
                        ns = {'ns': 'http://schemas.microsoft.com/win/2004/08/events/event'}
                        
                        system = root.find('ns:System', ns)
                        if system is None:
                            continue
                            
                        event_id_elem = system.find('ns:EventID', ns)
                        if event_id_elem is None:
                            continue
                            
                        event_id = int(event_id_elem.text)
                        
                        if event_id in self.target_event_ids:
                            time_created = system.find('ns:TimeCreated', ns)
                            timestamp = datetime.now()
                            if time_created is not None:
                                ts_str = time_created.get('SystemTime')
                                # 2023-10-25T12:00:00.000000Z
                                try:
                                    # Python 3.10 handles ISO fromisoformat fine usually, but Z might need handling
                                    timestamp = datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
                                except:
                                    pass

                            evidence = Evidence(
                                source_path=self.evtx_path,
                                artifact_type=f"Event Log {event_id}",
                                data={
                                    "event_id": event_id,
                                    "raw_xml": xml_content[:2000] # Truncate for sanity
                                },
                                timestamp=timestamp
                            )
                            evidence_list.append(evidence)

                    except Exception as e:
                        logging.debug(f"Error parsing record: {e}")
                        continue
                        
        except Exception as e:
            logging.error(f"Failed to open EVTX file {self.evtx_path}: {e}")

        return evidence_list
