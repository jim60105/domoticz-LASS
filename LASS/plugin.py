# LASS Python Plugin
#
# Author: jim60105
#
"""
<plugin key="LASS" name="LASS" author="jim60105" version="1.0.0" externallink="https://www.facebook.com/groups/LASSnet/">
    <params>
        <param field="Mode1" label="LASS_ID" width="80px" required="true" default="FT1_389"/>
        
        <param field="Mode6" label="Update Rate(Min)" width="30px" required="true" default="10"/>
    </params>
</plugin>
"""
import Domoticz
import json
import urllib.request

class BasePlugin:
    httpConn = None
    def __init__(self):
        return
    def onStart(self):
        Domoticz.Debugging(1)
        self.repeatTime = int(Parameters["Mode6"])
        self.intervalTime = self.repeatTime
        self.LASSURL = "https://pm25.lass-net.org"
        
        self.httpRequest()
        self.sensor = self.Response['feeds'][0]['LASS']
        self.sensorList = []
        # dust
        if ( 1 not in Devices):  
            if ( 's_d0' in self.sensor):
                Domoticz.Device(Name=Parameters["Mode1"] + " - PM2.5",  Unit=1, TypeName="Custom", Options={"Custom":"1;μg/m³"}, Used=1).Create()
                self.sensorList.append(['s_d0','1'])
        if ( 2 not in Devices):
            if ( 's_d1' in self.sensor):
                Domoticz.Device(Name=Parameters["Mode1"] + " - PM10",  Unit=2, TypeName="Custom", Options={"Custom":"1;μg/m³"}, Used=1).Create()
                self.sensorList.append(['s_d1','2'])
        if ( 3 not in Devices):
            if ( 's_d2' in self.sensor):
                Domoticz.Device(Name=Parameters["Mode1"] + " - PM1",  Unit=3, TypeName="Custom", Options={"Custom":"1;μg/m³"}, Used=1).Create()
                self.sensorList.append(['s_d2','3'])
        
        # baro
        if ( 4 not in Devices):  
            for i in range(0,2):
                if ( 's_b'+str(i) in self.sensor):
                    Domoticz.Device(Name=Parameters["Mode1"] + " - Barometer",  Unit=4, TypeName="Custom", Options={"Custom":"1;μg/m³"}, Used=1).Create()
                    self.sensorList.append(['s_b'+str(i),'4'])
                    break
        
        # humid
        if ( 5 not in Devices):  
            for i in range(0,5):
                if ( 's_h'+str(i) in self.sensor):
                    Domoticz.Log('5')
                    Domoticz.Device(Name=Parameters["Mode1"] + " - Humidity",  Unit=5, TypeName="Custom", Options={"Custom":"1;%"}, Used=1).Create()
                    self.sensorList.append(['s_h'+str(i),'5'])
                    break
        
        # temperature
        if ( 6 not in Devices):  
            for i in range(0,5):
                if ( 's_t'+str(i) in self.sensor):
                    Domoticz.Device(Name=Parameters["Mode1"] + " - Temperature",  Unit=6, TypeName="Custom", Options={"Custom":"1;℃"}, Used=1).Create()
                    self.sensorList.append(['s_t'+str(i),'6'])
                    break
        
        # gas
        gasList = ['NH3','CO','NO2','C3H8','C4H10','CH4','H2','C2H5OH','CO2']
        for i in range(7,15):
            if ( i not in Devices): 
                if ( 's_g'+str(i) in self.sensor):
                    Domoticz.Device(Name=Parameters["Mode1"] + " - " + gasList[i-7],  Unit=i, TypeName="Custom", Options={"Custom":"1;μg/m³"}, Used=1).Create()
                    self.sensorList.append(['s_g'+str(i),str(i)])
                    
        if ( 16 not in Devices): 
            if ( 's_gg' in self.sensor):
                Domoticz.Device(Name=Parameters["Mode1"] + " - TVOC",  Unit=16, TypeName="Custom", Options={"Custom":"1;μg/m³"}, Used=1).Create()
                self.sensorList.append(['s_gg','16'])
        
        Domoticz.Heartbeat(60)
        self.httpConn = Domoticz.Connection(Name="httpConn", Transport="TCP/IP", Protocol="HTTP", Address="pm25.lass-net.org", Port="443")
        self.httpConn.Connect()
    def onStop(self):
        Domoticz.Log("onStop - Plugin is stopping.")

    def onConnect(self, Connection, Status, Description):
        if (Status == 0):
            Domoticz.Log("Connected successfully.")
            self.httpConn.Disconnect()
            self.httpRequest()
            if (self.Status == 200):
                Domoticz.Log("Good Response received from LASS.")
                
                for index in range(len(self.sensorList)):
                    if self.sensorList[index][0] in self.Response['feeds'][0]['LASS']:
                        self.UpdateDevice(int(self.sensorList[index][1]),0,self.Response['feeds'][0]['LASS'][self.sensorList[index][0]])
                        
            elif (self.Status == 302):
                Domoticz.Log("LASS returned a Page Moved Error.")
            elif (self.Status == 400):
                Domoticz.Error("LASS returned a Bad Request Error.")
            elif (self.Status == 500):
                Domoticz.Error("LASS returned a Server Error.")
            else:
                Domoticz.Error("LASS returned a Status: "+str(self.Status))
        else:
            Domoticz.Log("Failed to connect ("+str(Status)+") to: "+self.LASSURL+" with error: "+Description)
            
    def onMessage(self, Connection, Data):
        Domoticz.Debug("onMessage: Status="+str(self.Status))

    def onCommand(self, Unit, Command, Level, Hue):
        Domoticz.Debug("onCommand called for Unit " + str(Unit) + ": Parameter '" + str(Command) + "', Level: " + str(Level))

    def onDisconnect(self, Connection):
        Domoticz.Log("onDisconnect called for connection to: "+Connection.Address+":"+Connection.Port)

    def onHeartbeat(self):
        if (self.httpConn.Connecting() or self.httpConn.Connected()):
            Domoticz.Debug("onHeartbeat called, Connection is alive.")
        else:
            self.intervalTime += 1
            if self.intervalTime >= self.repeatTime:
                self.intervalTime = 0
                self.httpConn.Connect()
    def httpRequest(self):
        r = urllib.request.urlopen(self.LASSURL+'/data/last.php?device_id='+Parameters["Mode1"])
        Data = r.read()
        strData = str(Data)
        Domoticz.Log(strData)

        self.Response = json.loads(Data)
        DumpHTTPResponseToLog(self.Response)
        self.Status = int(r.getcode())
        return
    def UpdateDevice(self, Unit, nValue, sValue):
        # Make sure that the Domoticz device still exists (they can be deleted) before updating it 
        if (Unit in Devices):
            if (Devices[Unit].nValue != nValue) or (Devices[Unit].sValue != sValue):
                Devices[Unit].Update(nValue=nValue, sValue=str(sValue))
                Domoticz.Log("Update "+str(nValue)+":'"+str(sValue)+"' ("+Devices[Unit].Name+")")
        return

