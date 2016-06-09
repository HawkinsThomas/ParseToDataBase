#Thomas Hawkins
#This file reads TestLog data from a Slot Lock integrated tester. 
#It will recursively run though the entire root directory looking for config files.
#Will only run if [Configuration_File] header is found at the top of the text file.
#Parses string data from testlog text file into array
#pushes data into remote database  

import sys, os, re, mysql.connector
root = sys.argv[1] #uncomment to enter root as a command line argument

def readData(root):
	#os.walk returns the following
	#root: current path
	#subdirs: directories in root
	#files in root
	testResults = []
	allResults = []
	for root, subdirs, files in os.walk(root):

		for filename in files:
			filename = os.path.join(root, filename)

			with open(filename) as f:
				config = False
				process_name = ""
				computer_name = ""
				date = ""
				unit = ""
				errorGroup = ""
				errorCode = ""
				for line in f:

					if str.find(line, "[Configuration_File]") != -1 and str.find(filename,".txt") != -1:
						print "Config file found. Loading data from " + filename
						config = True

					if config == True:
						dateformat = re.compile('\[[0-9][0-9]-[0-9][0-9]-[0-9][0-9][0-9][0-9]\]')
						processIndex = str.find(line, "process_name=")
						computerIndex = str.find(line, "computer_name=")
						dateIndex = dateformat.match(line)
						slotIndex = str.find(line, "slot")
						slotNumIndex = str.find(line,"=")
						errorGroupIndex
						

						if processIndex != -1:
							process_name = line[processIndex + len("process_name="):]

						elif computerIndex != -1:
							computer_name = line[computerIndex + len("computer_name="):]

						elif dateIndex != None:
							date = line[7:11]+"-"+line[1:4]+line[4:6]

						elif slotIndex != -1:
							slot = line[0:slotNumIndex]
							testData = line.replace(slot + "=", "")
							testData = testData.replace("<end>", "")

							if len(testData) > 5:
								data = testData.split("/")

								for i in range (0, len(data)):
									unitIndex = str.find(data[i], "{")
									unitEndIndex = str.find(data[i], "~")

									if unitIndex != -1 and unitEndIndex != -1:
										unit = data[i][unitIndex + 1:unitEndIndex]

									data[i] = data[i].replace(unit+ "~", "")

									data = data.split(",")
									for i in range(0, len(data)):


									testResults.append(i)								#append all data to list for writing to Database. Each iteration of this for loop is a test run
									testResults.append(process_name.replace('\n', ''))
									testResults.append(computer_name.replace('\n', ''))
									testResults.append(slot)
									testResults.append(date.replace('\n', ''))
									testResults.append(data[i].replace('\n', '')) #This will change
									testResults.append(unit)
									allResults.append(testResults)
									testResults = []
	print "done"
	return allResults

def insert_test(allData):
	query = "INSERT INTO testruns(RunNumber, Process, PC, Slot, Testdate, Status, Unit)" \
		"VALUES(%s, %s, %s, %s, %s, %s, %s)"
	
	try:
		cnx = mysql.connector.connect(host = 'localhost', user = "root", password = 'Hawk8tom', database='slotlock')
		cursor = cnx.cursor()
		
		for i in range (0, len(allData)):
			if allData[i][5] != "PASS{1100}":
				print allData[i][2], allData[i][5]

		for i in range (0, len(allData)):
			args = (allData[i][0], allData[i][1], allData[i][2], allData[i][3], allData[i][4], allData[i][5], allData[i][6])
			cursor.execute(query,args)

		
	except mysql.connector.Error as e:
		print 'Error', e

	finally:
		cnx.commit()
		cursor.close()
		cnx.close()

data = readData(root)
insert_test(data)
