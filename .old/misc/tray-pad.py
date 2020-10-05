import psutil
import subprocess

def changePadd(sub):
    sost = str(sub)
    lines = []
    with open(".config/polybar/pad.ini","w") as f:
        f.seek(0)
        f.truncate()
        f.write("[pad]\n padright = " + sost)

 
def isRunning(processName):
    for proc in psutil.process_iter():
        try:
            if processName.lower() in proc.name().lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False;


if __name__ == "__main__":
    procs = {
        "pia":"pia-client",
        "wapp":"whats-app",
    }
    pad = 9
      
    if(isRunning(procs["pia"])):
        pad += 3
        print("PIA is running")
    if(isRunning(procs["wapp"])):
        pad += 3
        print("Whatsapp is running")
    
    changePadd(pad)
    #subprocess.Popen("$HOME/.config/polybar/launch.sh", shell=True)
