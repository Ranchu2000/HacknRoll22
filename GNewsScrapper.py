from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.chrome.service import Service
import random
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from datetime import datetime
import time
from google.cloud import language_v1
import sys
import os
from dotenv import load_dotenv

ROOT_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__)))
load_dotenv(os.path.join(ROOT_DIR,'config','conf','.env'))   

#Check Arguments Provided
n= len(sys.argv)
if n !=2:
    print("Please provide exactly ONE stock for analysis")
    quit()
stock= sys.argv[1]

url= "https://news.google.com/search?q="+stock+"%20when%3A1h"
ser= Service(os.path.join(ROOT_DIR, 'chromedriver.exe'))
op= webdriver.ChromeOptions()
op.add_argument("headless") #prevents chrome from popping up
op.add_experimental_option('excludeSwitches', ['enable-logging']) #prevent error message
driver = webdriver.Chrome(service= ser, options=op)
client = language_v1.LanguageServiceClient() #for google nlp

#Fetch Data
def fetch_data():
    headlines= []
    links= []
    driver.get(url)
    wait= WebDriverWait(driver, 10)
    try:
        wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, ".DY5T1d"))) #wait for 10s or for the class to load before continuing
        articles= driver.find_elements(By.CSS_SELECTOR, ".DY5T1d")
        for indx, val in enumerate (articles):
            headlines.append(val.text)
            links.append(val.get_attribute('href'))
    except Exception as e:
        print(str(e))
    driver.close()
    return headlines, links

#Sentiment Analyse
def analyse_data(headlines):
    rating= []
    for x in headlines:
        #Pass into Google NLP for sentiment analysis
        text=x
        document = language_v1.Document(
            content=text, type_=language_v1.Document.Type.PLAIN_TEXT
        )
        sentiment = client.analyze_sentiment(
            request={"document": document}
        ).document_sentiment
        #sentiment= random.randrange(11) #psuedo code
        rating.append(sentiment.score*10)
    return rating

#Processing of data into dataframe
def process_data (headlines, links, rating, hour):
    data= {"Headlines:": headlines, "Links:": links, "Sentiment:" : rating}
    df= pd.DataFrame(data)
    df["Hour:"]= hour
    return df

#Saving DF into file
def save_data (df):
    if required_file.is_file():
        df.to_csv(required_file, mode="a", index=False, header=False)
    else:
        df.to_csv(required_file,index=False)

while(True):
    headlines, links= fetch_data()
    rating= analyse_data(headlines)
    current= datetime.now()
    date=current.date()
    hour=current.hour
    #hour=2
    df= process_data(headlines, links, rating, hour)
    required_file = Path(os.path.join(ROOT_DIR, 'Data/')+ stock +"_"+str(date)+".csv")
    save_data(df)
    if (hour==23):
        #End of the day, time to review the data
        df1= pd.read_csv(required_file)
        average_sentiment= df1["Sentiment:"].mean()
        hours= list(range(24))
        y=[]
        for x in hours:
            df2= df1.loc[df1["Hour:"]==x]
            value= df2["Sentiment:"].mean()
            y.append(value)
        #GRAPH GENERATION
        plt.plot(hours, y)
        plt.xlabel("Hour")
        plt.ylabel("Avg_Sentiment")
        plt.title(stock+"_"+str(date))
        location = Path(os.path.join(ROOT_DIR, 'Data/')+ stock +"_"+str(date)+'.png')
        plt.savefig(location, dpi=300, bbox_inches='tight')
        #plt.show()

        #Emailing Capabilities
        #Credits To: https://towardsdatascience.com/automate-email-sending-with-python-74128c7ca89a
        # Connection with the server
        server = smtplib.SMTP(host=os.environ.get("HOST_ADDRESS"), port=os.environ.get("HOST_PORT"))
        server.starttls()
        server.login(os.environ.get("MY_ADDRESS"), os.environ.get("MY_PASSWORD"))
        # Creation of the MIMEMultipart Object
        message = MIMEMultipart()
        # Setup of MIMEMultipart Object Header
        message['From'] = os.environ.get("MY_ADDRESS")
        message['To'] = os.environ.get("RECIPIENT_ADDRESS")
        message['Subject'] = stock +" report"
        # Creation of a MIMEText Part
        textPart = MIMEText("This is the report for " + stock + " on " + str(date)+ ".\n The overall sentiment for today is " + str(average_sentiment), 'plain')
        with open(location, 'rb') as f:
            img_data = f.read() #all attachments must be in byte format
        image = MIMEImage(img_data, name="Graph")
        message.attach(image)
        message.attach(textPart)
        # Send Email and close connection
        server.send_message(message)
        server.quit()
    print("COMPLETED FOR "+ str(hour) + "HR")
    time.sleep(3600) #wait for 1 hour
