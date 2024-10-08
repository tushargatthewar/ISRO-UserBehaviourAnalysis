from flask import Flask, request, jsonify, render_template
import csv
import os
import pandas as pd
import threading
import time
from datetime import datetime

app = Flask(__name__)

# Path to the CSV file for storing persisitant Data
overall_csv='overallhomedata.csv'
overall_csv_mapliteuserdata='overall_csv_mapliteuserdata.csv'
overall_csv_homesession='overall_csv_homesession.csv'
overall_csv_2DmapTimespent='overall_csv_2DmapTimespent.csv'
overall_csv_archivetimespent='overall_csv_archivetimespent.csv'
overall_csv_archive_user='overall_csv_archive_user.csv'

#path file for csv for the storing the session data for specific user
CSV_FILE_PATH = 'home_user_activity.csv'
CSV_FILE_PATH_Map= '2DmapTimespent.csv'
CSV_FILE_PATH_Homesession='Homesession.csv'
CSV_FILE_PATH_archive='archive.csv'
csv_file = 'archive_user activity.csv'#in process
CSV_FILE_PATH2 = 'mapLite_user_activity.csv'#lite map user data


@app.route('/')
def index():
    #complete data collection
    #home page for bhuvan
    return render_template('analyatical.html')

@app.route('/come')
def come():
    
    return render_template('comesoon.html')


@app.route('/tod')
def tod():
    #2d map page
    return render_template('2d.html')

@app.route('/thd')
def thd():
    #3d map page
    return render_template('3d.html')

@app.route('/archive')
def archive():
    #Bhuvan lite page
    return render_template('archive.html')

@app.route('/lite')
def lite():
    #complete data collection
    #Data archive page
    return render_template('lite.html')

@app.route('/map')
def map():
    #Task bar map page
    return render_template('map.html')

def get_client_ip():
    """Retrieve the client's IP address from the request."""
    if request.headers.getlist("X-Forwarded-For"):
        # If behind a proxy, the client's IP is in the first position
        ip = request.headers.getlist("X-Forwarded-For")[0].split(',')[0].strip()
    else:
        ip = request.remote_addr
    return ip


 #**************************here is the persistant Data******************************#
 #***********************************************************************************#
def overall_homeuserdata():
    if not os.path.exists(overall_csv):
        with open(overall_csv,mode='w',newline='') as file:
            writer=csv.writer(file)
            writer.writerow(['ip_address',
                'event', 'element', 'timestamp', 'x', 'y', 'page', 
                'relatedElement', 'inputValue', 'location', 
                'destination', 'timeSpent', 'scroll', 'depth', 'timeSpentOnHover'
            ])
overall_homeuserdata()

def overall_mapliteuserdata():
    if not os.path.exists(overall_csv_mapliteuserdata):
        with open(overall_csv_mapliteuserdata,mode='w',newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['ip_address','event', 'element', 'timestamp', 'x', 'y', 'page', 'relatedElement', 'inputValue', 'location', 'destination', 'timeSpent', 'scroll', 'depth', 'timeSpentOnHover']) 

overall_mapliteuserdata()

def overall_archiveuserdata():
    if not os.path.exists(overall_csv_archive_user):
        with open(overall_csv_archive_user, mode='w',newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['ip_address','Timestamp', 'Event', 'TimeSpent', 'Link', 'Section'])

overall_archiveuserdata()


def overall_2dmap():
        if not os.path.exists(overall_csv_2DmapTimespent):
            with open(overall_csv_2DmapTimespent,mode='w',newline='') as file:
                writer=csv.writer(file)
                writer.writerow(['ip_address','page', 'timeSpent'])  

overall_2dmap()


def overall_homesession():
    if not os.path.exists(overall_csv_homesession):
        with open(overall_csv_homesession,mode='w',newline='') as file:
            writer=csv.writer(file)
            writer.writerow(['ip_address','page','timeSpent'])

overall_homesession()


def overall_archivesession():
    if not os.path.exists(overall_csv_archivetimespent):
        with open(overall_csv_archivetimespent,mode='w',newline='') as file:
            writer=csv.writer(file)
            writer.writerow(['ip_address','page','timeSpent'])

