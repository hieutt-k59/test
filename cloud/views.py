import os
from django.core.wsgi import get_wsgi_application

os.environ['DJANGO_SETTINGS_MODULE'] = 'RbiCloud.settings'
application = get_wsgi_application()


from PIL.PngImagePlugin import _idat
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect, render_to_response
from django.http import Http404,HttpResponse
from cloud import models
from dateutil.relativedelta import relativedelta
from cloud.process.RBI import DM_CAL,CA_CAL,pofConvert
from datetime import datetime
from cloud.process.WebUI import location
from cloud.process.WebUI import roundData
from cloud.process.File import export_data
from cloud.process.WebUI import date2Str
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from cloud.process.File import import_data as ExcelImport
from cloud.process.RBI import fastCalulate as ReCalculate
from django.db.models import Q


from django.views.decorators.csrf import csrf_protect
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from cloud.tokens import gen_token
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from  django.contrib.auth import login
import time

# Create your views here.

################ Base ####################
def Base_citizen(request):
    try:
        count = models.Emailto.objects.filter(Q(Emailt=models.ZUser.objects.filter(id=request.session['id'])[0].email), Q(Is_see=0)).count()
    except:
        Http404
    return render(request,'BaseUI/BaseCitizen/baseCitizen.html',{'count':count})
def citizen_home(request):
    count = models.Emailto.objects.filter(Q(Emailt=models.ZUser.objects.filter(id=request.session['id'])[0].email),Q(Is_see=0)).count()
    if request.session['kind']=='citizen':
        return render(request, 'CitizenUI/CitizenHome.html',{'info':request.session,'count':count})
def base_manager(request):
    try:
        count = models.Emailto.objects.filter(Q(Emailt=models.ZUser.objects.filter(id=request.session['id'])[0].email),Q(Is_see=0)).count()
    except:
        Http404
    return render(request, 'BaseUI/BaseManager/baseManager.html',{'count':count})
def base_business(request):
    try:
        count = models.Emailto.objects.filter(Q(Emailt=models.ZUser.objects.filter(id=request.session['id'])[0].email), Q(Is_see=0)).count()
    except Exception as e:
        print(e)
        Http404
    return render(request,'BaseUI/BaseFacility/baseBusiness.html',{'count':count})
def business_home(request):
    return render(request, 'BaseUI/BaseFacility/baseFacility.html')
def base_equipment(request):
    return render(request, 'BaseUI/BaseFacility/baseEquipment.html')
def base_component(request):
    return render(request, 'BaseUI/BaseFacility/baseComponent.html')
def base_proposal(request):
    return render(request, 'BaseUI/BaseFacility/baseProposal.html')
def base_risksummary(request):
    return render(request, 'BaseUI/BaseFacility/baseRiskSummary.html')
def base_designcode(request):
    return render(request, 'BaseUI/BaseFacility/baseDesigncode.html')
def base_manufacture(request):
    return render(request, 'FacilityUI/manufacture/manufactureListDisplay.html')

################## 404 Error ###########################
def handler404(request):
    return render(request, '404/404.html', locals())

################ Business UI Control ###################
def ListFacilities(request, siteID):
    count = models.Emailto.objects.filter(Q(Emailt=models.ZUser.objects.filter(id=request.session['id'])[0].email), Q(Is_see=0)).count()
    try:
        risk = []

        data= models.Facility.objects.filter(siteid= siteID)
        for a in data:
            dataF = {}
            risTarget = models.FacilityRiskTarget.objects.get(facilityid= a.facilityid)
            dataF['ID'] = a.facilityid
            dataF['FacilitiName'] = a.facilityname
            dataF['ManagementFactor'] = a.managementfactor
            dataF['RiskTarget'] = risTarget.risktarget_fc
            risk.append(dataF)

        pagiFaci = Paginator(risk, 25)
        pageFaci = request.GET.get('page',1)
        try:
            users = pagiFaci.page(pageFaci)
        except PageNotAnInteger:
            users = pagiFaci.page(1)
        except EmptyPage:
            users = pageFaci.page(pagiFaci.num_pages)
        if '_edit' in request.POST:
            for a in data:
                if(request.POST.get('%d' %a.facilityid)):
                    return redirect('facilitiesEdit', a.facilityid)
        if '_delete' in request.POST:
            for a in data:
                if(request.POST.get('%d' %a.facilityid)):
                    a.delete()
            return redirect('facilitiesDisplay', siteID)
    except:
        raise Http404
    return render(request, 'FacilityUI/facility/facilityListDisplay.html', {'obj': users,'siteID':siteID,'count':count})
def NewFacilities(request,siteID):
    try:
        error = {}
        data = {}
        site = models.Sites.objects.get(siteid= siteID)
        if request.method == 'POST':
            data['facilityname'] = request.POST.get('FacilityName')
            data['manageFactor'] = request.POST.get('ManagementSystemFactor')
            data['targetFC'] = request.POST.get('Financial')
            data['targetAC'] = request.POST.get('Area')
            countFaci = models.Facility.objects.filter(facilityname= data['facilityname']).count()
            if countFaci > 0:
                error['exist'] = "This facility already exists!"
            else:
                fa = models.Facility(facilityname= data['facilityname'],managementfactor= data['manageFactor'], siteid_id=siteID)
                fa.save()
                faTarget = models.FacilityRiskTarget(facilityid_id= fa.facilityid , risktarget_ac= data['targetAC'],
                                                         risktarget_fc=data['targetFC'])
                faTarget.save()
                return redirect('facilitiesDisplay',siteID=siteID)
    except:
        raise Http404
    return render(request, 'FacilityUI/facility/facilityNew.html', {'site':site, 'error':error, 'data':data, 'siteID':siteID})
def EditFacilities(request,facilityID):
    try:
        error = {}
        dataNew = {}
        dataOld = models.Facility.objects.get(facilityid= facilityID)
        dataRisk = models.FacilityRiskTarget.objects.get(facilityid= facilityID)
        site = models.Sites.objects.get(siteid= dataOld.siteid_id)
        dataNew['facilityname'] = dataOld.facilityname
        dataNew['manageFactor'] = dataOld.managementfactor
        dataNew['targetFC'] = dataRisk.risktarget_fc
        dataNew['targetAC'] = dataRisk.risktarget_ac
        dataNew['sitename'] = site.sitename
        if request.method == 'POST':
            dataNew['facilityname'] = request.POST.get('FacilityName')
            dataNew['manageFactor'] = request.POST.get('ManagementSystemFactor')
            dataNew['targetFC'] = request.POST.get('Financial')
            dataNew['targetAC'] = request.POST.get('Area')
            countFaci = models.Facility.objects.filter(facilityname=dataNew['facilityname']).count()
            if dataNew['facilityname'] != dataOld.facilityname and countFaci > 0:
                error['exist'] = "This facility already exists!"
            else:
                dataOld.facilityname = dataNew['facilityname']
                dataOld.managementfactor = dataNew['manageFactor']
                dataOld.save()

                dataRisk.risktarget_fc = dataNew['targetFC']
                dataRisk.risktarget_ac = dataNew['targetAC']
                dataRisk.save()

                return redirect('facilitiesDisplay', siteID= dataOld.siteid_id)
    except:
        raise Http404
    return render(request, 'FacilityUI/facility/facilityEdit.html',{'dataNew': dataNew, 'error':error, 'siteID':dataOld.siteid_id})
def ListDesignCode(request, siteID):
    try:
        data = models.DesignCode.objects.filter(siteid= siteID)
        pagiDes = Paginator(data, 25)
        pageDes = request.GET.get('page',1)
        try:
            obj = pagiDes.page(pageDes)
        except PageNotAnInteger:
            obj = pagiDes.page(1)
        except EmptyPage:
            obj = pageDes.page(pagiDes.num_pages)
        if '_edit' in request.POST:
            for a in data:
                if request.POST.get('%d' %a.designcodeid):
                    return redirect('designcodeEdit', designcodeID= a.designcodeid)
        if '_delete' in request.POST:
            for a in data:
                if request.POST.get('%d' %a.designcodeid):
                    a.delete()
            return redirect('designcodeDisplay', siteID= siteID)
    except:
        raise Http404
    return render(request, 'FacilityUI/design_code/designcodeListDisplay.html', {'obj':obj, 'siteID':siteID})
def NewDesignCode(request,siteID):
    try:
        error = {}
        data = {}
        if request.method == 'POST':
            data['designcode'] = request.POST.get('design_code_name')
            data['designcodeapp'] = request.POST.get('design_code_app')
            count = models.DesignCode.objects.filter(designcode= data['designcode']).count()
            if count > 0:
                error['exist'] = "This design code already exist!"
            else:
                ds = models.DesignCode(designcode= data['designcode'], designcodeapp= data['designcodeapp'], siteid_id = siteID)
                ds.save()
                return redirect('designcodeDisplay', siteID= siteID)
    except:
        raise Http404
    return render(request, 'FacilityUI/design_code/designcodeNew.html',{'data':data, 'error':error, 'siteID':siteID})
def EditDesignCode(request,designcodeID):
    try:
        error = {}
        dataNew = {}
        dataOld = models.DesignCode.objects.get(designcodeid= designcodeID)
        dataNew['designcode'] = dataOld.designcode
        dataNew['designcodeapp'] = dataOld.designcodeapp
        if request.method == 'POST':
            dataNew['designcode'] = request.POST.get('design_code_name')
            dataNew['designcodeapp'] = request.POST.get('design_code_app')
            count = models.DesignCode.objects.filter(designcode= dataNew['designcodeapp']).count()
            if dataNew['designcode'] != dataOld.designcode and count > 0:
                error['exist'] = "This design code already exist!"
            else:
                dataOld.designcode = dataNew['designcode']
                dataOld.designcodeapp = dataNew['designcodeapp']
                dataOld.save()
                return redirect('designcodeDisplay', siteID=dataOld.siteid_id)
    except:
        raise Http404
    return render(request, 'FacilityUI/design_code/designcodeEdit.html', {'data':dataNew, 'error':error, 'siteID':dataOld.siteid_id})
def ListManufacture(request, siteID):
    try:
        data = models.Manufacturer.objects.filter(siteid= siteID)
        pagiManu = Paginator(data, 25)
        pageManu = request.GET.get('page',1)
        try:
            obj = pagiManu.page(pageManu)
        except PageNotAnInteger:
            obj = pagiManu.page(1)
        except EmptyPage:
            obj = pageManu.page(pagiManu.num_pages)
        if '_edit' in request.POST:
            for a in data:
                if request.POST.get('%d' %a.manufacturerid):
                    return redirect('manufactureEdit', manufactureID= a.manufacturerid)
        if '_delete' in request.POST:
            for a in data:
                if request.POST.get('%d' %a.manufacturerid):
                    a.delete()
            return redirect('manufactureDisplay', siteID= siteID)
    except:
        raise Http404
    return render(request, 'FacilityUI/manufacture/manufactureListDisplay.html', {'obj':obj, 'siteID':siteID})
def NewManufacture(request, siteID):
    try:
        error = {}
        data = {}
        if request.method == 'POST':
            data['manufacture'] = request.POST.get('manufacture')
            count = models.Manufacturer.objects.filter(manufacturername= data['manufacture']).count()
            if count > 0:
                error['exist'] = 'This manufacture already exist!'
            else:
                manu = models.Manufacturer(siteid_id= siteID, manufacturername= data['manufacture'])
                manu.save()
                return redirect('manufactureDisplay', siteID= siteID)
    except:
        raise Http404
    return render(request, 'FacilityUI/manufacture/manufactureNew.html', {'data':data, 'error':error, 'siteID':siteID})
def EditManufacture(request, manufactureID):
    try:
        error = {}
        dataNew = {}
        dataOld = models.Manufacturer.objects.get(manufacturerid= manufactureID)
        dataNew['manufacture'] = dataOld.manufacturername
        if request.method == 'POST':
            dataNew['manufacture'] = request.POST.get('manufacture')
            count = models.Manufacturer.objects.filter(manufacturername= dataNew['manufacture']).count()
            if dataNew['manufacture'] != dataOld.manufacturername and count > 0:
                error['exist'] = 'This manufacturer already exist!'
            else:
                dataOld.manufacturername = dataNew['manufacture']
                dataOld.save()
                return redirect('manufactureDisplay', siteID= dataOld.siteid_id)
    except:
        raise Http404
    return render(request, 'FacilityUI/manufacture/manufactureEdit.html', {'data': dataNew, 'error': error , 'siteID':dataOld.siteid_id})
def ListEquipment(request, facilityID):
    try:
        faci = models.Facility.objects.get(facilityid= facilityID)
        data = models.EquipmentMaster.objects.filter(facilityid= facilityID)
        pagiEquip = Paginator(data,25)
        pageEquip = request.GET.get('page',1)
        try:
            obj = pagiEquip.page(pageEquip)
        except PageNotAnInteger:
            obj = pagiEquip.page(1)
        except EmptyPage:
            obj = pageEquip.page(pagiEquip.num_pages)
        if '_edit' in request.POST:
            for a in data:
                if request.POST.get('%d' %a.equipmentid):
                    return redirect('equipmentEdit', equipmentID= a.equipmentid)
        if '_delete' in request.POST:
            for a in data:
                if request.POST.get('%d' %a.equipmentid):
                    a.delete()
            return redirect('equipmentDisplay' , facilityID= facilityID)
    except:
        raise Http404
    return render(request, 'FacilityUI/equipment/equipmentListDisplay.html', {'obj':obj, 'facilityID':facilityID, 'siteID':faci.siteid_id})
def NewEquipment(request, facilityID):
    try:
        data = {}
        error = {}
        faci = models.Facility.objects.get(facilityid= facilityID)
        manufacture = models.Manufacturer.objects.filter(siteid= faci.siteid_id)
        designcode = models.DesignCode.objects.filter(siteid= faci.siteid_id)
        equipmenttype = models.EquipmentType.objects.all()
        if request.method == 'POST':
            data['equipmentnumber'] = request.POST.get('equipmentNumber')
            data['equipmentname'] = request.POST.get('equipmentName')
            data['equipmenttype'] = request.POST.get('equipmentType')
            data['designcode'] = request.POST.get('designCode')
            data['manufacture'] = request.POST.get('manufacture')
            data['commissiondate'] = request.POST.get('CommissionDate')
            data['pdf'] = request.POST.get('PDFNo')
            data['processdescrip'] = request.POST.get('processDescription')
            data['description'] = request.POST.get('decription')
            count = models.EquipmentMaster.objects.filter(equipmentnumber= data['equipmentnumber']).count()
            if count > 0:
                error['exist']='This equipment already exist!'
            else:
                eq = models.EquipmentMaster(equipmentnumber= data['equipmentnumber'], equipmentname= data['equipmentname'], equipmenttypeid_id=models.EquipmentType.objects.get(equipmenttypename= data['equipmenttype']).equipmenttypeid,
                                                designcodeid_id= models.DesignCode.objects.get(designcode= data['designcode']).designcodeid, siteid_id= faci.siteid_id, facilityid_id= facilityID,
                                                manufacturerid_id= models.Manufacturer.objects.get(manufacturername= data['manufacture']).manufacturerid, commissiondate= data['commissiondate'], pfdno= data['pdf'], processdescription= data['processdescrip'], equipmentdesc= data['description'])
                eq.save()
                return redirect('equipmentDisplay', facilityID= facilityID)
    except:
        raise Http404
    return render(request, 'FacilityUI/equipment/equipmentNew.html', {'data':data, 'equipmenttype': equipmenttype, 'designcode':designcode, 'manufacture':manufacture, 'facilityID':facilityID, 'siteID':faci.siteid_id})
def EditEquipment(request, equipmentID):
    try:
        error = {}
        dataNew = {}
        dataOld = models.EquipmentMaster.objects.get(equipmentid= equipmentID)
        manufacture = models.Manufacturer.objects.filter(siteid=dataOld.siteid_id)
        designcode = models.DesignCode.objects.filter(siteid= dataOld.siteid_id)
        dataNew['equipmentnumber'] = dataOld.equipmentnumber
        dataNew['equipmentname'] = dataOld.equipmentname
        dataNew['equipmenttype'] = models.EquipmentType.objects.get(equipmenttypeid= dataOld.equipmenttypeid_id).equipmenttypename
        dataNew['designcode'] = models.DesignCode.objects.get(designcodeid= dataOld.designcodeid_id).designcode
        dataNew['manufacture'] = models.Manufacturer.objects.get(manufacturerid= dataOld.manufacturerid_id).manufacturername
        dataNew['commissiondate'] = dataOld.commissiondate.date().strftime('%Y-%m-%d')
        dataNew['pdf'] = dataOld.pfdno
        dataNew['processdescrip'] = dataOld.processdescription
        dataNew['description'] = dataOld.equipmentdesc
        if request.method == 'POST':
            dataNew['equipmentnumber'] = request.POST.get('equipmentNumber')
            dataNew['equipmentname'] = request.POST.get('equipmentName')
            dataNew['designcode'] = request.POST.get('designCode')
            dataNew['manufacture'] = request.POST.get('manufacture')
            dataNew['commissiondate'] = request.POST.get('CommissionDate')
            dataNew['pdf'] = request.POST.get('PDFNo')
            dataNew['processdescrip'] = request.POST.get('processDescription')
            dataNew['description'] = request.POST.get('decription')
            count = models.EquipmentMaster.objects.filter(equipmentnumber= dataNew['equipmentnumber']).count()
            if dataNew['equipmentnumber'] != dataOld.equipmentnumber and count > 0:
                error['exist'] = 'This equipment already exist!'
            else:
                dataOld.equipmentnumber = dataNew['equipmentnumber']
                dataOld.equipmentname = dataNew['equipmentname']
                dataOld.designcodeid_id = models.DesignCode.objects.get(designcode= dataNew['designcode']).designcodeid
                dataOld.manufacturerid_id = models.Manufacturer.objects.get(manufacturername= dataNew['manufacture']).manufacturerid
                dataOld.commissiondate = dataNew['commissiondate']
                dataOld.pfdno = dataNew['pdf']
                dataOld.processdescription = dataNew['processdescrip']
                dataOld.equipmentdesc = dataNew['description']
                dataOld.save()
                return redirect('equipmentDisplay', facilityID=dataOld.facilityid_id)
    except:
        raise Http404
    return render(request, 'FacilityUI/equipment/equipmentEdit.html', {'data': dataNew, 'error':error, 'designcode':designcode, 'manufacture':manufacture, 'facilityID':dataOld.facilityid_id, 'siteID':dataOld.siteid_id})
def ListComponent(request, equipmentID):
    try:
        eq = models.EquipmentMaster.objects.get(equipmentid= equipmentID)
        data = models.ComponentMaster.objects.filter(equipmentid= equipmentID)
        pagiComp = Paginator(data,25)
        pageComp = request.GET.get('page',1)
        try:
            obj = pagiComp.page(pageComp)
        except PageNotAnInteger:
            obj= pagiComp.page(1)
        except EmptyPage:
            obj = pageComp.page(pagiComp.num_pages)
        if '_edit' in request.POST:
            for a in data:
                if request.POST.get('%a' %a.componentid):
                    return redirect('componentEdit', componentID= a.componentid)
        if '_delete' in request.POST:
            for a in data:
                if request.POST.get('%d' %a.componentid):
                    a.delete()
            return  redirect('componentDisplay', equipmentID= equipmentID)
    except:
        raise Http404
    return render(request, 'FacilityUI/component/componentListDisplay.html', {'obj':obj, 'equipmentID':equipmentID, 'facilityID': eq.facilityid_id})
def NewComponent(request, equipmentID):
    try:
        eq = models.EquipmentMaster.objects.get(equipmentid= equipmentID)
        data = {}
        error = {}
        componentType = models.ComponentType.objects.all()
        apicomponentType = models.ApiComponentType.objects.all()
        tankapi = [6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 36, 38, 39]
        other = []
        for a in apicomponentType:
            if a.apicomponenttypeid not in tankapi:
                other.append(a)
        if request.method == 'POST':
            data['componentNumber'] = request.POST.get('componentNumer')
            data['componenttype'] = request.POST.get('componentType')
            data['apicomponenttype'] = request.POST.get('apiComponentType')
            data['componentname'] = request.POST.get('componentName')
            if request.POST.get('comRisk'):
                data['link'] = 1
            else:
                data['link'] = 0
            data['description'] = request.POST.get('decription')
            count = models.ComponentMaster.objects.filter(componentnumber= data['componentNumber']).count()
            if count >0:
                error['exist'] = 'This component already exist!'
            else:
                comp = models.ComponentMaster(componentnumber= data['componentNumber'], equipmentid_id= equipmentID,
                                              componenttypeid_id = models.ComponentType.objects.get(componenttypename= data['componenttype']).componenttypeid,
                                              componentname= data['componentname'], componentdesc= data['description'], isequipmentlinked= data['link'],
                                              apicomponenttypeid= models.ApiComponentType.objects.get(apicomponenttypename= data['apicomponenttype']).apicomponenttypeid)
                comp.save()
                return redirect('componentDisplay', equipmentID= equipmentID)
    except:
        raise Http404
    return render(request, 'FacilityUI/component/componentNew.html', {'error':error, 'componenttype': componentType, 'api':apicomponentType,'other':other, 'data':data, 'equipmentID':equipmentID, 'facilityID': eq.facilityid_id})
def EditComponent(request, componentID):
    try:
        dataNew = {}
        error = {}
        dataOld = models.ComponentMaster.objects.get(componentid= componentID)
        dataNew['componentnumber'] = dataOld.componentnumber
        dataNew['componentname'] = dataOld.componentname
        dataNew['componenttype'] = models.ComponentType.objects.get(componenttypeid= dataOld.componenttypeid_id).componenttypename
        dataNew['apicomponenttype'] = models.ApiComponentType.objects.get(apicomponenttypeid= dataOld.apicomponenttypeid).apicomponenttypename
        dataNew['link'] = dataOld.isequipmentlinked
        dataNew['description'] = dataOld.componentdesc
        if request.method == 'POST':
            dataNew['componentnumber'] = request.POST.get('componentNumer')
            dataNew['componentname'] = request.POST.get('componentName')
            if request.POST.get('comRisk'):
                dataNew['link'] = 1
            else:
                dataNew['link'] = 0
            dataNew['description'] = request.POST.get('decription')
            count = models.ComponentMaster.objects.filter(componentnumber= dataNew['componentnumber']).count()
            if count > 0 and dataNew['componentnumber'] != dataOld.componentnumber:
                error['exist'] = 'This component already exist!'
            else:
                dataOld.componentnumber = dataNew['componentnumber']
                dataOld.componentname = dataNew['componentname']
                dataOld.isequipmentlinked = dataNew['link']
                dataOld.componentdesc = dataNew['description']
                dataOld.save()
                return redirect('componentDisplay', equipmentID= dataOld.equipmentid_id)
    except:
        raise Http404
    return render(request, 'FacilityUI/component/componentEdit.html', {'data':dataNew, 'error':error, 'equipmentID':dataOld.equipmentid_id, 'facilityID': models.EquipmentMaster.objects.get(equipmentid= dataOld.equipmentid_id).facilityid_id})
