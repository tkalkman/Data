#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""


Purpose:
   

Version:
   

Date:
    04/2024

Author:
    Minh Hoang Bui
"""
###########################################################
### Imports
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm
import requests
from dateutil.parser import parse
from json import loads, dumps


###########################################################

def dataReadingTom():
    # df_raw = pd.read_csv("datametISBN.csv", converters={'authors': lambda x: x.strip("[]").replace("'", "").split(", ") if x != '[]' else list()})
    df_raw = pd.read_csv("datametISBN.csv",converters={'authors': lambda x: x[1:-1].split(', ')})

    # print(df_raw["previewLink"],"\n",df_raw["infoLink"])
    # df_raw.drop(['ratingsCount','previewLink','infoLink','publisher'],axis='columns',inplace=True)
    df_raw.drop(['ratingsCount','infoLink','publisher','ShortenedLink'],axis='columns',inplace=True)

    # print(df_raw.isna().sum())

    return df_raw
  
def CreateBook(LinkCreate,myobj):
    r = requests.post(LinkCreate, json = myobj)
    print(r.text)
    return 

def ReadAllBooks(LinkAll):
    r = requests.get(LinkAll)
    if r.status_code == 200:
        print("Success!")
    elif r.status_code == 404:
        print("Not Found.")
    print(r.content)
    return

def splitAuthors(df,iN):
    for i in tqdm(range(iN)):
        lOGList = df.loc[i,'authors']
        newList = list(map(lambda j: j[1:-1], lOGList))
        df.at[i,'authors'] = newList 
    return df

def cleanTitle(df):
    EmtpyRow=np.where(df['Title'].isnull())[0]
    df.loc[EmtpyRow,'Title']='Nan Yar -- Who Am I?'
    return df

def cleanCat(df):
    df['categories'] = df['categories'].str[2:].str[:-2]
    lEmptyIndex = df.loc[df['categories'].isnull()].index  

    # print(df.loc[lEmptyIndex,'categories'])
    df.loc[lEmptyIndex,'categories'] = 'Uncategorized'
    # print(df.loc[lEmptyIndex,'categories'])

    return df

def cleanDescr(df):
    lEmptyIndex = df.loc[df['description'].isnull()].index  
    lNotEmptyIndex = df.loc[df['description'].notnull()].index  
    # print(df.loc[lEmptyIndex,'description'])
    df.loc[lEmptyIndex,'description'] = 'Geen beschrijving'
    # print(df.loc[lEmptyIndex,'description'])
    for i in tqdm(lNotEmptyIndex):
        df.loc[i,'description'] = df.loc[i,'description'][:255]
    return df

def cleanAuthor(df):
    lEmptyIndex = df.loc[df['authors'].isnull()].index  

    # print(df.loc[lEmptyIndex,'authors'])
    for i in tqdm(lEmptyIndex):
        df.at[i,'authors'] = list(['No Author'])
    # print(df.loc[lEmptyIndex,'authors'])

    return df

def cleanPubDate(df):
    # print(df.isna().sum())
    lEmptyIndex = df.loc[df['publishedDate'].notnull()].index 
    # print(df.loc[lEmptyIndex,'publishedDate'])
    iCount = 0
    for i in tqdm(lEmptyIndex):
        iItem = str(df['publishedDate'][i]).replace('*', '')
        if "?" in iItem:
            iCount +=1
            df.loc[i,'publishedDate'] = np.nan
        else: 
            df.loc[i,'publishedDate'] = parse(iItem) 
    # print(df.loc[lEmptyIndex,'publishedDate']) 
    # print(df.isna().sum())     
    # df['publishedDate'] = pd.to_datetime(df['publishedDate'],errors='coerce')
    print("Number of rows with false publish date:",iCount)
    return df

def cleanISBN(df):
    
    lNonEmptyIndex = df.loc[df['ISBN'].notnull()].index  
    # print(df['ISBN'])
    for i in tqdm(lNonEmptyIndex):
        # print(i,df_raw.loc[i,'ISBN'])
        df.loc[i,'ISBN'] = df.loc[i,'ISBN'][-13:]
    # print(df['ISBN'])

    return df

def cleaningDF(df_raw,iN):
    print("\nInitial dataset:")
    print(df_raw.isna().sum())

    print("\nStart cleaning title:")
    df_wip = cleanTitle(df_raw)
    print(df_wip.isna().sum())

    print("\nStart splitting authors:")
    for i in tqdm(range(iN)):
        lOGList = df_raw.loc[i,'authors']
        if lOGList[0] == "":
            df_raw.at[i,'authors'] = np.nan
        else:
            newList = list(map(lambda j: j[1:-1], lOGList))
            df_raw.at[i,'authors'] = newList  
    print(df_raw.isna().sum())
    
    print("\nStart cleaning description:")
    df_wip = cleanDescr(df_wip)
    print(df_wip.isna().sum())

    print("\nStart cleaning categories:")
    df_wip = cleanCat(df_wip)
    print(df_wip.isna().sum())

    print("\nStart cleaning authors:")
    df_wip = cleanAuthor(df_wip)
    print(df_wip.isna().sum())

    print("\nStart cleaning publishedDate:")
    df_wip = cleanPubDate(df_wip)
    print(df_wip.isna().sum())

    df_wip = cleanISBN(df_wip)

    df_wip = df_wip.rename(columns={'Title': "title", 'image': 'imageLink', 'publishedDate': 'publishingDate', 'ISBN': 'isbn'})
    df_wip["states"] = 'Nieuw'

    print("\nCleaning is done.")
    df = df_wip
    return df

###########################################################
### main
def main():
    LinkAll = 'http://localhost:8080/book/all'
    LinkCreate = 'http://localhost:8080/book/create'

    
    # df = dataReading()
    
    
   
    ### HERE IS OUR CLEANING FUNCTION
    # df_raw = dataReadingTom()
    # iN = df_raw.shape[0]  #length of dataframe
    # df_clean = cleaningDF(df_raw,iN)        
    # df_clean.to_csv('cleanDataSet.csv',index=False)


    df = pd.read_csv("cleanDataSet.csv",converters={'authors': lambda x: x[1:-1].split(', ')})
    df.drop(['previewLink'],axis='columns',inplace=True)
    df = splitAuthors(df,df.shape[0])
    
    sRow = df.loc[1]
    # print(sRow,sRow['title'])
    # result = sRow.to_json(orient='index')
 
    # # testjson = dumps(loads(result))
    # print(result,type(result),"\n")
    
    myobj = {'title'          :sRow['title'],
             'description'    :sRow['description'],
             'authors'        :sRow['authors'],
              'imageLink'     :sRow['imageLink'],
              'publishingDate':sRow['publishingDate'],
              'categories'    :list([sRow['categories']]),
            #   'isbn'          :sRow['isbn'],
              'states'        :list([sRow['title']])              
              }
    print("\n",myobj,type(myobj),"\n")
    CreateBook(LinkCreate,myobj)
    
    # myobj = {'title':'Test no des',
    #          'description':''}
    



    # print("\n Item is:",testIN[1],testIN[1][0],type(testIN))
    
    # print(df_raw['authors'])
    # testIN = df_raw.loc[169297,"authors"]
    # print("\n Item is:",testIN,type(testIN))
   
   
    
    
    # dfExtra = pd.read_csv("DF_Tom_ExtraISBN.csv")
    # iBreakPoint = 169300
    # print(dfExtra.shape[0],df_Tom.shape[0])
    
    # indexTom = df_Tom.loc[df_Tom['ISBN'].isnull()].index
    # indexExtra = dfExtra.loc[dfExtra['ISBN'].isnull()].index
    # print(indexTom,indexExtra)

    # df_new = ISBNLoop(df_Tom,indexTom[:10000])
    # df_new.to_csv('DF_Tom_ExtraISBN.csv',index=False)

    # title = df['Title'][0]
    # isbn10,isbn13=GetISBN(title)
    # print("ISBN of book",title,'is',isbn10,isbn13)

    
    
    # title = 'Nan Yar -: Who Am I?'
    # isbn10_Test,isbn13_Test = GetISBN(title)
    # print("ISBN of book",title,'is',isbn10_Test,isbn13_Test)

    # CreateBook(LinkCreate, myobj)
    
    
    
    

###########################################################
### start main
if __name__ == "__main__":
    main()