overall_archivesession()



#*************************************Here is the session wise data is Storing******************************************#
#*********************************************************************************************************************#

def initialize_csv():
    """Delete existing CSV file and create a new one with headers."""
    if os.path.exists(CSV_FILE_PATH):
        os.remove(CSV_FILE_PATH)
    
    with open(CSV_FILE_PATH, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['ip_address','event', 'element', 'timestamp', 'x', 'y', 'page', 'relatedElement', 'inputValue', 'location', 'destination', 'timeSpent', 'scroll', 'depth', 'timeSpentOnHover'])

# Initialize the CSV file
initialize_csv()

#this is  for tarcking data of the maplite 
def initialize_csvmaplite():
    """Delete existing CSV file and create a new one with headers."""
    if os.path.exists(CSV_FILE_PATH2):
        os.remove(CSV_FILE_PATH2)
    
    with open(CSV_FILE_PATH2, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['ip_address','event', 'element', 'timestamp', 'x', 'y', 'page', 'relatedElement', 'inputValue', 'location', 'destination', 'timeSpent', 'scroll', 'depth', 'timeSpentOnHover'])

# Initialize the CSV file
initialize_csvmaplite()



def initialize_csv1():
    """Create a new CSV file if it doesn't exist with appropriate headers."""

    if os.path.exists(CSV_FILE_PATH_Map):
        os.remove(CSV_FILE_PATH_Map)

    # if not os.path.exists(CSV_FILE_PATH_Map):
    with open(CSV_FILE_PATH_Map, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['ip_address','page', 'timeSpent'])  # CSV Headers

initialize_csv1()

#home ke liye CSV timesspent
def initialize_csvhome():
    """Create a new CSV file if it doesn't exist with appropriate headers."""
    if os.path.exists(CSV_FILE_PATH_Homesession):
        os.remove(CSV_FILE_PATH_Homesession)
    
    #if not os.path.exists(CSV_FILE_PATH_Homesession):
    with open(CSV_FILE_PATH_Homesession, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['ip_address','page', 'timeSpent'])  # CSV Headers

initialize_csvhome()

#archive ke liye CSV time spent
def initialize_csvarchive():
    """Create a new CSV file if it doesn't exist with appropriate headers."""
    if os.path.exists(CSV_FILE_PATH_archive):
        os.remove(CSV_FILE_PATH_archive)
    
    #if not os.path.exists(CSV_FILE_PATH_archive):
    with open(CSV_FILE_PATH_archive, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['ip_address','page', 'timeSpent'])  # CSV Headers

initialize_csvarchive()

#lite page ke liye CSV file hain ye wali
def litecsv():
    if os.path.exists(csv_file):
        os.remove(csv_file)
    #if not os.path.exists(csv_file):
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['ip_address','Timestamp', 'Event', 'TimeSpent', 'Link', 'Section'])

litecsv()

