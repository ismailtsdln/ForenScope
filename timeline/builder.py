import csv
import json
from datetime import datetime
import os

class TimelineBuilder:
    def __init__(self, output_dir: str = "timeline_output"):
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    def build_csv(self, stream_generator, filename_prefix: str) -> str:
        filename = f"{filename_prefix}.csv"
        path = os.path.join(self.output_dir, filename)
        
        with open(path, "w", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Timestamp", "Type", "Path", "Size", "Mode"])
            
            for entry in stream_generator:
                ts = datetime.fromtimestamp(entry.modified_time).isoformat()
                type_ = "DIR" if entry.is_dir else "FILE"
                writer.writerow([ts, type_, entry.path, entry.size, entry.mode])
                
        return path

    def build_json(self, stream_generator, filename_prefix: str) -> str:
        filename = f"{filename_prefix}.json"
        path = os.path.join(self.output_dir, filename)
        
        events = []
        for entry in stream_generator:
             events.append({
                 "timestamp": datetime.fromtimestamp(entry.modified_time).isoformat(),
                 "type": "DIR" if entry.is_dir else "FILE",
                 "path": entry.path,
                 "size": entry.size,
                 "mode": entry.mode
             })
             
        with open(path, "w") as f:
            json.dump(events, f, indent=4)
            
        return path

    def build_timesketch_jsonl(self, stream_generator, filename_prefix: str) -> str:
        """
        Generates a JSONL file formatted for Timesketch import.
        Required fields: message, timestamp, datetime, timestamp_desc
        """
        filename = f"{filename_prefix}_timesketch.jsonl"
        path = os.path.join(self.output_dir, filename)
        
        with open(path, "w") as f:
            for entry in stream_generator:
                dt = datetime.fromtimestamp(entry.modified_time)
                type_ = "DIR" if entry.is_dir else "FILE"
                
                record = {
                    "message": f"{type_}: {entry.path} (Size: {entry.size})",
                    "timestamp": entry.modified_time, # Epoch integer
                    "datetime": dt.isoformat(),
                    "timestamp_desc": "File Modified",
                    "file_path": entry.path,
                    "file_size": entry.size,
                    "file_mode": entry.mode
                }
                
                f.write(json.dumps(record) + "\n")
                
        return path
