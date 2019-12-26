import fitbit
import gather_keys_oauth2 as Oauth2
import pandas as pd
import datetime
from datetime import timedelta  
import numpy as np

CLIENT_ID = "22B9YV"
CLIENT_SECRET = "ef1c8462955073dfd83d7a457e6af480"

server = Oauth2.OAuth2Server(CLIENT_ID, CLIENT_SECRET)
server.browser_authorize()

ACCESS_TOKEN = str(server.fitbit.client.session.token['access_token'])
REFRESH_TOKEN = str(server.fitbit.client.session.token['refresh_token'])

#Auth Client
auth2_client = fitbit.Fitbit(CLIENT_ID, CLIENT_SECRET, oauth2=True, access_token=ACCESS_TOKEN,
                             refresh_token=REFRESH_TOKEN, system="en_GB")

#Needed for sleep breakdown
auth2_client_new = fitbit.Fitbit(CLIENT_ID, CLIENT_SECRET, oauth2=True, access_token=ACCESS_TOKEN, refresh_token=REFRESH_TOKEN, system='en_GB')
auth2_client_new.API_VERSION = 1.2


yesterday = str((datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y%m%d"))
yesterday2 = str((datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d"))
today = str(datetime.datetime.now().strftime("%Y%m%d"))

fit_statsSTEPS = auth2_client.intraday_time_series('activities/steps', 
                                                base_date=yesterday2)

print(fit_statsSTEPS)

#https://towardsdatascience.com/collect-your-own-fitbit-data-with-python-ff145fa10873
#https://www.freecodecamp.org/news/how-i-analyzed-the-data-from-my-fitbit-to-improve-my-overall-health-a2e36426d8f9/

DATE_FORMAT = '%Y-%m-%d'
databaseFilename = 'data/database_main.xls'

def connectAndLoadDb():
    print("Connecting database...")
    database = pd.read_excel(databaseFilename)
    print("Database connected!")
    return database;

def getLastEntryDate(database):
    lastDateEntry = database.iloc[-1]['Date']
    lastDateEntry = datetime.datetime.strptime(lastDateEntry, DATE_FORMAT)    
    return lastDateEntry

def addEntriesInDB(dictionary, database):
    #print(dictionary)
    database = database.append(dictionary, ignore_index=True)
    return addEntriesInDB;

def writeDbToExcelFile(database):
    print('Writing database to filename: '+ databaseFilename)
    writer = pd.ExcelWriter(databaseFilename)
    database.to_excel(writer, 'main')
    writer.save()
    print('Database updated with new entries!!')
    
def prettyPrintDate(date):
    return date.strftime(DATE_FORMAT);

#x[4] if len(x) == 4 else 'No'
def safeGet(obj, key, defaultVal = np.nan):
    return obj.get(key, defaultVal)  

def percent(val):
    return np.ceil(val*100)

def filterArrObj(arrList, keyName, keyValue):
    for arrItem in arrList:
        if arrItem.get(keyName) == keyValue:
            return arrItem
    return {} 

def mergeDicts(dicts):
    super_dict = {}
    for singleDict in dicts:
        for k, v in singleDict.items(): 
            super_dict[k] = v
    return super_dict

    
def getActivities(date):
    activitiyResponse = auth2_client.activities(date=date)
    
    activitySummary = activitiyResponse['summary'];
    activityData = {
        'Calories Burned':safeGet(activitySummary,'caloriesOut'),
        'Calories BMR': safeGet(activitySummary,'caloriesBMR'),
        'Steps':safeGet(activitySummary,'steps'),
        'Distance (Km)':filterArrObj(activitySummary.get('distances', []), 'activity', 'total').get('distance', np.nan),
        'Elevation (Ft)':activitySummary['elevation'],
        'Floors':activitySummary['floors'],
        'Minutes Sedentary':activitySummary['sedentaryMinutes'],
        'Minutes Lightly Active':activitySummary['lightlyActiveMinutes'],
        'Minutes Fairly Active':activitySummary['fairlyActiveMinutes'],
        'Minutes Very Active':activitySummary['veryActiveMinutes'],
        'Activity Calories': activitySummary['activityCalories'],
        'Active Score': activitySummary['activeScore'],
        'Cardio minutes': filterArrObj(activitySummary.get('heartRateZones', []), 'name', 'Cardio').get('minutes', np.nan),
        'Cardio calories': filterArrObj(activitySummary.get('heartRateZones', []), 'name', 'Cardio').get('caloriesOut', np.nan),
        'Fat Burn minutes': filterArrObj(activitySummary.get('heartRateZones', []), 'name', 'Fat Burn').get('minutes', np.nan),
        'Fat Burn calories': filterArrObj(activitySummary.get('heartRateZones', []), 'name', 'Fat Burn').get('caloriesOut', np.nan),
        'Peak minutes': filterArrObj(activitySummary.get('heartRateZones', []), 'name', 'Peak').get('minutes', np.nan),
        'Peak calories': filterArrObj(activitySummary.get('heartRateZones', []), 'name', 'Peak').get('caloriesOut', np.nan),
        'Normal Cardio minutes': filterArrObj(activitySummary.get('heartRateZones', []), 'name', 'Out of Range').get('minutes', np.nan),
        'Normal Cardio calories': filterArrObj(activitySummary.get('heartRateZones', []), 'name', 'Out of Range').get('caloriesOut', np.nan),
    }
    
    return activityData

def getSleep(date):
    sleepResponse = auth2_client_new.sleep(date=date)
    
    sleepData = {}
    for sleepLog in sleepResponse.get('sleep', []):
        if sleepLog.get('isMainSleep'):
            sleepLevelsSummary = sleepLog.get('levels', {}).get('summary', {})
            
            sleepData['Sleep Efficiency'] = safeGet(sleepLog, 'efficiency')
            sleepData['Minutes Asleep'] = safeGet(sleepLog, 'minutesAsleep')
            sleepData['Minutes to fall asleep'] = safeGet(sleepLog, 'minutesToFallAsleep')
            sleepData['Sleep Start time'] = safeGet(sleepLog, 'startTime')
            sleepData['Sleep End time'] = safeGet(sleepLog, 'endTime')
            
            sleepData['Time in bed'] = safeGet(sleepLog, 'timeInBed')
            
            sleepData['Minutes Deep sleep'] = safeGet(sleepLevelsSummary.get('deep', {}), 'minutes')
            sleepData['Deep sleep count'] = safeGet(sleepLevelsSummary.get('deep', {}), 'count')
            sleepData['% Deep sleep'] = percent(safeGet(sleepData, 'Minutes Deep sleep', 0)/safeGet(sleepData, 'Time in bed', 0))
            
            sleepData['Minutes Light sleep'] = safeGet(sleepLevelsSummary.get('light', {}), 'minutes')
            sleepData['Light sleep count'] = safeGet(sleepLevelsSummary.get('light', {}), 'count')
            sleepData['% Light sleep'] = percent(safeGet(sleepData, 'Minutes Light sleep', 0)/safeGet(sleepData, 'Time in bed', 0))
            
            sleepData['Minutes REM sleep'] = safeGet(sleepLevelsSummary.get('rem', {}), 'minutes')
            sleepData['REM sleep count'] = safeGet(sleepLevelsSummary.get('rem', {}), 'count')
            sleepData['% REM sleep'] = percent(safeGet(sleepData, 'Minutes REM sleep', 0)/safeGet(sleepData, 'Time in bed', 0))
            
            sleepData['Minutes Asleep'] = sleepData['Minutes Deep sleep'] + sleepData['Minutes Light sleep'] + sleepData['Minutes REM sleep']
            sleepData['Minutes Awake'] = safeGet(sleepLevelsSummary.get('wake', {}), 'minutes')
            sleepData['Minutes Awake count'] = safeGet(sleepLevelsSummary.get('wake', {}), 'count')            
    return sleepData

def getDateData(date):
    weekDayNum = date.isoweekday()
    return {
        'Day of Week': weekDayNum,
        'Is Weekday': weekDayNum<6,
        'Is Weekend': weekDayNum>5,
        'Date': prettyPrintDate(date)
    };

def fetchAllData(date):
    dateStr = prettyPrintDate(date)
    
    print("Fetching fitbit data for: " + dateStr)
    
    nextDate = date + timedelta(days=1)
    sleepData = getSleep(prettyPrintDate(nextDate))
    
    activitiesData = getActivities(dateStr)
    dateData = getDateData(date)
    
    mergedData = mergeDicts([sleepData, activitiesData, dateData])
    return mergedData

    database = connectAndLoadDb()

def shouldFetchDataForProvidedDate(providedDate, todaysDate, API_COUNTER):
    return (providedDate < todaysDate) and API_COUNTER < 100;

def fetchAndAppendToDb(date, database):    
    mergedData = fetchAllData(date)
    database = database.append(mergedData, ignore_index=True)
    return database;

def fetchData(database, refetchAll = False):
    API_COUNTER = 0
    
    todaysDate = datetime.datetime.today()
    
    print("Date today is :" + prettyPrintDate(todaysDate))
    
    if refetchAll == True:
        lastEntryDate = datetime.datetime.strptime('2018-06-23', DATE_FORMAT)
    else:
        lastEntryDate = getLastEntryDate(database)
    
    print("Last entry in Db is of :" + prettyPrintDate(lastEntryDate))
    print("----------------------------------------------")
    
    dateToFetch = lastEntryDate + timedelta(days=1)

    while shouldFetchDataForProvidedDate(dateToFetch, todaysDate, API_COUNTER):    
        database = fetchAndAppendToDb(dateToFetch, database)
        dateToFetch = dateToFetch + timedelta(days=1)
        API_COUNTER = API_COUNTER+1
    
    print("----------------------------------------------")
    print("Data fill completed! 👍👍")
    return database

    database = fetchData(database)

    writeDbToExcelFile(database)
