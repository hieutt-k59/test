# Inspired and modified from https://github.com/CloudMQTT/python-mqtt-example
import os
from django.core.wsgi import get_wsgi_application

os.environ['DJANGO_SETTINGS_MODULE'] = 'RbiCloud.settings'
application = get_wsgi_application()

from cloud import models
# import configparser
# from urllib.parse import urlparse
import paho.mqtt.client as mqtt
from cloud import models
import json
from datetime import datetime

# Define event callbacks
def on_connect(client, userjson_comp, flags, rc):
    print("rc: " + str(rc))

def on_message(client, obj, msg):
	# humi = str(msg.payload)
    print(msg.topic + " || " + str(msg.qos) + " || " + str(msg.payload))
    # print(humi)
    comp_id = msg.topic.split('/')[0]
    assess = msg.topic.split('/')[1]
    topic = msg.topic.split('/')[2]
    temp = str(msg.payload)
    rw_assessment = {}
    rw_equipment = {}
    if topic == "assessment":
        comp = models.ComponentMaster.objects.get(componentid= int(comp_id))
        facility_id = models.EquipmentMaster.objects.get(equipmentid=comp.equipmentid_id).facilityid_id
        target = models.FacilityRiskTarget.objects.get(facilityid=facility_id)
        faci = models.Facility.objects.get(facilityid=facility_id)
        length = len(temp) - 1
        # print(temp[2:length])
        # temp1 = json.dumps(temp[2:length], sort_keys=True)
        # temp2 = temp1.replace("'", "")
        json_assess = eval(temp[2:length])
        print(json_assess)
        # Sensor_ID = json_assess["Sensor_ID"]
        # print(str(Sensor_ID))
        # Date_n_Time = json_assess["Date"]
        # print(Date_n_Time)
        # Temperature = json_assess["Temperature"]
        # print(Temperature)
        # new Component Master
        # comp_num = ["ComponentNumber"]
        # eq_id = ["EquipmentID"]
        # comp_type_id = ["ComponentTypeID"]
        # comp_name = ["ComponentName"]
        # comp_desc = ["ComponentDesc"]
        # is_eq_linked = ["IsEquipmentLinked"]
        # api_comp_type_id = 
        # ["Create"]
        # Assessment - rw_component
        json_assess["APIComponentTypeID"] = models.ApiComponentType.objects.get(apicomponenttypeid=comp.apicomponenttypeid).apicomponenttypename
        json_assess['equipmentType'] = models.EquipmentType.objects.get(equipmenttypeid=models.EquipmentMaster.objects.get(equipmentid=comp.equipmentid_id).equipmenttypeid_id).equipmenttypename
        json_assess['AssessmentDate'] = datetime.now()
        rw_assessment = models.RwAssessment(equipmentid_id=comp.equipmentid_id, componentid_id=comp.componentid, assessmentdate=json_assess['AssessmentDate'],
                                            riskanalysisperiod=json_assess['RiskAnalystPeriod'], isequipmentlinked= comp.isequipmentlinked,
                                            proposalname=assess)
        rw_assessment.save()

    if topic == "equipment":
        json_eq = eval(temp[2:length])
        rw_equipment = models.RwEquipment(id=rwassessment, commissiondate=models.EquipmentMaster.objects.get(equipmentid= comp.equipmentid_id).commissiondate,
                                      adminupsetmanagement=json_eq["AdminControlUpset"], containsdeadlegs=json_eq["ContainsDeadlegs"],
                                      cyclicoperation=json_eq["CylicOper"], highlydeadleginsp=json_eq["Highly"],
                                      downtimeprotectionused=json_eq["Downtime"], externalenvironment=json_eq['ExternalEnvironment'],
                                      heattraced=json_eq["HeatTraced"], interfacesoilwater=json_eq["InterfaceSoilWater"],
                                      lineronlinemonitoring=json_eq["LOM"], materialexposedtoclext=json_eq["MFTF"],
                                      minreqtemperaturepressurisation=json_eq["minTemp"],
                                      onlinemonitoring=json_eq['OnlineMonitoring'], presencesulphideso2=json_eq["PresenceofSulphides"],
                                      presencesulphideso2shutdown=json_eq["PresenceofSulphidesShutdown"],
                                      pressurisationcontrolled=json_eq["PressurisationControlled"], pwht=json_eq["PWHT"], steamoutwaterflush=json_eq["SteamedOut"],
                                      managementfactor= faci.managementfactor, thermalhistory=json_eq['ThermalHistory'],
                                      yearlowestexptemp=json_eq["EquOper"], volume=json_eq["EquipmentVolumn"])
        rw_equipment.save()
    if topic == "component":
        json_comp = eval(temp[2:length])
        rwcomponent = models.RwComponent(id=rwassessment, nominaldiameter=json_comp["NorminalDiameter"],
                                      nominalthickness=json_comp['NorminalThickness'], currentthickness=json_comp['CurrentThickness'],
                                      minreqthickness=json_comp['MinReqThickness'], currentcorrosionrate=json_comp['CurrentCorrosionRate'],
                                      branchdiameter=json_comp['BranchDiameter'], branchjointtype=json_comp['BranchJointType'],
                                      brinnelhardness=json_comp['MaxBrinell']
                                      , deltafatt=json_comp['DeltaFATT'], chemicalinjection=json_comp["ChemicalInjection"],
                                      highlyinjectioninsp=json_comp["HFICI"], complexityprotrusion=json_comp['complex'],
                                      correctiveaction=json_comp['CorrectiveAction'], crackspresent=json_comp["PresenceCracks"],
                                      cyclicloadingwitin15_25m=json_comp['CylicLoad'],
                                      damagefoundinspection=json_comp["DFDI"], numberpipefittings=json_comp['NumberPipeFittings'],
                                      pipecondition=json_comp['PipeCondition'],
                                      previousfailures=json_comp['PreviousFailures'], shakingamount=json_comp['ShakingAmount'],
                                      shakingdetected=json_comp["VASD"], shakingtime=json_comp['timeShakingPipe'],
                                      trampelements=json_comp["TrampElement"])
        rwcomponent.save()
    if topic == "rw_stream":
        json_stream = eval(temp[2:length])
        rwstream = models.RwStream(id=rwassessment, aminesolution=json_stream['AminSolution'], aqueousoperation=json_stream["AqueOp"],
                                aqueousshutdown=json_stream["AqueShutdown"], toxicconstituent=json_stream["ToxicConstituents"],
                                caustic=json_stream["EnvCaustic"],
                                chloride=json_stream['ChlorideIon'], co3concentration=json_stream['CO3'], cyanide=json_stream["PresenceCyanides"],
                                exposedtogasamine=json_stream["exposureAcid"], exposedtosulphur=json_stream["ExposedSulfur"],
                                exposuretoamine=json_stream['ExposureAmine'],
                                h2s=json_stream["EnvCH2S"], h2sinwater=json_stream['"H2SInWater"'], hydrogen=json_stream["ProcesHydrogen"],
                                hydrofluoric=json_stream["HydrogenFluoric"], materialexposedtoclint=json_stream["materialExposedFluid"],
                                maxoperatingpressure=json_stream['maxOP'],
                                maxoperatingtemperature=float(json_stream['maxOT']), minoperatingpressure=float(json_stream['minOP']),
                                minoperatingtemperature=json_stream['minOT'], criticalexposuretemperature=json_stream['criticalTemp'],
                                naohconcentration=json_stream['NaOHConcentration'],
                                releasefluidpercenttoxic=float(json_stream['ReleasePercentToxic']),
                                waterph=float(json_stream['PHWater']), h2spartialpressure=float(json_stream['OpHydroPressure']))
            rwstream.save()