def ListProposal(request, componentID):
    try:
        rwass = models.RwAssessment.objects.filter(componentid= componentID)
        data = []
        comp = models.ComponentMaster.objects.get(componentid= componentID)
        equip = models.EquipmentMaster.objects.get(equipmentid= comp.equipmentid_id)
        tank = [8,12,14,15]
        for a in rwass:
            df = models.RwFullPof.objects.filter(id= a.id)
            fc = models.RwFullFcof.objects.filter(id= a.id)
            dm = models.RwDamageMechanism.objects.filter(id_dm= a.id)
            obj1 = {}
            obj1['id'] = a.id
            obj1['name'] = a.proposalname
            obj1['lastinsp'] = a.assessmentdate.strftime('%Y-%m-%d')
            if df.count() != 0:
                obj1['df'] = round(df[0].totaldfap1, 2)
                obj1['gff'] = df[0].gfftotal
                obj1['fms'] = df[0].fms
            else:
                obj1['df'] = 0
                obj1['gff'] = 0
                obj1['fms'] = 0
            if fc.count() != 0:
                obj1['fc'] = round(fc[0].fcofvalue, 2)
            else:
                obj1['fc'] = 0
            if dm.count() != 0:
                obj1['duedate'] = dm[0].inspduedate.date().strftime('%Y-%m-%d')
            else:
                obj1['duedate'] = (a.assessmentdate.date() + relativedelta(years=15)).strftime('%Y-%m-%d')
                obj1['lastinsp'] = equip.commissiondate.date().strftime('%Y-%m-%d')
            obj1['risk'] = round(obj1['df'] * obj1['gff'] * obj1['fms'] * obj1['fc'], 2)
            data.append(obj1)
        pagidata = Paginator(data,25)
        pagedata = request.GET.get('page',1)
        try:
            obj = pagidata.page(pagedata)
        except PageNotAnInteger:
            obj = pagidata.page(1)
        except EmptyPage:
            obj = pagedata.page(pagidata.num_pages)

        if comp.componenttypeid_id in tank:
            istank = 1
        else:
            istank = 0
        if comp.componenttypeid_id == 8 or comp.componenttypeid_id == 14:
            isshell = 1
        else:
            isshell = 0
        if request.POST:
            if '_delete' in request.POST:
                for a in rwass:
                    if request.POST.get('%d' %a.id):
                        a.delete()
                return redirect('proposalDisplay', componentID=componentID)
            elif '_cancel' in request.POST:
                return redirect('proposalDisplay', componentID=componentID)
            elif '_edit' in request.POST:
                for a in rwass:
                    if request.POST.get('%d' %a.id):
                        if istank:
                            return redirect('tankEdit', proposalID= a.id)
                        else:
                            return redirect('prosalEdit', proposalID= a.id)
            else:
                for a in rwass:
                    if request.POST.get('%d' %a.id):
                        ReCalculate.ReCalculate(a.id)
                return redirect('proposalDisplay', componentID=componentID)
    except:
        raise Http404
    return render(request, 'FacilityUI/proposal/proposalListDisplay.html', {'obj':obj, 'istank': istank, 'isshell':isshell,
                                                                            'componentID':componentID,
                                                                            'equipmentID':comp.equipmentid_id})
def NewProposal(request, componentID):
    try:
        Fluid = ["Acid", "AlCl3", "C1-C2", "C13-C16", "C17-C25", "C25+", "C3-C4", "C5", "C6-C8", "C9-C12", "CO", "DEE",
             "EE", "EEA", "EG", "EO", "H2", "H2S", "HCl", "HF", "Methanol", "Nitric Acid", "NO2", "Phosgene", "PO",
             "Pyrophoric", "Steam", "Styrene", "TDI", "Water"]
        comp = models.ComponentMaster.objects.get(componentid= componentID)
        target = models.FacilityRiskTarget.objects.get(facilityid= models.EquipmentMaster.objects.get(equipmentid= comp.equipmentid_id).facilityid_id)
        datafaci = models.Facility.objects.get(facilityid= models.EquipmentMaster.objects.get(equipmentid= comp.equipmentid_id).facilityid_id)
        data = {}
        if request.method == 'POST':
            data['assessmentname'] = request.POST.get('AssessmentName')
            data['assessmentdate'] = request.POST.get('assessmentdate')
            data['apicomponenttypeid'] = models.ApiComponentType.objects.get(apicomponenttypeid= comp.apicomponenttypeid).apicomponenttypename
            data['equipmentType'] = models.EquipmentType.objects.get(equipmenttypeid= models.EquipmentMaster.objects.get(equipmentid= comp.equipmentid_id).equipmenttypeid_id).equipmenttypename
            data['riskperiod'] = request.POST.get('RiskAnalysisPeriod')
            if request.POST.get('adminControlUpset'):
                adminControlUpset = 1
            else:
                adminControlUpset = 0

            if request.POST.get('ContainsDeadlegs'):
                containsDeadlegs = 1
            else:
                containsDeadlegs = 0

            if request.POST.get('Highly'):
                HighlyEffe = 1
            else:
                HighlyEffe = 0

            if request.POST.get('CylicOper'):
                cylicOP = 1
            else:
                cylicOP = 0

            if request.POST.get('Downtime'):
                downtime = 1
            else:
                downtime = 0

            if request.POST.get('SteamedOut'):
                steamOut = 1
            else:
                steamOut = 0

            if request.POST.get('HeatTraced'):
                heatTrace = 1
            else:
                heatTrace = 0

            if request.POST.get('PWHT'):
                pwht = 1
            else:
                pwht = 0

            if request.POST.get('InterfaceSoilWater'):
                interfaceSoilWater = 1
            else:
                interfaceSoilWater = 0

            if request.POST.get('PressurisationControlled'):
                pressureControl = 1
            else:
                pressureControl = 0

            if request.POST.get('LOM'):
                linerOnlineMoniter = 1
            else:
                linerOnlineMoniter = 0

            if request.POST.get('EquOper'):
                lowestTemp = 1
            else:
                lowestTemp = 0

            if request.POST.get('PresenceofSulphidesShutdow'):
                presentSulphidesShutdown =1
            else:
                presentSulphidesShutdown = 0

            if request.POST.get('MFTF'):
                materialExposed = 1
            else:
                materialExposed = 0

            if request.POST.get('PresenceofSulphides'):
                presentSulphide = 1
            else:
                presentSulphide = 0

            data['minTemp'] = request.POST.get('Min')
            data['ExternalEnvironment'] = request.POST.get('ExternalEnvironment')
            data['ThermalHistory'] = request.POST.get('ThermalHistory')
            data['OnlineMonitoring'] = request.POST.get('OnlineMonitoring')
            data['EquipmentVolumn'] = request.POST.get('EquipmentVolume')

            data['normaldiameter'] = request.POST.get('NominalDiameter')
            data['normalthick'] = request.POST.get('NominalThickness')
            data['currentthick'] = request.POST.get('CurrentThickness')
            data['tmin'] = request.POST.get('tmin')
            data['currentrate'] = request.POST.get('CurrentRate')
            data['deltafatt'] = request.POST.get('DeltaFATT')

            if request.POST.get('DFDI'):
                damageDuringInsp = 1
            else:
                damageDuringInsp = 0

            if request.POST.get('ChemicalInjection'):
                chemicalInj = 1
            else:
                chemicalInj = 0

            if request.POST.get('PresenceCracks'):
                crackpresent = 1
            else:
                crackpresent = 0

            if request.POST.get('HFICI'):
                HFICI = 1
            else:
                HFICI = 0

            if request.POST.get('TrampElements'):
                TrampElement = 1
            else:
                TrampElement = 0

            data['MaxBrinell'] = request.POST.get('MBHW')
            data['complex'] = request.POST.get('ComplexityProtrusions')
            data['CylicLoad'] = request.POST.get('CLC')
            data['branchDiameter'] = request.POST.get('BranchDiameter')
            data['joinTypeBranch'] = request.POST.get('JTB')
            data['numberPipe'] = request.POST.get('NFP')
            data['pipeCondition'] = request.POST.get('PipeCondition')
            data['prevFailure'] = request.POST.get('PreviousFailures')

            if request.POST.get('VASD'):
                visibleSharkingProtect = 1
            else:
                visibleSharkingProtect = 0

            data['shakingPipe'] = request.POST.get('ASP')
            data['timeShakingPipe'] = request.POST.get('ATSP')
            data['correctActionMitigate'] = request.POST.get('CAMV')

            # OP condition
            data['maxOT'] = request.POST.get('MaxOT')
            data['maxOP'] = request.POST.get('MaxOP')
            data['minOT'] = request.POST.get('MinOT')
            data['minOP'] = request.POST.get('MinOP')
            data['OpHydroPressure'] = request.POST.get('OHPP')
            data['criticalTemp'] = request.POST.get('CET')
            data['OP1'] = request.POST.get('Operating1')
            data['OP2'] = request.POST.get('Operating2')
            data['OP3'] = request.POST.get('Operating3')
            data['OP4'] = request.POST.get('Operating4')
            data['OP5'] = request.POST.get('Operating5')
            data['OP6'] = request.POST.get('Operating6')
            data['OP7'] = request.POST.get('Operating7')
            data['OP8'] = request.POST.get('Operating8')
            data['OP9'] = request.POST.get('Operating9')
            data['OP10'] = request.POST.get('Operating10')

            #material
            data['material'] = request.POST.get('Material')
            data['maxDesignTemp'] = request.POST.get('MaxDesignTemp')
            data['minDesignTemp'] = request.POST.get('MinDesignTemp')
            data['designPressure'] = request.POST.get('DesignPressure')
            data['tempRef'] = request.POST.get('ReferenceTemperature')
            data['allowStress'] = request.POST.get('ASAT')
            data['BrittleFacture'] = request.POST.get('BFGT')
            data['CA'] = request.POST.get('CorrosionAllowance')
            data['sigmaPhase'] = request.POST.get('SigmaPhase')
            if request.POST.get('CoLAS'):
                cacbonAlloy = 1
            else:
                cacbonAlloy = 0

            if request.POST.get('AusteniticSteel'):
                austeniticStell = 1
            else:
                austeniticStell = 0

            if request.POST.get('SusceptibleTemper'):
                suscepTemp = 1
            else:
                suscepTemp = 0

            if request.POST.get('NickelAlloy'):
                nickelAlloy = 1
            else:
                nickelAlloy = 0

            if request.POST.get('Chromium'):
                chromium = 1
            else:
                chromium = 0

            data['sulfurContent'] = request.POST.get('SulfurContent')
            data['heatTreatment'] = request.POST.get('heatTreatment')

            if request.POST.get('MGTEHTHA'):
                materialHTHA = 1
            else:
                materialHTHA = 0

            data['HTHAMaterialGrade'] = request.POST.get('HTHAMaterialGrade')

            if request.POST.get('MaterialPTA'):
                materialPTA = 1
            else:
                materialPTA = 0

            data['PTAMaterialGrade'] = request.POST.get('PTAMaterialGrade')
            data['materialCostFactor'] = request.POST.get('MaterialCostFactor')

            #Coating, Clading
            if request.POST.get('InternalCoating'):
                InternalCoating = 1
            else:
                InternalCoating = 0

            if request.POST.get('ExternalCoating'):
                ExternalCoating = 1
            else:
                ExternalCoating = 0

            data['ExternalCoatingID'] = request.POST.get('ExternalCoatingID')
            data['ExternalCoatingQuality'] = request.POST.get('ExternalCoatingQuality')

            if request.POST.get('SCWD'):
                supportMaterial = 1
            else:
                supportMaterial = 0

            if request.POST.get('InternalCladding'):
                InternalCladding = 1
            else:
                InternalCladding = 0

            data['CladdingCorrosionRate'] = request.POST.get('CladdingCorrosionRate')

            if request.POST.get('InternalLining'):
                InternalLining = 1
            else:
                InternalLining = 0

            data['InternalLinerType'] = request.POST.get('InternalLinerType')
            data['InternalLinerCondition'] = request.POST.get('InternalLinerCondition')

            if request.POST.get('ExternalInsulation')== "on" or request.POST.get('ExternalInsulation')== 1:
                ExternalInsulation = 1
            else:
                ExternalInsulation = 0

            if request.POST.get('ICC'):
                InsulationCholride = 1
            else:
                InsulationCholride = 0

            data['ExternalInsulationType'] = request.POST.get('ExternalInsulationType')
            data['InsulationCondition'] = request.POST.get('InsulationCondition')

            # Steam
            data['NaOHConcentration'] = request.POST.get('NaOHConcentration')
            data['ReleasePercentToxic'] = request.POST.get('RFPT')
            data['ChlorideIon'] = request.POST.get('ChlorideIon')
            data['CO3'] = request.POST.get('CO3')
            data['H2SContent'] = request.POST.get('H2SContent')
            data['PHWater'] = request.POST.get('PHWater')

            if request.POST.get('EAGTA'):
                exposureAcid = 1
            else:
                exposureAcid = 0

            if request.POST.get('ToxicConstituents'):
                ToxicConstituents = 1
            else:
                ToxicConstituents = 0

            data['ExposureAmine'] = request.POST.get('ExposureAmine')
            data['AminSolution'] = request.POST.get('ASC')

            if request.POST.get('APDO'):
                aquaDuringOP = 1
            else:
                aquaDuringOP = 0

            if request.POST.get('APDSD'):
                aquaDuringShutdown = 1
            else:
                aquaDuringShutdown = 0

            if request.POST.get('EnvironmentCH2S'):
                EnvironmentCH2S = 1
            else:
                EnvironmentCH2S = 0

            if request.POST.get('PHA'):
                presentHF = 1
            else:
                presentHF = 0

            if request.POST.get('PresenceCyanides'):
                presentCyanide = 1
            else:
                presentCyanide = 0

            if request.POST.get('PCH'):
                processHydrogen = 1
            else:
                processHydrogen = 0

            if request.POST.get('ECCAC'):
                environCaustic = 1
            else:
                environCaustic = 0

            if request.POST.get('ESBC'):
                exposedSulfur = 1
            else:
                exposedSulfur = 0

            if request.POST.get('MEFMSCC'):
                materialExposedFluid = 1
            else:
                materialExposedFluid = 0
            # CA
            data['APIFluid'] = request.POST.get('APIFluid')
            data['MassInventory'] = request.POST.get('MassInventory')
            data['Systerm'] = request.POST.get('Systerm')
            data['MassComponent'] = request.POST.get('MassComponent')
            data['EquipmentCost'] = request.POST.get('EquipmentCost')
            data['MittigationSysterm'] = request.POST.get('MittigationSysterm')
            data['ProductionCost'] = request.POST.get('ProductionCost')
            data['ToxicPercent'] = request.POST.get('ToxicPercent')
            data['InjureCost'] = request.POST.get('InjureCost')
            data['ReleaseDuration'] = request.POST.get('ReleaseDuration')
            data['EnvironmentCost'] = request.POST.get('EnvironmentCost')
            data['PersonDensity'] = request.POST.get('PersonDensity')
            data['DetectionType'] = request.POST.get('DetectionType')
            data['IsulationType'] = request.POST.get('IsulationType')
            rwassessment = models.RwAssessment(equipmentid_id=comp.equipmentid_id, componentid_id=comp.componentid, assessmentdate=data['assessmentdate'],
                                        riskanalysisperiod=data['riskperiod'], isequipmentlinked= comp.isequipmentlinked,
                                        proposalname=data['assessmentname'])
            rwassessment.save()
            rwequipment = models.RwEquipment(id=rwassessment, commissiondate=models.EquipmentMaster.objects.get(equipmentid= comp.equipmentid_id).commissiondate,
                                      adminupsetmanagement=adminControlUpset, containsdeadlegs=containsDeadlegs,
                                      cyclicoperation=cylicOP, highlydeadleginsp=HighlyEffe,
                                      downtimeprotectionused=downtime, externalenvironment=data['ExternalEnvironment'],
                                      heattraced=heatTrace, interfacesoilwater=interfaceSoilWater,
                                      lineronlinemonitoring=linerOnlineMoniter, materialexposedtoclext=materialExposed,
                                      minreqtemperaturepressurisation=data['minTemp'],
                                      onlinemonitoring=data['OnlineMonitoring'], presencesulphideso2=presentSulphide,
                                      presencesulphideso2shutdown=presentSulphidesShutdown,
                                      pressurisationcontrolled=pressureControl, pwht=pwht, steamoutwaterflush=steamOut,
                                      managementfactor= datafaci.managementfactor, thermalhistory=data['ThermalHistory'],
                                      yearlowestexptemp=lowestTemp, volume=data['EquipmentVolumn'])
            rwequipment.save()
            rwcomponent = models.RwComponent(id=rwassessment, nominaldiameter=data['normaldiameter'],
                                      nominalthickness=data['normalthick'], currentthickness=data['currentthick'],
                                      minreqthickness=data['tmin'], currentcorrosionrate=data['currentrate'],
                                      branchdiameter=data['branchDiameter'], branchjointtype=data['joinTypeBranch'],
                                      brinnelhardness=data['MaxBrinell']
                                      , deltafatt=data['deltafatt'], chemicalinjection=chemicalInj,
                                      highlyinjectioninsp=HFICI, complexityprotrusion=data['complex'],
                                      correctiveaction=data['correctActionMitigate'], crackspresent=crackpresent,
                                      cyclicloadingwitin15_25m=data['CylicLoad'],
                                      damagefoundinspection=damageDuringInsp, numberpipefittings=data['numberPipe'],
                                      pipecondition=data['pipeCondition'],
                                      previousfailures=data['prevFailure'], shakingamount=data['shakingPipe'],
                                      shakingdetected=visibleSharkingProtect, shakingtime=data['timeShakingPipe'],
                                      trampelements=TrampElement)
            rwcomponent.save()
            rwstream = models.RwStream(id=rwassessment, aminesolution=data['AminSolution'], aqueousoperation=aquaDuringOP,
                                aqueousshutdown=aquaDuringShutdown, toxicconstituent=ToxicConstituents,
                                caustic=environCaustic,
                                chloride=data['ChlorideIon'], co3concentration=data['CO3'], cyanide=presentCyanide,
                                exposedtogasamine=exposureAcid, exposedtosulphur=exposedSulfur,
                                exposuretoamine=data['ExposureAmine'],
                                h2s=EnvironmentCH2S, h2sinwater=data['H2SContent'], hydrogen=processHydrogen,
                                hydrofluoric=presentHF, materialexposedtoclint=materialExposedFluid,
                                maxoperatingpressure=data['maxOP'],
                                maxoperatingtemperature=float(data['maxOT']), minoperatingpressure=float(data['minOP']),
                                minoperatingtemperature=data['minOT'], criticalexposuretemperature=data['criticalTemp'],
                                naohconcentration=data['NaOHConcentration'],
                                releasefluidpercenttoxic=float(data['ReleasePercentToxic']),
                                waterph=float(data['PHWater']), h2spartialpressure=float(data['OpHydroPressure']))
            rwstream.save()
            rwexcor = models.RwExtcorTemperature(id=rwassessment, minus12tominus8=data['OP1'], minus8toplus6=data['OP2'],
                                          plus6toplus32=data['OP3'], plus32toplus71=data['OP4'],
                                          plus71toplus107=data['OP5'],
                                          plus107toplus121=data['OP6'], plus121toplus135=data['OP7'],
                                          plus135toplus162=data['OP8'], plus162toplus176=data['OP9'],
                                          morethanplus176=data['OP10'])
            rwexcor.save()
            rwcoat = models.RwCoating(id=rwassessment, externalcoating=ExternalCoating, externalinsulation=ExternalInsulation,
                               internalcladding=InternalCladding, internalcoating=InternalCoating,
                               internallining=InternalLining,
                               externalcoatingdate=data['ExternalCoatingID'],
                               externalcoatingquality=data['ExternalCoatingQuality'],
                               externalinsulationtype=data['ExternalInsulationType'],
                               insulationcondition=data['InsulationCondition'],
                               insulationcontainschloride=InsulationCholride,
                               internallinercondition=data['InternalLinerCondition'],
                               internallinertype=data['InternalLinerType'],
                               claddingcorrosionrate=data['CladdingCorrosionRate'],
                               supportconfignotallowcoatingmaint=supportMaterial)
            rwcoat.save()
            rwmaterial = models.RwMaterial(id=rwassessment, corrosionallowance=data['CA'], materialname=data['material'],
                                    designpressure=data['designPressure'], designtemperature=data['maxDesignTemp'],
                                    mindesigntemperature=data['minDesignTemp'],
                                    brittlefracturethickness=data['BrittleFacture'], sigmaphase=data['sigmaPhase'],
                                    sulfurcontent=data['sulfurContent'], heattreatment=data['heatTreatment'],
                                    referencetemperature=data['tempRef'],
                                    ptamaterialcode=data['PTAMaterialGrade'],
                                    hthamaterialcode=data['HTHAMaterialGrade'], ispta=materialPTA, ishtha=materialHTHA,
                                    austenitic=austeniticStell, temper=suscepTemp, carbonlowalloy=cacbonAlloy,
                                    nickelbased=nickelAlloy, chromemoreequal12=chromium,
                                    allowablestress=data['allowStress'], costfactor=data['materialCostFactor'])
            rwmaterial.save()
            rwinputca = models.RwInputCaLevel1(id=rwassessment, api_fluid=data['APIFluid'], system=data['Systerm'],
                                        release_duration=data['ReleaseDuration'], detection_type=data['DetectionType'],
                                        isulation_type=data['IsulationType'],
                                        mitigation_system=data['MittigationSysterm'],
                                        equipment_cost=data['EquipmentCost'], injure_cost=data['InjureCost'],
                                        evironment_cost=data['EnvironmentCost'], toxic_percent=data['ToxicPercent'],
                                        personal_density=data['PersonDensity'],
                                        material_cost=data['materialCostFactor'],
                                        production_cost=data['ProductionCost'], mass_inventory=data['MassInventory'],
                                        mass_component=data['MassComponent'],
                                        stored_pressure=float(data['minOP']) * 6.895, stored_temp=data['minOT'])
            rwinputca.save()
            ReCalculate.ReCalculate(rwassessment.id)
            return redirect('damgeFactor', proposalID= rwassessment.id)
    except Exception as e:
        raise Http404
    return render(request, 'FacilityUI/proposal/proposalNormalNew.html',{'api':Fluid, 'componentID':componentID, 'equipmentID':comp.equipmentid_id})
