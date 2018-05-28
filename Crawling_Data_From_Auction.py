# -*- coding: utf-8 -*-
"""
Created on Wed Sep 27 17:16:00 2017

@author: Xinqing Wen
"""

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
import pandas as pd

city_list = ['collin','denton','harris','galveston','brazoria','fort-bend','montgomery', 'bexar','Comal','guadalupe','travis','williamson','bell', 'hidalgo', 'el-paso', 'cameron', 'nueces']

label_full = ['Property Type', 'Bedrooms', 'Bathrooms', 'Square Footage', 'Lot Size (acres)', 'Year Built',
              'Foreclosure / Trustee #', 'APN', 'Event Item #', 'Property ID']

label = ['.col1 .row_index_i6jc:nth-child(1) .label_index_2LU_ span', '.col1 .row_index_i6jc:nth-child(2) .label_index_2LU_ span',
         '.col1 .row_index_i6jc:nth-child(3) .label_index_2LU_ span', '.col1 .row_index_i6jc:nth-child(4) .label_index_2LU_ span',
         '.col1 .row_index_i6jc:nth-child(5) .label_index_2LU_ span', '.col1 .row_index_i6jc:nth-child(6) .label_index_2LU_ span',
         '.col2 .row_index_i6jc:nth-child(1) .label_index_2LU_ span', '.col2 .row_index_i6jc:nth-child(2) .label_index_2LU_ span',
         '.col2 .row_index_i6jc:nth-child(3) .label_index_2LU_ span', '.col2 .row_index_i6jc:nth-child(4) .label_index_2LU_ span']

value = ['.col1 .row_index_i6jc:nth-child(1) .value_index_3vzk span', '.col1 .row_index_i6jc:nth-child(2) .value_index_3vzk span',
         '.col1 .row_index_i6jc:nth-child(3) .value_index_3vzk span', '.col1 .row_index_i6jc:nth-child(4) .value_index_3vzk span',
         '.col1 .row_index_i6jc:nth-child(5) .value_index_3vzk span', '.col1 .row_index_i6jc:nth-child(6) .value_index_3vzk span',
         '.col2 .row_index_i6jc:nth-child(1) .value_index_3vzk span', '.col2 .row_index_i6jc:nth-child(2) .value_index_3vzk span',
         '.col2 .row_index_i6jc:nth-child(3) .value_index_3vzk span', '.col2 .row_index_i6jc:nth-child(4) .value_index_3vzk span']

property_tpye           = '.col1 .row_index_i6jc:nth-child(1) .value_index_3vzk span'
street_address          = '.address1_index_15vM'
city_state              = '.address2_index_1flE'
firm_name               = '.section_index_3Qkx+ .section_index_3Qkx div:nth-child(2)'
phone                   = '.section_index_3Qkx div~ div+ div'
start_tdate             = '.day_index_azJp'
auction_time            = '.time_index_MTI0'
opening_bid             = '.column_index_1KJu.highlight_index_XeMb'
element_css_list        = (property_tpye, street_address, city_state, firm_name, phone, 
                          start_tdate, auction_time, opening_bid)
property_info_label = ['Source', 'County', 'Property Tpye', 'Street Address','City&State$Zip', 'Contact (for Borrowers/Homeowners)', 
                       'Phone Number', 'Auction Date', 'Acution Time', 'Opening Bid', 'Url Link']


def click(display):
    try:
        display.click()
    except TimeoutException:
        driver.refresh()
    except NoSuchElementException:
        pass

def get_back():
    try:
        driver.back()
    except TimeoutException:
        driver.refresh()    
    
def find_elements(city):
    df_temp = []
    status = driver.find_elements_by_css_selector('.root_index_uNz7')
    
    count = []
    for j in range(len(status)):
        if status[j].text == 'Active - Scheduled for Auction':
            count.append(j)
            
    cnt = 0        
    for x in count:
        propertyinfo = ['auction.com', city]
        display = driver.find_elements_by_css_selector('.property-card-address-line1_list_view_3Q2o')
        click(display[x])
        #####
        label_list = []
        value_list = []
             
        for i in range(len(label)):
            try:
                label_text = driver.find_element_by_css_selector(label[i]).text
                value_text = driver.find_element_by_css_selector(value[i]).text
                label_list.append(label_text)
                value_list.append(value_text)
            except NoSuchElementException:
                continue
        label_value = dict(zip(label_list, value_list))
        for elem in label_full:
            label_value[elem] = label_value.get(elem, 'NA')
                    
        df_label_value = pd.DataFrame(label_value, index=[0])
        #####
        for cont in element_css_list:
            try:
                text = driver.find_element_by_css_selector(cont).text
                propertyinfo.append(text)
            except NoSuchElementException:
                propertyinfo.append('NA')
        propertyinfo.append(driver.current_url)
        df_info = pd.DataFrame([propertyinfo], columns = property_info_label)
        #####
        l = [df_label_value, df_info]
        df_all = pd.concat(l, axis=1)

        if cnt == 0:
            df_temp = df_all.copy()
            cnt = cnt + 1
        else:
            frames = [df_temp, df_all]
            df_temp = pd.concat(frames)
            cnt = cnt + 1
            
        print(cnt, city)
        get_back()
        
    print("total", cnt, "finish", city)
    if cnt == 0:
        df_temp = pd.DataFrame()
        return df_temp
    else:
        return df_temp


driver = webdriver.Chrome()
for city in city_list:
    page = 1
    url = 'https://www.auction.com/residential/tx/'+city+'-county/'+str(page)+'_cp/'
    driver.get(url)
    df_final = find_elements(city).copy()
    
    if df_final.empty == True:
        print('pass', city)
        continue
           
    writer = pd.ExcelWriter(city +'.xlsx', engine='xlsxwriter')
    active = driver.find_elements_by_css_selector('.auction-status-override_list_view_1MGg')
    try:
        while active[-1].text == 'Active - Scheduled for Auction':
            page = page+1
            url = 'https://www.auction.com/residential/tx/'+city +'-county/'+str(page)+'_cp/'
            driver.get(url)
            print('page', page)
            df_next = find_elements(city)
            frames = [df_final, df_next]
            df_next = pd.concat(frames)
            df_final = df_next.copy()
            active = driver.find_elements_by_css_selector('.auction-status-override_list_view_1MGg')  
    except IndexError:
        pass
    
    url = 'https://www.auction.com/residential/tx/'+city+'-county/1_cp/'    
    driver.get(url)
        
    df_final = df_final[['Source', 'Foreclosure / Trustee #', 'APN', 'Event Item #', 'Property ID', 'Contact (for Borrowers/Homeowners)', 'Phone Number', 'Property Tpye', 'County', 'Street Address',
                             'City&State$Zip', 'Bedrooms', 'Bathrooms', 'Year Built', 'Square Footage', 'Lot Size (acres)',  'Auction Date', 'Acution Time', 'Opening Bid', 'Url Link']]  
    df_final.to_excel(writer, sheet_name=city, index=False)
    writer.save()
        
driver.close()