@app.route('/track-click', methods=['POST'])
def track_click():
    data = request.json
    
    # Print the data to debug
    #print(f"Received data: {data}")
    client_ip = get_client_ip()
    # Extract data from the JSON request
    event = data.get('event', '')  
    element = data.get('element', '')
    timestamp = data.get('timestamp', '')
    x = data.get('x', '')  # Ensure x is provided       
    y = data.get('y', '')
    page = data.get('page', '')
    relatedElement = data.get('relatedElement', '')
    inputValue = data.get('inputValue', '')
    location = data.get('location', '')
    destination = data.get('destination', '')
    timeSpent = data.get('timeSpent', 0)  # Ensure timeSpent is numeric
    scroll = data.get('scroll', 0)  # New parameter for scroll value
    depth = data.get('depth', 0)  # New parameter for depth
    timeSpentOnHover = data.get('timeSpentOnHover', 0)  # New parameter for hover time
    
    # Write the data to the CSV file, maintaining the original order
    with open(CSV_FILE_PATH, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([
            client_ip,event, element, timestamp, x, y, page, 
            relatedElement, inputValue, location, 
            destination, timeSpent, scroll, depth,
            timeSpentOnHover
        ])

    with open(overall_csv,mode='a',newline='') as file:
        writer=csv.writer(file)
        writer.writerow([
            client_ip,event, element, timestamp, x, y, page, 
            relatedElement, inputValue, location, 
            destination, timeSpent, scroll, depth,
            timeSpentOnHover
        ])

    return jsonify({'status': 'success'}), 201

@app.route('/archive1', methods=['POST'])
def archive1():
    data = request.json
    
    # Print the data to debug
    #print(f"Received data: {data}")
    client_ip = get_client_ip()
    # Extract data from the JSON request
    event = data.get('event', '')  
    element = data.get('element', '')
    timestamp = data.get('timestamp', '')
    x = data.get('x', '')  # Ensure x is provided
    y = data.get('y', '')
    page = data.get('page', '')
    relatedElement = data.get('relatedElement', '')
    inputValue = data.get('inputValue', '')
    location = data.get('location', '')
    destination = data.get('destination', '')
    timeSpent = data.get('timeSpent', 0)  # Ensure timeSpent is numeric
    scroll = data.get('scroll', 0)  # New parameter for scroll value
    depth = data.get('depth', 0)  # New parameter for depth
    timeSpentOnHover = data.get('timeSpentOnHover', 0)  # New parameter for hover time
    
    # Write the data to the CSV file, maintaining the original order
    with open(CSV_FILE_PATH2, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([
            client_ip, event, element, timestamp, x, y, page, 
            relatedElement, inputValue, location, 
            destination, timeSpent, scroll, depth,
            timeSpentOnHover
        ])

    with open(overall_csv_mapliteuserdata, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([
            client_ip, event, element, timestamp, x, y, page, 
            relatedElement, inputValue, location, 
            destination, timeSpent, scroll, depth,
            timeSpentOnHover
        ])

    return jsonify({'status': 'success'}),201 


@app.route('/track_activitylite', methods=['POST'])
def track_activitylite():
    activity_data = request.json
    client_ip = get_client_ip()
    event = activity_data.get('event')
    time_spent = activity_data.get('timeSpent', None)
    link = activity_data.get('link', None)
    section = activity_data.get('section', None)
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Log activity into CSV file
    with open(csv_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([client_ip,timestamp, event, time_spent, link, section])

    with open(overall_csv_archive_user, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([client_ip,timestamp, event, time_spent, link, section])

    

    return jsonify({'status': 'success', 'message': 'Activity recorded successfully'}), 201



@app.route('/track-time', methods=['POST'])
def track_time():
    data = request.json
    client_ip = get_client_ip()
    page = data.get('page', '')
    time_spent = data.get('timeSpent', 0)  # Time spent in seconds

    # Log the time spent to the CSV file
    with open(CSV_FILE_PATH_Map, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([client_ip, page, time_spent])

    with open(overall_csv_2DmapTimespent, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([client_ip, page, time_spent])

    return jsonify({'status': 'success', 'message': 'Time spent recorded successfully'}), 201


@app.route('/track-timehome', methods=['POST'])
def track_timehome():
    data = request.json
    client_ip = get_client_ip()
    page = data.get('page', '')
    time_spent = data.get('timeSpent', 0)  # Time spent in seconds

    # Log the time spent to the CSV file
    with open(CSV_FILE_PATH_Homesession, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([client_ip, page , time_spent])

    with open(overall_csv_homesession, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([client_ip, page , time_spent])


    return jsonify({'status': 'success', 'message': 'Time spent recorded successfully'}), 201

@app.route('/track_timearchive', methods=['POST'])
def track_timearchive():
    data = request.json
    print(data)
    client_ip = get_client_ip()
    page = data.get('page', '')
    print(page)
    time_spent = data.get('timeSpent', 0)  # Time spent in seconds

    # Log the time spent to the CSV file
    with open(CSV_FILE_PATH_archive, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([client_ip, page , time_spent])

    with open(overall_csv_archivetimespent, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([client_ip, page , time_spent])

    return jsonify({'status': 'success', 'message': 'Time spent recorded successfully'}), 201





if __name__ == '__main__':
    app.run(debug=True)
