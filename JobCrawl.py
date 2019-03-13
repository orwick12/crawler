# Created by Brian Orwick
# 12/14/17
# Scrape Indeed for jobs in cities

import sys
import requests
from bs4 import BeautifulSoup  # need to pip install lxml
from time import sleep
import pandas as pd
# from tkinter import Tk, Label, Button
# from automail import email_me
import os
import re

os.getcwd()
path = 'C:/Users/orwic/Desktop/JobHunt/'
os.chdir(path)
max_results_per_city = 100
cities = ['bethesda']   # cities for the scraper to visit
targetFile = 'brianProspects.csv'
columns = ['Length Posted', 'Job Title', 'Location', 'Summary', 'Company', 'Link']  # column for csv
jobs = ['java+entry', 'java', 'python', 'python+entry']
job_df = pd.DataFrame(columns=columns)  # dataframe

for city in cities:
    for job in jobs:
        count = 0
        for start in range(0, max_results_per_city, 10):
            page = requests.get('https://www.indeed.com/jobs?q=' + str(job) + '&l=' + str(city) + '&start=' +
                                str(start))
            sleep(1)  # ensuring at least 1 second between page grabs
            soup = BeautifulSoup(page.text, 'lxml')  # from_encoding='utf-8')
            for div in soup.find_all(name='div', attrs={'class':'row'}):
                try:
                    # specifying row num for index of job posting in dataframe
                    num = (len(job_df) + 1)
                    # creating an empty list to hold the data for each posting
                    job_post = []
                    postLength = div.findAll('span', attrs={'class': 'date'})
                    numbers = re.findall(r'\d+', str(postLength))
                    if not numbers:
                        job_post.append('Sponsored')
                    elif int(numbers[0]) < 30:  # check if the post was created recently
                        job_post.append(numbers.pop())
                    elif int(numbers[0]) >= 30:  # if it was to far out skip the job posting
                        break
                    # grabbing job title
                    for b in div.find_all(name='a', attrs={'data-tn-element':'jobTitle'}):
                        job_post.append(b['title'])
                    # grabbing location name
                    a = div.findAll(attrs={'class': 'location'})
                    for span in a:
                        job_post.append(span.text)
                    # grabbing summary text
                    c = div.findAll('span', attrs={'class': 'summary'})
                    for span in c:
                        job_post.append(span.text.strip())
                    # grabbing company name
                    company = div.find_all(name='span', attrs={'class':'company'})
                    if len(company) > 0:
                        for d in company:
                            job_post.append(d.text.strip())
                    else:
                        sec_try = div.find_all(name='span', attrs={'class':'result-link-source'})
                        for span in sec_try:
                            job_post.append(span.text)
                    # grab link to page
                    for link in div.find_all(name='a', attrs={'data-tn-element': 'jobTitle'}):
                        href = 'https://www.indeed.com' + link['href']
                        job_post.append(href)
                    job_df.loc[num] = job_post
                except KeyError:
                    pass
            count += 1
            print('Crawling ' + city.title() + ' page ' + str(count))

clean_df = job_df.drop_duplicates(subset=['Summary'])
clean_df.to_csv(path + targetFile, encoding='utf-8')
# email = 'orwick12@outlook.com'
# email_me(email, path, targetFile)
