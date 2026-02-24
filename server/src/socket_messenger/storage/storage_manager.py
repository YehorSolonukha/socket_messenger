from pathlib import Path

class StorageManager:
    def __init__(self):
        PROJECT_ROOT = Path(__file__).resolve().parents[4]

        DB_DIR = PROJECT_ROOT / "database"
        DB_DIR.mkdir(exist_ok=True)

        self.STORAGE_FILE = DB_DIR / "storage.txt"
        self.STORAGE_FILE.touch(exist_ok=True)


# AUTHENTICATION
    def create_client(self, username: str, password: str) -> bool:
        with self.STORAGE_FILE.open("a") as f:
            f.write(f"{username} {password}\n")
            return True
        return False

    def client_exists(self, target_username: str) -> bool:
        with self.STORAGE_FILE.open("r") as f:
            for line in f:
                parts = line.strip().split()
                if not parts:
                    continue
                username = parts[0]
                if username == target_username:
                    return True
        return False


    def verify_password(self, target_username: str, target_password: str) -> bool:
        with self.STORAGE_FILE.open("r") as f:
            for line in f:
                parts = line.strip().split()
                if not parts:
                    continue
                username, password = parts
                if username == target_username and password == target_password:
                    return True
        return False
