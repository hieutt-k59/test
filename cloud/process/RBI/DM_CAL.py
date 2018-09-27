import time
import time
import math
from builtins import property
from datetime import datetime
import  numpy as np
from dateutil.relativedelta import relativedelta
from pathlib import _Selector
#from rbi import MYSQL_CAL as DAL_CAL
from cloud.process.RBI import Postgresql as DAL_CAL


# nhung gia tri Num_inspec, EFF khong can truyen khi su dung ham
class DM_CAL:
    # ham khoi tao
    def __init__(self,ComponentNumber = "",Commissiondate = datetime.now(), AssessmentDate = datetime.now(), APIComponentType="",
                 Diametter=0, NomalThick=0, CurrentThick=0, MinThickReq=0, CorrosionRate=0, CA=0,
                 ProtectedBarrier=False, CladdingCorrosionRate=0, InternalCladding=False, NoINSP_THINNING=0,
                 EFF_THIN="E", OnlineMonitoring="", HighlyEffectDeadleg=False, ContainsDeadlegs=False,
                 TankMaintain653=False, AdjustmentSettle="", ComponentIsWeld=False,
                 LinningType="", LINNER_ONLINE=False, LINNER_CONDITION="", INTERNAL_LINNING=False,
                 CAUSTIC_INSP_EFF="E", CAUSTIC_INSP_NUM=0, HEAT_TREATMENT="", NaOHConcentration=0, HEAT_TRACE=False,
                 STEAM_OUT=False,
                 AMINE_INSP_EFF="E", AMINE_INSP_NUM=0, AMINE_EXPOSED=False, AMINE_SOLUTION="",
                 ENVIRONMENT_H2S_CONTENT=False, AQUEOUS_OPERATOR=False, AQUEOUS_SHUTDOWN=False, SULPHIDE_INSP_EFF="E",
                 SULPHIDE_INSP_NUM=0, H2SContent=0, PH=0, PRESENT_CYANIDE=False, BRINNEL_HARDNESS="",
                 SULFUR_INSP_EFF="E", SULFUR_INSP_NUM=0, SULFUR_CONTENT="",
                 CACBONATE_INSP_EFF="E", CACBONATE_INSP_NUM=0, CO3_CONTENT=0,
                 PTA_SUSCEP=False, NICKEL_ALLOY=False, EXPOSED_SULFUR=False, PTA_INSP_EFF="E", PTA_INSP_NUM=0,
                 ExposedSH2OOperation=False, ExposedSH2OShutdown=False, ThermalHistory="", PTAMaterial="",
                 DOWNTIME_PROTECTED=False,
                 INTERNAL_EXPOSED_FLUID_MIST=False, EXTERNAL_EXPOSED_FLUID_MIST=False, CHLORIDE_ION_CONTENT=0,
                 CLSCC_INSP_EFF="E", CLSCC_INSP_NUM=0,
                 HSC_HF_INSP_EFF="E", HSC_HF_INSP_NUM=0,
                 HICSOHIC_INSP_EFF="E", HICSOHIC_INSP_NUM=0, HF_PRESENT=False,
                 EXTERNAL_INSP_NUM=0, EXTERNAL_INSP_EFF="E",
                 INTERFACE_SOIL_WATER=False, SUPPORT_COATING=False, INSULATION_TYPE="", CUI_INSP_NUM=0,
                 CUI_INSP_EFF="E", CUI_PERCENT_1=0, CUI_PERCENT_2=0,
                 CUI_PERCENT_3=0, CUI_PERCENT_4=0, CUI_PERCENT_5=0, CUI_PERCENT_6=0, CUI_PERCENT_7=0, CUI_PERCENT_8=0,
                 CUI_PERCENT_9=0, CUI_PERCENT_10=0,
                 EXTERN_CLSCC_INSP_NUM=0, EXTERN_CLSCC_INSP_EFF="E",
                 EXTERNAL_INSULATION=False, COMPONENT_INSTALL_DATE=datetime.now().date(), CRACK_PRESENT=False,
                 EXTERNAL_EVIRONMENT="",EXTERN_COATING = False, EXTERN_COAT_QUALITY="", EXTERN_CLSCC_CUI_INSP_NUM=0,
                 EXTERN_CLSCC_CUI_INSP_EFF="E", PIPING_COMPLEXITY="", INSULATION_CONDITION="",
                 INSULATION_CHLORIDE=False,
                 MATERIAL_SUSCEP_HTHA=False, HTHA_MATERIAL="", HTHA_NUM_INSP=0, HTHA_EFFECT="E", HTHA_PRESSURE=0,
                 CRITICAL_TEMP=0, DAMAGE_FOUND=False,
                 LOWEST_TEMP=False,
                 TEMPER_SUSCEP=False, PWHT=False, BRITTLE_THICK=0, CARBON_ALLOY=False, DELTA_FATT=0,
                 MAX_OP_TEMP=0, CHROMIUM_12=False, MIN_OP_TEMP=0, MIN_DESIGN_TEMP=0, REF_TEMP=0,
                 AUSTENITIC_STEEL=False, PERCENT_SIGMA=0,
                 EquipmentType="", PREVIOUS_FAIL="", AMOUNT_SHAKING="", TIME_SHAKING="", CYLIC_LOAD="",
                 CORRECT_ACTION="", NUM_PIPE="", PIPE_CONDITION="", JOINT_TYPE="", BRANCH_DIAMETER=""):

        self.ComponentNumber = ComponentNumber
        self.CommissionDate = Commissiondate
        self.AssesmentDate = AssessmentDate
        self.APIComponentType = APIComponentType
        # Thinning input
        self.Diametter = Diametter
        self.NomalThick = NomalThick
        self.CurrentThick = CurrentThick
        self.MinThickReq = MinThickReq
        self.CorrosionRate = CorrosionRate
        self.CA = CA
        self.ProtectedBarrier = ProtectedBarrier
        self.CladdingCorrosionRate = CladdingCorrosionRate
        self.InternalCladding = InternalCladding
        self.NoINSP_THINNING = NoINSP_THINNING
        self.EFF_THIN = EFF_THIN
        self.OnlineMonitoring = OnlineMonitoring
        self.HighlyEffectDeadleg = HighlyEffectDeadleg
        self.ContainsDeadlegs = ContainsDeadlegs
        self.TankMaintain653 = TankMaintain653
        self.AdjustmentSettle = AdjustmentSettle
        self.ComponentIsWeld = ComponentIsWeld

        # Linning input
        self.LinningType = LinningType
        self.LINNER_ONLINE = LINNER_ONLINE
        self.LINNER_CONDITION = LINNER_CONDITION
        self.INTERNAL_LINNING = INTERNAL_LINNING

        # SCC Caustic input
        self.CAUSTIC_INSP_EFF = CAUSTIC_INSP_EFF
        self.CAUSTIC_INSP_NUM = CAUSTIC_INSP_NUM
        self.HEAT_TREATMENT = HEAT_TREATMENT
        self.NaOHConcentration = NaOHConcentration
        self.HEAT_TRACE = HEAT_TRACE
        self.STEAM_OUT = STEAM_OUT

        # SCC Amine input
        self.AMINE_INSP_EFF = AMINE_INSP_EFF
        self.AMINE_INSP_NUM = AMINE_INSP_NUM
        self.AMINE_EXPOSED = AMINE_EXPOSED
        self.AMINE_SOLUTION = AMINE_SOLUTION

        # Sulphide Stress Cracking input
        self.ENVIRONMENT_H2S_CONTENT = ENVIRONMENT_H2S_CONTENT
        self.AQUEOUS_OPERATOR = AQUEOUS_OPERATOR
        self.AQUEOUS_SHUTDOWN = AQUEOUS_SHUTDOWN
        self.SULPHIDE_INSP_EFF = SULPHIDE_INSP_EFF
        self.SULPHIDE_INSP_NUM = SULPHIDE_INSP_NUM
        self.H2SContent = H2SContent
        self.PH = PH
        self.PRESENT_CYANIDE = PRESENT_CYANIDE
        self.BRINNEL_HARDNESS = BRINNEL_HARDNESS

        # HIC/SOHIC H2S input
        self.SULFUR_INSP_EFF = SULFUR_INSP_EFF
        self.SULFUR_INSP_NUM = SULFUR_INSP_NUM
        self.SULFUR_CONTENT = SULFUR_CONTENT

        # Carboonate Cracking input
        self.CACBONATE_INSP_EFF = CACBONATE_INSP_EFF
        self.CACBONATE_INSP_NUM = CACBONATE_INSP_NUM
        self.CO3_CONTENT = CO3_CONTENT

        # PTA Cracking input
        self.PTA_SUSCEP = PTA_SUSCEP
        self.NICKEL_ALLOY = NICKEL_ALLOY
        self.EXPOSED_SULFUR = EXPOSED_SULFUR
        self.PTA_INSP_EFF = PTA_INSP_EFF
        self.PTA_INSP_NUM = PTA_INSP_NUM
        self.ExposedSH2OOperation = ExposedSH2OOperation
        self.ExposedSH2OShutdown = ExposedSH2OShutdown
        self.ThermalHistory = ThermalHistory
        self.PTAMaterial = PTAMaterial
        self.DOWNTIME_PROTECTED = DOWNTIME_PROTECTED

        # CLSCC input
        self.INTERNAL_EXPOSED_FLUID_MIST = INTERNAL_EXPOSED_FLUID_MIST
        self.EXTERNAL_EXPOSED_FLUID_MIST = EXTERNAL_EXPOSED_FLUID_MIST
        self.CHLORIDE_ION_CONTENT = CHLORIDE_ION_CONTENT
        self.CLSCC_INSP_EFF = CLSCC_INSP_EFF
        self.CLSCC_INSP_NUM = CLSCC_INSP_NUM

        # HFC-HS input
        self.HSC_HF_INSP_EFF = HSC_HF_INSP_EFF
        self.HSC_HF_INSP_NUM = HSC_HF_INSP_NUM

        # HICSOHIC-HF input
        self.HICSOHIC_INSP_EFF = HICSOHIC_INSP_EFF
        self.HICSOHIC_INSP_NUM = HICSOHIC_INSP_NUM
        self.HF_PRESENT = HF_PRESENT

        # EXTERNAL CORROSION input
        self.EXTERNAL_INSP_NUM = EXTERNAL_INSP_NUM
        self.EXTERNAL_INSP_EFF = EXTERNAL_INSP_EFF

        # CUI input
        self.INTERFACE_SOIL_WATER = INTERFACE_SOIL_WATER
        self.SUPPORT_COATING = SUPPORT_COATING
        self.INSULATION_TYPE = INSULATION_TYPE
        self.CUI_INSP_NUM = CUI_INSP_NUM
        self.CUI_INSP_EFF = CUI_INSP_EFF
        self.CUI_PERCENT_1 = CUI_PERCENT_1
        self.CUI_PERCENT_2 = CUI_PERCENT_2
        self.CUI_PERCENT_3 = CUI_PERCENT_3
        self.CUI_PERCENT_4 = CUI_PERCENT_4
        self.CUI_PERCENT_5 = CUI_PERCENT_5
        self.CUI_PERCENT_6 = CUI_PERCENT_6
        self.CUI_PERCENT_7 = CUI_PERCENT_7
        self.CUI_PERCENT_8 = CUI_PERCENT_8
        self.CUI_PERCENT_9 = CUI_PERCENT_9
        self.CUI_PERCENT_10 = CUI_PERCENT_10

        # EXTERNAL CLSCC input
        self.EXTERN_CLSCC_INSP_NUM = EXTERN_CLSCC_INSP_NUM
        self.EXTERN_CLSCC_INSP_EFF = EXTERN_CLSCC_INSP_EFF

        # EXTERN CUI CLSCC input
        self.EXTERNAL_INSULATION = EXTERNAL_INSULATION
        self.COMPONENT_INSTALL_DATE = COMPONENT_INSTALL_DATE
        self.CRACK_PRESENT = CRACK_PRESENT
        self.EXTERNAL_EVIRONMENT = EXTERNAL_EVIRONMENT
        self.EXTERN_COAT_QUALITY = EXTERN_COAT_QUALITY
        self.EXTERN_CLSCC_CUI_INSP_NUM = EXTERN_CLSCC_CUI_INSP_NUM
        self.EXTERN_CLSCC_CUI_INSP_EFF = EXTERN_CLSCC_CUI_INSP_EFF
        self.PIPING_COMPLEXITY = PIPING_COMPLEXITY
        self.INSULATION_CONDITION = INSULATION_CONDITION
        self.INSULATION_CHLORIDE = INSULATION_CHLORIDE
        self.EXTERN_COATING = EXTERN_COATING

        # HTHA input
        self.MATERIAL_SUSCEP_HTHA = MATERIAL_SUSCEP_HTHA
        self.HTHA_MATERIAL = HTHA_MATERIAL
        self.HTHA_NUM_INSP = HTHA_NUM_INSP
        self.HTHA_EFFECT = HTHA_EFFECT
        self.HTHA_PRESSURE = HTHA_PRESSURE
        self.CRITICAL_TEMP = CRITICAL_TEMP
        self.DAMAGE_FOUND = DAMAGE_FOUND

        # BRITTLE input
        self.LOWEST_TEMP = LOWEST_TEMP

        # TEMPER EMBRITTLE input
        self.TEMPER_SUSCEP = TEMPER_SUSCEP
        self.PWHT = PWHT
        self.BRITTLE_THICK = BRITTLE_THICK
        self.CARBON_ALLOY = CARBON_ALLOY
        self.DELTA_FATT = DELTA_FATT

        # 885 input
        self.MAX_OP_TEMP = MAX_OP_TEMP
        self.CHROMIUM_12 = CHROMIUM_12
        self.MIN_OP_TEMP = MIN_OP_TEMP
        self.MIN_DESIGN_TEMP = MIN_DESIGN_TEMP
        self.REF_TEMP = REF_TEMP

        # SIGMA input
        self.AUSTENITIC_STEEL = AUSTENITIC_STEEL
        self.PERCENT_SIGMA = PERCENT_SIGMA

        # PIPING MECHANICAL input
        self.EquipmentType = EquipmentType
        self.PREVIOUS_FAIL = PREVIOUS_FAIL
        self.AMOUNT_SHAKING = AMOUNT_SHAKING
        self.TIME_SHAKING = TIME_SHAKING
        self.CYLIC_LOAD = CYLIC_LOAD
        self.CORRECT_ACTION = CORRECT_ACTION
        self.NUM_PIPE = NUM_PIPE
        self.PIPE_CONDITION = PIPE_CONDITION
        self.JOINT_TYPE = JOINT_TYPE
        self.BRANCH_DIAMETER = BRANCH_DIAMETER

    # PoF convert cataloge
    def PoFCategory(self, DF_total):
        if DF_total <= 2:
            return "1"
        elif DF_total <= 20:
            return "2"
        elif DF_total <= 100:
            return "3"
        elif DF_total <= 1000:
            return "4"
        else:
            return "5"

    # DF LIST
    DM_Name = ["Internal Thinning", "Internal Lining Degradation", "Caustic Stress Corrosion Cracking",
               "Amine Stress Corrosion Cracking", "Sulphide Stress Corrosion Cracking (H2S)", "HIC/SOHIC-H2S",
               "Carbonate Stress Corrosion Cracking", "Polythionic Acid Stress Corrosion Cracking",
               "Chloride Stress Corrosion Cracking", "Hydrogen Stress Cracking (HF)", "HF Produced HIC/SOHIC",
               "External Corrosion", "Corrosion Under Insulation", "External Chloride Stress Corrosion Cracking",
               "Chloride Stress Corrosion Cracking Under Insulation", "High Temperature Hydrogen Attack",
               "Brittle Fracture", "Temper Embrittlement", "885F Embrittlement", "Sigma Phase Embrittlement",
               "Vibration-Induced Mechanical Fatigue"]
    # calculate Thinning Damage Factor
    def getTmin(self):
        if self.APIComponentType == "TANKBOTTOM" or self.APIComponentType =="TANKROOFFLOAT":
            if (self.ProtectedBarrier):
                t = 3.2
            else:
                t = 6.4
        else:
            t = self.MinThickReq
        return t

    def agerc(self):
        try:
            return max(abs((self.CurrentThick - self.NomalThick) / self.CorrosionRate), 0)
        except:
            return 0

    def Art(self, age):
        try:
            if self.InternalCladding:
                return max(1 - (self.CurrentThick - self.CladdingCorrosionRate * self.agerc() - self.CorrosionRate * (
                age - self.agerc())) / (self.getTmin() + self.CA), 0.0)
            else:
                return max(1 - (self.CurrentThick - self.CorrosionRate * age) / (self.getTmin() + self.CA), 0.0)
        except:
            return 1

    def API_ART(self, a):
        if self.APIComponentType == 'TANKBOTTOM' or self.APIComponentType == 'TANKROOFFLOAT':
            data = [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9,
                    0.95, 1]
            if (a < (data[0] + data[1]) / 2):
                return data[0]
            elif (a < (data[1] + data[2]) / 2):
                return data[1]
            elif (a < (data[2] + data[3]) / 2):
                return data[2]
            elif (a < (data[3] + data[4]) / 2):
                return data[3]
            elif (a < (data[4] + data[5]) / 2):
                return data[4]
            elif (a < (data[5] + data[6]) / 2):
                return data[5]
            elif (a < (data[6] + data[7]) / 2):
                return data[6]
            elif (a < (data[7] + data[8]) / 2):
                return data[7]
            elif (a < (data[8] + data[9]) / 2):
                return data[8]
            elif (a < (data[9] + data[10]) / 2):
                return data[9]
            elif (a < (data[10] + data[11]) / 2):
                return data[10]
            elif (a < (data[11] + data[12]) / 2):
                return data[11]
            elif (a < (data[12] + data[13]) / 2):
                return data[12]
            elif (a < (data[13] + data[14]) / 2):
                return data[13]
            elif (a < (data[14] + data[15]) / 2):
                return data[14]
            elif (a < (data[15] + data[16]) / 2):
                return data[15]
            elif (a < (data[16] + data[17]) / 2):
                return data[16]
            elif (a < (data[17] + data[18]) / 2):
                return data[17]
            elif (a < (data[18] + data[19]) / 2):
                return data[18]
            else:
                return data[19]
        else:
            data = [0.02, 0.04, 0.06, 0.08, 0.1, 0.12, 0.14, 0.16, 0.18, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55,
                    0.6, 0.65]
            if (a < (data[0] + data[1]) / 2):
                return data[0]
            elif (a < (data[1] + data[2]) / 2):
                return data[1]
            elif (a < (data[2] + data[3]) / 2):
                return data[2]
            elif (a < (data[3] + data[4]) / 2):
                return data[3]
            elif (a < (data[4] + data[5]) / 2):
                return data[4]
            elif (a < (data[5] + data[6]) / 2):
                return data[5]
            elif (a < (data[6] + data[7]) / 2):
                return data[6]
            elif (a < (data[7] + data[8]) / 2):
                return data[7]
            elif (a < (data[8] + data[9]) / 2):
                return data[8]
            elif (a < (data[9] + data[10]) / 2):
                return data[9]
            elif (a < (data[10] + data[11]) / 2):
                return data[10]
            elif (a < (data[11] + data[12]) / 2):
                return data[11]
            elif (a < (data[12] + data[13]) / 2):
                return data[12]
            elif (a < (data[13] + data[14]) / 2):
                return data[13]
            elif (a < (data[14] + data[15]) / 2):
                return data[14]
            elif (a < (data[15] + data[16]) / 2):
                return data[15]
            elif (a < (data[16] + data[17]) / 2):
                return data[16]
            elif (a < (data[17] + data[18]) / 2):
                return data[17]
            else:
                return data[18]


    def DFB_THIN(self, age):
        self.EFF_THIN = DAL_CAL.POSTGRESQL.GET_MAX_INSP(self.ComponentNumber, self.DM_Name[0])
        self.NoINSP_THINNING = DAL_CAL.POSTGRESQL.GET_NUMBER_INSP(self.ComponentNumber,self.DM_Name[0])
        if (self.APIComponentType == 'TANKBOTTOM' or self.APIComponentType == 'TANKROOFFLOAT'):
            if (self.NomalThick == 0 or self.CurrentThick == 0):
                return 1390
            else:
                return DAL_CAL.POSTGRESQL.GET_TBL_512(self.API_ART(self.Art(age)), self.EFF_THIN)
        else:
            if (self.NomalThick == 0 or self.CurrentThick == 0):
                return 1900
            else:
                return DAL_CAL.POSTGRESQL.GET_TBL_511(self.API_ART(self.Art(age)), self.NoINSP_THINNING, self.EFF_THIN)

    def DF_THIN(self, age):
        Fwd = 1
        Fam = 1
        Fsm = 1
        if (self.HighlyEffectDeadleg):
            Fip = 3
        else:
            Fip = 1

        if (self.ContainsDeadlegs):
            Fdl = 3
        else:
            Fdl = 1

        if self.EquipmentType == "Tank":
            if (self.ComponentIsWeld):
                Fwd = 1
            else:
                Fwd = 10

            if (self.TankMaintain653):
                Fam = 1
            else:
                Fam = 5

            if (self.AdjustmentSettle == "Recorded settlement exceeds API 653 criteria"):
                Fsm = 2
            elif (self.AdjustmentSettle == "Recorded settlement meets API 653 criteria"):
                Fsm = 1
            elif (self.AdjustmentSettle == "Settlement never evaluated"):
                Fsm = 1.5
            else:
                Fsm = 1

        if (
                                                                self.OnlineMonitoring == "Amine high velocity corrosion - Electrical resistance probes" or self.OnlineMonitoring == "Amine high velocity corrosion - Key process variable" or self.OnlineMonitoring == "Amine low velocity corrosion - Electrical resistance probes" or self.OnlineMonitoring == "HCL corrosion - Electrical resistance probes" or
                                                    self.OnlineMonitoring == "HCL corrosion - Key process variable" or self.OnlineMonitoring == "HF corrosion - Key process variable" or self.OnlineMonitoring == "High temperature H2S/H2 corrosion - Electrical resistance probes" or self.OnlineMonitoring == "High temperature Sulfidic / Naphthenic acid corrosion - Electrical resistance probes" or
                                    self.OnlineMonitoring == "High temperature Sulfidic / Naphthenic acid corrosion - Key process variable" or self.OnlineMonitoring == "Sour water high velocity corrosion - Key process variable" or self.OnlineMonitoring == "Sour water low velocity corrosion - Electrical resistance probes" or self.OnlineMonitoring == "Sulfuric acid (H2S/H2) corrosion high velocity - Electrical resistance probes" or
                    self.OnlineMonitoring == "Sulfuric acid (H2S/H2) corrosion high velocity - Key process parameters" or self.OnlineMonitoring == "Sulfuric acid (H2S/H2) corrosion low velocity - Electrical resistance probes"):
            Fom = 10
        elif (
                                    self.OnlineMonitoring == "Amine low velocity corrosion - Corrosion coupons" or self.OnlineMonitoring == "HCL corrosion - Corrosion coupons" or self.OnlineMonitoring == "High temperature Sulfidic / Naphthenic acid corrosion - Corrosion coupons" or self.OnlineMonitoring == "Sour water high velocity corrosion - Corrosion coupons" or self.OnlineMonitoring == "Sour water high velocity corrosion - Electrical resistance probes" or
                    self.OnlineMonitoring == "Sour water low velocity corrosion - Corrosion coupons" or self.OnlineMonitoring == "Sulfuric acid (H2S/H2) corrosion low velocity - Corrosion coupons"):
            Fom = 2
        elif (
                            self.OnlineMonitoring == "Amine low velocity corrosion - Key process variable" or self.OnlineMonitoring == "HCL corrosion - Key process variable & Electrical resistance probes" or self.OnlineMonitoring == "Sour water low velocity corrosion - Key process variable" or self.OnlineMonitoring == "Sulfuric acid (H2S/H2) corrosion high velocity - Key process parameters & electrical resistance probes" or self.OnlineMonitoring == "Sulfuric acid(H2S / H2) corrosion low velocity - Key process parameters"):
            Fom = 20
        else:
            Fom = 1

        return self.DFB_THIN(age) * Fip * Fdl * Fwd * Fsm * Fam / Fom

    # Calculate Linning:
    def DFB_LINNING(self, age):
        if (self.LinningType == "Organic"):
            if (age <= 3):
                SUSCEP_LINNING = "WithinLast3Years"
            elif (age > 3 and age <= 6):
                SUSCEP_LINNING = "WithinLast6Years"
            else:
                SUSCEP_LINNING = "MoreThan6Years"
            #YEAR_IN_SERVICE = self.GET_AGE_INSERVICE()
            return DAL_CAL.POSTGRESQL.GET_TBL_65(int(age), SUSCEP_LINNING)
        else:
            return DAL_CAL.POSTGRESQL.GET_TBL_64(int(round(age)), self.LinningType)

    def DF_LINNING(self, age):
        if (self.INTERNAL_LINNING):
            if (self.LINNER_CONDITION == "Poor"):
                Fdl = 10
            elif (self.LINNER_CONDITION == "Average"):
                Fdl = 2
            else:
                Fdl = 1

            if (self.LINNER_ONLINE):
                Fom = 0.1
            else:
                Fom = 1
            return self.DFB_LINNING(age) * Fdl * Fom
        else:
            return 0

    # Calculate Caustic:

    def plotinArea(self):
        TempBase = -0.6*self.NaOHConcentration + 80
        if (self.MIN_OP_TEMP < TempBase):
            k = 'A'
        else:
            k = 'B'
        return k

    def getSusceptibility_Caustic(self):
        if (self.CRACK_PRESENT):
            sus = "High"
        elif (self.HEAT_TREATMENT == "Stress Relieved"):
            sus = "None"
        else:
            if (self.plotinArea() == 'A'):
                if (self.NaOHConcentration < 5):
                    if (self.HEAT_TRACE):
                        sus = "Medium"
                    elif (self.STEAM_OUT):
                        sus = "Low"
                    else:
                        sus = "None"
                elif (self.HEAT_TRACE):
                    sus = "High"
                elif (self.STEAM_OUT):
                    sus = "Medium"
                else:
                    sus = "None"
            else:
                if (self.NaOHConcentration < 5):
                    sus = "Medium"
                else:
                    sus = "High"
        return sus

    def SVI_CAUSTIC(self):
        if (self.getSusceptibility_Caustic() == "High"):
            sev = 5000
        elif (self.getSusceptibility_Caustic() == "Medium"):
            sev = 500
        elif (self.getSusceptibility_Caustic() == "Low"):
            sev = 50
        else:
            sev = 1
        return sev

    def DF_CAUSTIC(self, age):
        if (self.CARBON_ALLOY and self.NaOHConcentration != 0):
            self.CAUSTIC_INSP_EFF = DAL_CAL.POSTGRESQL.GET_MAX_INSP(self.ComponentNumber, self.DM_Name[2])
            self.CACBONATE_INSP_NUM = DAL_CAL.POSTGRESQL.GET_NUMBER_INSP(self.ComponentNumber, self.DM_Name[2])
            if (self.CAUSTIC_INSP_EFF == "E" or self.CAUSTIC_INSP_NUM == 0):
                FIELD = "E"
            else:
                FIELD = str(self.CAUSTIC_INSP_NUM) + self.CAUSTIC_INSP_EFF
            DFB_CAUSTIC = DAL_CAL.POSTGRESQL.GET_TBL_74(self.SVI_CAUSTIC(), FIELD)
            return DFB_CAUSTIC * pow(age, 1.1)
        else:
            return 0

    # Calculate SCC AMINE:
    def getSusceptibility_Amine(self):
        if (self.CRACK_PRESENT):
            sus = "High"
        elif (self.HEAT_TREATMENT == "Stress Relieved"):
            sus = "None"
        elif (not self.AMINE_EXPOSED):
            sus = "None"
        else:
            if (self.AMINE_SOLUTION == "Methyldiethanolamine MDEA" or self.AMINE_SOLUTION == "Disopropanolamine DIPA"):
                if (self.MAX_OP_TEMP > 82.22):
                    sus = "High"
                elif ((self.MAX_OP_TEMP > 37.78 and self.MAX_OP_TEMP < 82.22) or self.HEAT_TRACE or self.STEAM_OUT):
                    sus = "Medium"
                else:
                    sus = "Low"
            elif (self.AMINE_SOLUTION == "Diethanolamine DEA"):
                if (self.MAX_OP_TEMP > 82.22):
                    sus = "Medium"
                elif ((self.MAX_OP_TEMP > 60 and self.MAX_OP_TEMP < 82.22) or self.HEAT_TRACE or self.STEAM_OUT):
                    sus = "Low"
                else:
                    sus = "None"
            else:
                if (self.MAX_OP_TEMP > 82.22 or self.HEAT_TRACE or self.STEAM_OUT):
                    sus = "Low"
                else:
                    sus = "None"
        return sus

    def SVI_AMINE(self):
        if (self.getSusceptibility_Amine() == "High"):
            return 1000
        elif (self.getSusceptibility_Amine() == "Medium"):
            return 100
        elif (self.getSusceptibility_Amine() == "Low"):
            return 10
        else:
            return 1

    def DF_AMINE(self, age):
        if (self.CARBON_ALLOY):
            self.AMINE_INSP_EFF = DAL_CAL.POSTGRESQL.GET_MAX_INSP(self.ComponentNumber, self.DM_Name[3])
            self.AMINE_INSP_NUM = DAL_CAL.POSTGRESQL.GET_NUMBER_INSP(self.ComponentNumber, self.DM_Name[3])
            if (self.AMINE_INSP_EFF == "E" or self.AMINE_INSP_NUM == 0):
                FIELD = "E"
            else:
                FIELD = str(self.AMINE_INSP_NUM) + self.AMINE_INSP_EFF
            DFB_AMIN = DAL_CAL.POSTGRESQL.GET_TBL_74(self.SVI_AMINE(), FIELD)
            return DFB_AMIN * pow(age, 1.1)
        else:
            return 0

    # Calculate Sulphide Stress Cracking
    def GET_ENVIRONMENTAL_SEVERITY(self):
        if (self.PH < 5.5):
            if (self.H2SContent < 50):
                env = "Low"
            elif (self.H2SContent <= 1000):
                env = "Moderate"
            else:
                env = "High"
        elif (self.PH <= 7.5 and self.PH >= 5.5):
            if (self.H2SContent > 10000):
                env = "Moderate"
            else:
                env = "Low"
        elif (self.PH >= 7.6 and self.PH <= 8.3):
            if (self.H2SContent < 50):
                env = "Low"
            else:
                env = "Moderate"
        elif (self.PH >= 8.4 and self.PH <= 8.9):
            if (self.H2SContent < 50):
                env = "Low"
            elif (self.H2SContent <= 10000 and self.PRESENT_CYANIDE):
                env = "High"
            elif (self.H2SContent <= 10000):
                env = "Moderate"
            else:
                env = "High"
        else:
            if (self.H2SContent < 50):
                env = "Low"
            elif (self.H2SContent <= 1000):
                env = "Moderate"
            else:
                env = "High"
        return env

    def GET_SUSCEPTIBILITY_SULPHIDE(self):
        env = self.GET_ENVIRONMENTAL_SEVERITY()
        if (self.CRACK_PRESENT):
            sus = "High"
        elif (self.PWHT):
            if (self.BRINNEL_HARDNESS == "Below 200"):
                sus = "None"
            elif (self.BRINNEL_HARDNESS == "Between 200 and 237"):
                if (env == "High"):
                    sus = "Low"
                else:
                    sus = "None"
            else:
                if (env == "High"):
                    sus = "Medium"
                elif (env == "Moderate"):
                    sus = "Low"
                else:
                    sus = "None"
        else:
            if (self.BRINNEL_HARDNESS == "Below 200"):
                sus = "Low"
            elif (self.BRINNEL_HARDNESS == "Between 200 and 237"):
                if (env == "Low"):
                    sus = "Low"
                else:
                    sus = "Medium"
            else:
                if (env == "Low"):
                    sus = "Medium"
                else:
                    sus = "High"
        return sus

    def SVI_SULPHIDE(self):
        if (self.GET_SUSCEPTIBILITY_SULPHIDE() == "High"):
            return 100
        elif (self.GET_SUSCEPTIBILITY_SULPHIDE() == "Medium"):
            return 10
        else:
            return 1

    def DF_SULPHIDE(self, age):
        if (self.CARBON_ALLOY and self.AQUEOUS_OPERATOR and self.ENVIRONMENT_H2S_CONTENT):
            self.SULPHIDE_INSP_EFF = DAL_CAL.POSTGRESQL.GET_MAX_INSP(self.ComponentNumber, self.DM_Name[4])
            self.SULPHIDE_INSP_NUM = DAL_CAL.POSTGRESQL.GET_NUMBER_INSP(self.ComponentNumber,self.DM_Name[4])
            if (self.SULPHIDE_INSP_EFF == "E" or self.SULPHIDE_INSP_NUM == 0):
                FIELD = "E"
            else:
                FIELD = str(self.SULPHIDE_INSP_NUM) + self.SULPHIDE_INSP_EFF
            DFB_SULPHIDE = DAL_CAL.POSTGRESQL.GET_TBL_74(self.SVI_SULPHIDE(), FIELD)
            return DFB_SULPHIDE * pow(age, 1.1)
        else:
            return 0

    # Calculate HIC/SOHIC-H2S
    def GET_ENVIROMENTAL_HICSOHIC_H2S(self):
        if (self.PH < 5.5):
            if (self.H2SContent < 50):
                env = "Low"
            elif (self.H2SContent <= 1000):
                env = "Moderate"
            else:
                env = "High"
        elif (self.PH >= 5.5 and self.PH <= 7.5):
            if (self.H2SContent > 10000):
                env = "Moderate"
            else:
                env = "Low"
        elif (self.PH >= 7.6 and self.PH <= 8.3):
            if (self.H2SContent < 50):
                env = "Low"
            else:
                env = "Moderate"
        elif (self.PH >= 8.4 and self.PH <= 8.9):
            if (self.H2SContent < 50):
                env = "Low"
            elif (self.H2SContent <= 10000 and self.PRESENT_CYANIDE):
                env = "High"
            elif (self.H2SContent <= 10000):
                env = "Moderate"
            else:
                env = "High"
        else:
            if (self.H2SContent < 50):
                env = "Low"
            elif (self.H2SContent <= 1000):
                env = "Moderate"
            else:
                env = "High"
        return env

    def GET_SUSCEPTIBILITY_HICSOHIC_H2S(self):
        env = self.GET_ENVIROMENTAL_HICSOHIC_H2S()
        if (self.CRACK_PRESENT):
            sus = "High"
        elif (self.PWHT):
            if (self.SULFUR_CONTENT == "High > 0.01%"):
                if (env == "High"):
                    sus = "High"
                elif (env == "Moderate"):
                    sus = "Medium"
                else:
                    sus = "Low"
            elif (self.SULFUR_CONTENT == "Low 0.002 - 0.01%"):
                if (env == "High"):
                    sus = "Medium"
                else:
                    sus = "Low"
            else:
                if (env == "Low"):
                    sus = "None"
                else:
                    sus = "Low"
        else:
            if (self.SULFUR_CONTENT == "High > 0.01%"):
                if (env == "Low"):
                    sus = "Medium"
                else:
                    sus = "High"
            elif (self.SULFUR_CONTENT == "Low 0.002 - 0.01%"):
                if (env == "High"):
                    sus = "High"
                elif (env == "Moderate"):
                    sus = "Medium"
                else:
                    sus = "Low"
            else:
                if (env == "High"):
                    sus = "Medium"
                elif (env == "Moderate"):
                    sus = "Low"
                else:
                    sus = "None"
        return sus

    def SVI_HICSOHIC_H2S(self):
        if (self.GET_SUSCEPTIBILITY_HICSOHIC_H2S() == "High"):
            return 100
        elif (self.GET_SUSCEPTIBILITY_HICSOHIC_H2S() == "Medium"):
            return 10
        else:
            return 1

    def DF_HICSOHIC_H2S(self, age):
        if (self.CARBON_ALLOY and self.AQUEOUS_OPERATOR and self.ENVIRONMENT_H2S_CONTENT):
            self.SULFUR_INSP_EFF = DAL_CAL.POSTGRESQL.GET_MAX_INSP(self.ComponentNumber, self.DM_Name[5])
            self.SULFUR_INSP_NUM = DAL_CAL.POSTGRESQL.GET_NUMBER_INSP(self.ComponentNumber, self.DM_Name[5])
            if (self.SULFUR_INSP_EFF == "E" or self.SULFUR_INSP_NUM == 0):
                FIELD = "E"
            else:
                FIELD = str(self.SULPHIDE_INSP_NUM) + self.SULFUR_INSP_NUM
            DFB_SULFUR = DAL_CAL.POSTGRESQL.GET_TBL_74(self.SVI_HICSOHIC_H2S(), FIELD)
            return DFB_SULFUR * pow(age, 1.1)
        else:
            return 0

    # Calculate Cacbonate Cracking
    def GET_SUSCEPTIBILITY_CARBONATE(self):
        if (self.CRACK_PRESENT):
            sus = "High"
        else:
            if (self.CO3_CONTENT < 100):
                sus = "Low"
            elif (self.CO3_CONTENT <= 500):
                if (self.PH >= 9.0):
                    sus = "Medium"
                else:
                    sus = "Low"
            elif (self.CO3_CONTENT <= 1000):
                if (self.PH >= 9.0):
                    sus = "High"
                elif (self.PH > 8.3 and self.PH <= 9.0):
                    sus = "Medium"
                else:
                    sus = "Low"
            else:
                if (self.PH >= 7.6 and self.PH <= 8.3):
                    sus = "Medium"
                else:
                    sus = "High"
        return sus

    def SVI_CARBONATE(self):
        if (self.GET_SUSCEPTIBILITY_CARBONATE() == "High"):
            return 1000
        elif (self.GET_SUSCEPTIBILITY_CARBONATE() == "Medium"):
            return 100
        elif (self.GET_SUSCEPTIBILITY_CARBONATE() == "Low"):
            return 10
        else:
            return 1

    def DF_CACBONATE(self, age):
        if (self.CARBON_ALLOY and self.AQUEOUS_OPERATOR and self.PH >= 7.5):
            self.CACBONATE_INSP_EFF = DAL_CAL.POSTGRESQL.GET_MAX_INSP(self.ComponentNumber, self.DM_Name[6])
            self.CACBONATE_INSP_NUM = DAL_CAL.POSTGRESQL.GET_NUMBER_INSP(self.ComponentNumber, self.DM_Name[6])
            if (self.CACBONATE_INSP_EFF == "E" or self.CACBONATE_INSP_NUM == 0):
                FIELD = "E"
            else:
                FIELD = str(self.CACBONATE_INSP_NUM) + self.CACBONATE_INSP_EFF
            DFB_CACBONATE = DAL_CAL.POSTGRESQL.GET_TBL_74(self.SVI_CARBONATE(), FIELD)
            return DFB_CACBONATE * pow(age, 1.1)
        else:
            return 0

    # Calculate PTA Cracking
    def GET_SUSCEPTIBILITY_PTA(self):
        if (self.CRACK_PRESENT):
            sus = "High"
            return sus
        if (not self.ExposedSH2OOperation and not self.ExposedSH2OShutdown):
            sus = "None"
        else:
            if (self.MAX_OP_TEMP < 427):
                if (self.ThermalHistory == "Solution Annealed"):
                    if (self.PTAMaterial == "Regular 300 series Stainless Steels and Alloys 600 and 800"):
                        sus = "Medium"
                    elif (self.PTAMaterial == "H Grade 300 series Stainless Steels"):
                        sus = "High"
                    elif (self.PTAMaterial == "L Grade 300 series Stainless Steels"):
                        sus = "Low"
                    elif (self.PTAMaterial == "321 Stainless Steel"):
                        sus = "Medium"
                    elif (self.PTAMaterial == "347 Stainless Steel, Alloy 20, Alloy 625, All austenitic weld overlay"):
                        sus = "Low"
                    else:
                        sus = "None"
                elif (self.ThermalHistory == "Stabilised Before Welding"):
                    if (self.PTAMaterial == "321 Stainless Steel"):
                        sus = "Medium"
                    elif (self.PTAMaterial == "347 Stainless Steel, Alloy 20, Alloy 625, All austenitic weld overlay"):
                        sus = "Low"
                    else:
                        sus = "None"
                elif (self.ThermalHistory == "Stabilised After Welding"):
                    if (self.PTAMaterial == "321 Stainless Steel"):
                        sus = "Low"
                    elif (self.PTAMaterial == "347 Stainless Steel, Alloy 20, Alloy 625, All austenitic weld overlay"):
                        sus = "Low"
                    else:
                        sus = "None"
                else:
                    sus = "None"
            else:
                if (self.ThermalHistory == "Solution Annealed"):
                    if (self.PTAMaterial == "Regular 300 series Stainless Steels and Alloys 600 and 800"):
                        sus = "High"
                    elif (self.PTAMaterial == "H Grade 300 series Stainless Steels"):
                        sus = "High"
                    elif (self.PTAMaterial == "L Grade 300 series Stainless Steels"):
                        sus = "Medium"
                    elif (self.PTAMaterial == "321 Stainless Steel"):
                        sus = "High"
                    elif (self.PTAMaterial == "347 Stainless Steel, Alloy 20, Alloy 625, All austenitic weld overlay"):
                        sus = "Medium"
                    else:
                        sus = "None"
                elif (self.ThermalHistory == "Stabilised Before Welding"):
                    if (self.PTAMaterial == "321 Stainless Steel"):
                        sus = "High"
                    elif (self.PTAMaterial == "347 Stainless Steel, Alloy 20, Alloy 625, All austenitic weld overlay"):
                        sus = "Low"
                    else:
                        sus = "None"
                elif (self.ThermalHistory == "Stabilised After Welding"):
                    if (self.PTAMaterial == "321 Stainless Steel"):
                        sus = "Low"
                    elif (self.PTAMaterial == "347 Stainless Steel, Alloy 20, Alloy 625, All austenitic weld overlay"):
                        sus = "Low"
                    else:
                        sus = "None"
                else:
                    sus = "None"
        if (self.DOWNTIME_PROTECTED):
            if (sus == "High"):
                sus = "Medium"
            elif (sus == "Medium"):
                sus = "Low"
            else:
                sus = "None"
        return sus

    def SVI_PTA(self):
        if (self.GET_SUSCEPTIBILITY_PTA() == "High"):
            return 5000
        elif (self.GET_SUSCEPTIBILITY_PTA() == "Medium"):
            return 500
        elif (self.GET_SUSCEPTIBILITY_PTA() == "Low"):
            return 50
        else:
            return 1

    def DF_PTA(self, age):
        if (self.PTA_SUSCEP or ((self.CARBON_ALLOY or self.NICKEL_ALLOY) and self.EXPOSED_SULFUR)):
            self.PTA_INSP_EFF = DAL_CAL.POSTGRESQL.GET_MAX_INSP(self.ComponentNumber, self.DM_Name[7])
            self.PTA_INSP_NUM = DAL_CAL.POSTGRESQL.GET_NUMBER_INSP(self.ComponentNumber, self.DM_Name[7])
            if (self.PTA_INSP_EFF == "E" or self.PTA_INSP_NUM == 0):
                FIELD = "E"
            else:
                FIELD = str(self.PTA_INSP_NUM) + self.PTA_INSP_EFF
            DFB_PTA = DAL_CAL.POSTGRESQL.GET_TBL_74(self.SVI_PTA(), FIELD)
            return DFB_PTA * pow(age, 1.1)
        else:
            return 0

    # Calculate CLSCC
    def GET_SUSCEPTIBILITY_CLSCC(self):
        if (self.CRACK_PRESENT):
            sus = "High"
            return sus
        if (self.PH > 10):
            if (self.MAX_OP_TEMP >= 93 and self.MAX_OP_TEMP <= 149 and self.CHLORIDE_ION_CONTENT > 1000):
                sus = "Medium"
            else:
                sus = "Low"
        else:
            if (self.MAX_OP_TEMP <= 66 and self.MAX_OP_TEMP > 38):
                if (self.CHLORIDE_ION_CONTENT <= 10):
                    sus = "Low"
                elif (self.CHLORIDE_ION_CONTENT <= 1000):
                    sus = "Medium"
                else:
                    sus = "High"
            elif (self.MAX_OP_TEMP <= 93 and self.MAX_OP_TEMP > 66):
                if (self.CHLORIDE_ION_CONTENT <= 100):
                    sus = "Medium"
                else:
                    sus = "High"
            elif (self.MAX_OP_TEMP > 93 and self.MAX_OP_TEMP <= 149):
                if (self.CHLORIDE_ION_CONTENT < 10):
                    sus = "Medium"
                else:
                    sus = "High"
            else:
                sus = "None"
        return sus

    def SVI_CLSCC(self):
        if (self.GET_SUSCEPTIBILITY_CLSCC() == "High"):
            return 5000
        elif (self.GET_SUSCEPTIBILITY_CLSCC() == "Medium"):
            return 500
        elif (self.GET_SUSCEPTIBILITY_CLSCC() == "Low"):
            return 50
        else:
            return 1

    def DF_CLSCC(self, age):
        if (self.INTERNAL_EXPOSED_FLUID_MIST and self.AUSTENITIC_STEEL and self.MAX_OP_TEMP > 38):
            self.CLSCC_INSP_EFF = DAL_CAL.POSTGRESQL.GET_MAX_INSP(self.ComponentNumber, self.DM_Name[8])
            self.CLSCC_INSP_NUM = DAL_CAL.POSTGRESQL.GET_NUMBER_INSP(self.ComponentNumber, self.DM_Name[8])
            if (self.CLSCC_INSP_EFF == "E" or self.CLSCC_INSP_NUM == 0):
                FIELD = "E"
            else:
                FIELD = str(self.CLSCC_INSP_NUM) + self.CLSCC_INSP_EFF
            DFB_CLSCC = DAL_CAL.POSTGRESQL.GET_TBL_74(self.SVI_CLSCC(), FIELD)
            return DFB_CLSCC * pow(age, 1.1)
        else:
            return 0

    # Calculate HSC-HF
    def GET_SUSCEPTIBILITY_HSCHF(self):
        if (self.CRACK_PRESENT):
            sus = "High"
            return sus
        if (not self.HF_PRESENT or not self.CARBON_ALLOY):
            sus = "None"
        else:
            if (self.PWHT):
                if (self.BRINNEL_HARDNESS == "Below 200"):
                    sus = "None"
                elif (self.BRINNEL_HARDNESS == "Between 200 and 237"):
                    sus = "Low"
                else:
                    sus = "High"
            else:
                if (self.BRINNEL_HARDNESS == "Below 200"):
                    sus = "Low"
                elif (self.BRINNEL_HARDNESS == "Between 200 and 237"):
                    sus = "Medium"
                else:
                    sus = "High"
        return sus

    def SVI_HSCHF(self):
        if (self.GET_SUSCEPTIBILITY_HSCHF() == "High"):
            return 100
        elif (self.GET_SUSCEPTIBILITY_HSCHF() == "Medium"):
            return 10
        else:
            return 1

    def DF_HSCHF(self, age):
        if (self.CARBON_ALLOY and self.HF_PRESENT):
            self.HSC_HF_INSP_EFF = DAL_CAL.POSTGRESQL.GET_MAX_INSP(self.ComponentNumber, self.DM_Name[9])
            self.HSC_HF_INSP_NUM = DAL_CAL.POSTGRESQL.GET_NUMBER_INSP(self.ComponentNumber, self.DM_Name[9])
            if (self.HSC_HF_INSP_EFF == "E" or self.HSC_HF_INSP_NUM == 0):
                FIELD = "E"
            else:
                FIELD = str(self.HSC_HF_INSP_NUM) + self.HSC_HF_INSP_EFF
            DFB_HSCHF = DAL_CAL.POSTGRESQL.GET_TBL_74(self.SVI_HSCHF(), FIELD)
            return DFB_HSCHF * pow(age, 1.1)
        else:
            return 0

    # Calculate HICSOHIC-HF
    def GET_SUSCEPTIBILITY_HICSOHIC_HF(self):
        if (self.CRACK_PRESENT):
            return "High"
        if (not self.HF_PRESENT or not self.CARBON_ALLOY):
            return "None"
        if (self.PWHT):
            if (self.SULFUR_CONTENT == "High > 0.01%"):
                sus = "High"
            elif (self.SULFUR_CONTENT == "Low 0.002 - 0.01%"):
                sus = "Medium"
            else:
                sus = "Low"
        else:
            if (self.SULFUR_CONTENT == "High > 0.01%" or self.SULFUR_CONTENT == "Low 0.002 - 0.01%"):
                sus = "High"
            else:
                sus = "Medium"
        return sus

    def SVI_HICSOHIC_HF(self):
        if (self.GET_SUSCEPTIBILITY_HICSOHIC_HF() == "High"):
            return 100
        elif (self.GET_SUSCEPTIBILITY_HICSOHIC_HF() == "Medium"):
            return 10
        else:
            return 1

    def DF_HIC_SOHIC_HF(self, age):
        if (self.CARBON_ALLOY and self.HF_PRESENT):
            self.HICSOHIC_INSP_EFF = DAL_CAL.POSTGRESQL.GET_MAX_INSP(self.ComponentNumber, self.DM_Name[10])
            self.HICSOHIC_INSP_NUM = DAL_CAL.POSTGRESQL.GET_NUMBER_INSP(self.ComponentNumber, self.DM_Name[10])
            if (self.HICSOHIC_INSP_EFF == "E" or self.HICSOHIC_INSP_NUM == 0):
                FIELD = "E"
            else:
                FIELD = str(self.HICSOHIC_INSP_NUM) + self.HICSOHIC_INSP_EFF
            DFB_HICSOHIC_HF = DAL_CAL.POSTGRESQL.GET_TBL_74(self.SVI_HICSOHIC_HF(), FIELD)
            return DFB_HICSOHIC_HF * pow(age, 1.1)
        else:
            return 0

    # Calculate EXTERNAL CORROSION
    def AGE_CLSCC(self):
        if (self.EXTERN_COAT_QUALITY == "High coating quality"):
            AGE_COAT = self.COMPONENT_INSTALL_DATE + relativedelta(years=+15)  # Age + 15
        elif (self.EXTERN_COAT_QUALITY == "Medium coating quality"):
            AGE_COAT = self.COMPONENT_INSTALL_DATE + relativedelta(years=+5)  # Age + 5
        else:
            AGE_COAT = self.COMPONENT_INSTALL_DATE
        TICK_SPAN = abs((self.AssesmentDate.date() - AGE_COAT.date()).days)
        return TICK_SPAN / 365

    def AGE_CUI(self, age):
        return min(self.AGE_CLSCC(), age)

    def API_EXTERNAL_CORROSION_TEMP(self):
        data = [-12, -8, 6, 32, 71, 107, 121, 121, 121, 121]
        list = [self.CUI_PERCENT_1, self.CUI_PERCENT_2, self.CUI_PERCENT_3, self.CUI_PERCENT_4, self.CUI_PERCENT_5,
                self.CUI_PERCENT_6, self.CUI_PERCENT_7, self.CUI_PERCENT_8, self.CUI_PERCENT_9, self.CUI_PERCENT_10]
        return data[list.index(max(list))]

    def API_EXTERNAL_CORROSION_RATE(self):
        EXTERNAL_TEMP = self.API_EXTERNAL_CORROSION_TEMP()
        if (self.EXTERNAL_EVIRONMENT == "Arid/dry"):
            if (EXTERNAL_TEMP == -12 or EXTERNAL_TEMP == -8 or EXTERNAL_TEMP == 107 or EXTERNAL_TEMP == 121):
                CR_EXTERN = 0
            else:
                CR_EXTERN = 0.025
        elif (self.EXTERNAL_EVIRONMENT == "Marine"):
            if (EXTERNAL_TEMP == -12 or EXTERNAL_TEMP == 121):
                CR_EXTERN = 0
            elif (EXTERNAL_TEMP == -8 or EXTERNAL_TEMP == 107):
                CR_EXTERN = 0.025
            else:
                CR_EXTERN = 0.127
        elif (self.EXTERNAL_EVIRONMENT == "Severe"):
            if (EXTERNAL_TEMP == -12 or EXTERNAL_TEMP == -8 or EXTERNAL_TEMP == 121):
                CR_EXTERN = 0
            elif (EXTERNAL_TEMP == 6 or EXTERNAL_TEMP == 32 or EXTERNAL_TEMP == 71):
                CR_EXTERN = 0.254
            else:
                CR_EXTERN = 0.051
        elif (self.EXTERNAL_EVIRONMENT == "Temperate"):
            if (EXTERNAL_TEMP == -12 or EXTERNAL_TEMP == -8 or EXTERNAL_TEMP == 121 or EXTERNAL_TEMP == 107):
                CR_EXTERN = 0
            elif (EXTERNAL_TEMP == 6 or EXTERNAL_TEMP == 32):
                CR_EXTERN = 0.076
            else:
                CR_EXTERN = 0.051
        else:
            CR_EXTERN = 0
        return CR_EXTERN

    def API_ART_EXTERNAL(self, age):
        if (self.SUPPORT_COATING):
            FPS = 2
        else:
            FPS = 1
        if (self.INTERFACE_SOIL_WATER):
            FIP = 2
        else:
            FIP = 1
        CR = self.API_EXTERNAL_CORROSION_RATE() * max(FPS, FIP)
        try:
            ART_EXT = max(1 - (self.CurrentThick - CR * self.AGE_CUI(age)) / (self.getTmin() + self.CA), 0)
        except:
            ART_EXT = 1
        return self.API_ART(ART_EXT)

    def DF_EXTERNAL_CORROSION(self, age):
        if (self.EXTERNAL_EXPOSED_FLUID_MIST or (
            self.CARBON_ALLOY and not (self.MAX_OP_TEMP < -23 or self.MIN_OP_TEMP > 121))):
            self.EXTERNAL_INSP_EFF = DAL_CAL.POSTGRESQL.GET_MAX_INSP(self.ComponentNumber, self.DM_Name[11])
            self.EXTERNAL_INSP_NUM = DAL_CAL.POSTGRESQL.GET_NUMBER_INSP(self.ComponentNumber, self.DM_Name[11])
            if (self.EXTERNAL_INSP_EFF == "" or self.EXTERNAL_INSP_NUM == 0):
                self.EXTERNAL_INSP_EFF = "E"
            if (self.APIComponentType == "TANKBOTTOM" or self.APIComponentType == "TANKROOFFLOAT"):
                if (self.NomalThick == 0 or self.CurrentThick == 0):
                    return 1390
                else:
                    return DAL_CAL.POSTGRESQL.GET_TBL_512(self.API_ART_EXTERNAL(age), self.EXTERNAL_INSP_EFF)
            else:
                if (self.NomalThick == 0 or self.CurrentThick == 0):
                    return 1900
                else:
                    return DAL_CAL.POSTGRESQL.GET_TBL_511(self.API_ART_EXTERNAL(age), self.EXTERNAL_INSP_NUM,
                                                         self.EXTERNAL_INSP_EFF)
        else:
            return 0

    # Calculate CUI
    def API_CUI_TEMP(self):
        data = [-12, -8, 6, 32, 71, 107, 107, 135, 162, 176]
        list = [self.CUI_PERCENT_1, self.CUI_PERCENT_2, self.CUI_PERCENT_3, self.CUI_PERCENT_4, self.CUI_PERCENT_5,
                self.CUI_PERCENT_6, self.CUI_PERCENT_7, self.CUI_PERCENT_8, self.CUI_PERCENT_9, self.CUI_PERCENT_10]
        return data[list.index(max(list))]

    def API_CORROSION_RATE(self):
        CUI_TEMP = self.API_CUI_TEMP()
        if (self.EXTERNAL_EVIRONMENT == "Arid/dry"):
            if (CUI_TEMP == -12 or CUI_TEMP == -8 or CUI_TEMP == 135 or CUI_TEMP == 162 or CUI_TEMP == 176):
                CR_CUI = 0
            elif (CUI_TEMP == 6 or CUI_TEMP == 32 or CUI_TEMP == 107):
                CR_CUI = 0.025
            else:
                CR_CUI = 0.051
        elif (self.EXTERNAL_EVIRONMENT == "Marine"):
            if (CUI_TEMP == -12 or CUI_TEMP == 176):
                CR_CUI = 0
            elif (CUI_TEMP == -8 or CUI_TEMP == 162):
                CR_CUI = 0.025
            elif (CUI_TEMP == 6 or CUI_TEMP == 32 or CUI_TEMP == 107):
                CR_CUI = 0.127
            elif (CUI_TEMP == 135):
                CR_CUI = 0.051
            else:
                CR_CUI = 0.254
        elif (self.EXTERNAL_EVIRONMENT == "Severe"):
            if (CUI_TEMP == -12 or CUI_TEMP == 176):
                CR_CUI = 0
            elif (CUI_TEMP == -8):
                CR_CUI = 0.076
            elif (CUI_TEMP == 162):
                CR_CUI = 0.127
            elif (CUI_TEMP == 6 or CUI_TEMP == 32 or CUI_TEMP == 107 or CUI_TEMP == 135):
                CR_CUI = 0.254
            else:
                CR_CUI = 0.508
        elif (self.EXTERNAL_EVIRONMENT == "Temperate"):
            if (CUI_TEMP == -12 or CUI_TEMP == -8 or CUI_TEMP == 162 or CUI_TEMP == 176):
                CR_CUI = 0
            elif (CUI_TEMP == 107 or CUI_TEMP == 135):
                CR_CUI = 0.025
            elif (CUI_TEMP == 6 or CUI_TEMP == 32):
                CR_CUI = 0.076
            else:
                CR_CUI = 0.127
        else:
            CR_CUI = 0
        return CR_CUI

    def API_ART_CUI(self, age):
        if (
                        self.INSULATION_TYPE == "Asbestos" or self.INSULATION_TYPE == "Calcium Silicate" or self.INSULATION_TYPE == "Mineral Wool" or self.INSULATION_TYPE == "Fibreglass"):
            FIN = 1.25
        elif (self.INSULATION_TYPE == "Foam Glass"):
            FIN = 0.75
        else:
            FIN = 1

        if (self.PIPING_COMPLEXITY == "Below average"):
            FCM = 0.75
        elif (self.PIPING_COMPLEXITY == "Above average"):
            FCM = 1.75
        else:
            FCM = 1

        if (self.INSULATION_CONDITION == "Below average"):
            FIC = 1.25
        elif (self.INSULATION_CONDITION == "Above average"):
            FIC = 0.75
        else:
            FIC = 1

        if (self.SUPPORT_COATING):
            FPS = 2
        else:
            FPS = 1

        if (self.INTERFACE_SOIL_WATER):
            FIP = 2
        else:
            FIP = 1

        CR = self.API_CORROSION_RATE() * FIN * FCM * FIC * max(FPS, FIP)
        try:
            ART_CUI = max(1 - (self.CurrentThick - CR * self.AGE_CUI(age)) / (self.getTmin() + self.CA), 0)
        except:
            ART_CUI = 1
        return self.API_ART(ART_CUI)

    def DF_CUI(self, age):
        if (self.EXTERNAL_EXPOSED_FLUID_MIST or (
                    self.CARBON_ALLOY and not (self.MAX_OP_TEMP < -12 or self.MIN_OP_TEMP > 177))):
            self.CUI_INSP_EFF = DAL_CAL.POSTGRESQL.GET_MAX_INSP(self.ComponentNumber, self.DM_Name[12])
            self.CUI_INSP_NUM = DAL_CAL.POSTGRESQL.GET_NUMBER_INSP(self.ComponentNumber, self.DM_Name[12])
            if (self.CUI_INSP_EFF == "" or self.CUI_INSP_NUM == 0):
                self.CUI_INSP_EFF = "E"
            if (self.APIComponentType == "TANKBOTTOM" or self.APIComponentType == "TANKROOFFLOAT"):
                if (self.NomalThick == 0 or self.CurrentThick == 0):
                    return 1390
                else:
                    return DAL_CAL.POSTGRESQL.GET_TBL_512(self.API_ART_CUI(age), self.CUI_INSP_EFF)
            else:
                if (self.NomalThick == 0 or self.CurrentThick == 0):
                    return 1900
                else:
                    return DAL_CAL.POSTGRESQL.GET_TBL_511(self.API_ART_CUI(age), self.CUI_INSP_NUM, self.CUI_INSP_EFF)
        else:
            return 0

    # cal EXTERNAL CLSCC
    def CLSCC_SUSCEP(self):
        if (self.CRACK_PRESENT):
            sus = "High"
        else:
            if (self.EXTERNAL_EVIRONMENT == "Arid/dry"):
                sus = "Not"
            elif (self.EXTERNAL_EVIRONMENT == "Marine"):
                if (self.MAX_OP_TEMP < 49 or self.MAX_OP_TEMP > 149):
                    sus = "Not"
                elif (self.MAX_OP_TEMP >= 49 and self.MAX_OP_TEMP < 93):
                    sus = "Medium"
                else:
                    sus = "Low"
            elif (self.EXTERNAL_EVIRONMENT == "Severe"):
                if (self.MAX_OP_TEMP < 49 or self.MAX_OP_TEMP > 149):
                    sus = "Not"
                elif (self.MAX_OP_TEMP >= 49 and self.MAX_OP_TEMP < 93):
                    sus = "High"
                else:
                    sus = "Medium"
            elif (self.EXTERNAL_EVIRONMENT == "Temperate"):
                if (self.MAX_OP_TEMP < 49 or self.MAX_OP_TEMP > 149):
                    sus = "Not"
                else:
                    sus = "Low"
            else:
                sus = "Not"
        return sus

    def DFB_EXTERN_CLSCC(self):
        sus = self.CLSCC_SUSCEP()
        if (sus == "High"):
            SVI = 50
        elif (sus == "Medium"):
            SVI = 10
        else:
            SVI = 1
        self.EXTERN_CLSCC_INSP_EFF = DAL_CAL.POSTGRESQL.GET_MAX_INSP(self.ComponentNumber, self.DM_Name[13])
        self.EXTERN_CLSCC_INSP_NUM = DAL_CAL.POSTGRESQL.GET_NUMBER_INSP(self.ComponentNumber, self.DM_Name[14])
        if (self.EXTERN_CLSCC_INSP_EFF == "E" or self.EXTERN_CLSCC_INSP_NUM == 0):
            FIELD = "E"
        else:
            FIELD = str(self.EXTERN_CLSCC_INSP_NUM) + self.EXTERN_CLSCC_INSP_EFF
        return DAL_CAL.POSTGRESQL.GET_TBL_74(SVI, FIELD)

    def DF_EXTERN_CLSCC(self):
        if (self.AUSTENITIC_STEEL and self.EXTERNAL_EXPOSED_FLUID_MIST and not (
                self.MAX_OP_TEMP < 49 or self.MIN_DESIGN_TEMP > 149)):
            return self.DFB_EXTERN_CLSCC() * pow(self.AGE_CLSCC(), 1.1)
        else:
            return 0

    # Calculate EXTERN CUI CLSCC
    def CUI_CLSCC_SUSCEP(self):
        if (self.CRACK_PRESENT):
            sus = "High"
        else:
            if (self.EXTERNAL_EVIRONMENT == "Arid/dry"):
                if (self.MAX_OP_TEMP >= 49 and self.MAX_OP_TEMP < 93):
                    sus = "Low"
                else:
                    sus = "Not"
            elif (self.EXTERNAL_EVIRONMENT == "Marine"):
                if (self.MAX_OP_TEMP < 49 or self.MAX_OP_TEMP > 149):
                    sus = "Not"
                elif (self.MAX_OP_TEMP >= 49 and self.MAX_OP_TEMP < 93):
                    sus = "High"
                else:
                    sus = "Medium"
            elif (self.EXTERNAL_EVIRONMENT == "Severe"):
                if (self.MAX_OP_TEMP < 49 or self.MAX_OP_TEMP > 149):
                    sus = "Not"
                else:
                    sus = "High"
            elif (self.EXTERNAL_EVIRONMENT == "Temperate"):
                if (self.MAX_OP_TEMP < 49 or self.MAX_OP_TEMP > 149):
                    sus = "Not"
                elif (self.MAX_OP_TEMP >= 49 and self.MAX_OP_TEMP < 93):
                    sus = "Medium"
                else:
                    sus = "Low"
            else:
                sus = "Not"
        return sus

    def ADJUST_COMPLEXITY(self):
        SCP = self.CUI_CLSCC_SUSCEP()
        if (SCP == "High"):
            if (self.PIPING_COMPLEXITY == "Below average"):
                SCP = "Medium"
            else:
                SCP = "High"
        elif (SCP == "Medium"):
            if (self.PIPING_COMPLEXITY == "Below average"):
                SCP = "Low"
            elif (self.PIPING_COMPLEXITY == "Above average"):
                SCP = "High"
            else:
                SCP = "Medium"
        else:
            if (self.PIPING_COMPLEXITY == "Above average"):
                SCP = "Medium"
            else:
                SCP = "Low"
        return SCP

    def ADJUST_ISULATION(self):
        SCP = self.ADJUST_COMPLEXITY()
        if (SCP == "High"):
            if (self.INSULATION_CONDITION == "Above average"):
                SCP = "Medium"
            else:
                SCP = "High"
        elif (SCP == "Medium"):
            if (self.INSULATION_CONDITION == "Above average"):
                SCP = "Low"
            elif (self.INSULATION_CONDITION == "Below average"):
                SCP = "High"
            else:
                SCP = "Medium"
        else:
            if (self.INSULATION_CONDITION == "Below average"):
                SCP = "Medium"
            else:
                SCP = "Low"
        return SCP

    def ADJUST_CHLORIDE_INSULATION(self):
        SCP = self.ADJUST_ISULATION()
        if (self.INSULATION_CHLORIDE):
            if (SCP == "High"):
                SCP = "Medium"
            elif (SCP == "Medium"):
                SCP = "Low"
            else:
                SCP = "Low"
        else:
            SCP = self.ADJUST_ISULATION()
        return SCP

    def DFB_CUI_CLSCC(self):
        SCP = self.ADJUST_CHLORIDE_INSULATION()
        if (SCP == "High"):
            SVI = 50
        elif (SCP == "Medium"):
            SVI = 10
        else:
            SVI = 1
        self.EXTERN_CLSCC_CUI_INSP_EFF = DAL_CAL.POSTGRESQL.GET_MAX_INSP(self.ComponentNumber, self.DM_Name[14])
        self.EXTERN_CLSCC_CUI_INSP_NUM = DAL_CAL.POSTGRESQL.GET_NUMBER_INSP(self.ComponentNumber, self.DM_Name[14])

        if (self.EXTERN_CLSCC_CUI_INSP_EFF == "E" or self.EXTERN_CLSCC_CUI_INSP_NUM == 0):
            FIELD = "E"
        else:
            FIELD = str(self.EXTERN_CLSCC_CUI_INSP_NUM) + self.EXTERN_CLSCC_CUI_INSP_EFF
        return DAL_CAL.POSTGRESQL.GET_TBL_74(SVI, FIELD)

    def DF_CUI_CLSCC(self):
        if not self.EXTERN_COATING:
            return 0
        if (self.AUSTENITIC_STEEL and self.EXTERNAL_INSULATION and self.EXTERNAL_EXPOSED_FLUID_MIST and not (
                self.MIN_OP_TEMP > 150 or self.MAX_OP_TEMP < 50)):
            return self.DFB_CUI_CLSCC() * pow(self.AGE_CLSCC(), 1.1)
        else:
            return 0

    # Calculate HTHA
    def HTHA_PV(self, age):
        try:
            HTHA_AGE = age * 24 * 365
            log1 = math.log10(self.HTHA_PRESSURE / 0.0979)
            log2 = 3.09 * pow(10, -4) * (self.CRITICAL_TEMP + 273) * (math.log10(HTHA_AGE) + 14)
            return log1 + log2
        except:
            return 0

    def HTHA_SUSCEP(self, age):
        PV = self.HTHA_PV(age)
        if (self.HTHA_PRESSURE > 8.274):
            self.HTHA_MATERIAL = "1.25Cr-0.5Mo"
        if (self.HTHA_MATERIAL == "Carbon Steel"):
            if (PV > 4.7):
                SUSCEP = "High"
            elif (PV > 4.61 and PV <= 4.7):
                SUSCEP = "Medium"
            elif (PV > 4.53 and PV <= 4.61):
                SUSCEP = "Low"
            else:
                SUSCEP = "Not"
        elif (self.HTHA_MATERIAL == "C-0.5Mo (Annealed)"):
            if (PV > 4.95):
                SUSCEP = "High"
            elif (PV > 4.87 and PV <= 4.95):
                SUSCEP = "Medium"
            elif (PV > 4.78 and PV <= 4.87):
                SUSCEP = "Low"
            else:
                SUSCEP = "Not"
        elif (self.HTHA_MATERIAL == "C-0.5Mo (Normalised)"):
            if (PV > 5.6):
                SUSCEP = "High"
            elif (PV > 5.51 and PV <= 5.6):
                SUSCEP = "Medium"
            elif (PV > 5.43 and PV <= 5.51):
                SUSCEP = "Low"
            else:
                SUSCEP = "Not"
        elif (self.HTHA_MATERIAL == "1Cr-0.5Mo"):
            if (PV > 5.8):
                SUSCEP = "High"
            elif (PV > 5.71 and PV <= 5.8):
                SUSCEP = "Medium"
            elif (PV > 5.63 and PV <= 5.71):
                SUSCEP = "Low"
            else:
                SUSCEP = "Not"
        elif (self.HTHA_MATERIAL == "1.25Cr-0.5Mo"):
            if (PV > 6.0):
                SUSCEP = "High"
            elif (PV > 5.92 and PV <= 6.0):
                SUSCEP = "Medium"
            elif (PV > 5.83 and PV <= 5.92):
                SUSCEP = "Low"
            else:
                SUSCEP = "Not"
        elif (self.HTHA_MATERIAL == "2.25Cr-1Mo"):
            if (PV > 6.53):
                SUSCEP = "High"
            elif (PV > 6.45 and PV <= 6.53):
                SUSCEP = "Medium"
            elif (PV > 6.36 and PV <= 6.45):
                SUSCEP = "Low"
            else:
                SUSCEP = "Not"
        else:
            SUSCEP = "Not"
        return SUSCEP

    def API_DF_HTHA(self, age):
        API_HTHA = DAL_CAL.POSTGRESQL.GET_TBL_204(self.HTHA_SUSCEP(age))
        self.HTHA_EFFECT = DAL_CAL.POSTGRESQL.GET_MAX_INSP(self.ComponentNumber, self.DM_Name[15])
        self.HTHA_NUM_INSP = DAL_CAL.POSTGRESQL.GET_NUMBER_INSP(self.ComponentNumber, self.DM_Name[15])
        if self.HTHA_NUM_INSP > 2:
            self.HTHA_NUM_INSP = 2

        if (self.DAMAGE_FOUND):
            return 2000
        else:
            if (self.HTHA_NUM_INSP == 0):
                return API_HTHA[0]
            elif (self.HTHA_NUM_INSP == 1 and self.HTHA_EFFECT == "D"):
                return API_HTHA[1]
            elif (self.HTHA_NUM_INSP == 1 and self.HTHA_EFFECT == "C"):
                return API_HTHA[2]
            elif (self.HTHA_NUM_INSP == 1 and self.HTHA_EFFECT == "B"):
                return API_HTHA[3]
            elif (self.HTHA_NUM_INSP == 2 and self.HTHA_EFFECT == "D"):
                return API_HTHA[4]
            elif (self.HTHA_NUM_INSP == 2 and self.HTHA_EFFECT == "C"):
                return API_HTHA[5]
            else:
                return API_HTHA[6]

    def DF_HTHA(self, age):
        if (self.MATERIAL_SUSCEP_HTHA):
            if (self.MAX_OP_TEMP <= 204 and self.HTHA_PRESSURE <= 0.552):
                return 1
            else:
                return self.API_DF_HTHA(age)
        else:
            return 0

    # Calculate BRITTLE
    def DFB_BRIITLE(self):
        TEMP_BRITTLE = min(self.MIN_DESIGN_TEMP, self.MIN_OP_TEMP)
        if (self.PWHT):
            return DAL_CAL.POSTGRESQL.GET_TBL_215(self.API_TEMP(TEMP_BRITTLE - self.REF_TEMP),
                                                 self.API_SIZE_BRITTLE(self.BRITTLE_THICK))
        else:
            return DAL_CAL.POSTGRESQL.GET_TBL_214(self.API_TEMP(TEMP_BRITTLE - self.REF_TEMP),
                                                 self.API_SIZE_BRITTLE(self.BRITTLE_THICK))

    def DF_BRITTLE(self):
        if (self.CARBON_ALLOY and (
                self.CRITICAL_TEMP < self.MIN_DESIGN_TEMP or self.MAX_OP_TEMP < self.MIN_DESIGN_TEMP)):
            if (self.LOWEST_TEMP):
                return self.DFB_BRIITLE() * 0.01
            else:
                return self.DFB_BRIITLE()
        else:
            return 0

    # Calculate TEMP EMBRITTLE
    def API_SIZE_BRITTLE(self, SIZE):
        data = [6.4, 12.7, 25.4, 38.1, 50.8, 63.5, 76.2, 88.9, 101.6]
        if (SIZE < (data[0] + data[1]) / 2):
            return data[0]
        elif (SIZE < (data[1] + data[2]) / 2):
            return data[1]
        elif (SIZE < (data[2] + data[3]) / 2):
            return data[2]
        elif (SIZE < (data[3] + data[4]) / 2):
            return data[3]
        elif (SIZE < (data[4] + data[5]) / 2):
            return data[4]
        elif (SIZE < (data[5] + data[6]) / 2):
            return data[5]
        elif (SIZE < (data[6] + data[7]) / 2):
            return data[6]
        elif (SIZE < (data[7] + data[8]) / 2):
            return data[7]
        else:
            return data[8]

    def API_TEMP(self, TEMP):
        data = [-73, -62, -51, -40, -29, -18, -7, 4, 16, 27, 38]
        if (TEMP < (data[0] + data[1]) / 2):
            return data[0]
        elif (TEMP < (data[1] + data[2]) / 2):
            return data[1]
        elif (TEMP < (data[2] + data[3]) / 2):
            return data[2]
        elif (TEMP < (data[3] + data[4]) / 2):
            return data[3]
        elif (TEMP < (data[4] + data[5]) / 2):
            return data[4]
        elif (TEMP < (data[5] + data[6]) / 2):
            return data[5]
        elif (TEMP < (data[6] + data[7]) / 2):
            return data[6]
        elif (TEMP < (data[7] + data[8]) / 2):
            return data[7]
        elif (TEMP < (data[8] + data[9]) / 2):
            return data[8]
        elif (TEMP < (data[9] + data[10]) / 2):
            return data[9]
        else:
            return data[10]

    def DF_TEMP_EMBRITTLE(self):
        if (self.TEMPER_SUSCEP or (self.CARBON_ALLOY and not (self.MAX_OP_TEMP < 343 or self.MIN_OP_TEMP > 577))):
            TEMP_EMBRITTLE = min(self.MIN_DESIGN_TEMP, self.MIN_OP_TEMP) - (self.REF_TEMP + self.DELTA_FATT)
            if (self.PWHT):
                return DAL_CAL.POSTGRESQL.GET_TBL_215(self.API_TEMP(TEMP_EMBRITTLE),
                                                     self.API_SIZE_BRITTLE(self.BRITTLE_THICK))
            else:
                return DAL_CAL.POSTGRESQL.GET_TBL_214(self.API_TEMP(TEMP_EMBRITTLE),
                                                     self.API_SIZE_BRITTLE(self.BRITTLE_THICK))
        else:
            return 0

    # Calculate 885
    def DF_885(self):
        if (self.CHROMIUM_12 and not (self.MIN_OP_TEMP > 566 or self.MAX_OP_TEMP < 371)):
            TEMP_885 = min(self.MIN_DESIGN_TEMP, self.MIN_OP_TEMP) - self.REF_TEMP
            data = [-73, -62, -51, -40, -29, -18, -7, 4, 16, 27, 38]
            if (TEMP_885 < (data[0] + data[1]) / 2):
                return 1381
            elif (TEMP_885 < (data[1] + data[2]) / 2):
                return 1216
            elif (TEMP_885 < (data[2] + data[3]) / 2):
                return 1022
            elif (TEMP_885 < (data[3] + data[4]) / 2):
                return 806
            elif (TEMP_885 < (data[4] + data[5]) / 2):
                return 581
            elif (TEMP_885 < (data[5] + data[6]) / 2):
                return 371
            elif (TEMP_885 < (data[6] + data[7]) / 2):
                return 200
            elif (TEMP_885 < (data[7] + data[8]) / 2):
                return 87
            elif (TEMP_885 < (data[8] + data[9]) / 2):
                return 30
            elif (TEMP_885 < (data[9] + data[10]) / 2):
                return 8
            else:
                return 2
        else:
            return 0

    # Calculate SIGMA
    def API_TEMP_SIGMA(self):
        DATA = [-46, -18, 10, 38, 66, 93, 204, 316, 427, 538, 649]
        if (self.MIN_OP_TEMP < (DATA[0] + DATA[1]) / 2):
            TEMP = DATA[0]
        elif (self.MIN_OP_TEMP < (DATA[1] + DATA[2]) / 2):
            TEMP = DATA[1]
        elif (self.MIN_OP_TEMP < (DATA[2] + DATA[3]) / 2):
            TEMP = DATA[2]
        elif (self.MIN_OP_TEMP < (DATA[3] + DATA[4]) / 2):
            TEMP = DATA[3]
        elif (self.MIN_OP_TEMP < (DATA[4] + DATA[5]) / 2):
            TEMP = DATA[4]
        elif (self.MIN_OP_TEMP < (DATA[5] + DATA[6]) / 2):
            TEMP = DATA[5]
        elif (self.MIN_OP_TEMP < (DATA[6] + DATA[7]) / 2):
            TEMP = DATA[6]
        elif (self.MIN_OP_TEMP < (DATA[7] + DATA[8]) / 2):
            TEMP = DATA[7]
        elif (self.MIN_OP_TEMP < (DATA[8] + DATA[9]) / 2):
            TEMP = DATA[8]
        elif (self.MIN_OP_TEMP < (DATA[9] + DATA[10]) / 2):
            TEMP = DATA[9]
        else:
            TEMP = DATA[10]
        return TEMP

    def DF_SIGMA(self):
        if (self.AUSTENITIC_STEEL and not (self.MIN_OP_TEMP > 927 or self.MAX_OP_TEMP < 593)):
            TEMP = self.API_TEMP_SIGMA()
            if (TEMP == 649):
                if (self.PERCENT_SIGMA < 10):
                    DFB_SIGMA = 0
                else:
                    DFB_SIGMA = 18
            elif (TEMP == 538):
                if (self.PERCENT_SIGMA < 10):
                    DFB_SIGMA = 0
                else:
                    DFB_SIGMA = 53
            elif (TEMP == 427):
                if (self.PERCENT_SIGMA < 5):
                    DFB_SIGMA = 0
                elif (self.PERCENT_SIGMA >= 5 and self.PERCENT_SIGMA < 10):
                    DFB_SIGMA = 0.2
                else:
                    DFB_SIGMA = 160
            elif (TEMP == 316):
                if (self.PERCENT_SIGMA < 5):
                    DFB_SIGMA = 0
                elif (self.PERCENT_SIGMA >= 5 and self.PERCENT_SIGMA < 10):
                    DFB_SIGMA = 0.9
                else:
                    DFB_SIGMA = 481
            elif (TEMP == 204):
                if (self.PERCENT_SIGMA < 5):
                    DFB_SIGMA = 0
                elif (self.PERCENT_SIGMA >= 5 and self.PERCENT_SIGMA < 10):
                    DFB_SIGMA = 1.3
                else:
                    DFB_SIGMA = 1333
            elif (TEMP == 93):
                if (self.PERCENT_SIGMA < 5):
                    DFB_SIGMA = 0.1
                elif (self.PERCENT_SIGMA >= 5 and self.PERCENT_SIGMA < 10):
                    DFB_SIGMA = 3
                else:
                    DFB_SIGMA = 3202
            elif (TEMP == 66):
                if (self.PERCENT_SIGMA < 5):
                    DFB_SIGMA = 0.3
                elif (self.PERCENT_SIGMA >= 5 and self.PERCENT_SIGMA < 10):
                    DFB_SIGMA = 5
                else:
                    DFB_SIGMA = 3871
            elif (TEMP == 38):
                if (self.PERCENT_SIGMA < 5):
                    DFB_SIGMA = 0.6
                elif (self.PERCENT_SIGMA >= 5 and self.PERCENT_SIGMA < 10):
                    DFB_SIGMA = 7
                else:
                    DFB_SIGMA = 4196
            elif (TEMP == 10):
                if (self.PERCENT_SIGMA < 5):
                    DFB_SIGMA = 0.9
                elif (self.PERCENT_SIGMA >= 5 and self.PERCENT_SIGMA < 10):
                    DFB_SIGMA = 11
                else:
                    DFB_SIGMA = 4196
            elif (TEMP == -18):
                if (self.PERCENT_SIGMA < 5):
                    DFB_SIGMA = 1
                elif (self.PERCENT_SIGMA >= 5 and self.PERCENT_SIGMA < 10):
                    DFB_SIGMA = 20
                else:
                    DFB_SIGMA = 4196
            else:
                if (self.PERCENT_SIGMA < 5):
                    DFB_SIGMA = 1.1
                elif (self.PERCENT_SIGMA >= 5 and self.PERCENT_SIGMA < 10):
                    DFB_SIGMA = 34
                else:
                    DFB_SIGMA = 4196
            return DFB_SIGMA
        else:
            return 0

    # Calculate Pipping
    def DFB_PIPE(self):
        if (self.PREVIOUS_FAIL == "Greater than one"):
            DFB_PF = 500
        elif (self.PREVIOUS_FAIL == "One"):
            DFB_PF = 50
        else:
            DFB_PF = 1

        if (self.AMOUNT_SHAKING == "Severe"):
            DFB_AS = 500
        elif (self.AMOUNT_SHAKING == "Moderate"):
            DFB_AS = 50
        else:
            DFB_AS = 1

        if (self.TIME_SHAKING == "13 to 52 weeks"):
            FFB_AS = 0.02
        elif (self.TIME_SHAKING == "2 to 13 weeks"):
            FFB_AS = 0.2
        else:
            FFB_AS = 1

        if (self.CYLIC_LOAD == "Reciprocating machinery"):
            DFB_CF = 50
        elif (self.CYLIC_LOAD == "PRV chatter"):
            DFB_CF = 25
        elif (self.CYLIC_LOAD == "Valve with high pressure drop"):
            DFB_CF = 10
        else:
            DFB_CF = 1

        return max(DFB_PF, max(DFB_AS * FFB_AS, DFB_CF))

    def checkPiping(self):
        pip = ["PIPE-1", "PIPE-2", "PIPE-4", "PIPE-6", "PIPE-8", "PIPE-10", "PIPE-12","PIPE-16", "PIPEGT16"]
        check = False
        for a in pip:
            if self.APIComponentType == a:
                check = True
                break
        return check

    def DF_PIPE(self):
        if (self.checkPiping()):
            if (self.CORRECT_ACTION == "Engineering Analysis"):
                FCA = 0.002
            elif (self.CORRECT_ACTION == "Experience"):
                FCA = 0.2
            else:
                FCA = 2

            if (self.NUM_PIPE == "Up to 5"):
                FPC = 0.5
            elif (self.NUM_PIPE == "6 to 10"):
                FPC = 1
            else:
                FPC = 2

            if (
                    self.PIPE_CONDITION == "Broken gussets or gussets welded directly to pipe" or self.PIPE_CONDITION == "Missing or damage supports, improper support"):
                FCP = 2
            else:
                FCP = 1

            if (self.JOINT_TYPE == "Sweepolets"):
                FJB = 0.02
            elif (self.JOINT_TYPE == "Piping tee weldolets"):
                FJB = 0.2
            elif (self.JOINT_TYPE == "Threaded, socket welded, or saddle on"):
                FJB = 2
            else:
                FJB = 1

            if (self.BRANCH_DIAMETER == "All branches greater than 2\" Nominal OD"):
                FBD = 0.02
            else:
                FBD = 1

            return self.DFB_PIPE() * FCA * FPC * FCP * FJB * FBD
        else:
            return 0


    ##################################################################################
    def GET_AGE_INSERVICE(self):
        return int((self.AssesmentDate.date() - self.CommissionDate.date()).days/365)

    def GET_AGE(self):
        age = np.zeros(14)
        for a in range(0,14):
            age[a] = DAL_CAL.POSTGRESQL.GET_AGE_INSP(self.ComponentNumber,self.DM_Name[a],self.CommissionDate, self.AssesmentDate)
        return age

    def DF_THINNING_API(self, i):
        return self.DF_THIN(self.GET_AGE()[0] + i)

    def DF_LINNING_API(self, i):
        return self.DF_LINNING(self.GET_AGE()[1] + i)

    def DF_CAUTISC_API(self, i):
        return self.DF_CAUSTIC(self.GET_AGE()[2] + i)

    def DF_AMINE_API(self, i):
        return self.DF_AMINE(self.GET_AGE()[3] + i)

    def DF_SULPHIDE_API(self, i):
        return self.DF_SULPHIDE(self.GET_AGE()[4] + i)

    def DF_HICSOHIC_H2S_API(self, i):
        return self.DF_HICSOHIC_H2S(self.GET_AGE()[5] + i)

    def DF_CACBONATE_API(self,i):
        return self.DF_CACBONATE(self.GET_AGE()[6] + i)

    def DF_PTA_API(self,i):
        return self.DF_PTA(self.GET_AGE()[7] + i)

    def DF_CLSCC_API(self,i):
        return self.DF_CLSCC(self.GET_AGE()[8] + i)

    def DF_HSCHF_API(self, i):
        return self.DF_HSCHF(self.GET_AGE()[9] + i)

    def DF_HIC_SOHIC_HF_API(self, i):
        return self.DF_HIC_SOHIC_HF(self.GET_AGE()[10] + i)

    def DF_EXTERNAL_CORROSION_API(self, i):
        return self.DF_EXTERNAL_CORROSION(self.GET_AGE()[11] + i)

    def DF_CUI_API(self, i):
        return self.DF_CUI(self.GET_AGE()[12] + i)

    def DF_EXTERN_CLSCC_API(self):
        return self.DF_EXTERN_CLSCC()

    def DF_CUI_CLSCC_API(self):
        return self.DF_CUI_CLSCC()

    def DF_HTHA_API(self, i):
        return self.DF_HTHA(self.GET_AGE()[13] + i)

    def DF_BRITTLE_API(self):
        return  self.DF_BRITTLE()

    def DF_TEMP_EMBRITTLE_API(self):
        return self.DF_TEMP_EMBRITTLE()

    def DF_885_API(self):
        return self.DF_885()

    def DF_SIGMA_API(self):
        return self.DF_SIGMA()

    def DF_PIPE_API(self):
        return self.DF_PIPE()

    # TOTAL ---------------------
    def DF_SSC_TOTAL_API(self, i):
        DF_SCC = max(self.DF_CAUTISC_API(i), self.DF_AMINE_API(i), self.DF_SULPHIDE_API(i), self.DF_HIC_SOHIC_HF_API(i), self.DF_HICSOHIC_H2S_API(i),
                     self.DF_CACBONATE_API(i), self.DF_PTA_API(i), self.DF_CLSCC_API(i), self.DF_HSCHF(i))
        return DF_SCC

    def DF_EXT_TOTAL_API(self, i):
        DF_EXT = max(self.DF_EXTERNAL_CORROSION_API(i), self.DF_CUI_API(i),self.DF_EXTERN_CLSCC_API(), self.DF_CUI_CLSCC_API())
        return DF_EXT

    def DF_BRIT_TOTAL_API(self):
        DF_BRIT = max(self.DF_BRITTLE_API() + self.DF_TEMP_EMBRITTLE_API(), self.DF_SIGMA_API(), self.DF_885_API())
        return DF_BRIT

    def DF_THINNING_TOTAL_API(self, i):
        if self.INTERNAL_LINNING and (self.DF_LINNING_API(i) != 0):
            DF_THINNING_TOTAL = min(self.DF_THINNING_API(i), self.DF_LINNING_API(i))
        else:
            DF_THINNING_TOTAL = self.DF_THINNING_API(i)
        return DF_THINNING_TOTAL

    def DF_TOTAL_API(self,i):
        TOTAL_DF_API = max(self.DF_THINNING_TOTAL_API(i),self.DF_EXT_TOTAL_API(i)) + self.DF_SSC_TOTAL_API(i) + self.DF_HTHA_API(i) + self.DF_BRIT_TOTAL_API() + self.DF_PIPE_API()
        return TOTAL_DF_API

    def DF_TOTAL_GENERAL(self, i):
        TOTAL_DF_API = self.DF_THINNING_TOTAL_API(i) + self.DF_EXT_TOTAL_API(i) + self.DF_SSC_TOTAL_API(
            i) + self.DF_HTHA_API(i) + self.DF_BRIT_TOTAL_API() + self.DF_PIPE_API()
        return TOTAL_DF_API

    def convertRisk(self,risk):
        if risk >= 1:
            return 1
        else:
            return risk

    def DF_LIST_16(self, FC_Total, GFF, FSM, Risk_Target):
        data = []
        data.append(Risk_Target)
        for a in range(1, 16):
            risk=self.convertRisk( self.DF_TOTAL_API(a) * GFF * FSM) * FC_Total
            data.append(risk)
        return data

    def DF_LIST_16_GENERAL(self,FC_Total, GFF, FSM, Risk_Target):
        data = []
        data.append(Risk_Target)
        for a in range(1,16):
            risk = self.convertRisk(self.DF_TOTAL_GENERAL(a) * GFF * FSM) * FC_Total
            data.append(risk)
        return data

    def INSP_DUE_DATE(self, FC_Total, GFF, FSM, Risk_Target):
        DF_TARGET = Risk_Target/(FC_Total * GFF * FSM)
        for a in range(1,16):
            if self.DF_TOTAL_API(a) >= DF_TARGET:
                break
        return self.AssesmentDate + relativedelta(years= a)

    def INSP_DUE_DATE_General(self, FC_total, GFF, FSM, Risk_Target):
        DF_TARGET = Risk_Target/(FC_total*GFF*FSM)
        for a in range(1,16):
            if self.DF_TOTAL_GENERAL(a) >= DF_TARGET:
                break
        return self.AssesmentDate + relativedelta(year=a)

    def ISDF(self):
        DM_ID = [8, 9, 61, 57, 73, 69, 60, 72, 62, 70, 67, 34, 32, 66, 63, 68, 2, 18, 1, 14, 10]
        data_mechanism = []
        DF_ITEM = np.zeros(21)
        DF_ITEM[0] = self.DF_THINNING_API(0)
        DF_ITEM[1] = self.DF_LINNING_API(0)
        DF_ITEM[2] = self.DF_CAUTISC_API(0)
        DF_ITEM[3] = self.DF_AMINE_API(0)
        DF_ITEM[4] = self.DF_SULPHIDE_API(0)
        DF_ITEM[5] = self.DF_HICSOHIC_H2S_API(0)
        DF_ITEM[6] = self.DF_CACBONATE_API(0)
        DF_ITEM[7] = self.DF_PTA_API(0)
        DF_ITEM[8] = self.DF_CLSCC_API(0)
        DF_ITEM[9] = self.DF_HSCHF_API(0)
        DF_ITEM[10] = self.DF_HIC_SOHIC_HF_API(0)
        DF_ITEM[11] = self.DF_EXTERNAL_CORROSION_API(0)
        DF_ITEM[12] = self.DF_CUI_API(0)
        DF_ITEM[13] = self.DF_EXTERN_CLSCC_API()
        DF_ITEM[14] = self.DF_CUI_CLSCC_API()
        DF_ITEM[15] = self.DF_HTHA_API(0)
        DF_ITEM[16] = self.DF_BRITTLE_API()
        DF_ITEM[17] = self.DF_TEMP_EMBRITTLE_API()
        DF_ITEM[18] = self.DF_885_API()
        DF_ITEM[19] = self.DF_SIGMA_API()
        DF_ITEM[20] = self.DF_PIPE_API()
        for i in range(0,21):
            if DF_ITEM[i] > 1:
                data_return = {}
                data_return['DF1'] = DF_ITEM[i]
                data_return['DM_ITEM_ID'] = DM_ID[i]
                data_return['isActive'] = 1
                data_return['highestEFF'] = DAL_CAL.POSTGRESQL.GET_MAX_INSP(self.ComponentNumber, self.DM_Name[i])
                data_return['secondEFF'] = data_return['highestEFF']
                data_return['numberINSP'] = DAL_CAL.POSTGRESQL.GET_NUMBER_INSP(self.ComponentNumber, self.DM_Name[i])
                data_return['lastINSP'] = DAL_CAL.POSTGRESQL.GET_LAST_INSP(self.ComponentNumber, self.DM_Name[i], self.CommissionDate)
                if i == 0:
                    data_return['DF2'] = self.DF_THINNING_API(3)
                    data_return['DF3'] = self.DF_THINNING_API(6)
                elif i == 1:
                    data_return['DF2'] = self.DF_LINNING_API(3)
                    data_return['DF3'] = self.DF_LINNING_API(6)
                elif i == 2:
                    data_return['DF2'] = self.DF_CAUTISC_API(3)
                    data_return['DF3'] = self.DF_CAUTISC_API(6)
                elif i == 3:
                    data_return['DF2'] = self.DF_AMINE_API(3)
                    data_return['DF3'] = self.DF_AMINE_API(6)
                elif i == 4:
                    data_return['DF2'] = self.DF_SULPHIDE_API(3)
                    data_return['DF3'] = self.DF_SULPHIDE_API(6)
                elif i == 5:
                    data_return['DF2'] = self.DF_HICSOHIC_H2S_API(3)
                    data_return['DF3'] = self.DF_HICSOHIC_H2S_API(6)
                elif i == 6:
                    data_return['DF2'] = self.DF_CACBONATE_API(3)
                    data_return['DF3'] = self.DF_CACBONATE_API(6)
                elif i == 7:
                    data_return['DF2'] = self.DF_PTA_API(3)
                    data_return['DF3'] = self.DF_PTA_API(6)
                elif i == 8:
                    data_return['DF2'] = self.DF_CLSCC_API(3)
                    data_return['DF3'] = self.DF_CLSCC_API(6)
                elif i == 9:
                    data_return['DF2'] = self.DF_HSCHF_API(3)
                    data_return['DF3'] = self.DF_HSCHF_API(6)
                elif i == 10:
                    data_return['DF2'] = self.DF_HIC_SOHIC_HF_API(3)
                    data_return['DF3'] = self.DF_HIC_SOHIC_HF_API(6)
                elif i == 11:
                    data_return['DF2'] = self.DF_EXTERNAL_CORROSION_API(3)
                    data_return['DF3'] = self.DF_EXTERNAL_CORROSION_API(6)
                elif i == 12:
                    data_return['DF2'] = self.DF_CUI_API(3)
                    data_return['DF3'] = self.DF_CUI_API(6)
                elif i == 15:
                    data_return['DF2'] = self.DF_HTHA_API(3)
                    data_return['DF3'] = self.DF_HTHA_API(6)
                else:
                    data_return['DF2'] = DF_ITEM[i]
                    data_return['DF3'] = DF_ITEM[i]
                data_mechanism.append(data_return)
        return data_mechanism