import zipfile
from datetime import datetime
import csv

command_history = []
# Простая виртуальная файловая система
class VirtualFileSystem:
    def __init__(self, zip_file_path):
        self.zip_file_path = zip_file_path
        self.current_dir = "/"
        self.fs = {}
        self.files_content = {}
        self.load_zip()

    def load_zip(self):
        """Загружает файловую систему из zip-архива."""
        with zipfile.ZipFile(self.zip_file_path, 'r') as z:
            for file in z.namelist():
                parts = file.split('/')
                d = self.fs
                for part in parts[:-1]:
                    d = d.setdefault(part, {})
                if parts[-1]:
                    d[parts[-1]] = None
                    self.files_content[file] = z.read(file).decode('utf-8')

    def list_dir(self):
        """Возвращает отсортированное содержимое текущего каталога с папками первыми."""
        dirs = self.fs
        for part in self.current_dir.strip("/").split("/"):
            if part:
                dirs = dirs[part]
        # Разделяем на папки и файлы
        folders = sorted([name for name in dirs.keys() if isinstance(dirs[name], dict)])
        files = sorted([name for name in dirs.keys() if dirs[name] is None])
        return folders + files

    def change_dir(self, path):
        """Сменить каталог."""
        if path == "..":
            self.current_dir = "/".join(self.current_dir.split("/")[:-1])
            if not self.current_dir:
                self.current_dir = "/"
        elif path in self.list_dir():
            self.current_dir += f"/{path}".strip("/")
        else:
            raise FileNotFoundError(f"No such directory: {path}")

    def current_path(self):
        """Возвращает текущий путь."""
        return self.current_dir

    def read_file(self, file_path):
        """Читает содержимое файла."""
        full_path = f"{self.current_dir.strip('/')}/{file_path}".strip("/")
        if full_path in self.files_content:
            return self.files_content[full_path].splitlines()
        raise FileNotFoundError(f"No such file: {file_path}")


# Командная оболочка
class VirtualShell:
    def __init__(self, vfs):
        self.vfs = vfs

    def start(self):
        while True:
            command = input(f"{self.vfs.current_path()} # ")
            if command.strip() == "exit":
                break
            self.process_command(command)

    def process_command(self, command):
        parts = command.split()
        command_history.append(command)
        if not parts:
            return
        cmd = parts[0]

        try:
            if cmd == "ls":
                print("\n".join(self.vfs.list_dir()))
            elif cmd == "pwd":
                print(self.vfs.current_path())
            elif cmd == "cd":
                if len(parts) > 1:
                    self.vfs.change_dir(parts[1])
                else:
                    print("Usage: cd <directory>")
            elif cmd == "history":
                self.handle_history(parts)
            elif cmd == "date":
                self.handle_date()
            else:
                print(f"Command not found: {cmd}")
        except FileNotFoundError as e:
            print(str(e))
        except Exception as e:
            print(f"Error: {e}")

    def handle_history(self, parts):
        """Обрабатывает команду history."""
        for i in range(0, len(command_history)):
            print(i + 1, " ", command_history[i])

    def handle_date(self):
        """Обрабатывает команду date."""
        now = datetime.now()
        print(now.strftime("%a %b %d %H:%M:%S %Y"))


def load_config(config_file):
    """Загружает конфигурацию из CSV файла."""
    with open(config_file, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        config = next(reader)
    return config


def startConsole():
    config = load_config("config.csv")
    username = config["username"]
    computer_name = config["computer_name"]
    zip_file_path = config["zip_file_path"]

    vfs = VirtualFileSystem(zip_file_path)

    class VirtualShellWithPrompt(VirtualShell):
        def start(self):
            while True:
                command = input(f"{username}@{computer_name}:{self.vfs.current_path()} # ")
                if command.strip() == "exit":
                    break
                self.process_command(command)

    shell = VirtualShellWithPrompt(vfs)
    shell.start()
