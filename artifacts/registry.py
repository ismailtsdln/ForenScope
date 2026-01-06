from typing import List
from datetime import datetime
import os
import logging
from Registry import Registry

from core.artifact import Artifact, Evidence

class RegistryRunKeys(Artifact):
    def __init__(self, hive_path: str):
        self.hive_path = hive_path
        self._name = "Windows Registry Run Keys"
        self._description = "Extracts auto-start entries from Run keys in NTUSER.DAT or SOFTWARE hives."

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    def extract(self) -> List[Evidence]:
        evidence_list = []
        if not os.path.exists(self.hive_path):
            logging.warning(f"Registry hive not found: {self.hive_path}")
            return []

        try:
            reg = Registry.Registry(self.hive_path)
        except Exception as e:
            logging.error(f"Failed to parse registry hive {self.hive_path}: {e}")
            return []

        # Define common run key paths
        run_paths = [
            "Microsoft\\Windows\\CurrentVersion\\Run",
            "Microsoft\\Windows\\CurrentVersion\\RunOnce",
            "Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Run",
            "Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\RunOnce"
        ]

        # Determine root key based on Hive type (rough check)
        # Software hive usually doesn't have a root key wrapper like NTUSER sometimes does, 
        # but typically we start from root.
        
        for key_path in run_paths:
            try:
                # Attempt to open key. 
                # Note: Registry module usually requires traversal from root or open() method
                try:
                     key = reg.open(key_path)
                except Registry.RegistryKeyNotFoundException:
                     continue

                for value in key.values():
                    evidence = Evidence(
                        source_path=self.hive_path,
                        artifact_type="Registry Run Key",
                        data={
                            "key_path": key_path,
                            "value_name": value.name(),
                            "value_data": str(value.value()),
                            "value_type": value.value_type_str()
                        },
                        timestamp=key.timestamp() # Key timestamp is the last write time
                    )
                    evidence_list.append(evidence)

            except Exception as e:
                logging.debug(f"Error checking key {key_path} in {self.hive_path}: {e}")

        return evidence_list