def NewTank(request, componentID):
    try:
        comp = models.ComponentMaster.objects.get(componentid= componentID)
        eq = models.EquipmentMaster.objects.get(equipmentid= comp.equipmentid_id)
        target = models.FacilityRiskTarget.objects.get(facilityid= eq.facilityid_id)
        datafaci = models.Facility.objects.get(facilityid= eq.facilityid_id)
        data={}
        isshell = False
        if comp.componenttypeid_id == 8 or comp.componenttypeid_id == 14:
            isshell = True
        if request.method =='POST':
            # Data Assessment
            data['assessmentName'] = request.POST.get('AssessmentName')
            data['assessmentdate'] = request.POST.get('assessmentdate')
            data['riskperiod'] = request.POST.get('RiskAnalysisPeriod')
            data['apicomponenttypeid'] = models.ApiComponentType.objects.get(apicomponenttypeid= comp.apicomponenttypeid).apicomponenttypename
            data['equipmenttype'] = models.EquipmentType.objects.get(equipmenttypeid= eq.equipmenttypeid_id).equipmenttypename
            # Data Equipment Properties
            if request.POST.get('Admin'):
                adminControlUpset = 1
            else:
                adminControlUpset = 0

            if request.POST.get('CylicOper'):
                cylicOp = 1
            else:
                cylicOp = 0

            if request.POST.get('Highly'):
                highlyDeadleg = 1
            else:
                highlyDeadleg = 0

            if request.POST.get('Steamed'):
                steamOutWater = 1
            else:
                steamOutWater = 0

            if request.POST.get('Downtime'):
                downtimeProtect = 1
            else:
                downtimeProtect = 0

            if request.POST.get('PWHT'):
                pwht = 1
            else:
                pwht = 0

            if request.POST.get('HeatTraced'):
                heatTrace = 1
            else:
                heatTrace = 0

            data['distance'] = request.POST.get('Distance')

            if request.POST.get('InterfaceSoilWater'):
                interfaceSoilWater = 1
            else:
                interfaceSoilWater = 0

            data['soiltype'] = request.POST.get('typeofSoil')

            if request.POST.get('PressurisationControlled'):
                pressureControl = 1
            else:
                pressureControl = 0

            data['minRequireTemp'] = request.POST.get('MinReq')

            if request.POST.get('lowestTemp'):
                lowestTemp = 1
            else:
                lowestTemp = 0

            if request.POST.get('MFTF'):
                materialChlorineExt = 1
            else:
                materialChlorineExt = 0

            if request.POST.get('LOM'):
                linerOnlineMonitor = 1
            else:
                linerOnlineMonitor = 0

            if request.POST.get('PresenceofSulphides'):
                presenceSulphideOP = 1
            else:
                presenceSulphideOP = 0

            if request.POST.get('PresenceofSulphidesShutdow'):
                presenceSulphideShut = 1
            else:
                presenceSulphideShut = 0

            if request.POST.get('ComponentWelded'):
                componentWelded = 1
            else:
                componentWelded = 0

            if request.POST.get('TMA'):
                tankIsMaintain = 1
            else:
                tankIsMaintain = 0

            data['adjustSettlement'] = request.POST.get('AdjForSettlement')
            data['extEnvironment'] = request.POST.get('ExternalEnvironment')
            data['EnvSensitivity'] = request.POST.get('EnvironmentSensitivity')
            data['themalHistory'] = request.POST.get('ThermalHistory')
            data['onlineMonitor'] = request.POST.get('OnlineMonitoring')
            data['equipmentVolumn'] = request.POST.get('EquipmentVolume')
            # Component Properties
            data['tankDiameter'] = request.POST.get('TankDiameter')
            data['NominalThickness'] = request.POST.get('NominalThickness')
            data['currentThick'] = request.POST.get('CurrentThickness')
            data['minRequireThick'] = request.POST.get('MinReqThick')
            data['currentCorrosion'] = request.POST.get('CurrentCorrosionRate')
            data['shellHieght'] = request.POST.get('shellHeight')

            if request.POST.get('DFDI'):
                damageFound = 1
            else:
                damageFound = 0

            if request.POST.get('PresenceCracks'):
                crackPresence = 1
            else:
                crackPresence = 0

            if request.POST.get('TrampElements'):
                trampElements = 1
            else:
                trampElements = 0

            if request.POST.get('ReleasePreventionBarrier'):
                preventBarrier = 1
            else:
                preventBarrier = 0

            if request.POST.get('ConcreteFoundation'):
                concreteFoundation = 1
            else:
                concreteFoundation = 0

            data['maxBrinnelHardness'] = request.POST.get('MBHW')
            data['complexProtrusion'] = request.POST.get('ComplexityProtrusions')
            data['severityVibration'] = request.POST.get('SeverityVibration')

            # Operating condition
            data['maxOT'] = request.POST.get('MaxOT')
            data['maxOP'] = request.POST.get('MaxOP')
            data['minOT'] = request.POST.get('MinOT')
            data['minOP'] = request.POST.get('MinOP')
            data['H2Spressure'] = request.POST.get('OHPP')
            data['criticalTemp'] = request.POST.get('CET')
            data['OP1'] = request.POST.get('Operating1')
            data['OP2'] = request.POST.get('Operating2')
            data['OP3'] = request.POST.get('Operating3')
            data['OP4'] = request.POST.get('Operating4')
            data['OP5'] = request.POST.get('Operating5')
            data['OP6'] = request.POST.get('Operating6')
            data['OP7'] = request.POST.get('Operating7')
            data['OP8'] = request.POST.get('Operating8')
            data['OP9'] = request.POST.get('Operating9')
            data['OP10'] = request.POST.get('Operating10')

            # Material
            data['materialName'] = request.POST.get('materialname')
            data['maxDesignTemp'] = request.POST.get('MaxDesignTemp')
            data['minDesignTemp'] = request.POST.get('MinDesignTemp')
            data['designPressure'] = request.POST.get('DesignPressure')
            data['refTemp'] = request.POST.get('ReferenceTemperature')
            data['allowStress'] = request.POST.get('ASAT')
            data['brittleThick'] = request.POST.get('BFGT')
            data['corrosionAllow'] = request.POST.get('CorrosionAllowance')

            if request.POST.get('CoLAS'):
                carbonLowAlloySteel = 1
            else:
                carbonLowAlloySteel = 0

            if request.POST.get('AusteniticSteel'):
                austeniticSteel = 1
            else:
                austeniticSteel = 0

            if request.POST.get('NickelAlloy'):
                nickelAlloy = 1
            else:
                nickelAlloy = 0

            if request.POST.get('Chromium'):
                chromium = 1
            else:
                chromium = 0

            data['sulfurContent'] = request.POST.get('SulfurContent')
            data['heatTreatment'] = request.POST.get('heatTreatment')

            if request.POST.get('MGTEPTA'):
                materialPTA = 1
            else:
                materialPTA = 0

            data['PTAMaterialGrade'] = request.POST.get('PTAMaterialGrade')
            data['materialCostFactor'] = request.POST.get('MaterialCostFactor')
            data['productionCost'] = request.POST.get('ProductionCost')

            # Coating, Cladding
            if request.POST.get('InternalCoating'):
                internalCoating = 1
            else:
                internalCoating = 0

            if request.POST.get('ExternalCoating'):
                externalCoating = 1
            else:
                externalCoating = 0

            data['externalInstallDate'] = request.POST.get('ExternalCoatingID')
            data['externalCoatQuality'] = request.POST.get('ExternalCoatingQuality')

            if request.POST.get('SCWD'):
                supportCoatingMaintain = 1
            else:
                supportCoatingMaintain = 0

            if request.POST.get('InternalCladding'):
                internalCladding = 1
            else:
                internalCladding = 0

            data['cladCorrosion'] = request.POST.get('CladdingCorrosionRate')

            if request.POST.get('InternalLining'):
                internalLinning = 1
            else:
                internalLinning = 0

            data['internalLinnerType'] = request.POST.get('InternalLinerType')
            data['internalLinnerCondition'] = request.POST.get('InternalLinerCondition')

            if request.POST.get('ExternalInsulation'):
                extInsulation = 1
            else:
                extInsulation = 0

            if request.POST.get('ICC'):
                InsulationContainChloride = 1
            else:
                InsulationContainChloride = 0

            data['extInsulationType'] = request.POST.get('ExternalInsulationType')
            data['insulationCondition'] = request.POST.get('InsulationCondition')

            # Stream
            data['fluid'] = request.POST.get('Fluid')
            data['fluidHeight'] = request.POST.get('FluidHeight')
            data['fluidLeaveDike'] = request.POST.get('PFLD')
            data['fluidOnsite'] = request.POST.get('PFLDRS')
            data['fluidOffsite'] = request.POST.get('PFLDGoffsite')
            data['naohConcent'] = request.POST.get('NaOHConcentration')
            data['releasePercentToxic'] = request.POST.get('RFPT')
            data['chlorideIon'] = request.POST.get('ChlorideIon')
            data['co3'] = request.POST.get('CO3')
            data['h2sContent'] = request.POST.get('H2SContent')
            data['PHWater'] = request.POST.get('PHWater')

            if request.POST.get('EAGTA'):
                exposedAmine = 1
            else:
                exposedAmine = 0

            data['amineSolution'] = request.POST.get('AmineSolution')
            data['exposureAmine'] = request.POST.get('ExposureAmine')

            if request.POST.get('APDO'):
                aqueosOP = 1
            else:
                aqueosOP = 0

            if request.POST.get('EnvironmentCH2S'):
                environtH2S = 1
            else:
                environtH2S = 0

            if request.POST.get('APDSD'):
                aqueosShut = 1
            else:
                aqueosShut = 0

            if request.POST.get('PresenceCyanides'):
                cyanidesPresence = 1
            else:
                cyanidesPresence = 0

            if request.POST.get('presenceHF'):
                presentHF = 1
            else:
                presentHF = 0

            if request.POST.get('ECCAC'):
                environtCaustic = 1
            else:
                environtCaustic = 0

            if request.POST.get('PCH'):
                processContainHydro = 1
            else:
                processContainHydro = 0

            if request.POST.get('MEFMSCC'):
                materialChlorineIntern = 1
            else:
                materialChlorineIntern = 0

            if request.POST.get('ESBC'):
                exposedSulfur = 1
            else:
                exposedSulfur = 0

            if str(data['fluid']) == "Gasoline":
                apiFluid = "C6-C8"
            elif str(data['fluid']) == "Light Diesel Oil":
                apiFluid = "C9-C12"
            elif str(data['fluid']) == "Heavy Diesel Oil":
                apiFluid = "C13-C16"
            elif str(data['fluid']) == "Fuel Oil" or str(data['fluid']) == "Crude Oil":
                apiFluid = "C17-C25"
            else:
                apiFluid = "C25+"
            rwassessment = models.RwAssessment(equipmentid_id=comp.equipmentid_id, componentid_id=comp.componentid, assessmentdate=data['assessmentdate'],
                                        riskanalysisperiod=data['riskperiod'],
                                        isequipmentlinked=comp.isequipmentlinked, proposalname=data['assessmentName'])
            rwassessment.save()
            rwequipment = models.RwEquipment(id=rwassessment, commissiondate= eq.commissiondate,
                                      adminupsetmanagement=adminControlUpset,
                                      cyclicoperation=cylicOp, highlydeadleginsp=highlyDeadleg,
                                      downtimeprotectionused=downtimeProtect, steamoutwaterflush=steamOutWater,
                                      pwht=pwht, heattraced=heatTrace, distancetogroundwater=data['distance'],
                                      interfacesoilwater=interfaceSoilWater, typeofsoil=data['soiltype'],
                                      pressurisationcontrolled=pressureControl,
                                      minreqtemperaturepressurisation=data['minRequireTemp'], yearlowestexptemp=lowestTemp,
                                      materialexposedtoclext=materialChlorineExt, lineronlinemonitoring=linerOnlineMonitor,
                                      presencesulphideso2=presenceSulphideOP,
                                      presencesulphideso2shutdown=presenceSulphideShut,
                                      componentiswelded=componentWelded, tankismaintained=tankIsMaintain,
                                      adjustmentsettle=data['adjustSettlement'],
                                      externalenvironment=data['extEnvironment'],
                                      environmentsensitivity=data['EnvSensitivity'],
                                      onlinemonitoring=data['onlineMonitor'], thermalhistory=data['themalHistory'],
                                      managementfactor=datafaci.managementfactor,
                                      volume=data['equipmentVolumn'])
            rwequipment.save()
            rwcomponent = models.RwComponent(id=rwassessment, nominaldiameter=data['tankDiameter'],
                                      nominalthickness=data['NominalThickness'], currentthickness=data['currentThick'],
                                      minreqthickness=data['minRequireThick'],
                                      currentcorrosionrate=data['currentCorrosion'],
                                      shellheight=data['shellHieght'], damagefoundinspection=damageFound,
                                      crackspresent=crackPresence, trampelements=trampElements,
                                      releasepreventionbarrier=preventBarrier, concretefoundation=concreteFoundation,
                                      brinnelhardness=data['maxBrinnelHardness'],
                                      complexityprotrusion=data['complexProtrusion'],
                                      severityofvibration=data['severityVibration'])
            rwcomponent.save()
            rwstream = models.RwStream(id=rwassessment, maxoperatingtemperature=data['maxOT'], maxoperatingpressure=data['maxOP'],
                                minoperatingtemperature=data['minOT'], minoperatingpressure=data['minOP'],
                                h2spartialpressure=data['H2Spressure'], criticalexposuretemperature=data['criticalTemp'],
                                tankfluidname=data['fluid'], fluidheight=data['fluidHeight'],
                                fluidleavedikepercent=data['fluidLeaveDike'],
                                fluidleavedikeremainonsitepercent=data['fluidOnsite'],
                                fluidgooffsitepercent=data['fluidOffsite'],
                                naohconcentration=data['naohConcent'], releasefluidpercenttoxic=data['releasePercentToxic'],
                                chloride=data['chlorideIon'], co3concentration=data['co3'], h2sinwater=data['h2sContent'],
                                waterph=data['PHWater'], exposedtogasamine=exposedAmine,
                                aminesolution=data['amineSolution'],
                                exposuretoamine=data['exposureAmine'], aqueousoperation=aqueosOP, h2s=environtH2S,
                                aqueousshutdown=aqueosShut, cyanide=cyanidesPresence, hydrofluoric=presentHF,
                                caustic=environtCaustic, hydrogen=processContainHydro,
                                materialexposedtoclint=materialChlorineIntern,
                                exposedtosulphur=exposedSulfur)
            rwstream.save()
            rwexcor = models.RwExtcorTemperature(id=rwassessment, minus12tominus8=data['OP1'], minus8toplus6=data['OP2'],
                                          plus6toplus32=data['OP3'], plus32toplus71=data['OP4'],
                                          plus71toplus107=data['OP5'],
                                          plus107toplus121=data['OP6'], plus121toplus135=data['OP7'],
                                          plus135toplus162=data['OP8'], plus162toplus176=data['OP9'],
                                          morethanplus176=data['OP10'])
            rwexcor.save()
            rwcoat = models.RwCoating(id=rwassessment, internalcoating=internalCoating, externalcoating=externalCoating,
                               externalcoatingdate=data['externalInstallDate'],
                               externalcoatingquality=data['externalCoatQuality'],
                               supportconfignotallowcoatingmaint=supportCoatingMaintain, internalcladding=internalCladding,
                               claddingcorrosionrate=data['cladCorrosion'], internallining=internalLinning,
                               internallinertype=data['internalLinnerType'],
                               internallinercondition=data['internalLinnerCondition'], externalinsulation=extInsulation,
                               insulationcontainschloride=InsulationContainChloride,
                               externalinsulationtype=data['extInsulationType'],
                               insulationcondition=data['insulationCondition']
                               )
            rwcoat.save()
            rwmaterial = models.RwMaterial(id=rwassessment, materialname=data['materialName'],
                                    designtemperature=data['maxDesignTemp'],
                                    mindesigntemperature=data['minDesignTemp'], designpressure=data['designPressure'],
                                    referencetemperature=data['refTemp'],
                                    allowablestress=data['allowStress'], brittlefracturethickness=data['brittleThick'],
                                    corrosionallowance=data['corrosionAllow'],
                                    carbonlowalloy=carbonLowAlloySteel, austenitic=austeniticSteel, nickelbased=nickelAlloy,
                                    chromemoreequal12=chromium,
                                    sulfurcontent=data['sulfurContent'], heattreatment=data['heatTreatment'],
                                    ispta=materialPTA, ptamaterialcode=data['PTAMaterialGrade'],
                                    costfactor=data['materialCostFactor'])
            rwmaterial.save()
            rwinputca = models.RwInputCaTank(id=rwassessment, fluid_height=data['fluidHeight'],
                                      shell_course_height=data['shellHieght'],
                                      tank_diametter=data['tankDiameter'], prevention_barrier=preventBarrier,
                                      environ_sensitivity=data['EnvSensitivity'],
                                      p_lvdike=data['fluidLeaveDike'], p_offsite=data['fluidOffsite'],
                                      p_onsite=data['fluidOnsite'], soil_type=data['soiltype'],
                                      tank_fluid=data['fluid'], api_fluid=apiFluid, sw=data['distance'],
                                      productioncost=data['productionCost'])
            rwinputca.save()

            # Customize Caculate Here
            ReCalculate.ReCalculate(rwassessment.id)
            return redirect('damgeFactor', proposalID=rwassessment.id)
    except Exception as e:
        # print(e)
        raise Http404
    return render(request, 'FacilityUI/proposal/proposalTankNew.html', {'isshell':isshell, 'componentID':componentID, 'equipmentID':comp.equipmentid_id})
