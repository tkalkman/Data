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
    """
    -------- Input
    No input
    -------- Function
    Reads the data file, splits the author in a list and removes unwanted columns
    -------- Output
    df :pandas dataframe 
    """
    df_raw = pd.read_csv("datametISBN.csv",converters={'authors': lambda x: x[1:-1].split(', ')})
    df_raw.drop(['ratingsCount','infoLink','publisher','ShortenedLink'],axis='columns',inplace=True)

    return df_raw
  
def CreateBook(LinkCreate,myobj):
    """
    -------- Input
    LinkCreate : link to backend book create page
    myobj : dict that becomes the input for book
    -------- Function
    Calls the create book page and post myobj in that page
    -------- Output
    No output
    """
    r = requests.post(LinkCreate, json = myobj)
    # print(r.text)
    return 

def ReadAllBooks(LinkAll):
    """
    -------- Input
    LinkCreate : link to page that shows all books in database
    -------- Function
    Calls the page
    -------- Output
    No output
    """
    r = requests.get(LinkAll)
    if r.status_code == 200:
        print("Success!")
    elif r.status_code == 404:
        print("Not Found.")
    print(r.content)
    return

def splitAuthors(df,iN):
    """
    -------- Input
    df : dataframe of our dataset
    iN : lenght of dataframe we want to edit 
    -------- Function
    Splits the authors and put them in a list
    -------- Output
    df : dataframe of our dataset
    """
    for i in tqdm(range(iN)):
        lOGList = df.loc[i,'authors']
        newList = list(map(lambda j: j[1:-1], lOGList))
        df.at[i,'authors'] = newList 
    return df

def cleanTitle(df):
    """
    -------- Input
    df : dataframe of our dataset
    -------- Function
    Adds the one missing title in the dataset
    -------- Output
    df : dataframe of our dataset
    """
    EmtpyRow=np.where(df['Title'].isnull())[0]
    df.loc[EmtpyRow,'Title']='Nan Yar -- Who Am I?'
    return df

def cleanCat(df):
    """
    -------- Input
    df : dataframe of our dataset
    -------- Function
    Removes [' and '] from the categories string and make empty categories 'Uncategorized'
    -------- Output
    df : dataframe of our dataset
    """
    df['categories'] = df['categories'].str[2:].str[:-2]
    lEmptyIndex = df.loc[df['categories'].isnull()].index  
    df.loc[lEmptyIndex,'categories'] = 'Uncategorized'

    return df

def cleanDescr(df):
    """
    -------- Input
    df : dataframe of our dataset
    -------- Function
    Make emtpy descriptions 'Geen beschrijving' and limits the description to 255 characters
    -------- Output
    df : dataframe of our dataset
    """
    lEmptyIndex = df.loc[df['description'].isnull()].index  
    lNotEmptyIndex = df.loc[df['description'].notnull()].index  
    df.loc[lEmptyIndex,'description'] = 'Geen beschrijving'
    for i in tqdm(lNotEmptyIndex):
        if len(df.loc[i,'description'])>500:
            df.loc[i,'description'] = df.loc[i,'description'][:500]
    return df

def cleanAuthor(df):
    """
    -------- Input
    df : dataframe of our dataset
    -------- Function
    Turn empty author to 'No Author'
    -------- Output
    df : dataframe of our dataset
    """
    lEmptyIndex = df.loc[df['authors'].isnull()].index  
    for i in tqdm(lEmptyIndex):
        df.at[i,'authors'] = list(['No Author'])

    return df

def cleanPubDate(df):
    """
    -------- Input
    df : dataframe of our dataset
    -------- Function
    Make the publishingDate the same format for every row and remove the dates with ? in their value 
    -------- Output
    df : dataframe of our dataset
    """
    lEmptyIndex = df.loc[df['publishedDate'].notnull()].index 

    iCount = 0
    for i in tqdm(lEmptyIndex):
        iItem = str(df['publishedDate'][i]).replace('*', '')
        if "?" in iItem:
            iCount +=1
            df.loc[i,'publishedDate'] = np.nan
        else: 
            df.loc[i,'publishedDate'] = parse(iItem) 

    print("Number of rows with false publish date:",iCount)
    return df

def cleanISBN(df): 
    """
    -------- Input
    df : dataframe of our dataset
    -------- Function
    Since ISBN 13 is the last 13 numbers take only the isbn 13 from the dataset
    -------- Output
    df : dataframe of our dataset
    """ 
    lNonEmptyIndex = df.loc[df['ISBN'].notnull()].index  
    for i in tqdm(lNonEmptyIndex):
        df.loc[i,'ISBN'] = df.loc[i,'ISBN'][-13:]
    return df

def cleaningDF(df_raw,iN):
    """
    -------- Input
    df_raw : dataframe of our dataset
    iN : length we want to clean
    -------- Function
    Cleans the dataset with various functions
    -------- Output
    df : cleaned dataframe of our dataset
    """
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
    df_wip["states"] = 'NIEUW'

    print("\nCleaning is done.")
    df = df_wip
    return df

def addBookLoop(LinkCreate,df,iN):
    for i in tqdm(range(iN)):
        sRow = df.loc[i]
        
        myobj = {'title'          :sRow['title'],
                'description'    :sRow['description'],
                'authors'        :sRow['authors'],
                'categories'    :list([sRow['categories']]),
                'states'        :list([sRow['states']])              
                }
        if pd.notnull(sRow['imageLink']):
            myobj['imageLink'] = sRow['imageLink']
        if pd.notnull(sRow['isbn']):
            myobj['isbn'] = int(sRow['isbn']) 
        if pd.notnull(sRow['publishingDate']):
             myobj['publishingDate'] = sRow['publishingDate']    
        # print(myobj)
        CreateBook(LinkCreate,myobj)
    print("Done adding books")

    return

def readCleanData():
    df = pd.read_csv("cleanDataSet.csv",converters={'authors': lambda x: x[1:-1].split(', ')})
    df.drop(['previewLink'],axis='columns',inplace=True)

    print("\nEditing input file to match functions")
    df = splitAuthors(df,df.shape[0])
    df['publishingDate'] = pd.to_datetime(df['publishingDate'],errors='coerce').dt.strftime('%Y-%m-%d')

    return df
###########################################################
### main
def main():
    LinkAll = 'http://localhost:8080/book/all'
    LinkCreate = 'http://localhost:8080/book/create'
   
    ### HERE IS OUR CLEANING FUNCTION
    # df_raw = dataReadingTom()
    # iN = df_raw.shape[0]  #length of dataframe
    # df_clean = cleaningDF(df_raw,iN)        
    # df_clean.to_csv('cleanDataSet.csv',index=False)


    ### HERE WE ADD OUR BOOKS
    df = readCleanData()
    iN = 100 #df.shape[0] #length of dataframe. Can edit this to add less books.
    
    print("\nStart adding books to database")
    addBookLoop(LinkCreate,df,iN)


###########################################################
### start main
if __name__ == "__main__":
    main()
