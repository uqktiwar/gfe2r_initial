from django.shortcuts import render, HttpResponse
from rootApp.models import Contact, FreeboardConstructionCost, Sampledata, Sample, dataAll
from datetime import datetime
from django.contrib import messages
from django.db.models import Q
from functools import reduce
import operator
from django.http import JsonResponse
import json as simplejson
from bokeh.io import output_file, show
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models import HoverTool, LassoSelectTool, WheelZoomTool, PointDrawTool, ColumnDataSource, FactorRange
from bokeh.palettes import Category20c, Spectral6
from bokeh.transform import cumsum, factor_cmap, dodge
from bokeh.core.validation import silence
from bokeh.core.validation.warnings import EMPTY_LAYOUT
import math
from scipy.integrate import quad
from scipy import integrate as integrate
import numpy as np



datafile = dataAll
 
 
# Create your views here.
def index(request):
    return render(request, 'index.html')

def disclaimer(request):
    return render(request, 'disclaimer.html') 

def gotomap(request): 
    location = request.GET.get('location', 'default')   
    print("my location: ", location)
    stories = request.GET.get('stories', 'default')
    print("my stories: ", stories)

    commasplit =location.split(',')
    beforecomma = commasplit[0]
    locationList= beforecomma.split(' ')
    locationList = list(map(str.strip, locationList))

    #locationList=location.split(' ')
    print("locationlist space split : ", locationList)
    locationList = list(map(str.strip, locationList))
    streetlist = locationList[1:]
##Error message---------------------
    if (len(locationList)==1):
        queryset = datafile.objects.filter(Q(address__istartswith = locationList[0]) | (Q(street__icontains = locationList[0]))  ).all()[:10]
    elif (len(locationList)==2):
        queryset = datafile.objects.filter((Q(address__istartswith = locationList[0]) | (Q(street__icontains = locationList[0]))), (Q(address__icontains = locationList[1]) | Q(street__icontains = locationList[1]))  ).all()[:10]
    elif (len(locationList)==3):
        queryset = datafile.objects.filter((Q(address__istartswith = locationList[0]) | (Q(street__icontains = locationList[0]))), (Q(address__icontains = locationList[1]) | Q(street__icontains = locationList[1])), (Q(street__icontains = locationList[2]))).all()[:10]
    else:
        print("lalalala")
        queryset = datafile.objects.filter((Q(address__istartswith = locationList[0]) | (Q(street__icontains = locationList[0]))), (Q(address__icontains = locationList[1]) | Q(street__icontains = locationList[1])), (Q(street__icontains = locationList[2]))).all()[:10]

    mylist = []        
    if len(queryset)<=0:
        #mylist = ["Enter a valid address!"]
        messages.error(request, 'Enter a valid address!')

        return render(request, 'index.html')
    else:
        mylist = ["valid address"]  

##Error message ends-------------------------------
    
    
    location_json_list = simplejson.dumps(location)   
    data_dict = {"location": location_json_list}
    return render(request, 'map.html', data_dict)


def decisionmakingmap(request): 
    return render(request, 'map.html')

def nodisc(request): 
    return render(request, 'nodisc.html')

def autosuggest(request): 
    print(request.GET)  
    query_original = request.GET.get('term')

    query_originalList=query_original.split(' ')

    if (len(query_originalList)==1):
        queryset = datafile.objects.filter(Q(address__istartswith = query_originalList[0]) | (Q(street__icontains = query_originalList[0]))  ).all()[:10]
    elif (len(query_originalList)==2):
        queryset = datafile.objects.filter((Q(address__istartswith = query_originalList[0]) | (Q(street__icontains = query_originalList[0]))), (Q(street__icontains = query_originalList[1]))  ).all()[:10]
    elif (len(query_originalList)==3):
        queryset = datafile.objects.filter((Q(address__istartswith = query_originalList[0]) | (Q(street__icontains = query_originalList[0]))), (Q(street__icontains = query_originalList[1])), (Q(street__icontains = query_originalList[1]))).all()[:10]
    else:
        queryset = datafile.objects.filter((Q(address__istartswith = query_originalList[0]) | (Q(street__icontains = query_originalList[0]))), (Q(street__icontains = query_originalList[1])), (Q(street__icontains = query_originalList[1]))).all()[:10]

    mylist = []        
    if len(queryset)>0:
        mylist += [x.address+" "+x.street+","+" "+x.parish+ " Parish" for x in queryset]
    else:
        mylist = ["No results found"]    
    return JsonResponse(mylist, safe=False)