def EditProposal(request, proposalID):
    try:
        Fluid = ["Acid", "AlCl3", "C1-C2", "C13-C16", "C17-C25", "C25+", "C3-C4", "C5", "C6-C8", "C9-C12", "CO", "DEE",
                 "EE", "EEA", "EG", "EO", "H2", "H2S", "HCl", "HF", "Methanol", "Nitric Acid", "NO2", "Phosgene", "PO",
                 "Pyrophoric", "Steam", "Styrene", "TDI", "Water"]
        rwassessment = models.RwAssessment.objects.get(id= proposalID)
        rwequipment = models.RwEquipment.objects.get(id= proposalID)
        rwcomponent = models.RwComponent.objects.get(id= proposalID)
        rwstream = models.RwStream.objects.get(id= proposalID)
        rwexcor = models.RwExtcorTemperature.objects.get(id= proposalID)
        rwcoat = models.RwCoating.objects.get(id= proposalID)
        rwmaterial = models.RwMaterial.objects.get(id= proposalID)
        rwinputca = models.RwInputCaLevel1.objects.get(id= proposalID)
        assDate = rwassessment.assessmentdate.strftime('%Y-%m-%d')
        try:
            extDate = rwcoat.externalcoatingdate.strftime('%Y-%m-%d')
        except:
            extDate = datetime.now().strftime('%Y-%m-%d')

        comp = models.ComponentMaster.objects.get(componentid=rwassessment.componentid_id)
        data = {}
        if request.method == 'POST':
            data['assessmentname'] = request.POST.get('AssessmentName')
            data['assessmentdate'] = request.POST.get('assessmentdate')
            data['apicomponenttypeid'] = models.ApiComponentType.objects.get(
                apicomponenttypeid=comp.apicomponenttypeid).apicomponenttypename
            data['equipmentType'] = models.EquipmentType.objects.get(equipmenttypeid=models.EquipmentMaster.objects.get(
                equipmentid=comp.equipmentid_id).equipmenttypeid_id).equipmenttypename
            data['riskperiod'] = request.POST.get('RiskAnalysisPeriod')
            if request.POST.get('adminControlUpset'):
                adminControlUpset = 1
            else:
                adminControlUpset = 0

            if request.POST.get('ContainsDeadlegs'):
                containsDeadlegs = 1
            else:
                containsDeadlegs = 0

            if request.POST.get('Highly'):
                HighlyEffe = 1
            else:
                HighlyEffe = 0

            if request.POST.get('CylicOper'):
                cylicOP = 1
            else:
                cylicOP = 0

            if request.POST.get('Downtime'):
                downtime = 1
            else:
                downtime = 0

            if request.POST.get('SteamedOut'):
                steamOut = 1
            else:
                steamOut = 0

            if request.POST.get('HeatTraced'):
                heatTrace = 1
            else:
                heatTrace = 0

            if request.POST.get('PWHT'):
                pwht = 1
            else:
                pwht = 0

            if request.POST.get('InterfaceSoilWater'):
                interfaceSoilWater = 1
            else:
                interfaceSoilWater = 0

            if request.POST.get('PressurisationControlled'):
                pressureControl = 1
            else:
                pressureControl = 0

            if request.POST.get('LOM'):
                linerOnlineMoniter = 1
            else:
                linerOnlineMoniter = 0

            if request.POST.get('EquOper'):
                lowestTemp = 1
            else:
                lowestTemp = 0

            if request.POST.get('PresenceofSulphidesShutdow'):
                presentSulphidesShutdown = 1
            else:
                presentSulphidesShutdown = 0

            if request.POST.get('MFTF'):
                materialExposed = 1
            else:
                materialExposed = 0

            if request.POST.get('PresenceofSulphides'):
                presentSulphide = 1
            else:
                presentSulphide = 0

            data['minTemp'] = request.POST.get('Min')
            data['ExternalEnvironment'] = request.POST.get('ExternalEnvironment')
            data['ThermalHistory'] = request.POST.get('ThermalHistory')
            data['OnlineMonitoring'] = request.POST.get('OnlineMonitoring')
            data['EquipmentVolumn'] = request.POST.get('EquipmentVolume')

            data['normaldiameter'] = request.POST.get('NominalDiameter')
            data['normalthick'] = request.POST.get('NominalThickness')
            data['currentthick'] = request.POST.get('CurrentThickness')
            data['tmin'] = request.POST.get('tmin')
            data['currentrate'] = request.POST.get('CurrentRate')
            data['deltafatt'] = request.POST.get('DeltaFATT')

            if request.POST.get('DFDI'):
                damageDuringInsp = 1
            else:
                damageDuringInsp = 0

            if request.POST.get('ChemicalInjection'):
                chemicalInj = 1
            else:
                chemicalInj = 0

            if request.POST.get('PresenceCracks'):
                crackpresent = 1
            else:
                crackpresent = 0

            if request.POST.get('HFICI'):
                HFICI = 1
            else:
                HFICI = 0

            if request.POST.get('TrampElements'):
                TrampElement = 1
            else:
                TrampElement = 0

            data['MaxBrinell'] = request.POST.get('MBHW')
            data['complex'] = request.POST.get('ComplexityProtrusions')
            data['CylicLoad'] = request.POST.get('CLC')
            data['branchDiameter'] = request.POST.get('BranchDiameter')
            data['joinTypeBranch'] = request.POST.get('JTB')
            data['numberPipe'] = request.POST.get('NFP')
            data['pipeCondition'] = request.POST.get('PipeCondition')
            data['prevFailure'] = request.POST.get('PreviousFailures')

            if request.POST.get('VASD'):
                visibleSharkingProtect = 1
            else:
                visibleSharkingProtect = 0

            data['shakingPipe'] = request.POST.get('ASP')
            data['timeShakingPipe'] = request.POST.get('ATSP')
            data['correctActionMitigate'] = request.POST.get('CAMV')
            # OP condition
            data['maxOT'] = request.POST.get('MaxOT')
            data['maxOP'] = request.POST.get('MaxOP')
            data['minOT'] = request.POST.get('MinOT')
            data['minOP'] = request.POST.get('MinOP')
            data['OpHydroPressure'] = request.POST.get('OHPP')
            data['criticalTemp'] = request.POST.get('CET')
            data['OP1'] = request.POST.get('Operating1')
            data['OP2'] = request.POST.get('Operating2')
            data['OP3'] = request.POST.get('Operating3')
            data['OP4'] = request.POST.get('Operating4')
            data['OP5'] = request.POST.get('Operating5')
            data['OP6'] = request.POST.get('Operating6')
            data['OP7'] = request.POST.get('Operating7')
            data['OP8'] = request.POST.get('Operating8')
            data['OP9'] = request.POST.get('Operating9')
            data['OP10'] = request.POST.get('Operating10')
            # material
            data['material'] = request.POST.get('Material')
            data['maxDesignTemp'] = request.POST.get('MaxDesignTemp')
            data['minDesignTemp'] = request.POST.get('MinDesignTemp')
            data['designPressure'] = request.POST.get('DesignPressure')
            data['tempRef'] = request.POST.get('ReferenceTemperature')
            data['allowStress'] = request.POST.get('ASAT')
            data['BrittleFacture'] = request.POST.get('BFGT')
            data['CA'] = request.POST.get('CorrosionAllowance')
            data['sigmaPhase'] = request.POST.get('SigmaPhase')
            if request.POST.get('CoLAS'):
                cacbonAlloy = 1
            else:
                cacbonAlloy = 0

            if request.POST.get('AusteniticSteel'):
                austeniticStell = 1
            else:
                austeniticStell = 0

            if request.POST.get('SusceptibleTemper'):
                suscepTemp = 1
            else:
                suscepTemp = 0

            if request.POST.get('NickelAlloy'):
                nickelAlloy = 1
            else:
                nickelAlloy = 0

            if request.POST.get('Chromium'):
                chromium = 1
            else:
                chromium = 0

            data['sulfurContent'] = request.POST.get('SulfurContent')
            data['heatTreatment'] = request.POST.get('heatTreatment')

            if request.POST.get('MGTEHTHA'):
                materialHTHA = 1
            else:
                materialHTHA = 0

            data['HTHAMaterialGrade'] = request.POST.get('HTHAMaterialGrade')

            if request.POST.get('MaterialPTA'):
                materialPTA = 1
            else:
                materialPTA = 0

            data['PTAMaterialGrade'] = request.POST.get('PTAMaterialGrade')
            data['materialCostFactor'] = request.POST.get('MaterialCostFactor')
            # Coating, Clading
            if request.POST.get('InternalCoating'):
                InternalCoating = 1
            else:
                InternalCoating = 0

            if request.POST.get('ExternalCoating'):
                ExternalCoating = 1
            else:
                ExternalCoating = 0

            data['ExternalCoatingID'] = request.POST.get('ExternalCoatingID')
            data['ExternalCoatingQuality'] = request.POST.get('ExternalCoatingQuality')

            if request.POST.get('SCWD'):
                supportMaterial = 1
            else:
                supportMaterial = 0

            if request.POST.get('InternalCladding'):
                InternalCladding = 1
            else:
                InternalCladding = 0

            data['CladdingCorrosionRate'] = request.POST.get('CladdingCorrosionRate')

            if request.POST.get('InternalLining'):
                InternalLining = 1
            else:
                InternalLining = 0

            data['InternalLinerType'] = request.POST.get('InternalLinerType')
            data['InternalLinerCondition'] = request.POST.get('InternalLinerCondition')

            if request.POST.get('ExternalInsulation') == "on" or request.POST.get('ExternalInsulation') == 1:
                ExternalInsulation = 1
            else:
                ExternalInsulation = 0

            if request.POST.get('ICC'):
                InsulationCholride = 1
            else:
                InsulationCholride = 0

            data['ExternalInsulationType'] = request.POST.get('ExternalInsulationType')
            data['InsulationCondition'] = request.POST.get('InsulationCondition')
            # Steam
            data['NaOHConcentration'] = request.POST.get('NaOHConcentration')
            data['ReleasePercentToxic'] = request.POST.get('RFPT')
            data['ChlorideIon'] = request.POST.get('ChlorideIon')
            data['CO3'] = request.POST.get('CO3')
            data['H2SContent'] = request.POST.get('H2SContent')
            data['PHWater'] = request.POST.get('PHWater')

            if request.POST.get('EAGTA'):
                exposureAcid = 1
            else:
                exposureAcid = 0

            if request.POST.get('ToxicConstituents'):
                ToxicConstituents = 1
            else:
                ToxicConstituents = 0

            data['ExposureAmine'] = request.POST.get('ExposureAmine')
            data['AminSolution'] = request.POST.get('ASC')

            if request.POST.get('APDO'):
                aquaDuringOP = 1
            else:
                aquaDuringOP = 0

            if request.POST.get('APDSD'):
                aquaDuringShutdown = 1
            else:
                aquaDuringShutdown = 0

            if request.POST.get('EnvironmentCH2S'):
                EnvironmentCH2S = 1
            else:
                EnvironmentCH2S = 0

            if request.POST.get('PHA'):
                presentHF = 1
            else:
                presentHF = 0

            if request.POST.get('PresenceCyanides'):
                presentCyanide = 1
            else:
                presentCyanide = 0

            if request.POST.get('PCH'):
                processHydrogen = 1
            else:
                processHydrogen = 0

            if request.POST.get('ECCAC'):
                environCaustic = 1
            else:
                environCaustic = 0

            if request.POST.get('ESBC'):
                exposedSulfur = 1
            else:
                exposedSulfur = 0

            if request.POST.get('MEFMSCC'):
                materialExposedFluid = 1
            else:
                materialExposedFluid = 0
            # CA
            data['APIFluid'] = request.POST.get('APIFluid')
            data['MassInventory'] = request.POST.get('MassInventory')
            data['Systerm'] = request.POST.get('Systerm')
            data['MassComponent'] = request.POST.get('MassComponent')
            data['EquipmentCost'] = request.POST.get('EquipmentCost')
            data['MittigationSysterm'] = request.POST.get('MittigationSysterm')
            data['ProductionCost'] = request.POST.get('ProductionCost')
            data['ToxicPercent'] = request.POST.get('ToxicPercent')
            data['InjureCost'] = request.POST.get('InjureCost')
            data['ReleaseDuration'] = request.POST.get('ReleaseDuration')
            data['EnvironmentCost'] = request.POST.get('EnvironmentCost')
            data['PersonDensity'] = request.POST.get('PersonDensity')
            data['DetectionType'] = request.POST.get('DetectionType')
            data['IsulationType'] = request.POST.get('IsulationType')

            rwassessment.assessmentdate=data['assessmentdate']
            rwassessment.proposalname=data['assessmentname']
            rwassessment.save()

            rwequipment.adminupsetmanagement=adminControlUpset
            rwequipment.containsdeadlegs=containsDeadlegs
            rwequipment.cyclicoperation=cylicOP
            rwequipment.highlydeadleginsp=HighlyEffe
            rwequipment.downtimeprotectionused=downtime
            rwequipment.externalenvironment=data['ExternalEnvironment']
            rwequipment.heattraced=heatTrace
            rwequipment.interfacesoilwater=interfaceSoilWater
            rwequipment.lineronlinemonitoring=linerOnlineMoniter
            rwequipment.materialexposedtoclext=materialExposed
            rwequipment.minreqtemperaturepressurisation=data['minTemp']
            rwequipment.onlinemonitoring=data['OnlineMonitoring']
            rwequipment.presencesulphideso2=presentSulphide
            rwequipment.presencesulphideso2shutdown=presentSulphidesShutdown
            rwequipment.pressurisationcontrolled=pressureControl
            rwequipment.pwht=pwht
            rwequipment.steamoutwaterflush=steamOut
            rwequipment.thermalhistory=data['ThermalHistory']
            rwequipment.yearlowestexptemp=lowestTemp
            rwequipment.volume=data['EquipmentVolumn']
            rwequipment.save()

            rwcomponent.nominaldiameter=data['normaldiameter']
            rwcomponent.nominalthickness=data['normalthick']
            rwcomponent.currentthickness=data['currentthick']
            rwcomponent.minreqthickness=data['tmin']
            rwcomponent.currentcorrosionrate=data['currentrate']
            rwcomponent.branchdiameter=data['branchDiameter']
            rwcomponent.branchjointtype=data['joinTypeBranch']
            rwcomponent.brinnelhardness=data['MaxBrinell']
            rwcomponent.deltafatt=data['deltafatt']
            rwcomponent.chemicalinjection=chemicalInj
            rwcomponent.highlyinjectioninsp=HFICI
            rwcomponent.complexityprotrusion=data['complex']
            rwcomponent.correctiveaction=data['correctActionMitigate']
            rwcomponent.crackspresent=crackpresent
            rwcomponent.cyclicloadingwitin15_25m=data['CylicLoad']
            rwcomponent.damagefoundinspection=damageDuringInsp
            rwcomponent.numberpipefittings=data['numberPipe']
            rwcomponent.pipecondition=data['pipeCondition']
            rwcomponent.previousfailures=data['prevFailure']
            rwcomponent.shakingamount=data['shakingPipe']
            rwcomponent.shakingdetected=visibleSharkingProtect
            rwcomponent.shakingtime=data['timeShakingPipe']
            rwcomponent.trampelements=TrampElement
            rwcomponent.save()

            rwstream.aminesolution=data['AminSolution']
            rwstream.aqueousoperation=aquaDuringOP
            rwstream.aqueousshutdown=aquaDuringShutdown
            rwstream.toxicconstituent=ToxicConstituents
            rwstream.caustic=environCaustic
            rwstream.chloride=data['ChlorideIon']
            rwstream.co3concentration=data['CO3']
            rwstream.cyanide=presentCyanide
            rwstream.exposedtogasamine= exposureAcid
            rwstream.exposedtosulphur=exposedSulfur
            rwstream.exposuretoamine=data['ExposureAmine']
            rwstream.h2s=EnvironmentCH2S
            rwstream.h2sinwater=data['H2SContent']
            rwstream.hydrogen= processHydrogen
            rwstream.hydrofluoric=presentHF
            rwstream.materialexposedtoclint=materialExposedFluid
            rwstream.maxoperatingpressure=data['maxOP']
            rwstream.maxoperatingtemperature=float(data['maxOT'])
            rwstream.minoperatingpressure=float(data['minOP'])
            rwstream.minoperatingtemperature=data['minOT']
            rwstream.criticalexposuretemperature=data['criticalTemp']
            rwstream.naohconcentration=data['NaOHConcentration']
            rwstream.releasefluidpercenttoxic=float(data['ReleasePercentToxic'])
            rwstream.waterph=float(data['PHWater'])
            rwstream.h2spartialpressure=float(data['OpHydroPressure'])
            rwstream.save()

            rwexcor.minus12tominus8=data['OP1']
            rwexcor.minus8toplus6=data['OP2']
            rwexcor.plus6toplus32=data['OP3']
            rwexcor.plus32toplus71=data['OP4']
            rwexcor.plus71toplus107=data['OP5']
            rwexcor.plus107toplus121=data['OP6']
            rwexcor.plus121toplus135=data['OP7']
            rwexcor.plus135toplus162=data['OP8']
            rwexcor.plus162toplus176=data['OP9']
            rwexcor.morethanplus176=data['OP10']
            rwexcor.save()

            rwcoat.externalcoating=ExternalCoating
            rwcoat.externalinsulation=ExternalInsulation
            rwcoat.internalcladding=InternalCladding
            rwcoat.internalcoating=InternalCoating
            rwcoat.internallining=InternalLining
            rwcoat.externalcoatingdate=data['ExternalCoatingID']
            rwcoat.externalcoatingquality=data['ExternalCoatingQuality']
            rwcoat.externalinsulationtype=data['ExternalInsulationType']
            rwcoat.insulationcondition=data['InsulationCondition']
            rwcoat.insulationcontainschloride=InsulationCholride
            rwcoat.internallinercondition=data['InternalLinerCondition']
            rwcoat.internallinertype=data['InternalLinerType']
            rwcoat.claddingcorrosionrate=data['CladdingCorrosionRate']
            rwcoat.supportconfignotallowcoatingmaint=supportMaterial
            rwcoat.save()

            rwmaterial.corrosionallowance=data['CA']
            rwmaterial.materialname=data['material']
            rwmaterial.designpressure=data['designPressure']
            rwmaterial.designtemperature=data['maxDesignTemp']
            rwmaterial.mindesigntemperature=data['minDesignTemp']
            rwmaterial.brittlefracturethickness=data['BrittleFacture']
            rwmaterial.sigmaphase=data['sigmaPhase']
            rwmaterial.sulfurcontent=data['sulfurContent']
            rwmaterial.heattreatment=data['heatTreatment']
            rwmaterial.referencetemperature=data['tempRef']
            rwmaterial.ptamaterialcode=data['PTAMaterialGrade']
            rwmaterial.hthamaterialcode=data['HTHAMaterialGrade']
            rwmaterial.ispta=materialPTA
            rwmaterial.ishtha=materialHTHA
            rwmaterial.austenitic=austeniticStell
            rwmaterial.temper=suscepTemp
            rwmaterial.carbonlowalloy=cacbonAlloy
            rwmaterial.nickelbased=nickelAlloy
            rwmaterial.chromemoreequal12=chromium
            rwmaterial.allowablestress=data['allowStress']
            rwmaterial.costfactor=data['materialCostFactor']
            rwmaterial.save()

            rwinputca.api_fluid=data['APIFluid']
            rwinputca.system=data['Systerm']
            rwinputca.release_duration=data['ReleaseDuration']
            rwinputca.detection_type=data['DetectionType']
            rwinputca.isulation_type=data['IsulationType']
            rwinputca.mitigation_system=data['MittigationSysterm']
            rwinputca.equipment_cost=data['EquipmentCost']
            rwinputca.injure_cost=data['InjureCost']
            rwinputca.evironment_cost=data['EnvironmentCost']
            rwinputca.toxic_percent=data['ToxicPercent']
            rwinputca.personal_density=data['PersonDensity']
            rwinputca.material_cost=data['materialCostFactor']
            rwinputca.production_cost=data['ProductionCost']
            rwinputca.mass_inventory=data['MassInventory']
            rwinputca.mass_component=data['MassComponent']
            rwinputca.stored_pressure=float(data['minOP']) * 6.895
            rwinputca.stored_temp=data['minOT']
            rwinputca.save()

            #Customize code here
            ReCalculate.ReCalculate(proposalID)
            return redirect('damgeFactor', proposalID= proposalID)
    except Exception as e:
        print(e)
        raise Http404
    return render(request, 'FacilityUI/proposal/proposalNormalEdit.html', {'api':Fluid, 'rwAss':rwassessment, 'rwEq':rwequipment,
                                                                           'rwComp':rwcomponent, 'rwStream':rwstream, 'rwExcot':rwexcor,
                                                                           'rwCoat':rwcoat, 'rwMaterial':rwmaterial, 'rwInputCa':rwinputca,
                                                                           'assDate':assDate, 'extDate':extDate,
                                                                           'componentID': rwassessment.componentid_id,
                                                                           'equipmentID': rwassessment.equipmentid_id})
