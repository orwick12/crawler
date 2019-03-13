# Created by Brian Orwick
# 12/14/17
# Scrape Indeed for jobs in cities

import requests
from bs4 import BeautifulSoup  # need to pip install lxml for parsing
from time import sleep
import pandas as pd
# from automail import email_me
import os
import re

os.getcwd()
path = 'C:/Users/orwic/Desktop/JobHunt/'
os.chdir(path)
max_results_per_city = 100
cities = ['bethesda']   # cities for the scraper to visit
targetFile = 'scrapedJobListings.csv'
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
                    num = (len(job_df) + 1)  # specifying row num for index of job posting in dataframe
                    job_post = []  # creating an empty list to hold the data for each posting
                    postLength = div.findAll('span', attrs={'class': 'date'})
                    numbers = re.findall(r'\d+', str(postLength))
                    if not numbers:
                        job_post.append('Sponsored')
                    elif int(numbers[0]) < 30:  # check if the post was created recently
                        job_post.append(numbers.pop())
                    elif int(numbers[0]) >= 30:  # if it was to far out skip the job posting
                        break
                    for b in div.find_all(name='a', attrs={'data-tn-element':'jobTitle'}):  # grabbing job title
                        job_post.append(b['title'])
                    a = div.findAll(attrs={'class': 'location'})  # grabbing location name
                    for span in a:
                        job_post.append(span.text)
                    c = div.findAll('span', attrs={'class': 'summary'})  # grabbing summary text
                    for span in c:
                        job_post.append(span.text.strip())
                    company = div.find_all(name='span', attrs={'class':'company'})  # grabbing company name
                    if len(company) > 0:
                        for d in company:
                            job_post.append(d.text.strip())
                    else:
                        sec_try = div.find_all(name='span', attrs={'class':'result-link-source'})
                        for span in sec_try:
                            job_post.append(span.text)
                    for link in div.find_all(name='a', attrs={'data-tn-element': 'jobTitle'}):  # grab link to page
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