def on_publish(client, obj, mid):
    print("mid: " + str(mid))

def on_subscribe(client, obj, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))

def on_log(client, obj, level, string):
    print(string)

client = mqtt.Client()
# Assign event callbacks
client.on_message = on_message
client.on_connect = on_connect
client.on_publish = on_publish
client.on_subscribe = on_subscribe

# Uncomment to enable debug messages
#client.on_log = on_log

# Get CLOUDMQTT settings from config.ini 
# CONFIG = configparser.ConfigParser()
# CONFIG.read('config.ini')
# CONFIG_MQTT = CONFIG['Cloudmqtt']
# print(CONFIG_MQTT)
# TOPIC = CONFIG_MQTT['TOPIC']
# FIRST_MESSAGE = CONFIG_MQTT['MESSAGE']
CLOUDMQTT_URL='m14.cloudmqtt.com'
PORT=15101
SSL_PORT=25101 
USER='exurkrzh'
PASSWORD = 'fu_-7WLSfD71'
TOPIC = '+/+'
# MESSAGE = '62'

# Connect
client.username_pw_set(USER, PASSWORD)
client.connect(CLOUDMQTT_URL, PORT)

# Start subscribe, with QoS level 0
client.subscribe(TOPIC, 0)


# Publish a message
# client.pubqlish(TOPIC, FIRST_MESSAGE)

# Continue the network loop, exit when an error occurs
rc = 0
while rc == 0:
    rc = client.loop()
print("rc: " + str(rc))