def EditTank(request, proposalID):
    try:
        rwassessment = models.RwAssessment.objects.get(id=proposalID)
        rwequipment = models.RwEquipment.objects.get(id=proposalID)
        rwcomponent = models.RwComponent.objects.get(id=proposalID)
        rwstream = models.RwStream.objects.get(id=proposalID)
        rwexcor = models.RwExtcorTemperature.objects.get(id=proposalID)
        rwcoat = models.RwCoating.objects.get(id=proposalID)
        rwmaterial = models.RwMaterial.objects.get(id=proposalID)
        rwinputca = models.RwInputCaTank.objects.get(id=proposalID)
        assDate = rwassessment.assessmentdate.strftime('%Y-%m-%d')
        try:
            extDate = rwcoat.externalcoatingdate.strftime('%Y-%m-%d')
        except:
            extDate = datetime.now().strftime('%Y-%m-%d')

        comp = models.ComponentMaster.objects.get(componentid= rwassessment.componentid_id)
        eq = models.EquipmentMaster.objects.get(equipmentid= rwassessment.equipmentid_id)
        datafaci = models.Facility.objects.get(facilityid= eq.facilityid_id)
        data={}
        isshell = False
        if comp.componenttypeid_id == 8 or comp.componenttypeid_id == 14:
            isshell = True
        if request.method =='POST':
            # Data Assessment
            data['assessmentName'] = request.POST.get('AssessmentName')
            data['assessmentdate'] = request.POST.get('assessmentdate')
            data['riskperiod'] = request.POST.get('RiskAnalysisPeriod')
            data['apicomponenttypeid'] = models.ApiComponentType.objects.get(apicomponenttypeid= comp.apicomponenttypeid).apicomponenttypename
            data['equipmenttype'] = models.EquipmentType.objects.get(equipmenttypeid= eq.equipmenttypeid_id).equipmenttypename
            # Data Equipment Properties
            if request.POST.get('Admin'):
                adminControlUpset = 1
            else:
                adminControlUpset = 0

            if request.POST.get('CylicOper'):
                cylicOp = 1
            else:
                cylicOp = 0

            if request.POST.get('Highly'):
                highlyDeadleg = 1
            else:
                highlyDeadleg = 0

            if request.POST.get('Steamed'):
                steamOutWater = 1
            else:
                steamOutWater = 0

            if request.POST.get('Downtime'):
                downtimeProtect = 1
            else:
                downtimeProtect = 0

            if request.POST.get('PWHT'):
                pwht = 1
            else:
                pwht = 0

            if request.POST.get('HeatTraced'):
                heatTrace = 1
            else:
                heatTrace = 0

            data['distance'] = request.POST.get('Distance')

            if request.POST.get('InterfaceSoilWater'):
                interfaceSoilWater = 1
            else:
                interfaceSoilWater = 0

            data['soiltype'] = request.POST.get('typeofSoil')

            if request.POST.get('PressurisationControlled'):
                pressureControl = 1
            else:
                pressureControl = 0

            data['minRequireTemp'] = request.POST.get('MinReq')

            if request.POST.get('lowestTemp'):
                lowestTemp = 1
            else:
                lowestTemp = 0

            if request.POST.get('MFTF'):
                materialChlorineExt = 1
            else:
                materialChlorineExt = 0

            if request.POST.get('LOM'):
                linerOnlineMonitor = 1
            else:
                linerOnlineMonitor = 0

            if request.POST.get('PresenceofSulphides'):
                presenceSulphideOP = 1
            else:
                presenceSulphideOP = 0

            if request.POST.get('PresenceofSulphidesShutdow'):
                presenceSulphideShut = 1
            else:
                presenceSulphideShut = 0

            if request.POST.get('ComponentWelded'):
                componentWelded = 1
            else:
                componentWelded = 0

            if request.POST.get('TMA'):
                tankIsMaintain = 1
            else:
                tankIsMaintain = 0

            data['adjustSettlement'] = request.POST.get('AdjForSettlement')
            data['extEnvironment'] = request.POST.get('ExternalEnvironment')
            data['EnvSensitivity'] = request.POST.get('EnvironmentSensitivity')
            data['themalHistory'] = request.POST.get('ThermalHistory')
            data['onlineMonitor'] = request.POST.get('OnlineMonitoring')
            data['equipmentVolumn'] = request.POST.get('EquipmentVolume')
            # Component Properties
            data['tankDiameter'] = request.POST.get('TankDiameter')
            data['NominalThickness'] = request.POST.get('NominalThickness')
            data['currentThick'] = request.POST.get('CurrentThickness')
            data['minRequireThick'] = request.POST.get('MinReqThick')
            data['currentCorrosion'] = request.POST.get('CurrentCorrosionRate')
            data['shellHieght'] = request.POST.get('shellHeight')

            if request.POST.get('DFDI'):
                damageFound = 1
            else:
                damageFound = 0

            if request.POST.get('PresenceCracks'):
                crackPresence = 1
            else:
                crackPresence = 0

            if request.POST.get('TrampElements'):
                trampElements = 1
            else:
                trampElements = 0

            if request.POST.get('ReleasePreventionBarrier'):
                preventBarrier = 1
            else:
                preventBarrier = 0

            if request.POST.get('ConcreteFoundation'):
                concreteFoundation = 1
            else:
                concreteFoundation = 0

            data['maxBrinnelHardness'] = request.POST.get('MBHW')
            data['complexProtrusion'] = request.POST.get('ComplexityProtrusions')
            data['severityVibration'] = request.POST.get('SeverityVibration')

            # Operating condition
            data['maxOT'] = request.POST.get('MaxOT')
            data['maxOP'] = request.POST.get('MaxOP')
            data['minOT'] = request.POST.get('MinOT')
            data['minOP'] = request.POST.get('MinOP')
            data['H2Spressure'] = request.POST.get('OHPP')
            data['criticalTemp'] = request.POST.get('CET')
            data['OP1'] = request.POST.get('Operating1')
            data['OP2'] = request.POST.get('Operating2')
            data['OP3'] = request.POST.get('Operating3')
            data['OP4'] = request.POST.get('Operating4')
            data['OP5'] = request.POST.get('Operating5')
            data['OP6'] = request.POST.get('Operating6')
            data['OP7'] = request.POST.get('Operating7')
            data['OP8'] = request.POST.get('Operating8')
            data['OP9'] = request.POST.get('Operating9')
            data['OP10'] = request.POST.get('Operating10')

            # Material
            data['materialName'] = request.POST.get('materialname')
            data['maxDesignTemp'] = request.POST.get('MaxDesignTemp')
            data['minDesignTemp'] = request.POST.get('MinDesignTemp')
            data['designPressure'] = request.POST.get('DesignPressure')
            data['refTemp'] = request.POST.get('ReferenceTemperature')
            data['allowStress'] = request.POST.get('ASAT')
            data['brittleThick'] = request.POST.get('BFGT')
            data['corrosionAllow'] = request.POST.get('CorrosionAllowance')

            if request.POST.get('CoLAS'):
                carbonLowAlloySteel = 1
            else:
                carbonLowAlloySteel = 0

            if request.POST.get('AusteniticSteel'):
                austeniticSteel = 1
            else:
                austeniticSteel = 0

            if request.POST.get('NickelAlloy'):
                nickelAlloy = 1
            else:
                nickelAlloy = 0

            if request.POST.get('Chromium'):
                chromium = 1
            else:
                chromium = 0

            data['sulfurContent'] = request.POST.get('SulfurContent')
            data['heatTreatment'] = request.POST.get('heatTreatment')

            if request.POST.get('MGTEPTA'):
                materialPTA = 1
            else:
                materialPTA = 0

            data['PTAMaterialGrade'] = request.POST.get('PTAMaterialGrade')
            data['materialCostFactor'] = request.POST.get('MaterialCostFactor')
            data['productionCost'] = request.POST.get('ProductionCost')

            # Coating, Cladding
            if request.POST.get('InternalCoating'):
                internalCoating = 1
            else:
                internalCoating = 0

            if request.POST.get('ExternalCoating'):
                externalCoating = 1
            else:
                externalCoating = 0

            data['externalInstallDate'] = request.POST.get('ExternalCoatingID')
            data['externalCoatQuality'] = request.POST.get('ExternalCoatingQuality')

            if request.POST.get('SCWD'):
                supportCoatingMaintain = 1
            else:
                supportCoatingMaintain = 0

            if request.POST.get('InternalCladding'):
                internalCladding = 1
            else:
                internalCladding = 0

            data['cladCorrosion'] = request.POST.get('CladdingCorrosionRate')

            if request.POST.get('InternalLining'):
                internalLinning = 1
            else:
                internalLinning = 0

            data['internalLinnerType'] = request.POST.get('InternalLinerType')
            data['internalLinnerCondition'] = request.POST.get('InternalLinerCondition')

            if request.POST.get('ExternalInsulation'):
                extInsulation = 1
            else:
                extInsulation = 0

            if request.POST.get('ICC'):
                InsulationContainChloride = 1
            else:
                InsulationContainChloride = 0

            data['extInsulationType'] = request.POST.get('ExternalInsulationType')
            data['insulationCondition'] = request.POST.get('InsulationCondition')

            # Stream
            data['fluid'] = request.POST.get('Fluid')
            data['fluidHeight'] = request.POST.get('FluidHeight')
            data['fluidLeaveDike'] = request.POST.get('PFLD')
            data['fluidOnsite'] = request.POST.get('PFLDRS')
            data['fluidOffsite'] = request.POST.get('PFLDGoffsite')
            data['naohConcent'] = request.POST.get('NaOHConcentration')
            data['releasePercentToxic'] = request.POST.get('RFPT')
            data['chlorideIon'] = request.POST.get('ChlorideIon')
            data['co3'] = request.POST.get('CO3')
            data['h2sContent'] = request.POST.get('H2SContent')
            data['PHWater'] = request.POST.get('PHWater')

            if request.POST.get('EAGTA'):
                exposedAmine = 1
            else:
                exposedAmine = 0

            data['amineSolution'] = request.POST.get('AmineSolution')
            data['exposureAmine'] = request.POST.get('ExposureAmine')

            if request.POST.get('APDO'):
                aqueosOP = 1
            else:
                aqueosOP = 0

            if request.POST.get('EnvironmentCH2S'):
                environtH2S = 1
            else:
                environtH2S = 0

            if request.POST.get('APDSD'):
                aqueosShut = 1
            else:
                aqueosShut = 0

            if request.POST.get('PresenceCyanides'):
                cyanidesPresence = 1
            else:
                cyanidesPresence = 0

            if request.POST.get('presenceHF'):
                presentHF = 1
            else:
                presentHF = 0

            if request.POST.get('ECCAC'):
                environtCaustic = 1
            else:
                environtCaustic = 0

            if request.POST.get('PCH'):
                processContainHydro = 1
            else:
                processContainHydro = 0

            if request.POST.get('MEFMSCC'):
                materialChlorineIntern = 1
            else:
                materialChlorineIntern = 0

            if request.POST.get('ESBC'):
                exposedSulfur = 1
            else:
                exposedSulfur = 0

            if str(data['fluid']) == "Gasoline":
                apiFluid = "C6-C8"
            elif str(data['fluid']) == "Light Diesel Oil":
                apiFluid = "C9-C12"
            elif str(data['fluid']) == "Heavy Diesel Oil":
                apiFluid = "C13-C16"
            elif str(data['fluid']) == "Fuel Oil" or str(data['fluid']) == "Crude Oil":
                apiFluid = "C17-C25"
            else:
                apiFluid = "C25+"
            rwassessment.assessmentdate=data['assessmentdate']
            rwassessment.proposalname=data['assessmentName']
            rwassessment.save()

            rwequipment.adminupsetmanagement=adminControlUpset
            rwequipment.cyclicoperation=cylicOp
            rwequipment.highlydeadleginsp=highlyDeadleg
            rwequipment.downtimeprotectionused=downtimeProtect
            rwequipment.steamoutwaterflush=steamOutWater
            rwequipment.pwht=pwht
            rwequipment.heattraced=heatTrace
            rwequipment.distancetogroundwater=data['distance']
            rwequipment.interfacesoilwater=interfaceSoilWater
            rwequipment.typeofsoil=data['soiltype']
            rwequipment.pressurisationcontrolled=pressureControl
            rwequipment.minreqtemperaturepressurisation=data['minRequireTemp']
            rwequipment.yearlowestexptemp=lowestTemp
            rwequipment.materialexposedtoclext=materialChlorineExt
            rwequipment.lineronlinemonitoring=linerOnlineMonitor
            rwequipment.presencesulphideso2=presenceSulphideOP
            rwequipment.presencesulphideso2shutdown=presenceSulphideShut
            rwequipment.componentiswelded=componentWelded
            rwequipment.tankismaintained=tankIsMaintain
            rwequipment.adjustmentsettle=data['adjustSettlement']
            rwequipment.externalenvironment=data['extEnvironment']
            rwequipment.environmentsensitivity=data['EnvSensitivity']
            rwequipment.onlinemonitoring=data['onlineMonitor']
            rwequipment.thermalhistory=data['themalHistory']
            rwequipment.managementfactor=datafaci.managementfactor
            rwequipment.volume=data['equipmentVolumn']
            rwequipment.save()

            rwcomponent.nominaldiameter=data['tankDiameter']
            rwcomponent.nominalthickness=data['NominalThickness']
            rwcomponent.currentthickness=data['currentThick']
            rwcomponent.minreqthickness=data['minRequireThick']
            rwcomponent.currentcorrosionrate=data['currentCorrosion']
            rwcomponent.shellheight=data['shellHieght']
            rwcomponent.damagefoundinspection=damageFound
            rwcomponent.crackspresent=crackPresence
            rwcomponent.trampelements=trampElements
            rwcomponent.releasepreventionbarrier=preventBarrier
            rwcomponent.concretefoundation=concreteFoundation
            rwcomponent.brinnelhardness=data['maxBrinnelHardness']
            rwcomponent.complexityprotrusion=data['complexProtrusion']
            rwcomponent.severityofvibration=data['severityVibration']
            rwcomponent.save()

            rwstream.maxoperatingtemperature=data['maxOT']
            rwstream.maxoperatingpressure=data['maxOP']
            rwstream.minoperatingtemperature=data['minOT']
            rwstream.minoperatingpressure=data['minOP']
            rwstream.h2spartialpressure=data['H2Spressure']
            rwstream.criticalexposuretemperature=data['criticalTemp']
            rwstream.tankfluidname=data['fluid']
            rwstream.fluidheight=data['fluidHeight']
            rwstream.fluidleavedikepercent=data['fluidLeaveDike']
            rwstream.fluidleavedikeremainonsitepercent=data['fluidOnsite']
            rwstream.fluidgooffsitepercent=data['fluidOffsite']
            rwstream.naohconcentration=data['naohConcent']
            rwstream.releasefluidpercenttoxic=data['releasePercentToxic']
            rwstream.chloride=data['chlorideIon']
            rwstream.co3concentration=data['co3']
            rwstream.h2sinwater=data['h2sContent']
            rwstream.waterph=data['PHWater']
            rwstream.exposedtogasamine=exposedAmine
            rwstream.aminesolution=data['amineSolution']
            rwstream.exposuretoamine=data['exposureAmine']
            rwstream.aqueousoperation=aqueosOP
            rwstream.h2s=environtH2S
            rwstream.aqueousshutdown=aqueosShut
            rwstream.cyanide=cyanidesPresence
            rwstream.hydrofluoric=presentHF
            rwstream.caustic=environtCaustic
            rwstream.hydrogen=processContainHydro
            rwstream.materialexposedtoclint=materialChlorineIntern
            rwstream.exposedtosulphur=exposedSulfur
            rwstream.save()

            rwexcor.minus12tominus8=data['OP1']
            rwexcor.minus8toplus6=data['OP2']
            rwexcor.plus6toplus32=data['OP3']
            rwexcor.plus32toplus71=data['OP4']
            rwexcor.plus71toplus107=data['OP5']
            rwexcor.plus107toplus121=data['OP6']
            rwexcor.plus121toplus135=data['OP7']
            rwexcor.plus135toplus162=data['OP8']
            rwexcor.plus162toplus176=data['OP9']
            rwexcor.morethanplus176=data['OP10']
            rwexcor.save()

            rwcoat.internalcoating=internalCoating
            rwcoat.externalcoating=externalCoating
            rwcoat.externalcoatingdate=data['externalInstallDate']
            rwcoat.externalcoatingquality=data['externalCoatQuality']
            rwcoat.supportconfignotallowcoatingmaint=supportCoatingMaintain
            rwcoat.internalcladding=internalCladding
            rwcoat.claddingcorrosionrate=data['cladCorrosion']
            rwcoat.internallining=internalLinning
            rwcoat.internallinertype=data['internalLinnerType']
            rwcoat.internallinercondition=data['internalLinnerCondition']
            rwcoat.externalinsulation=extInsulation
            rwcoat.insulationcontainschloride=InsulationContainChloride
            rwcoat.externalinsulationtype=data['extInsulationType']
            rwcoat.insulationcondition=data['insulationCondition']
            rwcoat.save()

            rwmaterial.materialname=data['materialName']
            rwmaterial.designtemperature=data['maxDesignTemp']
            rwmaterial.mindesigntemperature=data['minDesignTemp']
            rwmaterial.designpressure=data['designPressure']
            rwmaterial.referencetemperature=data['refTemp']
            rwmaterial.allowablestress=data['allowStress']
            rwmaterial.brittlefracturethickness=data['brittleThick']
            rwmaterial.corrosionallowance=data['corrosionAllow']
            rwmaterial.carbonlowalloy=carbonLowAlloySteel
            rwmaterial.austenitic=austeniticSteel
            rwmaterial.nickelbased=nickelAlloy
            rwmaterial.chromemoreequal12=chromium
            rwmaterial.sulfurcontent=data['sulfurContent']
            rwmaterial.heattreatment=data['heatTreatment']
            rwmaterial.ispta=materialPTA
            rwmaterial.ptamaterialcode=data['PTAMaterialGrade']
            rwmaterial.costfactor=data['materialCostFactor']
            rwmaterial.save()

            rwinputca.fluid_height=data['fluidHeight']
            rwinputca.shell_course_height=data['shellHieght']
            rwinputca.tank_diametter=data['tankDiameter']
            rwinputca.prevention_barrier=preventBarrier
            rwinputca.environ_sensitivity=data['EnvSensitivity']
            rwinputca.p_lvdike=data['fluidLeaveDike']
            rwinputca.p_offsite=data['fluidOffsite']
            rwinputca.p_onsite=data['fluidOnsite']
            rwinputca.soil_type=data['soiltype']
            rwinputca.tank_fluid=data['fluid']
            rwinputca.api_fluid=apiFluid
            rwinputca.sw=data['distance']
            rwinputca.productioncost=data['productionCost']
            rwinputca.save()

            ReCalculate.ReCalculate(proposalID)
            return redirect('damgeFactor', proposalID= proposalID)
    except:
        raise Http404
    return render(request, 'FacilityUI/proposal/proposalTankEdit.html', {'isshell':isshell,'rwAss':rwassessment,
                                                                         'rwEq':rwequipment,'rwComp':rwcomponent,
                                                                         'rwStream':rwstream,'rwExcot':rwexcor,
                                                                         'rwCoat':rwcoat, 'rwMaterial':rwmaterial, 'rwInputCa':rwinputca,
                                                                         'assDate': assDate, 'extDate': extDate,
                                                                         'componentID': comp.componentid,
                                                                         'equipmentID': comp.equipmentid_id})
def RiskMatrix(request, proposalID):
    try:
        locatAPI1 = {}
        locatAPI2 = {}
        locatAPI3 = {}
        locatAPI1['x'] = 0
        locatAPI1['y'] = 500

        locatAPI2['x'] = 0
        locatAPI2['y'] = 500

        locatAPI3['x'] = 0
        locatAPI3['y'] = 500

        df = models.RwFullPof.objects.get(id=proposalID)
        ca = models.RwFullFcof.objects.get(id=proposalID)
        rwAss = models.RwAssessment.objects.get(id=proposalID)
        component = models.ComponentMaster.objects.get(componentid=rwAss.componentid_id)
        if component.componenttypeid_id == 8 or component.componenttypeid_id == 12 or component.componenttypeid_id == 14 or component.componenttypeid_id == 15:
            isTank = 1
        else:
            isTank = 0

        if component.componenttypeid_id == 8 or component.componenttypeid_id == 14:
            isShell = 1
        else:
            isShell = 0
        Ca = round(ca.fcofvalue, 2)
        DF1 = round(df.totaldfap1, 2)
        DF2 = round(df.totaldfap2, 2)
        DF3 = round(df.totaldfap3, 2)
    except:
        raise Http404
    return render(request, 'FacilityUI/risk_summary/riskMatrix.html',{'API1':location.locat(df.totaldfap1, ca.fcofvalue), 'API2':location.locat(df.totaldfap2, ca.fcofvalue),
                                                                      'API3':location.locat(df.totaldfap3, ca.fcofvalue),'DF1': DF1,'DF2': DF2,'DF3': DF3, 'ca':Ca,
                                                                      'ass':rwAss,'isTank': isTank, 'isShell': isShell, 'df':df, 'proposalID':proposalID})
def FullyDamageFactor(request, proposalID):
    try:
        df = models.RwFullPof.objects.get(id= proposalID)
        rwAss = models.RwAssessment.objects.get(id= proposalID)
        data={}
        component = models.ComponentMaster.objects.get(componentid=rwAss.componentid_id)
        if component.componenttypeid_id == 8 or component.componenttypeid_id == 12 or component.componenttypeid_id == 14 or component.componenttypeid_id == 15:
            isTank = 1
        else:
            isTank = 0
        if component.componenttypeid_id == 8 or component.componenttypeid_id == 14:
            isShell = 1
        else:
            isShell = 0
        data['thinningType'] = df.thinningtype
        data['gfftotal'] = df.gfftotal
        data['fms'] = df.fms
        data['thinningap1'] = roundData.roundDF(df.thinningap1)
        data['thinningap2'] = roundData.roundDF(df.thinningap2)
        data['thinningap3'] = roundData.roundDF(df.thinningap3)
        data['sccap1'] = roundData.roundDF(df.sccap1)
        data['sccap2'] = roundData.roundDF(df.sccap2)
        data['sccap3'] = roundData.roundDF(df.sccap3)
        data['externalap1'] = roundData.roundDF(df.externalap1)
        data['externalap2'] = roundData.roundDF(df.externalap2)
        data['externalap3'] = roundData.roundDF(df.externalap3)
        data['htha_ap1'] = roundData.roundDF(df.htha_ap1)
        data['htha_ap2'] = roundData.roundDF(df.htha_ap2)
        data['htha_ap3'] = roundData.roundDF(df.htha_ap3)
        data['brittleap1'] = roundData.roundDF(df.brittleap1)
        data['brittleap2'] = roundData.roundDF(df.brittleap2)
        data['brittleap3'] = roundData.roundDF(df.brittleap3)
        data['fatigueap1'] = roundData.roundDF(df.fatigueap1)
        data['fatigueap2'] = roundData.roundDF(df.fatigueap2)
        data['fatigueap3'] = roundData.roundDF(df.fatigueap3)
        data['thinninggeneralap1'] = roundData.roundDF(df.thinninggeneralap1)
        data['thinninggeneralap2'] = roundData.roundDF(df.thinninggeneralap2)
        data['thinninggeneralap3'] = roundData.roundDF(df.thinninggeneralap3)
        data['thinninglocalap1'] = roundData.roundDF(df.thinninglocalap1)
        data['thinninglocalap2'] = roundData.roundDF(df.thinninglocalap2)
        data['thinninglocalap3'] = roundData.roundDF(df.thinninglocalap3)
        data['totaldfap1'] = roundData.roundDF(df.totaldfap1)
        data['totaldfap2'] = roundData.roundDF(df.totaldfap2)
        data['totaldfap3'] = roundData.roundDF(df.totaldfap3)
        data['pofap1'] = roundData.roundPoF(df.pofap1)
        data['pofap2'] = roundData.roundPoF(df.pofap2)
        data['pofap3'] = roundData.roundPoF(df.pofap3)
        data['pofap1category'] = df.pofap1category
        data['pofap2category'] = df.pofap2category
        data['pofap3category'] = df.pofap3category
        if request.method == 'POST':
            df.thinningtype = request.POST.get('thinningType')
            df.save()
            ReCalculate.ReCalculate(proposalID)
            return redirect('damgeFactor', proposalID)
    except Exception as e:
        print(e)
        raise Http404
    return render(request, 'FacilityUI/risk_summary/dfFull.html', {'obj':data, 'assess': rwAss, 'isTank': isTank,
                                                                   'isShell': isShell, 'proposalID':proposalID})
