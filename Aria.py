# New aria command proccessor
import AriaDefinitions
import AriaModules

datetime=AriaModules.datetime
requests=AriaModules.requests
threading=AriaModules.threading
time=AriaModules.time
sr=AriaModules.sr
pyttsx3=AriaModules.pyttsx3
webbrowser=AriaModules.webbrowser
win32api=AriaModules.win32api
Key=AriaModules.Key
Controller=AriaModules.Controller
os=AriaModules.os
ctypes=AriaModules.ctypes
datetime=AriaModules.datetime
socket=AriaModules.socket
psutil=AriaModules.psutil
keyboard=AriaModules.keyboard
pyjokes=AriaModules.pyjokes
wikipedia=AriaModules.wikipedia
wolframalpha=AriaModules.wolframalpha
json=AriaModules.json
tk=AriaModules.tk
ImageTk=AriaModules.ImageTk
Image=AriaModules.Image
win32con=AriaModules.win32con

commandWords=AriaDefinitions.commandWords
queryWords=AriaDefinitions.queryWords
explainWords=AriaDefinitions.explainWords
apps=AriaDefinitions.appList

# Tello Controller
class TelloStats:
    def __init__(self, command, id):
        self.command = command
        self.response = None
        self.id = id

        self.start_time = datetime.now()
        self.end_time = None
        self.duration = None

    def add_response(self, response):
        self.response = response
        self.end_time = datetime.now()
        self.duration = self.get_duration()

    def get_duration(self):
        diff = self.end_time - self.start_time
        return diff.total_seconds()

    def print_stats(self):
        print('\nid: %s' % self.id)
        print('command: %s' % self.command)
        print('response: %s' % self.response)
        print('start time: %s' % self.start_time)
        print('end_time: %s' % self.end_time)
        print('duration: %s\n' % self.duration)

    def got_response(self):
        if self.response is None:
            return False
        else:
            return True

    def return_stats(self):
        str = ''
        str +=  '\nid: %s\n' % self.id
        str += 'command: %s\n' % self.command
        str += 'response: %s\n' % self.response
        str += 'start time: %s\n' % self.start_time
        str += 'end_time: %s\n' % self.end_time
        str += 'duration: %s\n' % self.duration
        return str

class TelloDeviceManager:
    def __init__(self):
        self.local_ip = ''
        self.local_port = 8889
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # socket for sending cmd
        self.socket.bind((self.local_ip, self.local_port))


        self.receive_thread = threading.Thread(target=self._receive_thread)
        self.receive_thread.daemon = True
        self.receive_thread.start()

        self.tello_ip = '192.168.10.1'
        self.tello_port = 8889
        self.tello_adderss = (self.tello_ip, self.tello_port)
        self.log = []

        self.MAX_TIME_OUT = 15.0

    def send_command(self, command):
        self.log.append(TelloStats(command, len(self.log)))

        self.socket.sendto(command.encode('utf-8'), self.tello_adderss)
        print('Sending command: %s to %s' % (command, self.tello_ip))

        start = time.time()
        while not self.log[-1].got_response():
            now = time.time()
            diff = now - start
            if diff > self.MAX_TIME_OUT:
                print('Max timeout exceeded... command %s' % command)
                return
        print('Command sent: %s to %s' % (command, self.tello_ip))

    def _receive_thread(self):
        while True:
            try:
                self.response, ip = self.socket.recvfrom(1024)
                print('Recieved %s from %s' % (self.response, ip))

                self.log[-1].add_response(self.response)
            except socket.error as exc:
                print("Caught exception socket.error : %s" % exc)

    def on_close(self):
        pass

    def get_log(self):
        return self.log
    
    def cmd(self):
        start_time = str(datetime.now())
        command='command'
        self.send_command(command.rstrip())
        command=''
        while True:
            command=input('>_ (Tello) ')
            if command != '' and command != '\n':
                command = command.rstrip()
                if command.find('delay') != -1:
                    sec = float(command.partition('delay')[2])
                    print('delay %s' % sec)
                    time.sleep(sec)
                    pass
                elif command == 'exit':
                    quit()
                elif command == 'em':
                    self.send_command('emergency')
                else:
                    self.send_command(command)

