import json
import os, time
from logger import log

DB_STATUS = {}

class database:
    def __init__(self, db_name: str = ""):
        self.db_name = db_name
        self.data = {}
        if not os.path.exists("db"):
            os.mkdir("db")
    
    def open(self, new_db_name: str = ""):
        global DB_STATUS
        if new_db_name != "":
            self.db_name = new_db_name
        if not self.db_name:
            raise Exception("db_name is empty")
        if self.db_name not in DB_STATUS:
                DB_STATUS[self.db_name] = False
        while True:
            if DB_STATUS[self.db_name] == False:
                DB_STATUS[self.db_name] = True
                try:
                    with open(f"db/{self.db_name}.json", "r", encoding="utf-8") as f:
                        data = json.load(f)
                        self.data = data
                        DB_STATUS[self.db_name] = True
                        return data
                except:
                    with open(f"db/{self.db_name}.json", "w", encoding="utf-8") as f:
                        f.write("{}")
                        self.data = {}
                        return {}
            else:
                log("db is locked", "WARNING")
                time.sleep(0.1)

    def read(self, new_db_name: str = ""):
        if new_db_name != "":
            self.db_name = new_db_name
        if not self.db_name:
            raise Exception("db_name is empty")
        with open(f"db/{self.db_name}.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            return data

    def exists(self):
        try:
            with open(f"db/{self.db_name}.json", "r", encoding="utf-8") as f:
                return True
        except:
            return False

    def save(self):
        global DB_STATUS
        with open(f"db/{self.db_name}.json", "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)
        DB_STATUS[self.db_name] = False

def exists(db_name: str):
    try:
        with open(f"db/{db_name}.json", "r", encoding="utf-8") as f:
            return True
    except:
        return False