def FullyConsequence(request, proposalID):
    data = {}
    try:
        rwAss = models.RwAssessment.objects.get(id=proposalID)
        component = models.ComponentMaster.objects.get(componentid=rwAss.componentid_id)
        if component.componenttypeid_id == 12 or component.componenttypeid_id == 15:
            isBottom = 1
        else:
            isBottom = 0
        if component.componenttypeid_id == 8 or component.componenttypeid_id == 14:
            isShell = 1
        else:
            isShell = 0
        if isBottom:
            bottomConsequences = models.RwCaTank.objects.get(id=proposalID)
            data['hydraulic_water'] = roundData.roundFC(bottomConsequences.hydraulic_water)
            data['hydraulic_fluid'] = roundData.roundFC(bottomConsequences.hydraulic_fluid)
            data['seepage_velocity'] = roundData.roundFC(bottomConsequences.seepage_velocity)
            data['flow_rate_d1'] = roundData.roundFC(bottomConsequences.flow_rate_d1)
            data['flow_rate_d4'] = roundData.roundFC(bottomConsequences.flow_rate_d4)
            data['leak_duration_d1'] = roundData.roundFC(bottomConsequences.leak_duration_d1)
            data['leak_duration_d4'] = roundData.roundFC(bottomConsequences.leak_duration_d4)
            data['release_volume_leak_d1'] = roundData.roundFC(bottomConsequences.release_volume_leak_d1)
            data['release_volume_leak_d4'] = roundData.roundFC(bottomConsequences.release_volume_leak_d4)
            data['release_volume_rupture'] = roundData.roundFC(bottomConsequences.release_volume_rupture)
            data['time_leak_ground'] = roundData.roundFC(bottomConsequences.time_leak_ground)
            data['volume_subsoil_leak_d1'] = roundData.roundFC(bottomConsequences.volume_subsoil_leak_d1)
            data['volume_subsoil_leak_d4'] = roundData.roundFC(bottomConsequences.volume_subsoil_leak_d4)
            data['volume_ground_water_leak_d1'] = roundData.roundFC(bottomConsequences.volume_ground_water_leak_d1)
            data['volume_ground_water_leak_d4'] = roundData.roundFC(bottomConsequences.volume_ground_water_leak_d4)
            data['barrel_dike_rupture'] = roundData.roundFC(bottomConsequences.barrel_dike_rupture)
            data['barrel_onsite_rupture'] = roundData.roundFC(bottomConsequences.barrel_onsite_rupture)
            data['barrel_offsite_rupture'] = roundData.roundFC(bottomConsequences.barrel_offsite_rupture)
            data['barrel_water_rupture'] = roundData.roundFC(bottomConsequences.barrel_water_rupture)
            data['fc_environ_leak'] = roundData.roundMoney(bottomConsequences.fc_environ_leak)
            data['fc_environ_rupture'] = roundData.roundMoney(bottomConsequences.fc_environ_rupture)
            data['fc_environ'] = roundData.roundMoney(bottomConsequences.fc_environ)
            data['material_factor'] = bottomConsequences.material_factor
            data['component_damage_cost'] = roundData.roundMoney(bottomConsequences.component_damage_cost)
            data['business_cost'] = roundData.roundMoney(bottomConsequences.business_cost)
            data['consequence'] = roundData.roundMoney(bottomConsequences.consequence)
            data['consequencecategory'] = bottomConsequences.consequencecategory
            return render(request, 'FacilityUI/risk_summary/fullyBottomConsequence.html', {'data': data, 'proposalID':proposalID, 'ass':rwAss})
        elif isShell:
            shellConsequences = models.RwCaTank.objects.get(id=proposalID)
            data['flow_rate_d1'] = roundData.roundFC(shellConsequences.flow_rate_d1)
            data['flow_rate_d2'] = roundData.roundFC(shellConsequences.flow_rate_d2)
            data['flow_rate_d3'] = roundData.roundFC(shellConsequences.flow_rate_d3)
            data['flow_rate_d4'] = roundData.roundFC(shellConsequences.flow_rate_d4)
            data['leak_duration_d1'] = roundData.roundFC(shellConsequences.leak_duration_d1)
            data['leak_duration_d2'] = roundData.roundFC(shellConsequences.leak_duration_d2)
            data['leak_duration_d3'] = roundData.roundFC(shellConsequences.leak_duration_d3)
            data['leak_duration_d4'] = roundData.roundFC(shellConsequences.leak_duration_d4)
            data['release_volume_leak_d1'] = roundData.roundFC(shellConsequences.release_volume_leak_d1)
            data['release_volume_leak_d2'] = roundData.roundFC(shellConsequences.release_volume_leak_d2)
            data['release_volume_leak_d3'] = roundData.roundFC(shellConsequences.release_volume_leak_d3)
            data['release_volume_leak_d4'] = roundData.roundFC(shellConsequences.release_volume_leak_d4)
            data['release_volume_rupture'] = roundData.roundFC(shellConsequences.release_volume_rupture)
            data['time_leak_ground'] = roundData.roundFC(shellConsequences.time_leak_ground)
            data['volume_subsoil_leak_d1'] = roundData.roundFC(shellConsequences.volume_subsoil_leak_d1)
            data['volume_subsoil_leak_d4'] = roundData.roundFC(shellConsequences.volume_subsoil_leak_d4)
            data['volume_ground_water_leak_d1'] = roundData.roundFC(shellConsequences.volume_ground_water_leak_d1)
            data['volume_ground_water_leak_d4'] = roundData.roundFC(shellConsequences.volume_ground_water_leak_d4)
            data['barrel_dike_rupture'] = roundData.roundFC(shellConsequences.barrel_dike_rupture)
            data['barrel_onsite_rupture'] = roundData.roundFC(shellConsequences.barrel_onsite_rupture)
            data['barrel_offsite_rupture'] = roundData.roundFC(shellConsequences.barrel_offsite_rupture)
            data['barrel_water_rupture'] = roundData.roundFC(shellConsequences.barrel_water_rupture)
            data['fc_environ_leak'] = roundData.roundMoney(shellConsequences.fc_environ_leak)
            data['fc_environ_rupture'] = roundData.roundMoney(shellConsequences.fc_environ_rupture)
            data['fc_environ'] = roundData.roundMoney(shellConsequences.fc_environ)
            data['component_damage_cost'] = roundData.roundMoney(shellConsequences.component_damage_cost)
            data['business_cost'] = roundData.roundMoney(shellConsequences.business_cost)
            data['consequence'] = roundData.roundMoney(shellConsequences.consequence)
            data['consequencecategory'] = shellConsequences.consequencecategory
            return render(request, 'FacilityUI/risk_summary/fullyShellConsequence.html', {'data': data, 'proposalID':proposalID, 'ass':rwAss})
        else:
            ca = models.RwCaLevel1.objects.get(id= proposalID)
            inputCa = models.RwInputCaLevel1.objects.get(id= proposalID)
            data['production_cost'] = roundData.roundMoney(inputCa.production_cost)
            data['equipment_cost'] = roundData.roundMoney(inputCa.equipment_cost)
            data['personal_density'] = inputCa.personal_density
            data['evironment_cost'] = roundData.roundMoney(inputCa.evironment_cost)
            data['ca_cmd'] = roundData.roundFC(ca.ca_cmd)
            data['ca_inj_flame'] = roundData.roundFC(ca.ca_inj_flame)
            data['fc_cmd'] = roundData.roundMoney(ca.fc_cmd)
            data['fc_affa'] = roundData.roundMoney(ca.fc_affa)
            data['fc_prod'] = roundData.roundMoney(ca.fc_prod)
            data['fc_inj'] = roundData.roundMoney(ca.fc_inj)
            data['fc_envi'] = roundData.roundMoney(ca.fc_envi)
            data['fc_total'] = roundData.roundMoney(ca.fc_total)
            data['fcof_category'] = ca.fcof_category
            return render(request, 'FacilityUI/risk_summary/fullyNormalConsequence.html', {'data': data, 'proposalID':proposalID, 'ass':rwAss})
    except:
        raise Http404
def RiskChart(request, proposalID):
    try:
        rwAssessment = models.RwAssessment.objects.get(id= proposalID)
        print(rwAssessment)
        rwFullpof = models.RwFullPof.objects.get(id= proposalID)
        rwFullcof = models.RwFullFcof.objects.get(id= proposalID)
        risk = rwFullpof.pofap1 * rwFullcof.fcofvalue
        chart = models.RwDataChart.objects.get(id= proposalID)
        assessmentDate = rwAssessment.assessmentdate
        dataChart = [risk, chart.riskage1, chart.riskage2, chart.riskage3, chart.riskage4, chart.riskage5, chart.riskage6,
                     chart.riskage7, chart.riskage8, chart.riskage9, chart.riskage9, chart.riskage10, chart.riskage11,
                     chart.riskage12, chart.riskage13, chart.riskage14, chart.riskage15]
        dataLabel = [date2Str.date2str(assessmentDate), date2Str.date2str(date2Str.dateFuture(assessmentDate,1)),
                     date2Str.date2str(date2Str.dateFuture(assessmentDate, 2)),date2Str.date2str(date2Str.dateFuture(assessmentDate,3)),
                     date2Str.date2str(date2Str.dateFuture(assessmentDate, 4)),date2Str.date2str(date2Str.dateFuture(assessmentDate,5)),
                     date2Str.date2str(date2Str.dateFuture(assessmentDate, 6)),date2Str.date2str(date2Str.dateFuture(assessmentDate,7)),
                     date2Str.date2str(date2Str.dateFuture(assessmentDate, 8)),date2Str.date2str(date2Str.dateFuture(assessmentDate,9)),
                     date2Str.date2str(date2Str.dateFuture(assessmentDate, 10)),date2Str.date2str(date2Str.dateFuture(assessmentDate,11)),
                     date2Str.date2str(date2Str.dateFuture(assessmentDate, 12)),date2Str.date2str(date2Str.dateFuture(assessmentDate,13)),
                     date2Str.date2str(date2Str.dateFuture(assessmentDate, 14))]
        dataTarget = [chart.risktarget,chart.risktarget,chart.risktarget,chart.risktarget,chart.risktarget,chart.risktarget,
                      chart.risktarget,chart.risktarget,chart.risktarget,chart.risktarget,chart.risktarget,chart.risktarget,
                      chart.risktarget,chart.risktarget,chart.risktarget,chart.risktarget]
        endLabel = date2Str.date2str(date2Str.dateFuture(assessmentDate, 15))
        content = {'label': dataLabel, 'data':dataChart, 'target':dataTarget, 'endLabel':endLabel, 'proposalname':rwAssessment.proposalname,
                   'proposalID':rwAssessment.id, 'componentID':rwAssessment.componentid_id}
        return render(request, 'FacilityUI/risk_summary/riskChart.html', content)
    except:
        raise Http404
def ExportExcel(request, index, type):
    try:
        return export_data.excelExport(index, type)
    except:
        raise Http404
def upload(request, siteID):
    try:
        showcontent = "Choose plan process file"
        if request.method =='POST' and request.FILES['myexcelFile']:
            myfile = request.FILES['myexcelFile']
            fs = FileSystemStorage()
            filename = fs.save(myfile.name, myfile)
            uploaded_file_url = fs.url(filename)
            url_file = settings.BASE_DIR.replace('\\', '//') + str(uploaded_file_url).replace('/', '//').replace('%20', ' ')
            ExcelImport.importPlanProcess(url_file)
            try:
                os.remove(url_file)
            except OSError:
                pass
    except:
        raise Http404
    return render(request, 'FacilityUI/facility/uploadData.html', {'siteID': siteID, 'showcontent': showcontent})
def uploadInspPlan(request, siteID):
    try:
        showcontent = "Choose inspection history file"
        if request.method == 'POST' and request.FILES['myexcelFile']:
            myfile = request.FILES['myexcelFile']
            fs = FileSystemStorage()
            filename = fs.save(myfile.name, myfile)
            upload_url = fs.url(filename)
            url_file = settings.BASE_DIR.replace('\\', '//') + str(upload_url).replace('/', '//').replace('%20', ' ')
            ExcelImport.importInspectionPlan(url_file)
            try:
                os.remove(url_file)
            except OSError:
                pass
    except Exception as e:
        print(e)
        raise Http404
    return render(request, 'FacilityUI/facility/uploadData.html' ,{'siteID': siteID, 'showcontent': showcontent})

############### Dang Nhap Dang Suat #################
def signin(request):
    error = ''
    try:
        if request.session.has_key('id'):
            if request.session['kind']=='citizen':
                return redirect('citizenHome')
            elif request.session['kind']=='factory':
                facilityID1 = models.Sites.objects.filter(userID_id=request.session['id'])[0].siteid
                return redirect('facilitiesDisplay',facilityID1)
            elif request.session['kind']=='manager':
                return redirect('manager',3)
        else:
            if request.method=='POST':
                xuser=request.POST.get('txtuser')
                xpass=request.POST.get('txtpass')
                data=models.ZUser.objects.filter(Q(username=xuser),Q(password=xpass),Q(active=1))
                if data.count():
                    request.session['id']=data[0].id
                    request.session['name']=data[0].name
                    request.session['kind']=data[0].kind
                    request.session['phone']=data[0].phone
                    request.session['address'] = data[0].adress
                    request.session['email'] = data[0].email
                    request.session['other_info'] = data[0].other_info
                    request.session.set_expiry(0)
                    if request.session['kind']=='citizen':
                        return redirect('citizenHome')
                    elif request.session['kind']=='factory':
                        facilityID = models.Sites.objects.filter(userID_id=request.session['id'])[0].siteid
                        return redirect('facilitiesDisplay',facilityID)
                    else:
                        return redirect('manager',3)
                else:
                    error="Tài khoản hoặc mật khẩu không đúng"
            return render(request,'Home/index.html',{'error':error})
    except Exception as e:
        print(e)
        raise Http404
def logout(request):
    try:
        del request.session['id']
        request.session.flush()
    except:
        pass
    return redirect('home')

################## Forum Dien Dan ###################
def base_forum(request):
    if request.session.has_key('id'):
        if 'btnsend' in request.POST:
            xtitle=request.POST.get('txttitle')
            xcontent=request.POST.get('txtcontent')
            xtag=request.POST.get('txttag')
            a=models.ZPosts(title=xtitle,tag=xtag,content=xcontent,time=datetime.now(),id_user=request.session['id'],views=0)
            a.save()
        mang=[]
        data=models.ZPosts.objects.all()
        for dataposts in data:
            posts={}
            posts['id']=dataposts.id
            posts['id_user']=dataposts.id_user
            posts['title']=dataposts.title
            posts['content']=dataposts.content
            posts['time']=dataposts.time
            posts['tag']=dataposts.tag
            posts['views']=dataposts.views
            posts['reply']=models.ZComment.objects.all().filter(id_posts=dataposts.id).count()
            mang.append(posts)
        noti=models.ZNotification.objects.all().filter(id_user=request.session['id'])
        countnoti=noti.filter(state=0).count()
        return render(request,'BaseUI/BaseForum/forumhome.html',{'data':mang, 'noti':noti, 'countnoti':countnoti})
    else:
        return redirect('home')
def posts_forum(request,postID):
    a=models.ZPosts.objects.filter(id=postID)[0]
    a.views+=1
    a.save()
    nameuserpost=models.ZUser.objects.all().filter(id=a.id_user)[0].name
    if request.session['id']==a.id_user:
        noti=models.ZNotification.objects.all().filter(link=postID)
        for notifi in noti:
            notifi.state=1
            notifi.save()
    if 'btncomment' in request.POST:
        xcontent=request.POST.get('txtcomment')
        data=models.ZComment(content=xcontent,time=datetime.now(),id_posts=postID,id_user=request.session['id'])
        data.save() #Thêm thông tin comment vào csdl
        #chức năng thông báo
        id_user=models.ZPosts.objects.all().filter(id=postID)[0].id_user #Lấy ID người đăng bài
        title_post = models.ZPosts.objects.all().filter(id=postID)[0].title
        if request.session['id']!=id_user:
            noti=models.ZNotification(id_user=id_user,subject=request.session['name'],content=' đã phản hồi bài viết ', object=title_post,link=postID,time=datetime.now())
            noti.save()

    comment=models.ZComment.objects.all().filter(id_posts=postID)#Lấy dữ liệu comment của this post
    datacmt=[]
    for data in comment:
        cmt={}
        cmt['name']=models.ZUser.objects.all().filter(id=data.id_user)[0].name
        cmt['content']=data.content
        datacmt.append(cmt)#mang chua Du lieu cac comment
    noti = models.ZNotification.objects.all().filter(id_user=request.session['id'])
    countnoti = noti.filter(state=0).count()
    return render(request,'BaseUI/BaseForum/forumposts.html',{'data':a,'nameuserpost':nameuserpost,'datacmt':datacmt,'session':request.session,'noti':noti, 'countnoti':countnoti})

################## Tin nhan Email ###################
def MassagesHome(request):
    datacontent = models.Emailto.objects.filter(Emailt=models.ZUser.objects.filter(id=request.session['id'])[0].email)
    try:
        if 'post' in request.POST:
            data={}
            data['emailto']=request.POST.get('sentto')
            print(data['emailto'])
            print(request.session['id'])
            data['subject']=request.POST.get('subject')
            data['emailsent']=models.ZUser.objects.filter(id=request.session['id'])[0].email
            data['content']=request.POST.get('content')
            a=models.Emailsent(content=data['content'],subject=data['subject'],Emails=data['emailsent'],Emailt=data['emailto'])
            a.save()
            b=models.Emailto(content=data['content'],subject=data['subject'],Emails=data['emailsent'],Emailt=data['emailto'],Is_see=0)
            b.save()
        if request.method=='POST':
            for data1 in datacontent:
                if request.POST.get('%d' %data1.id):
                    print(data1.id)
                    email1=models.Emailto.objects.get(id=data1.id)
                    email1.delete()
                    return redirect('massages')
    except Exception as e:
        print(e)
        Http404
    return render(request,'BaseUI/BaseMassages/BaseMassages.html',{'datacontent':datacontent})
def Email_Massage_sent(request):
    datacontent = models.Emailsent.objects.filter(Emails=models.ZUser.objects.filter(id=request.session['id'])[0].email)
    try:
        if 'post' in request.POST:
            data = {}
            data['emailto'] = request.POST.get('sentto')
            print(data['emailto'])
            print(request.session['id'])
            data['subject'] = request.POST.get('subject')
            data['emailsent'] = models.ZUser.objects.filter(id=request.session['id'])[0].email
            data['content'] = request.POST.get('content')
            a = models.Emailsent(content=data['content'], subject=data['subject'],Emails=data['emailsent'],Emailt=data['emailto'])
            a.save()
            b = models.Emailto(content=data['content'], subject=data['subject'], Emails=data['emailsent'],Emailt=data['emailto'], Is_see=0)
            b.save()
        if request.method == 'POST':
            for data1 in datacontent:
                if request.POST.get('%d' % data1.id):
                    print(data1.id)
                    email1 = models.Emailsent.objects.get(id=data1.id)
                    email1.delete()
                    return redirect('massagessent')
    except Exception as e:
        print(e)
        Http404
    return render(request, 'BaseUI/BaseMassages/Massages_sent.html', {'datacontent':datacontent})

################# Help #############
def Help(requset):
    print('aa')
    return render(requset,'help/help.html')

################ Dang ki tai khoan ####################
def AccountCitizen(request):
    infor = {}
    try:
        if request.method == "POST":
            user = request.POST.get('username')
            name = request.POST.get('name')
            # last_name = request.POST.get('txtlname')
            password = request.POST.get('txtpass')
            repassword = request.POST.get('repass')
            phone = request.POST.get('txtmobile')
            email = request.POST.get('txtmail')
            addr = request.POST.get('txtadd')
            kind = 'citizen'
            desc = request.POST.get('CompanyInformation')
            # print(companyName + " " + user + " " + email)
            if password == repassword:
                authUser = models.ZUser.objects.filter(Q(username=user) | Q(email=email))
                print("ok")
                if authUser.count() > 0:
                    infor['exist'] = "This User Name or E-mail was taken"
                    print(infor['exist'])
                else:
                    try:
                        authUser1 = models.ZUser(username=user, phone=phone, adress=addr, email=email, name=name,
                                                 kind=kind, password=password)
                        authUser1.save()
                        print(authUser1.username)
                        # profile = models.ZProfilebisiness(user_id=authUser1.id, organization_detail=desc)
                        # profile.save()
                    except Exception as e:
                        print(e)
                    current_site = get_current_site(request)
                    print("a")
                    email_subject = "Activate your block account"
                    message = render_to_string('Home/Account/activateEmail.html', {
                        'user': authUser1,
                        'domain': current_site.domain,
                        'uid': urlsafe_base64_encode(force_bytes(authUser1.pk)).decode(),
                        'token': gen_token.make_token(authUser1)
                    })
                    print('ok')
                    to_email = email
                    Email = EmailMessage(email_subject, message, to=[to_email])
                    Email.send()
                    print("sended")
                    # return HttpResponse("Please confirm in your e-mail")
                    return render_to_response('response/complete_regiatration.html')
            else:
                infor['match'] = "The password is not match"
    except Exception as e:
        print(e)
    return render(request, 'Home/Account/sigup_citizen.html')
def AccountBusiness(request):
    infor = {}
    try:
        if request.method == "POST":
            companyName = request.POST.get('companyname_business')
            user = request.POST.get('username')
            # first_name = request.POST.get('first_name')
            # last_name = request.POST.get('last_name')
            name=request.POST.get('name')
            password = request.POST.get('password')
            repassword = request.POST.get('repassword')
            phone = request.POST.get('phone')
            email = request.POST.get('txtmail')
            addr = request.POST.get('txtadd')
            kind='factory'
            desc = request.POST.get('CompanyInformation')
            print(companyName + " " + user + " " + email)
            if password == repassword:
                authUser = models.ZUser.objects.filter(Q(username=user) | Q(email=email))
                print("ok")
                if authUser.count() > 0:
                    infor['exist'] = "This User Name or E-mail was taken"
                    print(infor['exist'])
                else:
                    try:
                        authUser1 = models.ZUser(username=user,phone=phone,adress=addr ,email=email,name=name,kind=kind ,password=password)
                        authUser1.save()
                        print(authUser1.username)
                        fa = models.Sites(sitename=companyName, userID_id=authUser1.id)
                        fa.save()
                    except Exception as e:
                        print(e)
                    current_site = get_current_site(request)
                    print("a")
                    email_subject = "Activate your block account"
                    message = render_to_string('Home/Account/activateEmail.html', {
                        'user': authUser1,
                        'domain': current_site.domain,
                        'uid': urlsafe_base64_encode(force_bytes(authUser1.pk)).decode(),
                        'token': gen_token.make_token(authUser1)
                    })
                    print('ok')
                    to_email = email
                    Email = EmailMessage(email_subject, message, to=[to_email])
                    Email.send()
                    print("sended")
                    # return HttpResponse("Please confirm in your e-mail")
                    return render_to_response('response/complete_regiatration.html')
            else:
                infor['match'] = "The password is not match"
    except Exception as e:
        print(e)
    return render(request, 'Home/Account/signup_business.html')
def AccountManagement(request):
    infor = {}
    try:
        if request.method == "POST":
            org_name = request.POST.get('org_name_mng')
            user = request.POST.get('username_mng')
            # first_name = request.POST.get('first_name')
            # last_name = request.POST.get('last_name')
            name = request.POST.get('name')
            password = request.POST.get('pass_mng')
            repassword = request.POST.get('repass_mng')
            phone = request.POST.get('phone_mng')
            email = request.POST.get('email_mng')
            addr = request.POST.get('addr_mng')
            web = request.POST.get('web_mng')
            desc = request.POST.get('desc')
            kind='manager'
            print(org_name + " " + user + " " + email)
            if password == repassword:
                authUser = models.ZUser.objects.filter(Q(username=user) | Q(email=email))
                print("ok")
                if authUser.count() > 0:
                    infor['exist'] = "This User Name or E-mail was taken"
                    print(infor['exist'])
                else:
                    try:
                        authUser1 = models.ZUser(username=user, phone=phone, adress=addr, email=email, name=name,
                                                 kind=kind, password=password)
                        authUser1.save()
                        print(authUser1.username)
                        # profile = models.ZProfilebisiness(user_id=authUser1.id, organization_detail=desc)
                        # profile.save()
                    except Exception as e:
                        print(e)
                    current_site = get_current_site(request)
                    print("a")
                    email_subject = "Activate your block account"
                    message = render_to_string('Home/Account/activateEmail.html', {
                        'user': authUser1,
                        'domain': current_site.domain,
                        'uid': urlsafe_base64_encode(force_bytes(authUser1.pk)).decode(),
                        'token': gen_token.make_token(authUser1)
                    })
                    print('ok')
                    to_email = email
                    Email = EmailMessage(email_subject, message, to=[to_email])
                    Email.send()
                    print("sended")
                    # return HttpResponse("Please confirm in your e-mail")
                    return render_to_response('response/complete_regiatration.html')
            else:
                infor['match'] = "The password is not match"
    except Exception as e:
        print(e)
    return render(request, 'Home/Account/signup_management.html')
def activate(request, uidb64, token):
    try:
        # uid = force_text(urlsafe_base64_decode(uidb64))
        uid = urlsafe_base64_decode(uidb64).decode()
        user = models.ZUser.objects.get(pk=uid)
        print("1")
    except(TypeError, ValueError, OverflowError, models.ZUser.DoesNotExist):
        user = None
    print(gen_token.check_token(user, token))
    print("2")
    if user is not None and gen_token.check_token(user, token):
        user.active = True
        user.save()
        # login(request, user)
        # return HttpResponse("Activate is complete! Thanks for use our services")
        print("aaaaaa")
        return render_to_response('response/totally_complete.html')
    else:
        print(user.username)
        return HttpResponse("Can't activate now, please try again later or contact us")

