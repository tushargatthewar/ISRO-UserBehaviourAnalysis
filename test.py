from flask import Flask, request, jsonify, render_template
import csv
import os
import pandas as pd
import threading
import time
from datetime import datetime

app = Flask(__name__)

# Path to the CSV file
CSV_FILE_PATH = 'home_user_activity.csv'#home page user activity
CSV_FILE_PATH_Map= '2DmapTimespent.csv'#2 map timestamp
CSV_FILE_PATH_Homesession='Homesession.csv'#home timestamp
CSV_FILE_PATH_archive='archive.csv'#2d-lite timestamp

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

def initialize_csv():
    """Delete existing CSV file and create a new one with headers."""
    if os.path.exists(CSV_FILE_PATH):
        os.remove(CSV_FILE_PATH)
    
    with open(CSV_FILE_PATH, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['event', 'element', 'timestamp', 'x', 'y', 'page', 'relatedElement', 'inputValue', 'location', 'destination', 'timeSpent', 'scroll', 'depth', 'timeSpentOnHover'])

# Initialize the CSV file
initialize_csv()

#this is  for tarcking data of the maplite 
def initialize_csvmaplite():
    """Delete existing CSV file and create a new one with headers."""
    if os.path.exists(CSV_FILE_PATH2):
        os.remove(CSV_FILE_PATH2)
    
    with open(CSV_FILE_PATH2, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['event', 'element', 'timestamp', 'x', 'y', 'page', 'relatedElement', 'inputValue', 'location', 'destination', 'timeSpent', 'scroll', 'depth', 'timeSpentOnHover'])

# Initialize the CSV file
initialize_csvmaplite()



def initialize_csv1():
    """Create a new CSV file if it doesn't exist with appropriate headers."""

    if os.path.exists(CSV_FILE_PATH_Map):
        os.remove(CSV_FILE_PATH_Map)

    # if not os.path.exists(CSV_FILE_PATH_Map):
    with open(CSV_FILE_PATH_Map, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['page', 'timeSpent'])  # CSV Headers

initialize_csv1()

#home ke liye CSV timesspent
def initialize_csvhome():
    """Create a new CSV file if it doesn't exist with appropriate headers."""
    if os.path.exists(CSV_FILE_PATH_Homesession):
        os.remove(CSV_FILE_PATH_Homesession)
    
    #if not os.path.exists(CSV_FILE_PATH_Homesession):
    with open(CSV_FILE_PATH_Homesession, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['page', 'timeSpent'])  # CSV Headers

initialize_csvhome()

#archive ke liye CSV time spent
def initialize_csvarchive():
    """Create a new CSV file if it doesn't exist with appropriate headers."""
    if os.path.exists(CSV_FILE_PATH_archive):
        os.remove(CSV_FILE_PATH_archive)
    
    #if not os.path.exists(CSV_FILE_PATH_archive):
    with open(CSV_FILE_PATH_archive, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['page', 'timeSpent'])  # CSV Headers

initialize_csvarchive()

#lite page ke liye CSV file hain ye wali
def litecsv():
    if os.path.exists(csv_file):
        os.remove(csv_file)
    #if not os.path.exists(csv_file):
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Timestamp', 'Event', 'TimeSpent', 'Link', 'Section'])

litecsv()

@app.route('/track-click', methods=['POST'])
def track_click():
    data = request.json
    
    # Print the data to debug
    #print(f"Received data: {data}")
    
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
            event, element, timestamp, x, y, page, 
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
            event, element, timestamp, x, y, page, 
            relatedElement, inputValue, location, 
            destination, timeSpent, scroll, depth,
            timeSpentOnHover
        ])

    return jsonify({'status': 'success'}),201 


@app.route('/track_activitylite', methods=['POST'])
def track_activitylite():
    activity_data = request.json
    event = activity_data.get('event')
    time_spent = activity_data.get('timeSpent', None)
    link = activity_data.get('link', None)
    section = activity_data.get('section', None)
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Log activity into CSV file
    with open(csv_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, event, time_spent, link, section])

    print(f"User activity recorded: {event} at {timestamp}")

    return jsonify({'status': 'success', 'message': 'Activity recorded successfully'}), 201



@app.route('/track-time', methods=['POST'])
def track_time():
    data = request.json
    page = data.get('page', '')
    time_spent = data.get('timeSpent', 0)  # Time spent in seconds

    # Log the time spent to the CSV file
    with open(CSV_FILE_PATH_Map, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([page, time_spent])

    return jsonify({'status': 'success', 'message': 'Time spent recorded successfully'}), 201


@app.route('/track-timehome', methods=['POST'])
def track_timehome():
    data = request.json
    page = data.get('page', '')
    time_spent = data.get('timeSpent', 0)  # Time spent in seconds

    # Log the time spent to the CSV file
    with open(CSV_FILE_PATH_Homesession, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([page, time_spent])

    return jsonify({'status': 'success', 'message': 'Time spent recorded successfully'}), 201

@app.route('/track_timearchive', methods=['POST'])
def track_timearchive():
    data = request.json
    print(data)
    page = data.get('page', '')
    print(page)
    time_spent = data.get('timeSpent', 0)  # Time spent in seconds

    # Log the time spent to the CSV file
    with open(CSV_FILE_PATH_archive, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([page, time_spent])

    return jsonify({'status': 'success', 'message': 'Time spent recorded successfully'}), 201





if __name__ == '__main__':
    app.run(debug=True)
