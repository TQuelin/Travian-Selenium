# -*- coding: utf-8 -*-
"""
Created on Sat Mar 26 12:26:40 2022

@author: tomqu
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import numpy as np


class TravianSeleniumApi:

    def __init__(self, user, pwd, server, domain='com'):
        self.user = user
        self.pwd = pwd
        self.server = server
        self.domain = domain
        self.console = '[TravianAutoBot]'
        print(self.console,'Start','%dh%dm%ds'%(time.localtime()[3:6]))
        self.driver = webdriver.Firefox()
        self.driver.get('https://%s.travian.%s'%(server,domain))
        time.sleep(5)
        self.login()
        self.construction_order = []
    
    def __del__(self):
        self.close()
        
    def close(self):
        self.driver.close()
        print(self.console,'Finish')
        
    def login(self):
        try:
            # Accept cookies if there
            self.driver.find_element(By.XPATH,'/html/body/div[1]/div[1]/div[2]/span[1]/a').click()
        except:
            pass
        
        try:
            userform = self.driver.find_element(By.XPATH,"/html/body/div[3]/div[2]/div[2]/div[2]/div/div/div[1]/form/table/tbody/tr[1]/td[2]/input")
            userform.clear()
            userform.send_keys(self.user)
            
            pwdform = self.driver.find_element(By.XPATH,"/html/body/div[3]/div[2]/div[2]/div[2]/div/div/div[1]/form/table/tbody/tr[2]/td[2]/input")
            pwdform.clear()
            pwdform.send_keys(self.pwd)
            
            loginbutton = self.driver.find_element(By.XPATH,"//*[@id='s1']")
            loginbutton.click()
            print(self.console,'successfully logged in')
        except:
            print(self.console,'unsuccessfully logged in')


    def string2int(self,string):
        string2 = ""
        string = string.replace(',','')
        for carac in string:
            if carac in ['\u202a','\u202b','\u202c','\u202d','\u202e']:
                pass
            else :
                string2 += carac
        return int(string2)
           
     
    def goToResourcesPage(self):
        self.driver.get('https://%s.travian.%s/dorf1.php'%(self.server,self.domain))
    
    
    def goToBuildingsPage(self):
        self.driver.get('https://%s.travian.%s/dorf2.php'%(self.server,self.domain))
        
        
    def get_warehouse_capacity(self):
        self.goToResourcesPage()
        value = self.driver.find_element(By.XPATH,"//*[@id='stockBar']")
        capacity = self.string2int(value.text.split('\n')[0])
        return capacity
    
    
    def get_granary_capacity(self):
        self.goToResourcesPage()
        value = self.driver.find_element(By.XPATH,"//*[@id='stockBar']")
        capacity = self.string2int(value.text.split('\n')[4])
        return capacity
    
    
    def get_actual_resources(self):
        value = self.driver.find_element(By.XPATH,"//*[@id='stockBar']")
        string = value.text
        string = string.replace(',','')
        string = string.split('\n')
        string.pop(4)
        string.pop(0)
        return list(map(self.string2int,string[:4]))
    
    def get_actual_production(self):
        self.goToResourcesPage()
        production = self.driver.find_element(By.XPATH,'//*[@id="production"]')
        production = production.find_elements(By.XPATH,'//*[@class="num"]')
        nbre = [self.string2int(production[0].text),self.string2int(production[1].text),self.string2int(production[2].text),self.string2int(production[3].text)]
        return nbre


    def get_village_list(self):
        villages = self.driver.find_element(By.CLASS_NAME,'villageList')
        villages = villages.find_elements(By.XPATH,'*//a')
        villageList = ''
        for village in villages:
            viviId = village.get_attribute('href').split('=')[-1]
            villageList.append(viviId)
        self.villageList = villageList
		
    def goToVillage(self, number):
        villageId = self.villageList[number]
        self.driver.get('https://%s.travian.%s/dorf1.php?newid=%s'%(self.server,self.domain,villageId))
			
    def time_before_full(self):
        ress = self.get_actual_resources()
        capa = [self.get_warehouse_capacity(),self.get_granary_capacity()]
        prod = self.get_actual_production()
        ressmissing = np.append(capa[0]-np.array(ress[:3]),(capa[1]-ress[3]))
        time_bf_full = ressmissing*3600//np.array(prod)
        return time_bf_full

    def is_full(self):
        return not self.time_before_full().all()

    def is_busy(self):
        '''
        Returns
        -------
        int
            0 if is not busy.
            busy time in sec either.

        '''
        self.goToResourcesPage()
        try:
            construction = self.driver.find_element(By.XPATH,'//*[@class="buildingList"]')
            busytime = construction.find_element(By.XPATH,'//*[@class="buildDuration"]/span').get_attribute("value")
            return int(busytime.replace(',',''))
        except:
            return 0
        
        
    def upgrade(self,solarId):
        self.driver.get('https://%s.travian.%s/build.php?id=%d'%(self.server,self.domain,solarId))
        try :
            button = self.driver.find_element(By.XPATH,'//*[@class="textButtonV1 green build"]')
            button.click()
            return 1
        except:
            return 0
        
    def upgrade_faster(self,solarId):
        self.driver.get('https://%s.travian.%s/build.php?id=%d'%(self.server,self.domain,solarId))
        try :
            button = self.driver.find_element(By.XPATH,'//*[@class="textButtonV1 green build videoFeatureButton"]')
            button.click()
            time.sleep(20)
            return 1
        except:
            return 0
        
    
    def new_building(self,building,solarId):
        self.driver.get('https://%s.travian.%s/build.php?id=%d'%(self.server,self.domain,solarId))
        builds = self.driver.find_elements(By.CLASS_NAME,'buildingWrapper')
        flag = False
        for build in builds:
            if build.find_element(By.XPATH,'h2').text == building:
                print(self.console,'Creating ',build.find_element(By.XPATH,'h2').text)
                build.find_element(By.XPATH,'*//button').click()
                flag = True
                break
        if not(flag):
            print('%s is not existing'%building)
    

    
    def upgrade_needs(self,solarId):
        self.driver.get('https://%s.travian.%s/build.php?id=%d'%(self.server,self.domain,solarId))
        value = self.driver.find_element(By.XPATH,'//*[@id="contract"]')
        ress = value.find_elements(By.XPATH,'//*[@class="inlineIcon resource"]')
        ress = [ress[0].text,ress[1].text,ress[2].text,ress[3].text]
        return list(map(int,ress))
        
    
    def is_enough_ress(self,solarId):
        ress_needs = self.upgrade_needs(solarId)
        ress_available = self.get_actual_resources()
        ress_prod = self.get_actual_production()
        time2wait = []
        for ress,needs,prod in zip(ress_available,ress_needs,ress_prod):
            if ress > needs:
                time2wait.append(0)
            else:
                time2wait.append((needs-ress)//(prod/3600))
        tmax = 0
        for t in time2wait:
            if t>tmax:
                tmax=t            
        return tmax
        
        
    def add_order(self,solarId):
        self.construction_order.append(solarId)
        
        
    def start(self):
        
        while len(self.construction_order) > 0:
            busytime = self.is_busy()
            print(self.console,'busy during %ds'%busytime)
            time.sleep(busytime+5)
            time.sleep(self.is_enough_ress(self.construction_order[0]))
            if self.upgrade(self.construction_order[0]):
                print(self.console,self.construction_order[0],' was upgraded')
                self.construction_order.pop(0)
            else:
                print(self.console,self.construction_order[0],' fail to upgrade')
                print(self.console,'remaining constructions :',len(self.construction_order))


    def send_attack(self,x,y,mode=2,t1=0,t2=0,t3=0,t4=0,t5=0,t6=0,t7=0,t8=0,t9=0,t10=0,t11=0):
        self.driver.get('https://%s.travian.%s/build.php?id=39&gid=16&tt=2'%(self.server,self.domain))
        dic = {'t1':t1,'t2':t2,'t3':t3,'t4':t4,'t5':t5,'t6':t6,'t7':t7,'t8':t8,'t9':t9,'t10':t10,'t11':t11}
        time.sleep(0.2)
        table = self.driver.find_element(By.XPATH,'//*[@id="build"]/div/form')
        for key, value in dic.items():
            troop = table.find_element(By.NAME,'troops[0][%s]'%key)
            troop.send_keys(value)
        
        coordx = table.find_element(By.NAME,'x')
        coordx.send_keys(str(x))
        coordy = table.find_element(By.NAME,'y')
        coordy.send_keys(str(y))
        attackType = table.find_elements(By.NAME,'c')
        attackType[mode].click()
        table.submit()
        bouton = self.driver.find_element(By.XPATH,'//*[@id="btn_ok"]')
        bouton.click()
        
        
    def train_troops(self,tn,amount):
        if tn<=3:
            self.driver.get('https://%s.travian.%s/build.php?id=23'%(self.server,self.domain))
        elif tn<=6:
            tn = tn-3
            print('TODO')
        elif tn<=9:
            tn = tn-6
            print('TODO')
        else:
            return 0
        
        table = self.driver.find_element(By.XPATH,'//*[@id="nonFavouriteTroops"]')
        troops = table.find_elements(By.XPATH,'*//input')
        troops[tn-1].send_keys(amount)
        btn = self.driver.find_element(By.NAME,'s1')
        btn.click()
        print(self.console,'Training of %d of type %d'%(amount,tn))
             
           
    def start_adventure(self,number):
        self.driver.get('https://%s.travian.%s/hero/adventures'%(self.server,self.domain))

        table = self.driver.find_element(By.XPATH,'//*[@id="adventureListForm"]')
        forms = table.find_elements(By.XPATH,'*//form')
        forms[number].submit()
        print(self.console,'Adventure n°%d started'%number)
        
    def get_field_levels(self):
        self.goToResourcesPage()
        levelsa=self.driver.find_elements(By.XPATH,'/html/body/div[3]/div[3]/div[2]/div/div[1]/a')[1:]
        levels=[]
        for level in levelsa:
            levels.append(int(level.text))
        return levels
    
    def example(self):
        #value = self.driver.find_element(By.XPATH,'')
        pass
    

# value = player.driver.find_element(By.XPATH,'//*[@id="contract"]')