################ Manager UI Control ###################
def ManagerHome(request, siteID):
    count = models.Emailto.objects.filter(Q(Emailt=models.ZUser.objects.filter(id=request.session['id'])[0].email), Q(Is_see=0)).count()
    try:
        risk = []

        data = models.Sites.objects.all()
        # print(data.facilityname)
        for a in data:
            dataF = {}
            # risTarget = models.FacilityRiskTarget.objects.get(facilityid= a.facilityid)
            dataF['ID'] = a.siteid
            dataF['SideName'] = a.sitename
            # dataF['ManagementFactor'] = a.managementfactor
            # dataF['RiskTarget'] = risTarget.risktarget_fc
            risk.append(dataF)

        ## so doi tuong co tren 1 trang web ##
        pagiFaci = Paginator(risk, 25)
        pageFaci = request.GET.get('page',1)
        try:
            users = pagiFaci.page(pageFaci)
        except PageNotAnInteger:
            users = pagiFaci.page(1)
        except EmptyPage:
            users = pageFaci.page(pagiFaci.num_pages)
        #########################################
        # if '_edit' in request.POST:
        #     for a in data:
        #         if(request.POST.get('%d' %a.siteid)):
        #             return redirect('facilitiesEdit', a.siteid)
        if '_delete' in request.POST:
            for a in data:
                if(request.POST.get('%d' %a.siteid)):
                    a.delete()
            return redirect('facilitiesDisplay', siteID)
    except:
        raise Http404
    return render(request, 'ManagerUI/Business_List.html', {'obj': users,'siteID':siteID,'count':count})
def ListFacilitiesMana(request, siteID):
    count = models.Emailto.objects.filter(Q(Emailt=models.ZUser.objects.filter(id=request.session['id'])[0].email), Q(Is_see=0)).count()
    try:
        risk = []

        data= models.Facility.objects.filter(siteid= siteID)
        for a in data:
            dataF = {}
            risTarget = models.FacilityRiskTarget.objects.get(facilityid= a.facilityid)
            dataF['ID'] = a.facilityid
            dataF['FacilitiName'] = a.facilityname
            dataF['ManagementFactor'] = a.managementfactor
            dataF['RiskTarget'] = risTarget.risktarget_fc
            risk.append(dataF)

        pagiFaci = Paginator(risk, 25)
        pageFaci = request.GET.get('page',1)
        try:
            users = pagiFaci.page(pageFaci)
        except PageNotAnInteger:
            users = pagiFaci.page(1)
        except EmptyPage:
            users = pageFaci.page(pagiFaci.num_pages)
        if '_edit' in request.POST:
            for a in data:
                if(request.POST.get('%d' %a.facilityid)):
                    return redirect('facilitiesEdit', a.facilityid)
        if '_delete' in request.POST:
            for a in data:
                if(request.POST.get('%d' %a.facilityid)):
                    a.delete()
            return redirect('facilitiesDisplay', siteID)
    except:
        raise Http404
    return render(request, 'ManagerUI/facility_List.html', {'obj': users,'siteID':siteID,'count':count})
def ListEquipmentMana(request, facilityID):
    try:
        faci = models.Facility.objects.get(facilityid= facilityID)
        data = models.EquipmentMaster.objects.filter(facilityid= facilityID)
        pagiEquip = Paginator(data,25)
        pageEquip = request.GET.get('page',1)
        try:
            obj = pagiEquip.page(pageEquip)
        except PageNotAnInteger:
            obj = pagiEquip.page(1)
        except EmptyPage:
            obj = pageEquip.page(pagiEquip.num_pages)
        if '_edit' in request.POST:
            for a in data:
                if request.POST.get('%d' %a.equipmentid):
                    return redirect('equipmentEdit', equipmentID= a.equipmentid)
        if '_delete' in request.POST:
            for a in data:
                if request.POST.get('%d' %a.equipmentid):
                    a.delete()
            return redirect('equipmentDisplay' , facilityID= facilityID)
    except:
        raise Http404
    return render(request, 'ManagerUI/Equipment_List.html', {'obj':obj, 'facilityID':facilityID, 'siteID':faci.siteid_id})
def ListComponentMana(request, equipmentID):
    try:
        eq = models.EquipmentMaster.objects.get(equipmentid= equipmentID)
        data = models.ComponentMaster.objects.filter(equipmentid= equipmentID)
        pagiComp = Paginator(data,25)
        pageComp = request.GET.get('page',1)
        try:
            obj = pagiComp.page(pageComp)
        except PageNotAnInteger:
            obj= pagiComp.page(1)
        except EmptyPage:
            obj = pageComp.page(pagiComp.num_pages)
        if '_edit' in request.POST:
            for a in data:
                if request.POST.get('%a' %a.componentid):
                    return redirect('componentEdit', componentID= a.componentid)
        if '_delete' in request.POST:
            for a in data:
                if request.POST.get('%d' %a.componentid):
                    a.delete()
            return  redirect('componentDisplay', equipmentID= equipmentID)
    except:
        raise Http404
    return render(request, 'ManagerUI/component_List.html', {'obj':obj, 'equipmentID':equipmentID, 'facilityID': eq.facilityid_id})
def ListProposalMana(request, componentID):
    try:
        rwass = models.RwAssessment.objects.filter(componentid= componentID)
        data = []
        comp = models.ComponentMaster.objects.get(componentid= componentID)
        equip = models.EquipmentMaster.objects.get(equipmentid= comp.equipmentid_id)
        tank = [8,12,14,15]
        for a in rwass:
            df = models.RwFullPof.objects.filter(id= a.id)
            fc = models.RwFullFcof.objects.filter(id= a.id)
            dm = models.RwDamageMechanism.objects.filter(id_dm= a.id)
            obj1 = {}
            obj1['id'] = a.id
            obj1['name'] = a.proposalname
            obj1['lastinsp'] = a.assessmentdate.strftime('%Y-%m-%d')
            if df.count() != 0:
                obj1['df'] = round(df[0].totaldfap1, 2)
                obj1['gff'] = df[0].gfftotal
                obj1['fms'] = df[0].fms
            else:
                obj1['df'] = 0
                obj1['gff'] = 0
                obj1['fms'] = 0
            if fc.count() != 0:
                obj1['fc'] = round(fc[0].fcofvalue, 2)
            else:
                obj1['fc'] = 0
            if dm.count() != 0:
                obj1['duedate'] = dm[0].inspduedate.date().strftime('%Y-%m-%d')
            else:
                obj1['duedate'] = (a.assessmentdate.date() + relativedelta(years=15)).strftime('%Y-%m-%d')
                obj1['lastinsp'] = equip.commissiondate.date().strftime('%Y-%m-%d')
            obj1['risk'] = round(obj1['df'] * obj1['gff'] * obj1['fms'] * obj1['fc'], 2)
            data.append(obj1)
        pagidata = Paginator(data,25)
        pagedata = request.GET.get('page',1)
        try:
            obj = pagidata.page(pagedata)
        except PageNotAnInteger:
            obj = pagidata.page(1)
        except EmptyPage:
            obj = pagedata.page(pagidata.num_pages)

        if comp.componenttypeid_id in tank:
            istank = 1
        else:
            istank = 0
        if comp.componenttypeid_id == 8 or comp.componenttypeid_id == 14:
            isshell = 1
        else:
            isshell = 0
        if request.POST:
            if '_delete' in request.POST:
                for a in rwass:
                    if request.POST.get('%d' %a.id):
                        a.delete()
                return redirect('proposalDisplay', componentID=componentID)
            elif '_cancel' in request.POST:
                return redirect('proposalDisplay', componentID=componentID)
            elif '_edit' in request.POST:
                for a in rwass:
                    if request.POST.get('%d' %a.id):
                        if istank:
                            return redirect('tankEdit', proposalID= a.id)
                        else:
                            return redirect('prosalEdit', proposalID= a.id)
            else:
                for a in rwass:
                    if request.POST.get('%d' %a.id):
                        ReCalculate.ReCalculate(a.id)
                return redirect('proposalDisplay', componentID=componentID)
    except:
        raise Http404
    return render(request, 'ManagerUI/proposal_List.html', {'obj':obj, 'istank': istank, 'isshell':isshell,
                                                                            'componentID':componentID,
                                                                            'equipmentID':comp.equipmentid_id})
def FullyDamageFactorMana(request, proposalID):
    try:
        df = models.RwFullPof.objects.get(id= proposalID)
        rwAss = models.RwAssessment.objects.get(id= proposalID)
        data={}
        component = models.ComponentMaster.objects.get(componentid=rwAss.componentid_id)
        if component.componenttypeid_id == 8 or component.componenttypeid_id == 12 or component.componenttypeid_id == 14 or component.componenttypeid_id == 15:
            isTank = 1
        else:
            isTank = 0
        if component.componenttypeid_id == 8 or component.componenttypeid_id == 14:
            isShell = 1
        else:
            isShell = 0
        data['thinningType'] = df.thinningtype
        data['gfftotal'] = df.gfftotal
        data['fms'] = df.fms
        data['thinningap1'] = roundData.roundDF(df.thinningap1)
        data['thinningap2'] = roundData.roundDF(df.thinningap2)
        data['thinningap3'] = roundData.roundDF(df.thinningap3)
        data['sccap1'] = roundData.roundDF(df.sccap1)
        data['sccap2'] = roundData.roundDF(df.sccap2)
        data['sccap3'] = roundData.roundDF(df.sccap3)
        data['externalap1'] = roundData.roundDF(df.externalap1)
        data['externalap2'] = roundData.roundDF(df.externalap2)
        data['externalap3'] = roundData.roundDF(df.externalap3)
        data['htha_ap1'] = roundData.roundDF(df.htha_ap1)
        data['htha_ap2'] = roundData.roundDF(df.htha_ap2)
        data['htha_ap3'] = roundData.roundDF(df.htha_ap3)
        data['brittleap1'] = roundData.roundDF(df.brittleap1)
        data['brittleap2'] = roundData.roundDF(df.brittleap2)
        data['brittleap3'] = roundData.roundDF(df.brittleap3)
        data['fatigueap1'] = roundData.roundDF(df.fatigueap1)
        data['fatigueap2'] = roundData.roundDF(df.fatigueap2)
        data['fatigueap3'] = roundData.roundDF(df.fatigueap3)
        data['thinninggeneralap1'] = roundData.roundDF(df.thinninggeneralap1)
        data['thinninggeneralap2'] = roundData.roundDF(df.thinninggeneralap2)
        data['thinninggeneralap3'] = roundData.roundDF(df.thinninggeneralap3)
        data['thinninglocalap1'] = roundData.roundDF(df.thinninglocalap1)
        data['thinninglocalap2'] = roundData.roundDF(df.thinninglocalap2)
        data['thinninglocalap3'] = roundData.roundDF(df.thinninglocalap3)
        data['totaldfap1'] = roundData.roundDF(df.totaldfap1)
        data['totaldfap2'] = roundData.roundDF(df.totaldfap2)
        data['totaldfap3'] = roundData.roundDF(df.totaldfap3)
        data['pofap1'] = roundData.roundPoF(df.pofap1)
        data['pofap2'] = roundData.roundPoF(df.pofap2)
        data['pofap3'] = roundData.roundPoF(df.pofap3)
        data['pofap1category'] = df.pofap1category
        data['pofap2category'] = df.pofap2category
        data['pofap3category'] = df.pofap3category
        if request.method == 'POST':
            df.thinningtype = request.POST.get('thinningType')
            df.save()
            ReCalculate.ReCalculate(proposalID)
            return redirect('damgeFactor', proposalID)
    except Exception as e:
        print(e)
        raise Http404
    return render(request, 'ManagerUI/RiskSummaryMana/FullDF.html', {'obj':data, 'assess': rwAss, 'isTank': isTank,
                                                                   'isShell': isShell, 'proposalID':proposalID})
def FullyConsequenceMana(request, proposalID):
    data = {}
    try:
        rwAss = models.RwAssessment.objects.get(id=proposalID)
        component = models.ComponentMaster.objects.get(componentid=rwAss.componentid_id)
        if component.componenttypeid_id == 12 or component.componenttypeid_id == 15:
            isBottom = 1
        else:
            isBottom = 0
        if component.componenttypeid_id == 8 or component.componenttypeid_id == 14:
            isShell = 1
        else:
            isShell = 0
        if isBottom:
            bottomConsequences = models.RwCaTank.objects.get(id=proposalID)
            data['hydraulic_water'] = roundData.roundFC(bottomConsequences.hydraulic_water)
            data['hydraulic_fluid'] = roundData.roundFC(bottomConsequences.hydraulic_fluid)
            data['seepage_velocity'] = roundData.roundFC(bottomConsequences.seepage_velocity)
            data['flow_rate_d1'] = roundData.roundFC(bottomConsequences.flow_rate_d1)
            data['flow_rate_d4'] = roundData.roundFC(bottomConsequences.flow_rate_d4)
            data['leak_duration_d1'] = roundData.roundFC(bottomConsequences.leak_duration_d1)
            data['leak_duration_d4'] = roundData.roundFC(bottomConsequences.leak_duration_d4)
            data['release_volume_leak_d1'] = roundData.roundFC(bottomConsequences.release_volume_leak_d1)
            data['release_volume_leak_d4'] = roundData.roundFC(bottomConsequences.release_volume_leak_d4)
            data['release_volume_rupture'] = roundData.roundFC(bottomConsequences.release_volume_rupture)
            data['time_leak_ground'] = roundData.roundFC(bottomConsequences.time_leak_ground)
            data['volume_subsoil_leak_d1'] = roundData.roundFC(bottomConsequences.volume_subsoil_leak_d1)
            data['volume_subsoil_leak_d4'] = roundData.roundFC(bottomConsequences.volume_subsoil_leak_d4)
            data['volume_ground_water_leak_d1'] = roundData.roundFC(bottomConsequences.volume_ground_water_leak_d1)
            data['volume_ground_water_leak_d4'] = roundData.roundFC(bottomConsequences.volume_ground_water_leak_d4)
            data['barrel_dike_rupture'] = roundData.roundFC(bottomConsequences.barrel_dike_rupture)
            data['barrel_onsite_rupture'] = roundData.roundFC(bottomConsequences.barrel_onsite_rupture)
            data['barrel_offsite_rupture'] = roundData.roundFC(bottomConsequences.barrel_offsite_rupture)
            data['barrel_water_rupture'] = roundData.roundFC(bottomConsequences.barrel_water_rupture)
            data['fc_environ_leak'] = roundData.roundMoney(bottomConsequences.fc_environ_leak)
            data['fc_environ_rupture'] = roundData.roundMoney(bottomConsequences.fc_environ_rupture)
            data['fc_environ'] = roundData.roundMoney(bottomConsequences.fc_environ)
            data['material_factor'] = bottomConsequences.material_factor
            data['component_damage_cost'] = roundData.roundMoney(bottomConsequences.component_damage_cost)
            data['business_cost'] = roundData.roundMoney(bottomConsequences.business_cost)
            data['consequence'] = roundData.roundMoney(bottomConsequences.consequence)
            data['consequencecategory'] = bottomConsequences.consequencecategory
            return render(request, 'ManagerUI/RiskSummaryMana/fullyBottomConsequenceMana.html', {'data': data, 'proposalID':proposalID, 'ass':rwAss})
        elif isShell:
            shellConsequences = models.RwCaTank.objects.get(id=proposalID)
            data['flow_rate_d1'] = roundData.roundFC(shellConsequences.flow_rate_d1)
            data['flow_rate_d2'] = roundData.roundFC(shellConsequences.flow_rate_d2)
            data['flow_rate_d3'] = roundData.roundFC(shellConsequences.flow_rate_d3)
            data['flow_rate_d4'] = roundData.roundFC(shellConsequences.flow_rate_d4)
            data['leak_duration_d1'] = roundData.roundFC(shellConsequences.leak_duration_d1)
            data['leak_duration_d2'] = roundData.roundFC(shellConsequences.leak_duration_d2)
            data['leak_duration_d3'] = roundData.roundFC(shellConsequences.leak_duration_d3)
            data['leak_duration_d4'] = roundData.roundFC(shellConsequences.leak_duration_d4)
            data['release_volume_leak_d1'] = roundData.roundFC(shellConsequences.release_volume_leak_d1)
            data['release_volume_leak_d2'] = roundData.roundFC(shellConsequences.release_volume_leak_d2)
            data['release_volume_leak_d3'] = roundData.roundFC(shellConsequences.release_volume_leak_d3)
            data['release_volume_leak_d4'] = roundData.roundFC(shellConsequences.release_volume_leak_d4)
            data['release_volume_rupture'] = roundData.roundFC(shellConsequences.release_volume_rupture)
            data['time_leak_ground'] = roundData.roundFC(shellConsequences.time_leak_ground)
            data['volume_subsoil_leak_d1'] = roundData.roundFC(shellConsequences.volume_subsoil_leak_d1)
            data['volume_subsoil_leak_d4'] = roundData.roundFC(shellConsequences.volume_subsoil_leak_d4)
            data['volume_ground_water_leak_d1'] = roundData.roundFC(shellConsequences.volume_ground_water_leak_d1)
            data['volume_ground_water_leak_d4'] = roundData.roundFC(shellConsequences.volume_ground_water_leak_d4)
            data['barrel_dike_rupture'] = roundData.roundFC(shellConsequences.barrel_dike_rupture)
            data['barrel_onsite_rupture'] = roundData.roundFC(shellConsequences.barrel_onsite_rupture)
            data['barrel_offsite_rupture'] = roundData.roundFC(shellConsequences.barrel_offsite_rupture)
            data['barrel_water_rupture'] = roundData.roundFC(shellConsequences.barrel_water_rupture)
            data['fc_environ_leak'] = roundData.roundMoney(shellConsequences.fc_environ_leak)
            data['fc_environ_rupture'] = roundData.roundMoney(shellConsequences.fc_environ_rupture)
            data['fc_environ'] = roundData.roundMoney(shellConsequences.fc_environ)
            data['component_damage_cost'] = roundData.roundMoney(shellConsequences.component_damage_cost)
            data['business_cost'] = roundData.roundMoney(shellConsequences.business_cost)
            data['consequence'] = roundData.roundMoney(shellConsequences.consequence)
            data['consequencecategory'] = shellConsequences.consequencecategory
            return render(request, 'ManagerUI/RiskSummaryMana/fullySellConsequenceMana.html', {'data': data, 'proposalID':proposalID, 'ass':rwAss})
        else:
            ca = models.RwCaLevel1.objects.get(id= proposalID)
            inputCa = models.RwInputCaLevel1.objects.get(id= proposalID)
            data['production_cost'] = roundData.roundMoney(inputCa.production_cost)
            data['equipment_cost'] = roundData.roundMoney(inputCa.equipment_cost)
            data['personal_density'] = inputCa.personal_density
            data['evironment_cost'] = roundData.roundMoney(inputCa.evironment_cost)
            data['ca_cmd'] = roundData.roundFC(ca.ca_cmd)
            data['ca_inj_flame'] = roundData.roundFC(ca.ca_inj_flame)
            data['fc_cmd'] = roundData.roundMoney(ca.fc_cmd)
            data['fc_affa'] = roundData.roundMoney(ca.fc_affa)
            data['fc_prod'] = roundData.roundMoney(ca.fc_prod)
            data['fc_inj'] = roundData.roundMoney(ca.fc_inj)
            data['fc_envi'] = roundData.roundMoney(ca.fc_envi)
            data['fc_total'] = roundData.roundMoney(ca.fc_total)
            data['fcof_category'] = ca.fcof_category
            return render(request, 'ManagerUI/RiskSummaryMana/fullyNormalConsequenceMana.html', {'data': data, 'proposalID':proposalID, 'ass':rwAss})
    except:
        raise Http404
def RiskChartMana(request, proposalID):
    try:
        rwAssessment = models.RwAssessment.objects.get(id= proposalID)
        print(rwAssessment)
        rwFullpof = models.RwFullPof.objects.get(id= proposalID)
        rwFullcof = models.RwFullFcof.objects.get(id= proposalID)
        risk = rwFullpof.pofap1 * rwFullcof.fcofvalue
        chart = models.RwDataChart.objects.get(id= proposalID)
        assessmentDate = rwAssessment.assessmentdate
        dataChart = [risk, chart.riskage1, chart.riskage2, chart.riskage3, chart.riskage4, chart.riskage5, chart.riskage6,
                     chart.riskage7, chart.riskage8, chart.riskage9, chart.riskage9, chart.riskage10, chart.riskage11,
                     chart.riskage12, chart.riskage13, chart.riskage14, chart.riskage15]
        dataLabel = [date2Str.date2str(assessmentDate), date2Str.date2str(date2Str.dateFuture(assessmentDate,1)),
                     date2Str.date2str(date2Str.dateFuture(assessmentDate, 2)),date2Str.date2str(date2Str.dateFuture(assessmentDate,3)),
                     date2Str.date2str(date2Str.dateFuture(assessmentDate, 4)),date2Str.date2str(date2Str.dateFuture(assessmentDate,5)),
                     date2Str.date2str(date2Str.dateFuture(assessmentDate, 6)),date2Str.date2str(date2Str.dateFuture(assessmentDate,7)),
                     date2Str.date2str(date2Str.dateFuture(assessmentDate, 8)),date2Str.date2str(date2Str.dateFuture(assessmentDate,9)),
                     date2Str.date2str(date2Str.dateFuture(assessmentDate, 10)),date2Str.date2str(date2Str.dateFuture(assessmentDate,11)),
                     date2Str.date2str(date2Str.dateFuture(assessmentDate, 12)),date2Str.date2str(date2Str.dateFuture(assessmentDate,13)),
                     date2Str.date2str(date2Str.dateFuture(assessmentDate, 14))]
        dataTarget = [chart.risktarget,chart.risktarget,chart.risktarget,chart.risktarget,chart.risktarget,chart.risktarget,
                      chart.risktarget,chart.risktarget,chart.risktarget,chart.risktarget,chart.risktarget,chart.risktarget,
                      chart.risktarget,chart.risktarget,chart.risktarget,chart.risktarget]
        endLabel = date2Str.date2str(date2Str.dateFuture(assessmentDate, 15))
        content = {'label': dataLabel, 'data':dataChart, 'target':dataTarget, 'endLabel':endLabel, 'proposalname':rwAssessment.proposalname,
                   'proposalID':rwAssessment.id, 'componentID':rwAssessment.componentid_id}
        return render(request, 'ManagerUI/RiskSummaryMana/riskChartMana.html', content)
    except:
        raise Http404