global _plugin
_plugin = BasePlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def onStop():
    global _plugin
    _plugin.onStop()

def onConnect(Connection, Status, Description):
    global _plugin
    _plugin.onConnect(Connection, Status, Description)

def onMessage(Connection, Data):
    global _plugin
    _plugin.onMessage(Connection, Data, Status, Extra)

def onCommand(Unit, Command, Level, Hue):
    global _plugin
    _plugin.onCommand(Unit, Command, Level, Hue)

def onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile):
    global _plugin
    _plugin.onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile)

def onDisconnect(Connection):
    global _plugin
    _plugin.onDisconnect(Connection)

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()

# Generic helper functions
def LogMessage(Message):
    f = open(Parameters["HomeFolder"]+"http.html","w")
    f.write(Message)
    f.close()
    Domoticz.Log("File written")

def DumpConfigToLog():
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Debug( "'" + x + "':'" + str(Parameters[x]) + "'")
    Domoticz.Debug("Device count: " + str(len(Devices)))
    for x in Devices:
        Domoticz.Debug("Device:           " + str(x) + " - " + str(Devices[x]))
        Domoticz.Debug("Device ID:       '" + str(Devices[x].ID) + "'")
        Domoticz.Debug("Device Name:     '" + Devices[x].Name + "'")
        Domoticz.Debug("Device nValue:    " + str(Devices[x].nValue))
        Domoticz.Debug("Device sValue:   '" + Devices[x].sValue + "'")
        Domoticz.Debug("Device LastLevel: " + str(Devices[x].LastLevel))
    return

def DumpHTTPResponseToLog(httpDict):
    if isinstance(httpDict, dict):
        Domoticz.Log("HTTP Details ("+str(len(httpDict))+"):")
        for x in httpDict:
            if isinstance(httpDict[x], dict):
                Domoticz.Log("--->'"+x+" ("+str(len(httpDict[x]))+"):")
                for y in httpDict[x]:
                    Domoticz.Log("------->'" + y + "':'" + str(httpDict[x][y]) + "'")
            else:
                Domoticz.Log("--->'" + x + "':'" + str(httpDict[x]) + "'")