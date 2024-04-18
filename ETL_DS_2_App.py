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
import requests

###########################################################
def dataReading():
    df_raw = pd.read_csv("book_data_set/books_data.csv")
    # print(df_raw["previewLink"],"\n",df_raw["infoLink"])
    df_raw.drop(['ratingsCount','previewLink','infoLink','publisher'],axis='columns',inplace=True)
    print(df_raw.isna().sum())
    
    EmtpyRow=np.where(df_raw['Title'].isnull())[0]
    df_raw['Title'][EmtpyRow]='Nan Yar -- Who Am I?'
    

    # df_new = df_raw.dropna(subset=df_raw.columns.difference(['ratingsCount']))
    # df_new.reset_index(inplace=True)
    # df_new.iloc[:, 0] = df_new.iloc[:, 0].astype(int)
    # print("This is the new df\n:",df_new)
    # print(df_new.isna().sum())
    # print(df_new["infoLink"].iloc[0])
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

def GetISBN(title):
    url = 'https://www.googleapis.com/books/v1/volumes?q=intitle:'+title
    r = requests.get(url)
    data = r.json()
    # print(data) #now we basically have all the data regarding the book
    isbn10_Test = data['items'][0]['volumeInfo']['industryIdentifiers'][0]['identifier']
    isbn13_Test = data['items'][0]['volumeInfo']['industryIdentifiers'][1]['identifier']
    return isbn10_Test,isbn13_Test


def ISBNLoop(df,iN):
    df['ISBN_10'] = np.nan
    df['ISBN_13'] = np.nan
    print(df[:iN])
    for i in range(iN):
        title = df['Title'][i]
        isbn10,isbn13 = GetISBN(title)
        df['ISBN_10'][i] = isbn10
        df['ISBN_13'][i] = isbn13
        print("ISBN of book",title,'is',isbn10,isbn13)
    df[:iN]
    return df
###########################################################
### main
def main():
    LinkAll = 'http://localhost:8080/book/all'
    LinkCreate = 'http://localhost:8080/book/create'

    df = dataReading()
    df_new = ISBNLoop(df,10)
    # print(df)
    # myobj = {'title':'Test no des',
    #          'description':''}
    
    # title = 'Nan Yar -: Who Am I?'
    # isbn10_Test,isbn13_Test = GetISBN(title)
    # print("ISBN of book",title,'is',isbn10_Test,isbn13_Test)

    # CreateBook(LinkCreate, myobj)
    
    
    
    

###########################################################
### start main
if __name__ == "__main__":
    main()