# Home Assistant
class HomeAssistantDeviceManager:
    def __init__(self):
        self.active=True
        self.url = AriaDefinitions.homeAssistAPIURL
        self.headers = {
            "Authorization": AriaDefinitions.homeAssistAPIKEY,
            "content-type": "application/json",
        }
    
    def Controller(self,command):
        payload = { "text": command.split(';')[1], "language": "en"}
        response = requests.post(self.url, headers=self.headers, json=payload)
        return json.loads(response.text)['response']['speech']['plain']['speech']

# CODE:PYTHON:PAUSE
# end of old structure [v3]
#
# 28/11/2023 restructure [v4]
#
# MAJOR UPDATE LEFT TO: AriaIntent Class: Call passed instance to run whatever needed
# MAJOR UPDATE LEFT TO: CommandProcessor Function.
#
# Progress {Last updated on 05/12} -> Expected Finish by 5th Jan
#
# restructure aria class: into 2 modules: proccess, respond + add a responce/input class for data storage + api info + control class ✓
# centralise unknown request ✓
# add show school timetable sys ✓ (ID COMMAND)
# location data class? ✓
# differentiate between terminal command and voice command ✓
# add chat gpt X
# Implement straight command processing if from terminal -> powershell ✓
# add step [by 5] volume ✓
#
#
# front end updates
#
# finish command proccessor
# add get computer data [vc commmand]
# potental 'connect to server'? e.g. ssh to ultimate
# user data? -> user login plus terminal customisation on login
# ^^ Load from cloud server?
# basic: add web open concepts
#
#
# background service concept:
#
# aria processing offloaded to bck service
# add pypush to background service
# add music dowloader
# add terminal shortcut
#
#
# other complex ideas
#
# remote terminal? -> Poll server for updates? -> Need secure server <vmdi>
# MATRIX TEXTING -> Use beeper
# add google search?
# translate + dictiocary
# add <vmdi> control apis etc
# introduce laptop device control apis?
# timer?
#
# 
# new structre [v4] 
# CODE:PYTHON:BEGIN

class LocationData:
    def __init__(self,inRoom,inHome,setLoc):
        self.inRoom=inRoom
        self.inHome=inHome
        self.setLoc=setLoc

class AriaSpeechServices:
    def __init__(self):
        pass
    
    def takeCommand(self,trialCount=0):
        r=sr.Recognizer()
        with sr.Microphone() as source:
            audio=r.listen(source)
            try:
                print('>_ (Listening)')
                statement=r.recognize_google(audio,language='en-gb')
                print(f'>_ (Voice: In) {statement}\n')

            except Exception as e:
                self.speak('Pardon me sir, please say that again')
                print('>_ (Voice: Out - DEBUG) An error has occured: '+str(e))
                trialCount=trialCount+1
                if trialCount == 3:
                    return '>_ (Speech.Error) Timed out'
                return self.takeCommand(trialCount)
            return str(statement).lower()

    def speak(self,text):
        engine=pyttsx3.init('sapi5')
        voices=engine.getProperty('voices')
        engine.setProperty('voice','voices[0].id')
        print('>_ (Voice: Out) '+text)
        engine.say(text)
        engine.runAndWait()


class AriaInput:
    def __init__(self,text,interface):
        self.text=text
        self.interface = interface
        self.AriaSpeech=AriaSpeechServices()
        self.takeCommand=self.AriaSpeech.takeCommand
        self.output=AriaOutput(interface)
        self.Aria=AriaIntentProcessor(self.output)
        self.AriaAction=AriaResultGenerater(self.output)
    def proccessInput(self):
        intent=self.Aria.identifyIntent(self.text)
        if intent=='command':
            self.Aria.identifyCommand()
        elif intent=='query':
            self.Aria.identifyQuery()
        elif intent=='explain':
            self.Aria.identifyExplain()
        else:
            self.Aria.identifyExplain()
            self.Aria.identifyCommand()
            self.Aria.identifyQuery()
        return self.AriaAction.commandProccess()


