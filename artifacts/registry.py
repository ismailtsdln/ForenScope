from typing import List
from datetime import datetime
import os
import logging
import Registry
from core.artifact import Artifact, Evidence

class RegistryRunKeys(Artifact):
    def __init__(self, hive_path: str):
        self.hive_path = hive_path
        self._name = "Windows Registry Analysis"
        self._description = "Extracts auto-start entries, mount points, and UserAssist from Registry hives."

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

        # Define targets: (Key Path, Artifact Type Description)
        targets = [
            # Run Keys
            ("Microsoft\\Windows\\CurrentVersion\\Run", "Registry Run Key"),
            ("Microsoft\\Windows\\CurrentVersion\\RunOnce", "Registry Run Key"),
            ("Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Run", "Registry Run Key"),
            
            # MountPoints2 (Network shares / devices)
            ("Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\MountPoints2", "Registry Mount Point"),
            
            # UserAssist (Executed programs)
            ("Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\UserAssist", "Registry UserAssist"),
        ]

        for key_path, artifact_type in targets:
            try:
                key = reg.open(key_path)
                
                # For UserAssist, we need to go deeper into subkeys (GUIDs)
                if "UserAssist" in artifact_type:
                    for subkey in key.subkeys():
                        try:
                            count_key = subkey.open("Count")
                            for value in count_key.values():
                                # UserAssist values are ROT13 encoded
                                evidence_list.append(self._create_evidence(key_path + "\\" + subkey.name(), value, artifact_type, count_key))
                        except Exception:
                            continue
                else:
                    for value in key.values():
                        evidence_list.append(self._create_evidence(key_path, value, artifact_type, key))

            except Registry.RegistryKeyNotFoundException:
                continue
            except Exception as e:
                logging.debug(f"Error checking key {key_path} in {self.hive_path}: {e}")

        return evidence_list

    def _rot13_decode(self, s: str) -> str:
        """Decodes ROT13 encoded strings (used in UserAssist)."""
        result = ""
        for char in s:
            if 'a' <= char <= 'z':
                result += chr((ord(char) - ord('a') + 13) % 26 + ord('a'))
            elif 'A' <= char <= 'Z':
                result += chr((ord(char) - ord('A') + 13) % 26 + ord('A'))
            else:
                result += char
        return result

    def _create_evidence(self, key_path, value, artifact_type, key) -> Evidence:
        value_name = value.name()
        if "UserAssist" in artifact_type:
            value_name = self._rot13_decode(value_name)

        return Evidence(
            source_path=self.hive_path,
            artifact_type=artifact_type,
            data={
                "key_path": key_path,
                "value_name": value_name,
                "value_data": str(value.value()),
                "value_type": value.value_type_str()
            },
            timestamp=key.timestamp()
        )