def helpcenter(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        desc = request.POST.get('desc')
        contact = Contact(name=name, email=email, desc=desc, date=datetime.today()) 
        contact.save()
        messages.success(request, 'Your message has been sent!')

    return render(request, 'contact.html')    

def search(request):

##---------user input---------------------------------
#   community level #
    total_monthly_saving_list_c = []
    total_optimal_saving_list_c = [] 
    total_optimal_freeboard_list_c = [] 
    freeboardCost_list_c = []
    total_annual_premium_list_c = []
    AAL_absCurrency_list_c = []
    time_to_recover_FC_TB_list_c = []
          
    #buildinglist = ["28 ACADIA ST", "29 ACADIA ST", "30 ACADIA ST", "31 ACADIA ST", "32 ACADIA ST", "33 ACADIA ST", "34 ACADIA ST"]
    #buildinglist = ["113 WOODLAKE BLVD", "117 WOODLAKE BLVD", "121 WOODLAKE BLVD", "125 WOODLAKE BLVD", "129 WOODLAKE BLVD", "133 WOODLAKE BLVD", "135 WOODLAKE BLVD"]
    #buildinglist = ["76 WOODLAKE BLVD","80 WOODLAKE BLVD", "124 WOODLAKE BLVD", "52 WOODLAKE BLVD", "60 WOODLAKE BLVD", "56 WOODLAKE BLVD", "104 WOODLAKE BLVD"]
    buildinglist = ["113 WOODLAKE BLVD","80 WOODLAKE BLVD", "124 WOODLAKE BLVD", "135 WOODLAKE BLVD","52 WOODLAKE BLVD", "60 WOODLAKE BLVD", "56 WOODLAKE BLVD", "104 WOODLAKE BLVD"]
    #buildinglist = [ request.GET.get('location', 'default')]
    for i in range(len(buildinglist)):
        location = buildinglist[i]

    # parcel = request.GET.get('parcel', 'default')
    ##### find location of each building from parcel number, say buildinglist[*]
    #
    # for i in range(len(buildinglist)):
    #     location = buildinglist[i]   ##something like this 
    #     
        ##------location-----------------------
        #location = request.GET.get('location', 'default')
        commasplit =location.split(',')
        beforecomma = commasplit[0]
        locationList= beforecomma.split(' ')
        locationList = list(map(str.strip, locationList))
        streetlist = locationList[1:]

        ##-------number of stories------------------------
        No_Floors = request.GET['stories']
        print("accepted floors:", No_Floors)

        ##--------------square footage-----------------------
        Square_footage = float(request.GET.get('sqft', 'default'))
    ##----------user input ends---------------------------------------



    ##----------------------- Error message---------------------
        if (len(locationList)==1):
            queryset = datafile.objects.filter(Q(address__istartswith = locationList[0]) | (Q(street__icontains = locationList[0]))  ).all()[:10]
        elif (len(locationList)==2):
            queryset = datafile.objects.filter((Q(address__istartswith = locationList[0]) | (Q(street__icontains = locationList[0]))), (Q(street__icontains = locationList[1]))  ).all()[:10]
        elif (len(locationList)==3):
            queryset = datafile.objects.filter((Q(address__istartswith = locationList[0]) | (Q(street__icontains = locationList[0]))), (Q(address__icontains = locationList[1]) | Q(street__icontains = locationList[1])), (Q(street__icontains = locationList[2]))).all()[:10]
        else:
            queryset = datafile.objects.filter((Q(address__istartswith = locationList[0]) | (Q(street__icontains = locationList[0]))), (Q(address__icontains = locationList[1]) | Q(street__icontains = locationList[1])), (Q(street__icontains = locationList[2]))).all()[:10]

        mylist = []        
        if len(queryset)<=0:
            #mylist = ["Enter a valid address!"]
            messages.error(request, 'Enter a valid address!')

            return render(request, 'index.html')
        else:
            mylist = ["valid address"]  

    ##------------------Error message ends-------------------------------


    ##--------------------autocomplete-------------------------------------
        if (len(streetlist)==1):
            addressvalue = datafile.objects.filter(
            Q(address__icontains=locationList[0]) ,  (Q(address__icontains=locationList[1]) | Q(street__icontains=locationList[1]))).all()
        elif (len(streetlist)==2):
            addressvalue = datafile.objects.filter(
            Q(address__icontains=locationList[0]) ,  (Q(address__icontains=locationList[1]) | Q(street__icontains=locationList[1])), Q(street__icontains=locationList[2])).all()        
        elif (len(streetlist)==3):
            addressvalue = datafile.objects.filter(
                Q(address__icontains=locationList[0]) ,  (Q(address__icontains=locationList[1]) | Q(street__icontains=locationList[1])), Q(street__icontains=locationList[2]), Q(street__icontains=locationList[3])).all()    
        else:  
            addressvalue = datafile.objects.filter(
                Q(address__icontains=locationList[0]) ,  (Q(address__icontains=locationList[1]) | Q(street__icontains=locationList[1])), Q(street__icontains=locationList[2]), Q(street__icontains=locationList[3]), Q(street__icontains=locationList[4])).all()
        print("addressvalue: ", addressvalue, "type: ", type(addressvalue))
    ##------------------autocomplete ends--------------------------------------------------
                    
    ##-----------queries------------------------------
        u = ""
        a = ""
        zonevalue = ""
        parishvalue = ""
        for data in addressvalue:
            zonevalue = data.floodzone
            #u = 1.5218
            #a = 0.335
            u = data.u_intercept
            a = data.a_slope
            if u == "Unknown":
                u = 1.5218
            else:
                u=float(u)    
            if a == "Unknown" or a == "Problematic":
                a = 0.335   
            else:
                a=float(a)       

            print("ZONE: ", zonevalue )
            print("u value: ", u )
            print("a value: ", a )
            parishvalue = data.parish
    ##--------queries end----------------------------


    ##--------------DEMO values-----------------TO BE CHANGED------
        BFE = 3

        r = 0.03    # say, interest rate 3%
        n = 12       # no of payments per year
        t = 30      # loan term or number of years in the loan
        deductible_bldg = 1250   # demo-must be changed
        deductible_cont = 1250   # demo-must be changed

        
        coverage_lvl_bldg = 225000 #Building_value
        coverage_lvl_cont = 90000 #Building_value * 0.4
        
    ##---------demo values end--------------------


    ##------building cost, parishwise constant value and CRS------------- 
        if parishvalue == "Jefferson":
            Building_cost = 92.47
            CRS = 0.05                # demo-must be changed
        else:
            Building_cost = 100
            CRS = 0
            pass

    ##----Building value----------------------------------

        Building_value = Building_cost * Square_footage
        Actual_construction_cost = int(0.023 * Building_value)

    ##-------BFE increments i---------------------------

        #totalBFE = [0, 1, 2, 3, 4]
        totalBFE = [-4, -3, -2, -1, 0, 1, 2, 3, 4]

    ##----------FFE-----------------------------
        FFE = []
        for i in range(len(totalBFE)):
            FFE.append(totalBFE[i]+BFE)   

    ##-----------freeboard construction cost-----------------

        freeboardCost = []
        for i in range(len(totalBFE)):
            if totalBFE[i] <=0:
                freeboardCost.append(0)
            else:    
                freeboardCost.append(int(totalBFE[i] * 0.023 * Building_value))
        freeboardCost_list_c.append(freeboardCost)   
        print("Freeboard cost : ", freeboardCost) 

        freeboardCost_json = simplejson.dumps(freeboardCost)  

        optimal_freeboardCost = max(freeboardCost)
        
        for k in range(len(freeboardCost)):
            if optimal_freeboardCost == freeboardCost[k]:
                optimal_freeboard_freeboardCost = totalBFE[k]


        optimal_freeboardCost_json = simplejson.dumps(optimal_freeboardCost)  

    ##---------------AAL------------------------

        def integrand_Bldg(E):
            y = (E-u)/a
            term = -y - math.exp(-y)

            #### V zones functions for AAL building
            if zonevalue == "VE":
                
                EminusF_bldg = [-1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]
                damage_bldg = [0.215, 0.24, 0.29, 0.37, 0.54, 0.605, 0.645, 0.68, 0.7, 0.72, 0.74, 0.76, 0.78, 0.8, 0.815, 0.83, 0.84, 0.85, 0.86, 0.87]

                for i in range(len(EminusF_bldg)):
                    if EminusF_bldg[i] == math.floor(E-F):
                        loss_bldg_inftoneg1 = np.interp(E-F, EminusF_bldg, damage_bldg)
                    elif (E-F) < -1:
                        loss_bldg_inftoneg1 = 0                ### for now, check on the values
                    elif (E-F) > 18 :
                        loss_bldg_inftoneg1 = 0.87                 ### for now, check on the values
                    else:
                        pass    


            #### Not V zones functions for AAL building    
            else:    
                if No_Floors == "1" : 
                    #loss_bldg_inftoneg1 = (0.0092 *((E-F)**3)- 0.5342 * ((E-F)**2) + 10.404 *(E-F) + 13.418 )
                    loss_bldg_inftoneg1 = (0.0092 *((E-F)**3)- 0.5362 * ((E-F)**2) + 10.419 *(E-F) + 13.39 )        
                elif No_Floors == "2" :
                    #loss_bldg_inftoneg1 = ( -0.0001 *((E-F)**3)- 0.1464 * ((E-F)**2) + 6.1207 *(E-F) + 9.2646 )
                    loss_bldg_inftoneg1 = ( -0.0001 *((E-F)**3)- 0.1466 * ((E-F)**2) + 6.1218 *(E-F) + 9.2626 )
                else:
                    pass  

            loss=(((1/a)* math.exp(term))*loss_bldg_inftoneg1)

            return loss

        def integrand_Cont(E):
            y = (E-u)/a
            term = -y - math.exp(-y)

            #### V zones functions for AAL content
            if zonevalue == "VE":
                
                EminusF_cont = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]
                damage_cont = [0.15, 0.23, 0.35, 0.5, 0.58, 0.63, 0.67, 0.7, 0.72, 0.78, 0.78, 0.78, 0.78, 0.78, 0.78, 0.78, 0.78, 0.78, 0.78]

                for i in range(len(EminusF_cont)):
                    if EminusF_cont[i] == math.floor(E-F):
                        loss_cont_infto0 = np.interp(E-F, EminusF_cont, damage_cont)
                    elif (E-F) < 0:
                        loss_cont_infto0 = 0                ### for now, check on the values
                    elif (E-F) > 18 :
                        loss_cont_infto0 = 0.78                 ### for now, check on the values
                    else:
                        pass   

            #### Not V zones functions for AAL content    
            else:    
                if No_Floors == "1" :         
                    loss_cont_infto0 = ( 0.0049 *((E-F)**3)- 0.2996 * ((E-F)**2) + 5.5358 *(E-F) + 8.0402 )
                elif No_Floors == "2" :        
                    loss_cont_infto0 = ( -0.0001 *((E-F)**3)- 0.1116 * ((E-F)**2) + 3.8257 *(E-F) + 4.9975 )
                else:
                    pass  

            loss=(((1/a)* math.exp(term))*loss_cont_infto0)

            return loss


        # AAL_absCurrency = []
        # for i in range(len(totalBFE)): 
        #     F= FFE[i]
        #     AAL_B, errB = quad(integrand_Bldg, (F-1), math.inf)
        #     AAL_C, errC = quad(integrand_Cont, 0, math.inf)

        #     AAL_percentValue = (AAL_B + AAL_C)
        #     AAL_absCurrency.append(int(AAL_percentValue * Building_value))

        # print("AAL_percentValue : ", AAL_percentValue)
        # print("AAL_absCurrency : ", AAL_absCurrency)

            
        AAL_absCurrency = []
        AAL_B_ansNerr = []
        AAL_C_ansNerr = []
        for i in range(len(totalBFE)): 
            F= FFE[i]
            AAL_B_ansNerr.append(quad(integrand_Bldg, (F-1), math.inf))
            AAL_C_ansNerr.append(quad(integrand_Cont, F, math.inf))

        #print("AAL_Building_ansNerr : ", AAL_B_ansNerr)
        #print("AAL_Content_ansNerr : ", AAL_C_ansNerr)


        AAL_bldg = []
        AAL_cont = []
        for tuple in AAL_B_ansNerr:
            AAL_bldg.append(round(tuple[0],3))
        for tuple in AAL_C_ansNerr:  
            AAL_cont.append(round(tuple[0],3))

        print("\n")
        print("AAL_Building : ", AAL_bldg,"\n") 
        print("AAL_Content : ", AAL_cont,"\n") 

        ##--------Expected annual flood loss is AAL in absCurrency-------------------------
        AAL_percentValue=[]
        AAL_absCurrency=[]
        AAL_B_absCurrency=[]
        AAL_C_absCurrency=[]

        for i in range(len(totalBFE)): 
            AAL_B_absCurrency.append(int(AAL_bldg[i] * Building_value/100))
            AAL_C_absCurrency.append(int(AAL_cont[i] * Building_value/100))
            AAL_percentValue.append( round(AAL_bldg[i] + AAL_cont[i],3))
            AAL_absCurrency.append(int(AAL_percentValue[i] * Building_value/100))
    

        print("AAL_B_absCurrency : ", AAL_B_absCurrency)
        print("AAL_C_absCurrency : ", AAL_C_absCurrency)
        print("AAL_percentValue : ", AAL_percentValue)
        print("AAL_absCurrency : ", AAL_absCurrency)

        AAL_absCurrency_list_c.append(AAL_absCurrency)

        AAL_absCurrency_json = simplejson.dumps(AAL_absCurrency)  
        optimal_AAL_absCurrency = min(AAL_absCurrency)

        for k in range(len(AAL_absCurrency)):
            if optimal_AAL_absCurrency == AAL_absCurrency[k]:
                optimal_AAL_absCurrency_freeboard = totalBFE[k]

        optimal_AAL_absCurrency_json = simplejson.dumps(optimal_AAL_absCurrency)  


    ##----------------------AAL ends---------------------------------------

    ###----------------Insurance-----------------------------------------

        #------ coverage level--------------

        #coverage_lvl_bldg = Building_value
        #coverage_lvl_cont = Building_value * 0.4
        print("coverage_lvl_bldg", coverage_lvl_bldg)
        print("coverage_lvl_cont", coverage_lvl_cont)

        #--table--Zones AE, A, A1-A30------array values are BFE, BFE+1, BFE+2, BFE+3, BFE+5---- 
        if zonevalue == "AE" :
            # #--one story
            # BasicRate_1s_Bldg_BFE = [2.21,0.94,0.50,0.34,0.31]
            # AddiRate_1s_Bldg_BFE = [0.26,0.17,0.11,0.09,0.08]
            # BasicRate_1s_Cont_BFE = [1.02,0.53,0.38,0.38,0.38]
            # AddiRate_1s_Cont_BFE = [0.12,0.12,0.12,0.12,0.12]
            # print("one story")
            # #--twostory
            # BasicRate_2s_Bldg_BFE = [1.75,0.78,0.43,0.31,0.27]
            # AddiRate_2s_Bldg_BFE = [0.08,0.08,0.08,0.08,0.08]
            # BasicRate_2s_Cont_BFE = [0.75,0.40,0.38,0.38,0.38]
            # AddiRate_2s_Cont_BFE = [0.12,0.12,0.12,0.12,0.12]
            # print("two or more stories")

            #--one story below+
            BasicRate_1s_Bldg_BFE = [11.90, 9.85, 7.93, 5.37, 2.21,0.94,0.50,0.34,0.31]
            AddiRate_1s_Bldg_BFE = [1.79, 1.19, 0.70, 0.36, 0.26,0.17,0.11,0.09,0.08]
            BasicRate_1s_Cont_BFE = [6.53, 5.02, 3.69, 2.33, 1.02,0.53,0.38,0.38,0.38]
            AddiRate_1s_Cont_BFE = [0.24, 0.24, 0.14, 0.12, 0.12,0.12,0.12,0.12,0.12]
            print("one story below+")
            #--twostory below+
            BasicRate_2s_Bldg_BFE = [10.08, 8.17, 6.40, 4.31, 1.75,0.78,0.43,0.31,0.27]
            AddiRate_2s_Bldg_BFE = [0.37, 0.22, 0.13, 0.08, 0.08,0.08,0.08,0.08,0.08]
            BasicRate_2s_Cont_BFE = [5.02, 3.80, 2.75, 1.77, 0.75,0.40,0.38,0.38,0.38]
            AddiRate_2s_Cont_BFE = [0.12, 0.12, 0.12, 0.12, 0.12,0.12,0.12,0.12,0.12]
            print("two or more stories below+")
        #--table--Zones Unnumbered A------array values are BFE, BFE+1, BFE+2, BFE+3, BFE+5---- 
        elif zonevalue == "A" :                                  ####to be changed, what should go for zone unnumbered A?
            # #--one story
            # BasicRate_1s_Bldg_BFE = [2.67,2.67,0.57,0.57,0.57]
            # AddiRate_1s_Bldg_BFE = [0.20,0.20,0.10,0.10,0.10]
            # BasicRate_1s_Cont_BFE = [1.20,1.20,0.32,0.32,0.32]
            # AddiRate_1s_Cont_BFE = [0.09,0.09,0.08,0.08,0.08]
            # #--twostory
            # BasicRate_2s_Bldg_BFE = [2.67,2.67,0.57,0.57,0.57]
            # AddiRate_2s_Bldg_BFE = [0.20,0.20,0.10,0.10,0.10]
            # BasicRate_2s_Cont_BFE = [1.20,1.20,0.32,0.32,0.32]
            # AddiRate_2s_Cont_BFE = [0.09,0.09,0.08,0.08,0.08]

            #--one story below+
            BasicRate_1s_Bldg_BFE = [6.31, 6.31, 6.31, 6.31, 2.67,2.67,0.57,0.57,0.57]
            AddiRate_1s_Bldg_BFE = [0.35, 0.35, 0.35, 0.35, 0.20,0.20,0.10,0.10,0.10]
            BasicRate_1s_Cont_BFE = [2.71, 2.71, 2.71, 2.71, 1.20,1.20,0.32,0.32,0.32]
            AddiRate_1s_Cont_BFE = [0.16, 0.16, 0.16, 0.16, 0.09,0.09,0.08,0.08,0.08]
            #--twostory below+
            BasicRate_2s_Bldg_BFE = [6.31, 6.31, 6.31, 6.31, 2.67,2.67,0.57,0.57,0.57]
            AddiRate_2s_Bldg_BFE = [0.35, 0.35, 0.35, 0.35, 0.20,0.20,0.10,0.10,0.10]
            BasicRate_2s_Cont_BFE = [2.71, 2.71, 2.71, 2.71, 1.20,1.20,0.32,0.32,0.32]
            AddiRate_2s_Cont_BFE = [0.16, 0.16, 0.16, 0.16, 0.09,0.09,0.08,0.08,0.08]


        #--table--Zones V, V1-V30, VE------array values are BFE, BFE+1, BFE+2, BFE+3, BFE+5---- 
        elif  zonevalue == "VE":
            # #--one story
            # BasicRate_1s_Bldg_BFE = [3.28,2.67,2.18,1.79,1.51]
            # AddiRate_1s_Bldg_BFE = [3.28,2.67,2.18,1.79,1.51]
            # BasicRate_1s_Cont_BFE = [2.54,1.94,1.47,1.03,0.93]
            # AddiRate_1s_Cont_BFE = [2.54,1.94,1.47,1.03,0.93]
            # #--twostory
            # BasicRate_2s_Bldg_BFE = [3.28,2.67,2.18,1.79,1.51]
            # AddiRate_2s_Bldg_BFE = [3.28,2.67,2.18,1.79,1.51]
            # BasicRate_2s_Cont_BFE = [2.54,1.94,1.47,1.03,0.93]
            # AddiRate_2s_Cont_BFE = [2.54,1.94,1.47,1.03,0.93]

            #--one story below+
            BasicRate_1s_Bldg_BFE = [5.85, 5.85, 4.88, 4.04, 3.28, 2.67,2.18,1.79,1.51]
            AddiRate_1s_Bldg_BFE = [5.85, 5.85, 4.88, 4.04, 3.28, 2.67,2.18,1.79,1.51]
            BasicRate_1s_Cont_BFE = [5.09, 5.09, 4.14, 3.28, 2.54, 1.94,1.47,1.03,0.93]
            AddiRate_1s_Cont_BFE = [5.09, 5.09, 4.14, 3.28, 2.54, 1.94,1.47,1.03,0.93]
            #--twostory below+
            BasicRate_2s_Bldg_BFE = [5.85, 5.85, 4.88, 4.04, 3.28,2.67,2.18,1.79,1.51]
            AddiRate_2s_Bldg_BFE = [5.85, 5.85, 4.88, 4.04, 3.28,2.67,2.18,1.79,1.51]
            BasicRate_2s_Cont_BFE = [5.09, 5.09, 4.14, 3.28, 2.54,1.94,1.47,1.03,0.93]
            AddiRate_2s_Cont_BFE = [5.09, 5.09, 4.14, 3.28, 2.54,1.94,1.47,1.03,0.93]


        #--table--Zones X------array values are BFE, BFE+1, BFE+2, BFE+3, BFE+5---- 
        elif zonevalue == "X" or zonevalue == "X PROTECTED BY LEVEE" or zonevalue == "0.2 PCT ANNUAL CHANCE FLOOD HAZARD": 
            # #--one story
            # BasicRate_1s_Bldg_BFE = [1.11,1.11,1.11,1.11,1.11]
            # AddiRate_1s_Bldg_BFE = [0.31,0.31,0.31,0.31,0.31]
            # BasicRate_1s_Cont_BFE = [1.71,1.71,1.71,1.71,1.71]
            # AddiRate_1s_Cont_BFE = [0.54,0.54,0.54,0.54,0.54]
            # #--twostory
            # BasicRate_2s_Bldg_BFE = [1.11,1.11,1.11,1.11,1.11]
            # AddiRate_2s_Bldg_BFE = [0.31,0.31,0.31,0.31,0.31]
            # BasicRate_2s_Cont_BFE = [1.71,1.71,1.71,1.71,1.71]
            # AddiRate_2s_Cont_BFE = [0.54,0.54,0.54,0.54,0.54]

            #--one story below+
            BasicRate_1s_Bldg_BFE = [1.11,1.11,1.11,1.11,1.11,1.11,1.11,1.11,1.11]
            AddiRate_1s_Bldg_BFE = [0.31,0.31,0.31,0.31,0.31,0.31,0.31,0.31,0.31]
            BasicRate_1s_Cont_BFE = [1.71,1.71,1.71,1.71,1.71,1.71,1.71,1.71,1.71]
            AddiRate_1s_Cont_BFE = [0.54,0.54,0.54,0.54,0.54,0.54,0.54,0.54,0.54]
            #--twostory below+
            BasicRate_2s_Bldg_BFE = [1.11,1.11,1.11,1.11,1.11,1.11,1.11,1.11,1.11]
            AddiRate_2s_Bldg_BFE = [0.31,0.31,0.31,0.31,0.31,0.31,0.31,0.31,0.31]
            BasicRate_2s_Cont_BFE = [1.71,1.71,1.71,1.71,1.71,1.71,1.71,1.71,1.71]
            AddiRate_2s_Cont_BFE = [0.54,0.54,0.54,0.54,0.54,0.54,0.54,0.54,0.54]
        else:
            print("Flood zone does not match")

        ##---Premium fees----------------
        ICC_premium = 6
        Reserve_fund = 0.18
        HFIAA_surcharge = 25
        Federal_policy_fee = 50
        

        ##----insurance limits----------
        basic_bldg_insurance_limit = 0
        addi_bldg_insurance_amnt = 0
        basic_cont_insurance_limit = 0
        addi_cont_insurance_amnt = 0

        if coverage_lvl_bldg <= 60000:
            basic_bldg_insurance_limit  = coverage_lvl_bldg                 # demo-must be changed
            addi_bldg_insurance_amnt = 0                  # demo-must be changed
            print("building basic : ", basic_bldg_insurance_limit)
            print("building additional : ", addi_bldg_insurance_amnt)

        elif coverage_lvl_bldg > 60000 and coverage_lvl_bldg<= 250000:
            basic_bldg_insurance_limit  = 60000                  # demo-must be changed
            addi_bldg_insurance_amnt = coverage_lvl_bldg-60000                  # demo-must be changed
            print("building basic : ", basic_bldg_insurance_limit)
            print("building additional : ", addi_bldg_insurance_amnt)
        else:
            print("Building coverage level exceeds the limit")
            pass

        if coverage_lvl_cont <= 25000:
            basic_cont_insurance_limit = coverage_lvl_cont                  # demo-must be changed
            addi_cont_insurance_amnt = 0                  # demo-must be changed
            print("content basic : ", basic_cont_insurance_limit)
            print("content additional : ", addi_cont_insurance_amnt)
        elif coverage_lvl_cont > 25000 and coverage_lvl_cont <= 100000:
            basic_cont_insurance_limit = 25000                 # demo-must be changed
            addi_cont_insurance_amnt = coverage_lvl_cont-25000                  # demo-must be changed
            print("content basic : ", basic_cont_insurance_limit)
            print("content additional : ", addi_cont_insurance_amnt)
        else:
            print("Content coverage level exceeds the limit")
            pass


        ##----Premium deductible table------


        if deductible_bldg==1000 and deductible_cont==1000:
            fullrisk = 1.000

        elif deductible_bldg==1250 and deductible_cont==1000:
            fullrisk = 0.995
        elif deductible_bldg==1250 and deductible_cont==1250:
            fullrisk = 0.980

        elif deductible_bldg==1500 and deductible_cont==1000:
            fullrisk = 0.990
        elif deductible_bldg==1500 and deductible_cont==1250:
            fullrisk = 0.975
        elif deductible_bldg==1500 and deductible_cont==1500:
            fullrisk = 0.965

        elif deductible_bldg==2000 and deductible_cont==1000:
            fullrisk = 0.975
        elif deductible_bldg==2000 and deductible_cont==1250:
            fullrisk = 0.965
        elif deductible_bldg==2000 and deductible_cont==1500:
            fullrisk = 0.950
        elif deductible_bldg==2000 and deductible_cont==2000:
            fullrisk = 0.925

        elif deductible_bldg==3000 and deductible_cont==1000:
            fullrisk = 0.950
        elif deductible_bldg==3000 and deductible_cont==1250:
            fullrisk = 0.940
        elif deductible_bldg==3000 and deductible_cont==1500:
            fullrisk = 0.925
        elif deductible_bldg==3000 and deductible_cont==2000:
            fullrisk = 0.900
        elif deductible_bldg==3000 and deductible_cont==3000:
            fullrisk = 0.850

        elif deductible_bldg==4000 and deductible_cont==1000:
            fullrisk = 0.925
        elif deductible_bldg==4000 and deductible_cont==1250:
            fullrisk = 0.915
        elif deductible_bldg==4000 and deductible_cont==1500:
            fullrisk = 0.900
        elif deductible_bldg==4000 and deductible_cont==2000:
            fullrisk = 0.875
        elif deductible_bldg==4000 and deductible_cont==3000:
            fullrisk = 0.825
        elif deductible_bldg==4000 and deductible_cont==4000:
            fullrisk = 0.775

        elif deductible_bldg==5000 and deductible_cont==1000:
            fullrisk = 0.900
        elif deductible_bldg==5000 and deductible_cont==1250:
            fullrisk = 0.890
        elif deductible_bldg==5000 and deductible_cont==1500:
            fullrisk = 0.875
        elif deductible_bldg==5000 and deductible_cont==2000:
            fullrisk = 0.850
        elif deductible_bldg==5000 and deductible_cont==3000:
            fullrisk = 0.800
        elif deductible_bldg==5000 and deductible_cont==4000:
            fullrisk = 0.760
        elif deductible_bldg==5000 and deductible_cont==5000:
            fullrisk = 0.750

        elif deductible_bldg==10000 and deductible_cont==10000:
            fullrisk = 0.600    
        else:
            pass    

        total_bldg_BasicCoverage = []
        total_bldg_AddiCoverage = []
        total_cont_BasicCoverage = []
        total_cont_AddiCoverage = []    
        principle_premium = []
        deducted_premium = []
        total_annual_premium = []

        


        for i in range(len(totalBFE)):

            if No_Floors == "1" :    
                #print("one one one")
                total_bldg_BasicCoverage.append( (( basic_bldg_insurance_limit )/100) * BasicRate_1s_Bldg_BFE[i])
                total_bldg_AddiCoverage.append( (( addi_bldg_insurance_amnt )/100) * AddiRate_1s_Bldg_BFE[i])

                total_cont_BasicCoverage.append( (( basic_cont_insurance_limit )/100) * BasicRate_1s_Cont_BFE[i])
                total_cont_AddiCoverage.append( (( addi_cont_insurance_amnt )/100) * AddiRate_1s_Cont_BFE[i])
                # print("basicrate_B : ", BasicRate_1s_Bldg_BFE[i])
                # print("additionalraterate_B : ", AddiRate_1s_Bldg_BFE[i])
                # print("basicrate_C : ", BasicRate_1s_Cont_BFE[i])
                # print("additionalraterate_C : ", AddiRate_1s_Cont_BFE[i])
                # print("total building basic cov : ",  total_bldg_BasicCoverage, "total building additional cov : ", total_bldg_AddiCoverage)
                # print("total content basic cov : ",  total_cont_BasicCoverage, "total content additional cov : ", total_cont_AddiCoverage)
            elif No_Floors == "2" : 
                #print("two two two")
                total_bldg_BasicCoverage.append( (( basic_bldg_insurance_limit )/100) * BasicRate_2s_Bldg_BFE[i])
                total_bldg_AddiCoverage.append( (( addi_bldg_insurance_amnt )/100) * AddiRate_2s_Bldg_BFE[i])

                total_cont_BasicCoverage.append( (( basic_cont_insurance_limit )/100) * BasicRate_2s_Cont_BFE[i])
                total_cont_AddiCoverage.append( (( addi_cont_insurance_amnt )/100) * AddiRate_2s_Cont_BFE[i])
            else:
                pass

            principle_premium.append(round(((total_bldg_BasicCoverage[i] + total_bldg_AddiCoverage[i]) + (total_cont_BasicCoverage[i] + total_cont_AddiCoverage[i])),0))

            #deductible factor d is fullrisk
            deducted_premium.append(round((principle_premium[i] * fullrisk),0))
            #print("Deducted premium : ", deducted_premium)

            #total_annual_premium.append( int(((deducted_premium[i] + ICC_premium - CRS) + Reserve_fund * (deducted_premium[i] + ICC_premium - CRS)) + HFIAA_surcharge + Federal_policy_fee))
            total_annual_premium.append( int(((deducted_premium[i] + ICC_premium - CRS*(deducted_premium[i] + ICC_premium)) + Reserve_fund * (deducted_premium[i] + ICC_premium - CRS*(deducted_premium[i] + ICC_premium))) + HFIAA_surcharge + Federal_policy_fee))
     
            #print("Total annual premium : ", total_annual_premium)
            
            
            total_annual_premium_json = simplejson.dumps(total_annual_premium)  

            optimal_total_annual_premium = min(total_annual_premium)
        
            for k in range(len(total_annual_premium)):
                if optimal_total_annual_premium == total_annual_premium[k]:
                    optimal_total_annual_premium_freeboard = totalBFE[k]
    
        optimal_total_annual_premium_json = simplejson.dumps(optimal_total_annual_premium)  
        print("Deducted premium : ", deducted_premium)
        print("Total annual premium : ", total_annual_premium)
        total_annual_premium_list_c.append(total_annual_premium)
    
        ###---------------Insurance ends---------------------------------------

        


        ##---------------Amortized freeboard cost--------------------------
        Amortized_FC = []
        for i in range(len(totalBFE)): 
            principle_monthly_payment = (freeboardCost[i] * (r/n))/(1-((1+(r/n))**(-n*t)))
            loan_fees = principle_monthly_payment * 0.07
            Amortized_FC.append(int(principle_monthly_payment + loan_fees))

        Amortized_FC_json = simplejson.dumps(Amortized_FC)    

        print("Amortised cost :  ", Amortized_FC)

        ##--------------Avoided annual loss and monthly avoided loss---------------------------------    ####check*********
        annual_avoided_loss = []
        
        for i in range(len(totalBFE)):                                ###check************ i+1
            # if i==0:
            #     annual_avoided_loss.append((AAL_absCurrency[0]) 
            # else:    
            #     annual_avoided_loss.append(AAL_absCurrency[0]-AAL_absCurrency[i])  
            annual_avoided_loss.append(AAL_absCurrency[0]-AAL_absCurrency[i])          
        print("Avoided annual loss :  ", annual_avoided_loss)

        annual_avoided_loss_json = simplejson.dumps(annual_avoided_loss)  

        monthly_avoided_loss = []
        for i in range(len(totalBFE)): 
            monthly_avoided_loss.append(int(annual_avoided_loss[i]/12))
        print("Avoided monthly loss :  ", monthly_avoided_loss)

        monthly_avoided_loss_json = simplejson.dumps(monthly_avoided_loss)

        ##-----------------Annual and monthly premium saving------------------------------         ###check************
        annual_premium_saving = []
        
        for i in range(len(totalBFE)):                                   ###check************ i+1
            # if i ==0:
            #     annual_premium_saving.append(total_annual_premium[0]) 
            # else:    
            #     annual_premium_saving.append(total_annual_premium[0]-total_annual_premium[i])
            annual_premium_saving.append(total_annual_premium[0]-total_annual_premium[i])    
        print("Annual premium saving :  ", annual_premium_saving)
        annual_premium_saving_json = simplejson.dumps(annual_premium_saving)  

        monthly_premium_saving = []
        for i in range(len(totalBFE)):
            monthly_premium_saving.append(int(annual_premium_saving[i]/12))
        print("Monthly premium saving :  ", monthly_premium_saving)
        monthly_premium_saving_json = simplejson.dumps(monthly_premium_saving)


        ##-----------Total monthly saving---------------------------------------------
        total_monthly_saving = []
        
        for i in range(len(totalBFE)): 
            total_monthly_saving.append(int((annual_premium_saving[i]/12)+(annual_avoided_loss[i]/12)-Amortized_FC[i]))
        print("Total monthly saving :  ", total_monthly_saving)
        total_monthly_saving_list_c.append(total_monthly_saving)
        
        optimal_saving = max(total_monthly_saving)
        total_optimal_saving_list_c.append(max(total_monthly_saving))
        
        for k in range(len(total_monthly_saving)):
            if optimal_saving == total_monthly_saving[k]:
                optimal_freeboard = totalBFE[k]
        total_optimal_freeboard_list_c.append(optimal_freeboard)

        total_monthly_saving_json = simplejson.dumps(total_monthly_saving)  
        optimal_saving_json = simplejson.dumps(optimal_saving)  

        ##-----------Total yearly saving---------------------------------------------
        total_yearly_saving = []
        for i in range(len(totalBFE)): 
            total_yearly_saving.append(int(total_monthly_saving[i] * 12))
        print("Total yearly saving :  ", total_yearly_saving)
        

        ##-----------Total loanbased freeboard cost---------------------------------------------
        total_loanbased_FC = []
        for i in range(len(totalBFE)): 
            total_loanbased_FC.append(round(Amortized_FC[i] * 12 * t,2))
        print("Total loanbased freeboard cost :", total_loanbased_FC)

        ##---------Time to recover freeboard cost through premium savings alone------------
        time_to_recover_FC_PS = []
        #time_to_recover_FC_PS.append(round(total_loanbased_FC[i]/annual_premium_saving[i],1))
        for i in range(len(totalBFE)):
            if annual_premium_saving[i] == 0:
                time_to_recover_FC_PS.append(0)    ##
            else:    
                time_to_recover_FC_PS.append(round(total_loanbased_FC[i]/annual_premium_saving[i],1))
        print("Time to recover FC PS :", time_to_recover_FC_PS)
            
        time_to_recover_FC_PS_json = simplejson.dumps(time_to_recover_FC_PS)  

        ##---------Time to recover freeboard cost through avoided annual loss alone------------
        time_to_recover_FC_AvAL = []
        #time_to_recover_FC_AvAL.append(round(total_loanbased_FC[i]/annual_avoided_loss[i],1))
        for i in range(len(totalBFE)):
            if annual_avoided_loss[i] == 0:
                time_to_recover_FC_AvAL.append(0) ##
            else:    
                time_to_recover_FC_AvAL.append(round(total_loanbased_FC[i]/annual_avoided_loss[i],1))
        print("Time to recover FC AvAL :", time_to_recover_FC_AvAL)

        
        ##---------Time to recover freeboard cost through total benefit------------
        time_to_recover_FC_TB = []
        #time_to_recover_FC_TB.append(round(total_loanbased_FC[i]/(annual_premium_saving[i] + annual_avoided_loss[i]),1))   
        #print("Time to recover freeboard cost through total benefit", time_to_recover_FC_TB)
        for i in range(len(totalBFE)):
            if (annual_premium_saving[i] + annual_avoided_loss[i]) == 0:
                time_to_recover_FC_TB.append(0) ##
            else:    
                time_to_recover_FC_TB.append(round(total_loanbased_FC[i]/(annual_premium_saving[i] + annual_avoided_loss[i]),1))    

        print("Time to recover freeboard cost through total benefit", time_to_recover_FC_TB)
        time_to_recover_FC_TB_list_c.append(time_to_recover_FC_TB)
        time_to_recover_FC_TB_json = simplejson.dumps(time_to_recover_FC_TB)  

    ##---------Time to recover freeboard cost through monthly savings------------
        time_to_recover_FC_MS = []
        for i in range(len(totalBFE)):
            if (total_monthly_saving[i] == 0):
                time_to_recover_FC_MS.append(0) ##
            else:    
                time_to_recover_FC_MS.append(round((total_loanbased_FC[i]/(total_monthly_saving[i])),1) ) 
        print("Time to recover freeboard cost through monthly savings", time_to_recover_FC_MS)

        time_to_recover_FC_MS_json = simplejson.dumps(time_to_recover_FC_MS)       

        ##----------------------------------------------------------------------------
    

        ##---------------------total cost------------------------------
        totalcost = []
        for i in range(len(AAL_absCurrency)):
            totalcost.append(round((AAL_absCurrency[i]+total_annual_premium[i])*12+freeboardCost[i],3))    #discounted present value, estimated from:   1(1+R_D )^t = 12  for 7% real discount rate
        

        ##--------------------Net benefit-------------------------------

        #Net benefit (NB) is determined by subtracting the total cost of the freeboard scenario (step 10) 
        #from the total cost of the no action scenario.
        netbenefit = []
        for i in range(len(totalcost)):
            netbenefit.append(int(totalcost[0]-totalcost[i]))

        ##------------------Net benefit cost ratio-----------------------------------------------

        #Net benefit to cost ratio (NBCR) for each freeboard is the total net benefit of the freeboard scenario divided by its total cost.  

        # NBcostRatio = []
        # for i in range(len(totalcost)):
        #     if i==0:
        #         NBcostRatio.append(0)
        #     else:    
        #         NBcostRatio.append(math.trunc(netbenefit[i]/freeboardCost[i]))
        #     print(NBcostRatio[i])

        

    ##########-----for summery analysis section ---------------##########
    ##----------------TOTAL----savings per month (flood insurance only)---------------------

        total_savings_permonth_insurance = []
        for i in range(len(totalBFE)):
            total_savings_permonth_insurance.append(monthly_premium_saving[i]-Amortized_FC[i])
        print("total_savings_permonth_insurance :",total_savings_permonth_insurance)



    
   
    ##------------------barchart for insurance-------------------------------
    benefits = ['Insurance per year'] #['Construction Cost', 'Insurance ', 'AAL', 'Total Cost', 'Net Benefit']
    nofStories = ['BFE + 0ft','BFE + 1ft', 'BFE + 2ft','BFE + 3ft','BFE + 4ft']

    data = {'benefits' : benefits,
            'BFE + 0ft'   : [total_annual_premium[0]],  
            'BFE + 1ft'   : [total_annual_premium[1]], 
            'BFE + 2ft'   : [total_annual_premium[2]],  
            'BFE + 3ft'   : [total_annual_premium[3]],  
            'BFE + 4ft'   : [total_annual_premium[4]]}  

    x = [nofStories]
    counts = sum(zip( data['BFE + 0ft'],data['BFE + 1ft'],data['BFE + 2ft'], data['BFE + 3ft'],data['BFE + 4ft']), ()) # like an hstack
    
    source = ColumnDataSource(data=data)

    p = figure(x_range=benefits, plot_height=350, plot_width=500, 
            toolbar_location="below", tools="save, pan, wheel_zoom, box_zoom, reset, tap, crosshair")

    p.vbar(x=dodge('benefits',  -0.30,  range=p.x_range), top='BFE + 0ft', width=0.1, source=source,
        color="#253494", legend_label="BFE + 0ft")

    p.vbar(x=dodge('benefits',  -0.15,  range=p.x_range), top='BFE + 1ft', width=0.1, source=source,
        color="#2c7fb8", legend_label="BFE + 1ft")

    p.vbar(x=dodge('benefits',  0.00, range=p.x_range), top='BFE + 2ft', width=0.1, source=source,
        color="#41b6c4", legend_label="BFE + 2ft")
    
    p.vbar(x=dodge('benefits', 0.15, range=p.x_range), top='BFE + 3ft', width=0.1, source=source,
        color="#a1dab4", legend_label="BFE + 3ft")

    p.vbar(x=dodge('benefits', 0.30, range=p.x_range), top='BFE + 4ft', width=0.1, source=source,
        color="#ffffcc", legend_label="BFE + 4ft")
    
    p.y_range.start = 0
    p.xgrid.grid_line_color = None
    p.legend.location = "top_left"
    p.legend.orientation = "horizontal"
    
    # tooltip
    p.add_tools(HoverTool(
    tooltips=[
        ("Type", "@benefits"),
        ("Cost", "@count")
    ],

    # display a tooltip whenever the cursor is vertically in line with a glyph
    mode='vline'
    ))
    script_insurance, div_insurance = components(p)

    
    ##----------------barchart ends---------------------------------------
        
    ##New-------------------------------
    ##barchart for Net benefit to cost ratio-------------------------------
    ##benefits = ['1 foot freeboard', '2 feet freeboard', '3 feet freeboard', '4 feet freeboard']
    ##nofStories = ['Net benefit to cost ratio']
       
    #New barchart ends---------------------------------------

   ####################********Community level analysis ENDS*********########################
    print("\n")
    ## Total monthly saving ##
    print("total_monthly_saving_list_c : ", total_monthly_saving_list_c)

  
    summation_total_monthly_saving = []
    avg_total_monthly_saving = []
    for z in range(len(total_monthly_saving)):
        summation_total_monthly_saving.append(0)
    #print("summationlist_total_monthly_saving = " ,summation_total_monthly_saving)

    for i in range(len(buildinglist)):   
        for z in range(len(total_monthly_saving)):
            summation_total_monthly_saving[z] = summation_total_monthly_saving[z] + total_monthly_saving_list_c[i][z]
    print("summationlist_total_monthly_saving = " ,summation_total_monthly_saving)
    summation_total_monthly_saving_json = simplejson.dumps(summation_total_monthly_saving)        
    
    for z in range(len(total_monthly_saving)):
        avg_total_monthly_saving.append(int(summation_total_monthly_saving[z]/len(buildinglist)))
    print("avglist_total_monthly_saving = " ,avg_total_monthly_saving) 


    print("total_optimal_saving_list_c  : " , total_optimal_saving_list_c)
    print("total_optimal_freeboard_list_c : ", total_optimal_freeboard_list_c)

    optimal_saving = max(summation_total_monthly_saving)
    optimal_saving_json = simplejson.dumps(optimal_saving) 

    print("\n")
    
   ## Freeboard cost ##

    print("freeboardCost_list_c : ", freeboardCost_list_c)

  
    summation_freeboardCost = []
    avg_freeboardCost = []
    for z in range(len(freeboardCost)):
        summation_freeboardCost.append(0)
    #print("summationlist_freeboardCost = " ,summation_freeboardCost)

    for i in range(len(buildinglist)):   
        for z in range(len(freeboardCost)):
            summation_freeboardCost[z] = summation_freeboardCost[z] + freeboardCost_list_c[i][z]
    print("summationlist_freeboardCost = " ,summation_freeboardCost)
    summation_freeboardCost_json = simplejson.dumps(summation_freeboardCost )

    for k in range(len(summation_total_monthly_saving)):
        if optimal_saving == summation_total_monthly_saving[k]:
            optimal_freeboard = totalBFE[k]

    
    for z in range(len(freeboardCost)):
        avg_freeboardCost.append(int(summation_freeboardCost[z]/len(buildinglist)))
    print("avglist_freeboardCost = " ,avg_freeboardCost) 
    print("\n")

    
    ## Total annual premium ##
    print("total_annual_premium_list_c : ", total_annual_premium_list_c)

    summation_total_annual_premium = []
    avg_total_annual_premium = []
    for z in range(len(total_annual_premium)):
        summation_total_annual_premium.append(0)
    #print("summationlist_total_annual_premium = " ,summation_total_annual_premium)

    for i in range(len(buildinglist)):   
        for z in range(len(total_annual_premium)):
            summation_total_annual_premium[z] = summation_total_annual_premium[z] + total_annual_premium_list_c[i][z]
    print("summationlist_total_annual_premium = " ,summation_total_annual_premium)        
    summation_total_annual_premium_json = simplejson.dumps(summation_total_annual_premium)


    for z in range(len(total_annual_premium)):
        avg_total_annual_premium.append(int(summation_total_annual_premium[z]/len(buildinglist)))
    print("avglist_total_annual_premium = " ,avg_total_annual_premium) 
    print("\n")

    ## Expected annual flood loss ##
    print("AAL_absCurrency_list_c : ", AAL_absCurrency_list_c)

    summation_AAL_absCurrency = []
    avg_AAL_absCurrency = []
    for z in range(len(AAL_absCurrency)):
        summation_AAL_absCurrency.append(0)
    #print("summationlist_AAL_absCurrency = " ,summation_AAL_absCurrency)

    for i in range(len(buildinglist)):   
        for z in range(len(AAL_absCurrency)):
            summation_AAL_absCurrency[z] = summation_AAL_absCurrency[z] + AAL_absCurrency_list_c[i][z]
    print("summationlist_AAL_absCurrency = " ,summation_AAL_absCurrency)        
    summation_AAL_absCurrency_json = simplejson.dumps(summation_AAL_absCurrency)

    for z in range(len(AAL_absCurrency)):
        avg_AAL_absCurrency.append(int(summation_AAL_absCurrency[z]/len(buildinglist)))
    print("avglist_AAL_absCurrency = " ,avg_AAL_absCurrency) 
    print("\n")

