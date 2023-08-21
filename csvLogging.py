import csv
import datetime

#Append query, function that adds a row to the csv file
#First Row should be index second should be time the rest can be data points

def append(CSVName, item, confirm):
    lastIndex = 0
    with open(CSVName,'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for line in csv_reader:

            lastIndex = line['Index'] 
    newIndex = str(int(lastIndex)+1)
    time = str(datetime.datetime.now())[:22]
    entry = newIndex + "," + time + "," + str(item) + "\n"
    '''
    for item in itemsToAppend:
        entry = entry + "," + str(item)
    finalEntry = entry + "\n"
    '''
    if confirm == True:
        print(entry)
        print("appended to " + CSVName)
    with open('table.csv','a') as csv_file:
        csv_file.write(entry)
        #csv_file.write(finalEntry)
    

if __name__ == "__main__":
    append("table.csv", ["Current"], True)

