import json
from logger import cfp

class database:
    def __init__(self, db_name: str = ""):
        self.db_name = db_name
        self.data = {}
    
    def open(self, new_db_name: str = ""):
        if new_db_name != "":
            self.db_name = new_db_name
        if not self.db_name:
            raise Exception("db_name is empty")
        try:
            with open(f"{cfp}/db/{self.db_name}.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                self.data = data
                return data
        except:
            with open(f"{cfp}/db/{self.db_name}.json", "w", encoding="utf-8") as f:
                f.write("{}")
                self.data = {}
                return {}
    
    def exists(self):
        try:
            with open(f"db/{self.db_name}.json", "r", encoding="utf-8") as f:
                return True
        except:
            return False

    def save(self):
        with open(f"db/{self.db_name}.json", "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)

def exists(db_name: str):
    try:
        with open(f"db/{db_name}.json", "r", encoding="utf-8") as f:
            return True
    except:
        return False