class AriaOutput:
    def __init__(self,interface):
        self.statement=None
        self.interface=interface
        self.AriaSpeech=AriaSpeechServices()
    # Storage Data
    def setAction(self,action,moreAction=None):
        self.action=action
        self.moreAction=moreAction
    # Set Output Data
    def setOutput(self,text):
        self.text=text
        self.speech=text
    # Grab Data
    def grabRawData(self): return self.text,self.speech,self.interface
    # Output
    # Func below for weather function to give more information
    def addMoreActInfo(self,moreText):
        self.moreText=moreText
        self.moreAct=True      
    # Output actual func cos why not
    def outputData(self):
        self.AriaSpeech.speak(self.text)
        if self.moreAct:
            self.speak('Would you like more information?')
            statement=self.AriaSpeech.takeCommand().lower()
            if 'no' in statement:
                a=1
            elif 'yes' in statement:
                self.AriaSpeech.speak(self.moreText)
    def outputDataText(self):
        print('>_ (Out) '+self.text)
        print('>_ (Out: More Info) '+self.moreText)



class AriaIntentProcessor:
    def __init__(self,output=AriaOutput) -> None:
        self.output=output

    def identifyIntent(self,statement):
        self.statement=statement
        self.output.statement=self.statement
        self.statementSplit=statement.split(' ')
        self.statementType=None
        for x in commandWords:
            if x in self.statementSplit:
                self.statementType='command'
                return 'command'
        for x in queryWords:
            if x in self.statementSplit:
                self.statementType='query'
                return 'query'
        for x in explainWords:
            if x in self.statementSplit:
                self.statementType='explain'
                return 'explain'
        
    def identifyQuery(self):
        if 'tell' in self.statement and 'time' in self.statement and 'times' not in self.statement:
            self.command=self.output.setAction('time')
        elif 'give' in self.statement and 'time' in self.statement and 'times' not in self.statement:
            self.command=self.output.setAction('time')
        elif 'what' in self.statement and 'time' in self.statement and 'times' not in self.statement:
            self.command=self.output.setAction('time')
        elif 'current' in self.statement and 'time' in self.statement and 'times' not in self.statement:
            self.command=self.output.setAction('time')

        elif 'tell' in self.statement and 'weather' in self.statement:
            self.command=self.output.setAction('weather')
        elif 'give' in self.statement and 'weather' in self.statement:
            self.command=self.output.setAction('weather')
        elif 'what' in self.statement and 'weather' in self.statement:
            self.command=self.output.setAction('weather')
        elif 'current' in self.statement and 'weather' in self.statement:
            self.command=self.output.setAction('weather')
        
        elif 'tell' in self.statement and 'news' in self.statement:
            self.command=self.output.setAction('news')
        elif 'give' in self.statement and 'news' in self.statement:
            self.command=self.output.setAction('news')
        elif 'what' in self.statement and 'news' in self.statement:
            self.command=self.output.setAction('news')
        elif 'current' in self.statement and 'news' in self.statement:
            self.command=self.output.setAction('news')

        elif 'who made you' in self.statement:
            self.command=self.output.setAction('return','Hi, My name is '+AriaDefinitions.name+' and I was made by '+AriaDefinitions.userName+'. I am an AI Assistant powered by the internet of things. You can ask me any question you like. I was born in the March 2021')
        elif  'who are you' in self.statement:
            self.command=self.output.setAction('return','Hi, My name is '+AriaDefinitions.name+' and I was made by '+AriaDefinitions.userName+'. I am an AI Assistant powered by the internet of things. You can ask me any question you like. I was born in the March 2021')
        elif 'what are you' in self.statement:
            self.command=self.output.setAction('return','Hi, My name is '+AriaDefinitions.name+' and I was made by '+AriaDefinitions.userName+'. I am an AI Assistant powered by the internet of things. You can ask me any question you like. I was born in the March 2021')
        elif  'when were you made' in self.statement:
            self.command=self.output.setAction('return','Hi, My name is '+AriaDefinitions.name+' and I was made by '+AriaDefinitions.userName+'. I am an AI Assistant powered by the internet of things. You can ask me any question you like. I was born in the March 2021')

        elif 'views on' in self.statement and 'assistant' in self.statement:
            self.command=self.output.setAction('return','My mortal enemy is Siri but I dont mind Google or Alexa. Although, it is a very hard job.')
        elif 'do you' in self.statement and 'siri' in self.statement:
            self.command=self.output.setAction('return','My mortal enemy is Siri but I dont mind Google or Alexa. Although, it is a very hard job.')
        elif 'do you' in self.statement and 'google' in self.statement:
            self.command=self.output.setAction('return','My mortal enemy is Siri but I dont mind Google or Alexa. Although, it is a very hard job.')
        elif 'do you' in self.statement and 'alexa' in self.statement:
            self.command=self.output.setAction('return','My mortal enemy is Siri but I dont mind Google or Alexa. Although, it is a very hard job.')
        elif 'being an assistant' in self.statement:
            self.command=self.output.setAction('return','My mortal enemy is Siri but I dont mind Google or Alexa. Although, it is a very hard job.')

        else:
            if self.aiProccessorEnabled:
                self.command=self.output.setAction('web','chatgpt')
            else:
                self.command=self.output.setAction('web','wolfram')

    def identifyCommand(self):
        if 'play' in self.statement and 'music' in self.statement:
            self.command=self.output.setAction('play')
        elif 'play' in self.statement and 'video' in self.statement:
            self.command=self.output.setAction('play')
        elif 'play' in self.statement and 'film' in self.statement:
            self.command=self.output.setAction('play')
        elif 'play' in self.statement and 'movie' in self.statement:
            self.command=self.output.setAction('play')
        elif 'play' in self.statement and 'media' in self.statement:
            self.command=self.output.setAction('play')
        elif 'pause' in self.statement and 'music' in self.statement:
            self.command=self.output.setAction('pause')
        elif 'pause' in self.statement and 'video' in self.statement:
            self.command=self.output.setAction('pause')
        elif 'pause' in self.statement and 'film' in self.statement:
            self.command=self.output.setAction('pause')
        elif 'pause' in self.statement and 'movie' in self.statement:
            self.command=self.output.setAction('pause')
        elif 'pause' in self.statement and 'media' in self.statement:
            self.command=self.output.setAction('pause')
        
        elif self.statement=='play':
            self.command=self.output.setAction('play')
        elif self.statement=='pause':
            self.command=self.output.setAction('pause')

        elif 'increase' in self.statement and 'volume' in self.statement:      
            self.command=self.output.setAction('vol-up')
        elif 'make' in self.statement and 'louder' in self.statement:             
            self.command=self.output.setAction('vol-up')
        elif 'turn' in self.statement and 'up' in self.statement and 'volume' in self.statement:    
            self.command=self.output.setAction('vol-up')
        elif 'volume' in self.statement and 'up' in self.statement:    
            self.command=self.output.setAction('vol-up')
        elif 'decrease' in self.statement and 'volume' in self.statement:      
            self.command=self.output.setAction('vol-down')
        elif 'make' in self.statement and 'quieter' in self.statement:    
            self.command=self.output.setAction('vol-down')
        elif 'turn' in self.statement and 'down' in self.statement and 'volume' in self.statement:    
            self.command=self.output.setAction('vol-down')
        elif 'volume' in self.statement and 'down' in self.statement:    
            self.command=self.output.setAction('vol-down')
    
        elif 'take' in self.statement and 'photo' in self.statement:    
            self.command=self.output.setAction('photo')
        elif 'take' in self.statement and 'picture' in self.statement:    
            self.command=self.output.setAction('photo')
        elif 'take' in self.statement and 'selfie' in self.statement:    
            self.command=self.output.setAction('photo')
        elif 'take' in self.statement and 'shot' in self.statement:    
            self.command=self.output.setAction('photo')
        elif 'open' in self.statement and 'camera' in self.statement:    
            self.command=self.output.setAction('photo')

        elif 'open' in self.statement and 'timetable' in self.statement and 'today' in self.statement:    
            self.command=self.output.setAction('timetable','today')
        elif 'show' in self.statement and 'timetable' in self.statement and 'today' in self.statement:    
            self.command=self.output.setAction('timetable','today')
        elif 'give' in self.statement and 'timetable' in self.statement and 'today' in self.statement:    
            self.command=self.output.setAction('timetable','today')
        elif 'what' in self.statement and 'timetable' in self.statement and 'today' in self.statement:    
            self.command=self.output.setAction('timetable','today')

        elif 'open' in self.statement and 'timetable' in self.statement and 'tomorrow' in self.statement:    
            self.command=self.output.setAction('timetable','tomorrow')
        elif 'show' in self.statement and 'timetable' in self.statement and 'tomorrow' in self.statement:    
            self.command=self.output.setAction('timetable','tomorrow')
        elif 'give' in self.statement and 'timetable' in self.statement and 'tomorrow' in self.statement:    
            self.command=self.output.setAction('timetable','tomorrow')
        elif 'what' in self.statement and 'timetable' in self.statement and 'tomorrow' in self.statement:    
            self.command=self.output.setAction('timetable','tomorrow')

    
        elif 'turn the ' in self.statement:
            newState=self.statementSplit[4]
            device=self.statementSplit[3]
            self.command=self.output.setAction('control',self.statement)
        elif 'turn' in self.statement:
            newState=self.statementSplit[1]
            device=self.statementSplit[3]
            self.command=self.output.setAction('control',self.statement)

        elif 'launch' in self.statement or 'open' in self.statement:
            if '-' in self.statementSplit[1]:
                hasFlags=True
            else:
                hasFlags=False
            if not hasFlags:
                toRemoveSect=self.statementSplit[0]
                appGiven=self.statement.replace(toRemoveSect)
                for app in apps:
                    if app==appGiven:
                        self.command=self.output.setAction('launch',app)
            elif hasFlags:
                toRemoveSect=self.statementSplit[0]+' '+self.statementSplit[1]
                appGiven=self.statement.replace(toRemoveSect)
                for app in apps:
                    if app==appGiven:
                        self.command=self.output.setAction('launch',app)
        
        elif 'exit' in self.statement:
            exit()

        else:
            self.command=self.output.setAction('return',Error('unknown.query'))

        
    def identifyExplain(self):
        pass


