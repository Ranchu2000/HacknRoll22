#7th January 22 NUS HacknRoll solo
#This is a web scrapping application that scraps headlines of a particular subject every hour and runs GoogleNews headlines through the Google NLP for sentiment analysis before storing it in a csv. At the end of the day, an email will be sent to containing the average sentiment of the day as well as a graph of the average sentiment throughout the day

#To improve: 
# the NLP is a general use-case NLP and not one for financial overview- good news for competitiors means bad news for subject which is not reflected in this matter- soln will be to train own NLP
# sources of information could be more broadly sourced- not just Google News but also other news outlets as well as perhaps the first paragraph of the article could be incorportated
#use ml to classifiy similar issues? reptition count?
#alert for super polarizing news

# set GOOGLE_APPLICATION_CREDENTIALS=C:\Users\yufei\OneDrive - Nanyang Technological University\Backup\Desktop\Coding\Python\Web Scrapper\hacknroll22-nlp-e674a1942655.json
#^ run before execution to set up credentials for Google NLP