## Time to recover the freeboard cost ##
    print("time_to_recover_FC_TB_list_c : ", time_to_recover_FC_TB_list_c)
 
    summation_time_to_recover_FC_TB = []
    avg_time_to_recover_FC_TB = []
    for z in range(len(time_to_recover_FC_TB)):
        summation_time_to_recover_FC_TB.append(0)
    #print("summationlist_time_to_recover_FC_TB = " ,summation_time_to_recover_FC_TB)

    for i in range(len(buildinglist)):   
        for z in range(len(time_to_recover_FC_TB)):
            summation_time_to_recover_FC_TB[z] = round(summation_time_to_recover_FC_TB[z] + time_to_recover_FC_TB_list_c[i][z],3)
    print("summationlist_time_to_recover_FC_TB = " ,summation_time_to_recover_FC_TB)
    summation_time_to_recover_FC_TB_json = simplejson.dumps(summation_time_to_recover_FC_TB)       
    
    for z in range(len(time_to_recover_FC_TB)):
        avg_time_to_recover_FC_TB.append(round(summation_time_to_recover_FC_TB[z]/len(buildinglist),3))
    print("avglist_time_to_recover_FC_TB = " ,avg_time_to_recover_FC_TB) 
    print("\n")

    ####################********Community level analysis ENDS*********########################

    #Json---------------------------------------
    time_to_recover_FC_TB_json = summation_time_to_recover_FC_TB_json
    freeboardCost_json = summation_freeboardCost_json
    total_annual_premium_json = summation_total_annual_premium_json
    total_monthly_saving_json = summation_total_monthly_saving_json
    AAL_absCurrency_json = summation_AAL_absCurrency_json
    
    location_json_list = simplejson.dumps(location)    

    data_dictionary = {"location": location_json_list, "time_to_recover_FC_TB_json":time_to_recover_FC_TB_json, "time_to_recover_FC_PS1": time_to_recover_FC_PS[1], "time_to_recover_FC_PS2": time_to_recover_FC_PS[2],"time_to_recover_FC_PS3": time_to_recover_FC_PS[3],"time_to_recover_FC_PS4": time_to_recover_FC_PS[4], "time_to_recover_FC_TB1": time_to_recover_FC_TB[1], "time_to_recover_FC_TB2": time_to_recover_FC_TB[2], "time_to_recover_FC_TB3": time_to_recover_FC_TB[3], "time_to_recover_FC_TB4": time_to_recover_FC_TB[4], "optimal_total_annual_premium_freeboard":optimal_total_annual_premium_freeboard, "optimal_total_annual_premium":optimal_total_annual_premium, "total_annual_premium_json":total_annual_premium_json,"total_annual_premium0": total_annual_premium[0],"total_annual_premium1": total_annual_premium[1],"total_annual_premium2": total_annual_premium[2],"total_annual_premium3": total_annual_premium[3],"total_annual_premium4": total_annual_premium[4],"total_savings_permonth_insurance0" :total_savings_permonth_insurance[0],"total_savings_permonth_insurance1" :total_savings_permonth_insurance[1],"total_savings_permonth_insurance2" :total_savings_permonth_insurance[2],"total_savings_permonth_insurance3" :total_savings_permonth_insurance[3],"total_savings_permonth_insurance4" :total_savings_permonth_insurance[4],"optimal_freeboardCost": optimal_freeboardCost,"optimal_freeboard_freeboardCost":optimal_freeboard_freeboardCost,"optimal_freeboardCost_json":optimal_freeboardCost_json, "optimal_AAL_absCurrency_freeboard":optimal_AAL_absCurrency_freeboard, "optimal_AAL_absCurrency": optimal_AAL_absCurrency, "AAL_absCurrency0":AAL_absCurrency[0],"AAL_absCurrency1":AAL_absCurrency[1],"AAL_absCurrency2":AAL_absCurrency[2],"AAL_absCurrency3":AAL_absCurrency[3],"AAL_absCurrency4":AAL_absCurrency[4],"AAL_absCurrency_json":AAL_absCurrency_json, "monthly_premium_saving_json":monthly_premium_saving_json,"monthly_premium_saving0": monthly_premium_saving[0],"monthly_premium_saving1": monthly_premium_saving[1],"monthly_premium_saving2": monthly_premium_saving[2],"monthly_premium_saving3": monthly_premium_saving[3],"monthly_premium_saving4": monthly_premium_saving[4], "Actual_construction_cost": Actual_construction_cost, "Amortized_FC_json" : Amortized_FC_json, "Amortized_FC0": Amortized_FC[0], "Amortized_FC1": Amortized_FC[1], "Amortized_FC2": Amortized_FC[2], "Amortized_FC3": Amortized_FC[3], "Amortized_FC4": Amortized_FC[4],"floodzone": zonevalue, "optimal_saving_json":optimal_saving_json, "freeboardCost_json": freeboardCost_json, "monthly_avoided_loss_json": monthly_avoided_loss_json, "annual_avoided_loss_json": annual_avoided_loss_json, "total_annual_premium": total_annual_premium, "total_monthly_saving_json":total_monthly_saving_json, "time_to_recover_FC_MS": time_to_recover_FC_MS, "time_to_recover_FC_PS_json": time_to_recover_FC_PS_json, "SquareFootage":Square_footage, "No_Floors": No_Floors, "OptimalSaving" : optimal_saving, "OptimalFreeboard" : optimal_freeboard, "FreeboardCost0": freeboardCost[0], "FreeboardCost1": freeboardCost[1], "FreeboardCost2": freeboardCost[2], "FreeboardCost3": freeboardCost[3], "FreeboardCost4": freeboardCost[4], "total_monthly_saving0" : total_monthly_saving[0],"total_monthly_saving1" : total_monthly_saving[1],"total_monthly_saving2" : total_monthly_saving[2],"total_monthly_saving3" : total_monthly_saving[3],"total_monthly_saving4" : total_monthly_saving[4], "AAL_absCurrency0": AAL_absCurrency[0],"AAL_absCurrency1": AAL_absCurrency[1],"AAL_absCurrency2": AAL_absCurrency[2],"AAL_absCurrency3": AAL_absCurrency[3],"AAL_absCurrency4": AAL_absCurrency[4], "total_annual_premium_BFE": total_annual_premium[0], "total_annual_premium_BFE1": total_annual_premium[1], "total_annual_premium_BFE2": total_annual_premium[2], "total_annual_premium_BFE3": total_annual_premium[3], "total_annual_premium_BFE4": total_annual_premium[4], "monthly_avoided_loss0": monthly_avoided_loss[0], "monthly_avoided_loss1": monthly_avoided_loss[1],"monthly_avoided_loss2": monthly_avoided_loss[2],"monthly_avoided_loss3": monthly_avoided_loss[3],"monthly_avoided_loss4": monthly_avoided_loss[4],"time_to_recover_FC_MS0" : time_to_recover_FC_MS[0], "time_to_recover_FC_MS1" : time_to_recover_FC_MS[1],"time_to_recover_FC_MS2" : time_to_recover_FC_MS[2],"time_to_recover_FC_MS3" : time_to_recover_FC_MS[3],"time_to_recover_FC_MS4" : time_to_recover_FC_MS[4], "netbenefit0" : netbenefit[0],"netbenefit1" : netbenefit[1],"netbenefit2" : netbenefit[2],"netbenefit3" : netbenefit[3], "netbenefit4" : netbenefit[4], 'script_insurance': script_insurance, 'div_insurance':div_insurance,  "annual_avoided_loss0": annual_avoided_loss[0], "annual_avoided_loss1": annual_avoided_loss[1],"annual_avoided_loss2":annual_avoided_loss[2],"annual_avoided_loss3": annual_avoided_loss[3],"annual_avoided_loss4": annual_avoided_loss[4] }

    
    return render(request, 'nodisc.html', data_dictionary)


def starter(request):
  
    source = ColumnDataSource(data=dict(
    x=[1, 2, 3, 4, 5],
    y1=[500,1500,3500,4000,7000],
    y2=[300, 200,150, 100, ],
    ))
    p = figure(plot_width=400, plot_height=400)

    p.vline_stack(['y1', 'y2'], x='x', source=source)
    p.x_range.range_padding = 0.1
    p.xgrid.grid_line_color = None
    p.legend.location = "top_left"
    p.legend.orientation = "horizontal"

    script, div = components(p)
    return render(request, 'starter.html' , {'script': script, 'div':div})