def RiskMatrixMana(request, proposalID):
    try:
        locatAPI1 = {}
        locatAPI2 = {}
        locatAPI3 = {}
        locatAPI1['x'] = 0
        locatAPI1['y'] = 500

        locatAPI2['x'] = 0
        locatAPI2['y'] = 500

        locatAPI3['x'] = 0
        locatAPI3['y'] = 500

        df = models.RwFullPof.objects.get(id=proposalID)
        ca = models.RwFullFcof.objects.get(id=proposalID)
        rwAss = models.RwAssessment.objects.get(id=proposalID)
        component = models.ComponentMaster.objects.get(componentid=rwAss.componentid_id)
        if component.componenttypeid_id == 8 or component.componenttypeid_id == 12 or component.componenttypeid_id == 14 or component.componenttypeid_id == 15:
            isTank = 1
        else:
            isTank = 0

        if component.componenttypeid_id == 8 or component.componenttypeid_id == 14:
            isShell = 1
        else:
            isShell = 0
        Ca = round(ca.fcofvalue, 2)
        DF1 = round(df.totaldfap1, 2)
        DF2 = round(df.totaldfap2, 2)
        DF3 = round(df.totaldfap3, 2)
    except:
        raise Http404
    return render(request, 'ManagerUI/RiskSummaryMana/RiskMatrixMana.html',{'API1':location.locat(df.totaldfap1, ca.fcofvalue), 'API2':location.locat(df.totaldfap2, ca.fcofvalue),
                                                                      'API3':location.locat(df.totaldfap3, ca.fcofvalue),'DF1': DF1,'DF2': DF2,'DF3': DF3, 'ca':Ca,
                                                                      'ass':rwAss,'isTank': isTank, 'isShell': isShell, 'df':df, 'proposalID':proposalID})
def Inputdata(request, proposalID):
    try:
        Fluid = ["Acid", "AlCl3", "C1-C2", "C13-C16", "C17-C25", "C25+", "C3-C4", "C5", "C6-C8", "C9-C12", "CO", "DEE",
                 "EE", "EEA", "EG", "EO", "H2", "H2S", "HCl", "HF", "Methanol", "Nitric Acid", "NO2", "Phosgene", "PO",
                 "Pyrophoric", "Steam", "Styrene", "TDI", "Water"]
        rwassessment = models.RwAssessment.objects.get(id= proposalID)
        rwequipment = models.RwEquipment.objects.get(id= proposalID)
        rwcomponent = models.RwComponent.objects.get(id= proposalID)
        rwstream = models.RwStream.objects.get(id= proposalID)
        rwexcor = models.RwExtcorTemperature.objects.get(id= proposalID)
        rwcoat = models.RwCoating.objects.get(id= proposalID)
        rwmaterial = models.RwMaterial.objects.get(id= proposalID)
        rwinputca = models.RwInputCaLevel1.objects.get(id= proposalID)
        assDate = rwassessment.assessmentdate.strftime('%Y-%m-%d')
        try:
            extDate = rwcoat.externalcoatingdate.strftime('%Y-%m-%d')
        except:
            extDate = datetime.now().strftime('%Y-%m-%d')

        comp = models.ComponentMaster.objects.get(componentid=rwassessment.componentid_id)
        data = {}
        if request.method == 'POST':
            data['assessmentname'] = request.POST.get('AssessmentName')
            data['assessmentdate'] = request.POST.get('assessmentdate')
            data['apicomponenttypeid'] = models.ApiComponentType.objects.get(
                apicomponenttypeid=comp.apicomponenttypeid).apicomponenttypename
            data['equipmentType'] = models.EquipmentType.objects.get(equipmenttypeid=models.EquipmentMaster.objects.get(
                equipmentid=comp.equipmentid_id).equipmenttypeid_id).equipmenttypename
            data['riskperiod'] = request.POST.get('RiskAnalysisPeriod')
            if request.POST.get('adminControlUpset'):
                adminControlUpset = 1
            else:
                adminControlUpset = 0

            if request.POST.get('ContainsDeadlegs'):
                containsDeadlegs = 1
            else:
                containsDeadlegs = 0

            if request.POST.get('Highly'):
                HighlyEffe = 1
            else:
                HighlyEffe = 0

            if request.POST.get('CylicOper'):
                cylicOP = 1
            else:
                cylicOP = 0

            if request.POST.get('Downtime'):
                downtime = 1
            else:
                downtime = 0

            if request.POST.get('SteamedOut'):
                steamOut = 1
            else:
                steamOut = 0

            if request.POST.get('HeatTraced'):
                heatTrace = 1
            else:
                heatTrace = 0

            if request.POST.get('PWHT'):
                pwht = 1
            else:
                pwht = 0

            if request.POST.get('InterfaceSoilWater'):
                interfaceSoilWater = 1
            else:
                interfaceSoilWater = 0

            if request.POST.get('PressurisationControlled'):
                pressureControl = 1
            else:
                pressureControl = 0

            if request.POST.get('LOM'):
                linerOnlineMoniter = 1
            else:
                linerOnlineMoniter = 0

            if request.POST.get('EquOper'):
                lowestTemp = 1
            else:
                lowestTemp = 0

            if request.POST.get('PresenceofSulphidesShutdow'):
                presentSulphidesShutdown = 1
            else:
                presentSulphidesShutdown = 0

            if request.POST.get('MFTF'):
                materialExposed = 1
            else:
                materialExposed = 0

            if request.POST.get('PresenceofSulphides'):
                presentSulphide = 1
            else:
                presentSulphide = 0

            data['minTemp'] = request.POST.get('Min')
            data['ExternalEnvironment'] = request.POST.get('ExternalEnvironment')
            data['ThermalHistory'] = request.POST.get('ThermalHistory')
            data['OnlineMonitoring'] = request.POST.get('OnlineMonitoring')
            data['EquipmentVolumn'] = request.POST.get('EquipmentVolume')

            data['normaldiameter'] = request.POST.get('NominalDiameter')
            data['normalthick'] = request.POST.get('NominalThickness')
            data['currentthick'] = request.POST.get('CurrentThickness')
            data['tmin'] = request.POST.get('tmin')
            data['currentrate'] = request.POST.get('CurrentRate')
            data['deltafatt'] = request.POST.get('DeltaFATT')

            if request.POST.get('DFDI'):
                damageDuringInsp = 1
            else:
                damageDuringInsp = 0

            if request.POST.get('ChemicalInjection'):
                chemicalInj = 1
            else:
                chemicalInj = 0

            if request.POST.get('PresenceCracks'):
                crackpresent = 1
            else:
                crackpresent = 0

            if request.POST.get('HFICI'):
                HFICI = 1
            else:
                HFICI = 0

            if request.POST.get('TrampElements'):
                TrampElement = 1
            else:
                TrampElement = 0

            data['MaxBrinell'] = request.POST.get('MBHW')
            data['complex'] = request.POST.get('ComplexityProtrusions')
            data['CylicLoad'] = request.POST.get('CLC')
            data['branchDiameter'] = request.POST.get('BranchDiameter')
            data['joinTypeBranch'] = request.POST.get('JTB')
            data['numberPipe'] = request.POST.get('NFP')
            data['pipeCondition'] = request.POST.get('PipeCondition')
            data['prevFailure'] = request.POST.get('PreviousFailures')

            if request.POST.get('VASD'):
                visibleSharkingProtect = 1
            else:
                visibleSharkingProtect = 0

            data['shakingPipe'] = request.POST.get('ASP')
            data['timeShakingPipe'] = request.POST.get('ATSP')
            data['correctActionMitigate'] = request.POST.get('CAMV')
            # OP condition
            data['maxOT'] = request.POST.get('MaxOT')
            data['maxOP'] = request.POST.get('MaxOP')
            data['minOT'] = request.POST.get('MinOT')
            data['minOP'] = request.POST.get('MinOP')
            data['OpHydroPressure'] = request.POST.get('OHPP')
            data['criticalTemp'] = request.POST.get('CET')
            data['OP1'] = request.POST.get('Operating1')
            data['OP2'] = request.POST.get('Operating2')
            data['OP3'] = request.POST.get('Operating3')
            data['OP4'] = request.POST.get('Operating4')
            data['OP5'] = request.POST.get('Operating5')
            data['OP6'] = request.POST.get('Operating6')
            data['OP7'] = request.POST.get('Operating7')
            data['OP8'] = request.POST.get('Operating8')
            data['OP9'] = request.POST.get('Operating9')
            data['OP10'] = request.POST.get('Operating10')
            # material
            data['material'] = request.POST.get('Material')
            data['maxDesignTemp'] = request.POST.get('MaxDesignTemp')
            data['minDesignTemp'] = request.POST.get('MinDesignTemp')
            data['designPressure'] = request.POST.get('DesignPressure')
            data['tempRef'] = request.POST.get('ReferenceTemperature')
            data['allowStress'] = request.POST.get('ASAT')
            data['BrittleFacture'] = request.POST.get('BFGT')
            data['CA'] = request.POST.get('CorrosionAllowance')
            data['sigmaPhase'] = request.POST.get('SigmaPhase')
            if request.POST.get('CoLAS'):
                cacbonAlloy = 1
            else:
                cacbonAlloy = 0

            if request.POST.get('AusteniticSteel'):
                austeniticStell = 1
            else:
                austeniticStell = 0

            if request.POST.get('SusceptibleTemper'):
                suscepTemp = 1
            else:
                suscepTemp = 0

            if request.POST.get('NickelAlloy'):
                nickelAlloy = 1
            else:
                nickelAlloy = 0

            if request.POST.get('Chromium'):
                chromium = 1
            else:
                chromium = 0

            data['sulfurContent'] = request.POST.get('SulfurContent')
            data['heatTreatment'] = request.POST.get('heatTreatment')

            if request.POST.get('MGTEHTHA'):
                materialHTHA = 1
            else:
                materialHTHA = 0

            data['HTHAMaterialGrade'] = request.POST.get('HTHAMaterialGrade')

            if request.POST.get('MaterialPTA'):
                materialPTA = 1
            else:
                materialPTA = 0

            data['PTAMaterialGrade'] = request.POST.get('PTAMaterialGrade')
            data['materialCostFactor'] = request.POST.get('MaterialCostFactor')
            # Coating, Clading
            if request.POST.get('InternalCoating'):
                InternalCoating = 1
            else:
                InternalCoating = 0

            if request.POST.get('ExternalCoating'):
                ExternalCoating = 1
            else:
                ExternalCoating = 0

            data['ExternalCoatingID'] = request.POST.get('ExternalCoatingID')
            data['ExternalCoatingQuality'] = request.POST.get('ExternalCoatingQuality')

            if request.POST.get('SCWD'):
                supportMaterial = 1
            else:
                supportMaterial = 0

            if request.POST.get('InternalCladding'):
                InternalCladding = 1
            else:
                InternalCladding = 0

            data['CladdingCorrosionRate'] = request.POST.get('CladdingCorrosionRate')

            if request.POST.get('InternalLining'):
                InternalLining = 1
            else:
                InternalLining = 0

            data['InternalLinerType'] = request.POST.get('InternalLinerType')
            data['InternalLinerCondition'] = request.POST.get('InternalLinerCondition')

            if request.POST.get('ExternalInsulation') == "on" or request.POST.get('ExternalInsulation') == 1:
                ExternalInsulation = 1
            else:
                ExternalInsulation = 0

            if request.POST.get('ICC'):
                InsulationCholride = 1
            else:
                InsulationCholride = 0

            data['ExternalInsulationType'] = request.POST.get('ExternalInsulationType')
            data['InsulationCondition'] = request.POST.get('InsulationCondition')
            # Steam
            data['NaOHConcentration'] = request.POST.get('NaOHConcentration')
            data['ReleasePercentToxic'] = request.POST.get('RFPT')
            data['ChlorideIon'] = request.POST.get('ChlorideIon')
            data['CO3'] = request.POST.get('CO3')
            data['H2SContent'] = request.POST.get('H2SContent')
            data['PHWater'] = request.POST.get('PHWater')

            if request.POST.get('EAGTA'):
                exposureAcid = 1
            else:
                exposureAcid = 0

            if request.POST.get('ToxicConstituents'):
                ToxicConstituents = 1
            else:
                ToxicConstituents = 0

            data['ExposureAmine'] = request.POST.get('ExposureAmine')
            data['AminSolution'] = request.POST.get('ASC')

            if request.POST.get('APDO'):
                aquaDuringOP = 1
            else:
                aquaDuringOP = 0

            if request.POST.get('APDSD'):
                aquaDuringShutdown = 1
            else:
                aquaDuringShutdown = 0

            if request.POST.get('EnvironmentCH2S'):
                EnvironmentCH2S = 1
            else:
                EnvironmentCH2S = 0

            if request.POST.get('PHA'):
                presentHF = 1
            else:
                presentHF = 0

            if request.POST.get('PresenceCyanides'):
                presentCyanide = 1
            else:
                presentCyanide = 0

            if request.POST.get('PCH'):
                processHydrogen = 1
            else:
                processHydrogen = 0

            if request.POST.get('ECCAC'):
                environCaustic = 1
            else:
                environCaustic = 0

            if request.POST.get('ESBC'):
                exposedSulfur = 1
            else:
                exposedSulfur = 0

            if request.POST.get('MEFMSCC'):
                materialExposedFluid = 1
            else:
                materialExposedFluid = 0
            # CA
            data['APIFluid'] = request.POST.get('APIFluid')
            data['MassInventory'] = request.POST.get('MassInventory')
            data['Systerm'] = request.POST.get('Systerm')
            data['MassComponent'] = request.POST.get('MassComponent')
            data['EquipmentCost'] = request.POST.get('EquipmentCost')
            data['MittigationSysterm'] = request.POST.get('MittigationSysterm')
            data['ProductionCost'] = request.POST.get('ProductionCost')
            data['ToxicPercent'] = request.POST.get('ToxicPercent')
            data['InjureCost'] = request.POST.get('InjureCost')
            data['ReleaseDuration'] = request.POST.get('ReleaseDuration')
            data['EnvironmentCost'] = request.POST.get('EnvironmentCost')
            data['PersonDensity'] = request.POST.get('PersonDensity')
            data['DetectionType'] = request.POST.get('DetectionType')
            data['IsulationType'] = request.POST.get('IsulationType')

            rwassessment.assessmentdate=data['assessmentdate']
            rwassessment.proposalname=data['assessmentname']
            rwassessment.save()

            rwequipment.adminupsetmanagement=adminControlUpset
            rwequipment.containsdeadlegs=containsDeadlegs
            rwequipment.cyclicoperation=cylicOP
            rwequipment.highlydeadleginsp=HighlyEffe
            rwequipment.downtimeprotectionused=downtime
            rwequipment.externalenvironment=data['ExternalEnvironment']
            rwequipment.heattraced=heatTrace
            rwequipment.interfacesoilwater=interfaceSoilWater
            rwequipment.lineronlinemonitoring=linerOnlineMoniter
            rwequipment.materialexposedtoclext=materialExposed
            rwequipment.minreqtemperaturepressurisation=data['minTemp']
            rwequipment.onlinemonitoring=data['OnlineMonitoring']
            rwequipment.presencesulphideso2=presentSulphide
            rwequipment.presencesulphideso2shutdown=presentSulphidesShutdown
            rwequipment.pressurisationcontrolled=pressureControl
            rwequipment.pwht=pwht
            rwequipment.steamoutwaterflush=steamOut
            rwequipment.thermalhistory=data['ThermalHistory']
            rwequipment.yearlowestexptemp=lowestTemp
            rwequipment.volume=data['EquipmentVolumn']
            rwequipment.save()

            rwcomponent.nominaldiameter=data['normaldiameter']
            rwcomponent.nominalthickness=data['normalthick']
            rwcomponent.currentthickness=data['currentthick']
            rwcomponent.minreqthickness=data['tmin']
            rwcomponent.currentcorrosionrate=data['currentrate']
            rwcomponent.branchdiameter=data['branchDiameter']
            rwcomponent.branchjointtype=data['joinTypeBranch']
            rwcomponent.brinnelhardness=data['MaxBrinell']
            rwcomponent.deltafatt=data['deltafatt']
            rwcomponent.chemicalinjection=chemicalInj
            rwcomponent.highlyinjectioninsp=HFICI
            rwcomponent.complexityprotrusion=data['complex']
            rwcomponent.correctiveaction=data['correctActionMitigate']
            rwcomponent.crackspresent=crackpresent
            rwcomponent.cyclicloadingwitin15_25m=data['CylicLoad']
            rwcomponent.damagefoundinspection=damageDuringInsp
            rwcomponent.numberpipefittings=data['numberPipe']
            rwcomponent.pipecondition=data['pipeCondition']
            rwcomponent.previousfailures=data['prevFailure']
            rwcomponent.shakingamount=data['shakingPipe']
            rwcomponent.shakingdetected=visibleSharkingProtect
            rwcomponent.shakingtime=data['timeShakingPipe']
            rwcomponent.trampelements=TrampElement
            rwcomponent.save()

            rwstream.aminesolution=data['AminSolution']
            rwstream.aqueousoperation=aquaDuringOP
            rwstream.aqueousshutdown=aquaDuringShutdown
            rwstream.toxicconstituent=ToxicConstituents
            rwstream.caustic=environCaustic
            rwstream.chloride=data['ChlorideIon']
            rwstream.co3concentration=data['CO3']
            rwstream.cyanide=presentCyanide
            rwstream.exposedtogasamine= exposureAcid
            rwstream.exposedtosulphur=exposedSulfur
            rwstream.exposuretoamine=data['ExposureAmine']
            rwstream.h2s=EnvironmentCH2S
            rwstream.h2sinwater=data['H2SContent']
            rwstream.hydrogen= processHydrogen
            rwstream.hydrofluoric=presentHF
            rwstream.materialexposedtoclint=materialExposedFluid
            rwstream.maxoperatingpressure=data['maxOP']
            rwstream.maxoperatingtemperature=float(data['maxOT'])
            rwstream.minoperatingpressure=float(data['minOP'])
            rwstream.minoperatingtemperature=data['minOT']
            rwstream.criticalexposuretemperature=data['criticalTemp']
            rwstream.naohconcentration=data['NaOHConcentration']
            rwstream.releasefluidpercenttoxic=float(data['ReleasePercentToxic'])
            rwstream.waterph=float(data['PHWater'])
            rwstream.h2spartialpressure=float(data['OpHydroPressure'])
            rwstream.save()

            rwexcor.minus12tominus8=data['OP1']
            rwexcor.minus8toplus6=data['OP2']
            rwexcor.plus6toplus32=data['OP3']
            rwexcor.plus32toplus71=data['OP4']
            rwexcor.plus71toplus107=data['OP5']
            rwexcor.plus107toplus121=data['OP6']
            rwexcor.plus121toplus135=data['OP7']
            rwexcor.plus135toplus162=data['OP8']
            rwexcor.plus162toplus176=data['OP9']
            rwexcor.morethanplus176=data['OP10']
            rwexcor.save()

            rwcoat.externalcoating=ExternalCoating
            rwcoat.externalinsulation=ExternalInsulation
            rwcoat.internalcladding=InternalCladding
            rwcoat.internalcoating=InternalCoating
            rwcoat.internallining=InternalLining
            rwcoat.externalcoatingdate=data['ExternalCoatingID']
            rwcoat.externalcoatingquality=data['ExternalCoatingQuality']
            rwcoat.externalinsulationtype=data['ExternalInsulationType']
            rwcoat.insulationcondition=data['InsulationCondition']
            rwcoat.insulationcontainschloride=InsulationCholride
            rwcoat.internallinercondition=data['InternalLinerCondition']
            rwcoat.internallinertype=data['InternalLinerType']
            rwcoat.claddingcorrosionrate=data['CladdingCorrosionRate']
            rwcoat.supportconfignotallowcoatingmaint=supportMaterial
            rwcoat.save()

            rwmaterial.corrosionallowance=data['CA']
            rwmaterial.materialname=data['material']
            rwmaterial.designpressure=data['designPressure']
            rwmaterial.designtemperature=data['maxDesignTemp']
            rwmaterial.mindesigntemperature=data['minDesignTemp']
            rwmaterial.brittlefracturethickness=data['BrittleFacture']
            rwmaterial.sigmaphase=data['sigmaPhase']
            rwmaterial.sulfurcontent=data['sulfurContent']
            rwmaterial.heattreatment=data['heatTreatment']
            rwmaterial.referencetemperature=data['tempRef']
            rwmaterial.ptamaterialcode=data['PTAMaterialGrade']
            rwmaterial.hthamaterialcode=data['HTHAMaterialGrade']
            rwmaterial.ispta=materialPTA
            rwmaterial.ishtha=materialHTHA
            rwmaterial.austenitic=austeniticStell
            rwmaterial.temper=suscepTemp
            rwmaterial.carbonlowalloy=cacbonAlloy
            rwmaterial.nickelbased=nickelAlloy
            rwmaterial.chromemoreequal12=chromium
            rwmaterial.allowablestress=data['allowStress']
            rwmaterial.costfactor=data['materialCostFactor']
            rwmaterial.save()

            rwinputca.api_fluid=data['APIFluid']
            rwinputca.system=data['Systerm']
            rwinputca.release_duration=data['ReleaseDuration']
            rwinputca.detection_type=data['DetectionType']
            rwinputca.isulation_type=data['IsulationType']
            rwinputca.mitigation_system=data['MittigationSysterm']
            rwinputca.equipment_cost=data['EquipmentCost']
            rwinputca.injure_cost=data['InjureCost']
            rwinputca.evironment_cost=data['EnvironmentCost']
            rwinputca.toxic_percent=data['ToxicPercent']
            rwinputca.personal_density=data['PersonDensity']
            rwinputca.material_cost=data['materialCostFactor']
            rwinputca.production_cost=data['ProductionCost']
            rwinputca.mass_inventory=data['MassInventory']
            rwinputca.mass_component=data['MassComponent']
            rwinputca.stored_pressure=float(data['minOP']) * 6.895
            rwinputca.stored_temp=data['minOT']
            rwinputca.save()

            #Customize code here
            ReCalculate.ReCalculate(proposalID)
            return redirect('inputdata', proposalID= proposalID)
    except Exception as e:
        print(e)
        raise Http404
    return render(request, 'BaseUI/BaseManager/Inputdata.html', {'api':Fluid, 'rwAss':rwassessment, 'rwEq':rwequipment,
                                                                           'rwComp':rwcomponent, 'rwStream':rwstream, 'rwExcot':rwexcor,
                                                                           'rwCoat':rwcoat, 'rwMaterial':rwmaterial, 'rwInputCa':rwinputca,
                                                                           'assDate':assDate, 'extDate':extDate,
                                                                           'componentID': rwassessment.componentid_id,
                                                                           'equipmentID': rwassessment.equipmentid_id})