class AriaResultGenerater:
    def __init__(self,output=AriaOutput) -> None:
        self.output=output

    def proccessTerminalCommand(self,op):
        if op == 'ssh ultimate':
            os.system('powershell '+AriaDefinitions.basePath+'/Onedrive/Desktop/Other/ssh.bat')
        elif op == 'ssh tab':
            os.system(AriaDefinitions.basePath+'/Onedrive/Desktop/SshTab.bat')
        elif op == 'vc':
            hostname=socket.gethostname()
            IPAddr=socket.gethostbyname(hostname)
            battery = psutil.sensors_battery()
            print('Computer Status: ')
            if battery.power_plugged:
                print("Charging: "+str(battery.percent)+"%")
            else:
                print("Not Charging: "+str(battery.percent)+"%")
            print("Computer Name: "+hostname)
            print("Computer IP Address: "+IPAddr)
            if IPAddr == '172.30.64.1':
                print('Wifi Status: Not Connected')
            else:
                print('Wifi Status: Connected')
        elif op == 'ssh cust':
            host=input('Host: ')
            username=input(host+' login: ')
            os.system('powershell ssh '+username+'@'+host)
        elif op == 'tt':
            webbrowser.open_new_tab('https://eqe.fireflycloud.net/planner/day/'+(datetime.date.today() + datetime.timedelta(days=1).strftime("%Y-%m-%d")))
        elif op == 'launch aria':
            print('Aria not availiable yet.')
        elif op == 'status ultimate':
            print('powershell ssh pi@ultimate neofetch')
        elif op == 'launch -wsl ubuntu':
            os.system('powershell wsl -d ubuntu')
        elif op == 'launch -cli power':
            os.system('powershell')
        elif op == 'vo':
            print('Options: SSH to Ultimate [SU], SSH to custom host [SC], View status of Ultimate [STU], Open Ubuntu [OU], Open Debian [OD], Open windows powershell [OP], Open Browse [OB], View these options again [VO], \nStart Shizuku [SS], Launch adb [LA], Screen mirror [SM], Bluestacks [BS], Start Aria [SA], SSH to '+AriaDefinitions.userFirstName+'s Tablet (The service sshd must be running!) [SV].')
            print('If you enter any other command it will be passed through to Windows Powershell.')
        elif op == 'launch browse':
            os.system(r'C:\Windows\py.exe "'+AriaDefinitions.basePath+'\Projects\python-utils\browser.py"')
        elif op == 'launch -adb shizuku':
            os.system('cd '+AriaDefinitions.basePath+'/Google/platform-tools && adb shell sh /storage/emulated/0/Android/data/moe.shizuku.privileged.api/start.sh ')
        elif op == 'launch -adb':
            os.system('cd '+AriaDefinitions.basePath+'/Google/platform-tools && cmd')
        elif op == 'launch -adb scrcpy':
            os.system(AriaDefinitions.basePath+'/Google/Scrcpy/scrcpy.exe')
        elif op == 'ts':
            print('Terminal: v8.6')
            print('Python: 3.9')
            print('Windows: 11')
            print('AriaCore: v2.1')
            print('Adb: v12')
            print('Ubuntu: 22.04')
        elif op == '':
            print('',end="")
        elif 'em-lock' in op:
            print('Initiating PERMANENT lockdown')
            if input('Continue? Y/n: ') == 'y':
                print('Ok, beginning system lockdown.')
                print('ARIA lockdown >_ v.8.6')
                print('[WARN]: Ubuntu will not be reinstalled after removal')
                print('[INFO]: Uninstalling wsl...')
                os.system('wsl --unregister ubuntu')
                print('[INFO]: Locking Terminal...')
                print('[INFO]: Opening lock file')
                lock=open(AriaDefinitions.basePath+r'\My Drive\Coding\VirtualAssist\Aria_Client_V2.0\lock','w')
                lock.write('lock')
                lock.close()
                print('[NOTICE]: Lock complete!')
                time.sleep(20)
                while True:
                    print('Locked: Please close this window')
            else:
                print('Abort')
        elif op == 'launch -wsa settings':
            os.system('powershell "Start-Process wsa://com.android.settings"')
        elif op == 'exit':
            print("This commands breaks a lot of things, so for now it has been reallocated to just close the session.")
            os.system('powershell pause')
        elif op == "launch -wsa shizuku":
            os.system('cd D:/'+AriaDefinitions.userName+'/Google/platform-tools && adb connect 127.0.0.1:58526 && adb shell sh /storage/emulated/0/Android/data/moe.shizuku.privileged.api/start.sh')
        elif op == 'launch':
            print('ERROR: You must specify an app')
        else:
            os.system('powershell.exe "'+op+'"')
    
    def openInBrowser(self,addr):
        webbrowser.open_new_tab(addr)
        return 'Ok, opening that up'

    def open_app(self,app):
        os.system('start'+app+':')
        return 'Ok, opening '+app

    def playPause(self):
        VK_MEDIA_PLAY_PAUSE = 0xB3
        hwcode = win32api.MapVirtualKey(VK_MEDIA_PLAY_PAUSE, 0)
        win32api.keybd_event(VK_MEDIA_PLAY_PAUSE, hwcode)
        return 'Ok, ',' the music.'

    def volumeUp(self):
        hwcode = win32api.MapVirtualKey(win32con.VK_VOLUME_UP, 0)
        win32api.keybd_event(win32con.VK_VOLUME_UP, hwcode)
        win32api.keybd_event(win32con.VK_VOLUME_UP, hwcode)
        return 'Ok, increasing the volume'

    def volumeDown(self):
        hwcode = win32api.MapVirtualKey(win32con.VK_VOLUME_DOWN, 0)
        win32api.keybd_event(win32con.VK_VOLUME_DOWN, hwcode)
        win32api.keybd_event(win32con.VK_VOLUME_DOWN, hwcode)
        return 'Ok, decreasing the volume'

    def lock(self):
        ctypes.windll.user32.LockWorkStation()
        return 'Ok, locking your device'
    
    def tellJoke(self):
        return pyjokes.get_joke
    
    def getWeather(self,city):
        weatherAPI=OpenWeatherAPI(AriaDefinitions.openWeatherMapAPIKEY,AriaDefinitions.openWeatherMapAPIURL)
        weather,weather_more=weatherAPI.query(city)
        return weather,weather_more
    
    def searchWiki(self,statement):
        statement =statement.replace("search wikipedia for", "")
        return wikipedia.summary(statement, sentences=2)
    
    def getTime(self):
        return datetime.datetime.now().strftime("%H:%M")
    
    def askAria(self,statement):
        try:
            question=statement
            app_id=AriaDefinitions.wolframAlphaAPIKEY
            client = wolframalpha.Client(app_id)
            res = client.query(question)
            answer = next(res.results).text
            return answer
        except:
            return "Sorry, I'm afraid I do not know the answer to that" 
    
    def commandProccess(self):
        commandAction=self.output.action
        if commandAction=='time':
            self.output.setOutput(self.getTime())
            return self.output
        elif commandAction=='weather':
            weather,weather_more= self.getWeather('amersham')
            self.output.setOutput(weather)
            self.output.addMoreActInfo(weather_more)
            return self.output
        elif commandAction=='news':
            self.output.setOutput(self.getNews)
            return self.output
        elif commandAction.split(':')[0] == 'return':
            self.output.setOutput(commandAction.split(':')[1])
            return self.output
        elif commandAction == 'play':
            startSen,endSen=self.playPause()
            self.output.setOutput(startSen+'playing'+endSen)
            return self.output
        elif commandAction == 'pause':
            startSen,endSen=self.playPause()
            self.output.setOutput(startSen+'pausing'+endSen)
            return self.output
        elif commandAction == 'vol-up':
            self.output.setOutput(self.volumeUp())
            return self.output
        elif commandAction == 'vol-down':
            self.output.setOutput(self.volumeDown())
            return self.output
        elif commandAction== 'web' and self.output.moreAction == 'chatgpt':
            self.output.setOutput(self.askAria(self.output.statement))
            return self.output
        elif commandAction== 'web' and self.output.moreAction == 'wolframalpha':
            self.output.setOutput(self.askAria(self.output.statement))
            return self.output
        elif commandAction== 'control':
            self.output.setOutput(self.HomeAssistant.Controller(self.output.statement))
            return self.output
        else:
            if self.output.interface == 'cmd':
                os.system('powershell '+self.output.statement)
                self.output.setOutput('Exectuted Query')
                return self.output
            elif self.output.interface == 'voice':
                self.output.setOutput(Error('unknown.query'))
                return self.output

