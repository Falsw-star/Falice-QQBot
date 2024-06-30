import subprocess, os, time
import threading
import mcrcon
from logger import log
from typing import Union

# Errors
server_not_found = "Server Not Found."
rcon_port_not_set = "rcon.port is not set."
rcon_port_is_not_number = "rcon.port is not a number."
rcon_password_not_set = "rcon.password is not set."
rcon_not_enabled = "rcon.enabled is not true."
server_is_starting = "Server [{}] is Starting." # Server_Name
server_crashed = "Server [{}] Stopped with code {}. Please run '{}' for fixing it." # Server_Name, Exit Code(process.poll()), Server_Run_Command
server_is_stopping = "Stopping Server [{}]." # Server_Name"
server_stopped = "Server [{}] Stopped with code {}." # Server_Name, Exit Code(process.poll())
server_started = "Server [{}] Started on port {}." # Server_Name, Server_Port
server_is_not_running = "Server [{}] is Offline." # Server_Name
server_is_calling = "Calling Server [{}]: {}" # Server_Name, Command

class Server():

    def __init__(self, Server_Name: str, Jar_File_Name: str, server_done_string: str, xmx: str = "2048M", xms: str = "1024M", use_screen: bool = False):

        if not os.path.exists("plugins/mcserver/servers/{}/{}".format(Server_Name, Jar_File_Name)):
            raise FileNotFoundError(server_not_found)
        
        self.use_screen = use_screen

        self.Server_Name = Server_Name
        self.Jar_File_Name = Jar_File_Name
        self.server_done_string = server_done_string
        self.xmx = xmx
        self.xms = xms
        self.rcon_port: int = 25575
        self.rcon_password = None
        self.rcon_enabled = None
        self.motd = None
        self.view_distance: int = 10
        self.gamemode = None
        self.difficulty = None
        self.level_name = None
        self.server_port: int = 25565
        self.online_mode = None
        self.max_players: int = 20
        self.rcon: mcrcon.MCRcon
        self.process: subprocess.Popen

        self.status = -1 # -1 = Offline, 0 = Starting, 1 = Online

        def _readline(line: str):
            return line.split("=")[1].strip()

        # Read Server Properties
        with open("plugins/mcserver/servers/{}/server.properties".format(self.Server_Name), "r") as f:
            for line in f:

                if line.startswith("rcon.port"): # rcon.port
                    if not _readline(line):
                        raise ValueError(rcon_port_not_set)
                    try:
                        self.rcon_port = int(_readline(line))
                    except Exception:
                        raise Exception(rcon_port_is_not_number)
                
                if line.startswith("rcon.password"): # rcon.password
                    self.rcon_password = _readline(line)
                    if not self.rcon_password:
                        raise ValueError(rcon_password_not_set)
                
                if line.startswith("enable-rcon"):
                    self.rcon_enabled = _readline(line)
                    if self.rcon_enabled != "true":
                        raise ValueError(rcon_not_enabled)

                if line.startswith("motd"):
                    self.motd = _readline(line)
                if line.startswith("view-distance"):
                    self.view_distance = int(_readline(line))
                if line.startswith("max-players"):
                    self.max_players = int(_readline(line))
                if line.startswith("online-mode"):
                    self.online_mode = _readline(line)
                    if self.online_mode == "true":
                        self.online_mode = True
                    else:
                        self.online_mode = False
                if line.startswith("gamemode"):
                    self.gamemode = _readline(line)
                if line.startswith("level-seed"):
                    self.level_seed = _readline(line)
                if line.startswith("level-name"):
                    self.level_name = _readline(line)
                if line.startswith("server-port"):
                    self.server_port = int(_readline(line))
                if line.startswith("server-ip"):
                    self.server_ip = _readline(line)
                if line.startswith("difficulty"):
                    self.difficulty = _readline(line)
                self.rcon = mcrcon.MCRcon("127.0.0.1", self.rcon_password, self.rcon_port)


    def start(self):

        if self.use_screen:
            start_screen = ["screen", "-S", self.Server_Name]
            self.process = subprocess.Popen(start_screen, cwd=f"plugins/mcserver/servers/{self.Server_Name}", stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
            log(server_is_starting.format(self.Server_Name), "RUNTIME")
            if self.process.stdin is not None:
                self.process.stdin.write(f"java -Xmx{self.xmx} -Xms{self.xms} -jar {self.Jar_File_Name} nogui\n".encode())
                self.process.stdin.flush()
                self.status = 0

                while True:
                    if self.process.poll() is not None:
                        self.status = -1
                        log(server_crashed.format(self.Server_Name, self.process.poll(), "screen -r {}".format(self.Server_Name)), "ERROR")
                        return False
                    if self.process.stdout is not None:
                        if self.server_done_string in self.process.stdout.readline():
                            time.sleep(5)
                            self.status = 1
                            log(server_started.format(self.Server_Name, self.server_port), "SUCCESS")

                            def tracker(server: Server):
                                while True:
                                    if server.process.poll() is not None:
                                        server.status = -1
                                        log(server_stopped.format(server.Server_Name, str(server.process.poll())), "WARNING")
                                        return
                            threading.Thread(target=tracker, args=(self,)).start()
                            return True

        else:
            cmd = ["java", f"-Xmx{self.xmx}", f"-Xms{self.xms}", "-jar", self.Jar_File_Name, "nogui"]
            log(server_is_starting.format(self.Server_Name), "RUNTIME")
            self.process = subprocess.Popen(cmd, cwd=f"plugins/mcserver/servers/{self.Server_Name}", stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, universal_newlines=True)
            self.status = 0

            while True:
                if self.process.poll() is not None:
                    self.status = -1
                    log(server_crashed.format(self.Server_Name, str(self.process.poll()), ' '.join(e for e in cmd)), "WARNING")
                    return False
                if self.process.stdout is not None:
                    if self.server_done_string in self.process.stdout.readline():
                        time.sleep(5)
                        self.status = 1
                        log(server_started.format(self.Server_Name, self.server_port), "SUCCESS")

                        def tracker(server: Server):
                            while True:
                                if server.process.poll() is not None:
                                    server.status = -1
                                    log(server_stopped.format(server.Server_Name, str(server.process.poll())), "WARNING")
                                    return
                        threading.Thread(target=tracker, args=(self,)).start()
                        return True
        
    def call(self, command: Union[str, list]):
        if type(command) == str:
            command = [command]
        if self.status != 1:
            return server_is_not_running.format(self.Server_Name)
        try:
            self.rcon.connect()
            rsp_list = []
            for cmd in command:
                log(server_is_calling.format(self.Server_Name, cmd), "RUNTIME")
                rsp = self.rcon.command(cmd)
                if rsp == "Stopping the server":
                    log(server_is_stopping.format(self.Server_Name))
                rsp_list.append(rsp)
            self.rcon.disconnect()
        except Exception as e:
            return [e]
        return rsp_list
    
    def stop(self):
        if self.status != 1:
            return server_is_not_running.format(self.Server_Name)
        try:
            self.rcon.connect()
            self.rcon.command("stop")
            self.rcon.disconnect()
            while self.status == 1:
                time.sleep(1)
        except:
            return False
        return True