class API:
    def __init__(self,apiKey,apiEndpoint=None):
        self.apiEndpoint=apiEndpoint
        self.apiKey=apiKey

class WolframAlphaAPI(API):
    def __init__(self, apiKey, apiEndpoint=None):
        super().__init__(apiKey, apiEndpoint)
    
    def query(self,statement):
        try:
            question=statement
            app_id=AriaDefinitions.wolframAlphaAPIKEY
            client = wolframalpha.Client(app_id)
            res = client.query(question)
            answer = next(res.results).text
            return answer
        except:
            return Error('unknown.answer')

class OpenWeatherAPI(API):
    def __init__(self, apiKey, apiEndpoint=None):
        super().__init__(apiKey, apiEndpoint)
        self.apiKey=AriaDefinitions.openWeatherMapAPIKEY
        self.apiEndpoint=AriaDefinitions.openWeatherMapAPIURL

    def kelvinToCelsius(self,kelvin):
        return kelvin - 273.15

    def query(self,city):
        api_key=self.apiKey
        base_url=self.apiEndpoint
        complete_url=base_url+"appid="+api_key+"&q="+city
        response = requests.get(complete_url)
        x=response.json()
        if x["cod"]!="404":
            y=x["main"]
            current_temperature = y["temp"]
            current_humidiy = y["humidity"]
            z = x["weather"]
            weather_description = z[0]["description"]
            print(current_temperature)
            current_temperature_cel=self.kelvinToCelsius(current_temperature)
            weather = "Sure sir, the temperature is " + str(current_temperature_cel) + " celsius"
            weather_more = "Okay, here's a quick description: " + str(weather_description)
            return weather,weather_more
        else:
            return Error('unknown.city')


class Error:
    def __init__(self,error_type):
        if error_type=='unknown.answer':
            return "Sorry, I'm afraid I do not know the answer to that"
        elif error_type=='unknown.query':
            return "Sorry, I'm afraid I'm unable to do that yet."
        elif error_type=='unknown.city':
            return "Sorry sir, city not found"
        else:
            return "Sorry, I'm afraid I'm unable to do that yet."            
        
    
class AriaUI:
    def __init__(self,root=tk.Tk()):
        self.root = root
    def __init__tkinkter(self):
        self.root.title("Aria")
        image_path = AriaDefinitions.basePath+r"\My Drive\Projects\Coding\VirtualAssist\Aria v3.0\AriaOverlay.png"
        self.image = Image.open(image_path)
        self.tk_image = ImageTk.PhotoImage(self.image)
        self.image_label = tk.Label(self.root, image=self.tk_image)
        self.image_label.pack()
        self.root.wm_attributes("-topmost", 1)
        window_width = self.image.width
        window_height = self.image.height
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        taskbar_height = self.root.winfo_screenmmheight() - screen_height
        window_x = screen_width - window_width
        window_y = screen_height - window_height + taskbar_height
        self.root.geometry(f"{window_width}x{window_height}+{window_x}+{window_y}")
    
    def TerminalWelcome(self):
        print('>_ (Welcome) to Aria...')
        print('>_ (Copyright) © Vivaan Modi 2021 -> Present. All Rights Reserved.')


    def TerminalUI(self):
        while True:
            AriaInput(input('>_ '),'cmd').proccessInput().outputDataText()

    def VoiceOnTrigger(self):
        AriaInput(AriaSpeechServices().takeCommand().lower(),'voice').proccessInput().outputData()
        self.TriggerSetter()

    def TriggerSetter(self):
        hotkey_combination = 'ctrl+shift+a'
        keyboard.add_hotkey(hotkey_combination, self.VoiceOnTrigger)

    def TerminalUIThreadCreate(self):
        self.TerminalUIThread=threading.Thread(target=self.TerminalUI())
 

    def TerminalUIThreadManager(self):
        return self.TerminalUIThread

if __name__=='__main__':
    import threading
    AriaMain = AriaUI()
    AriaMain.TerminalWelcome()
    AriaMain.TriggerSetter()
    AriaMain.TerminalUIThreadCreate()
    AriaMain.TerminalUIThreadManager().start()