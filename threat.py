import csv
import ast
from flask import Flask, render_template

app = Flask(__name__)

# Path to the CSV file
csv_file_path = 'zap_results.csv'

@app.route('/')
def display_logs():
    log_list = []

    # Open and read the CSV file
    with open(csv_file_path, mode='r') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            source = row[0]  # Assuming source is in the first column
            timestamp = row[1]  # Assuming timestamp is in the second column
            
            # Convert the string representation of a list of dictionaries to an actual list
            alerts = ast.literal_eval(row[2])  

            # Process each alert in the list of alerts
            alert_entries = []
            for alert in alerts:
                # Create a dictionary for each alert, extracting known keys
                alert_entry = {
                    'sourceid': alert.get('sourceid', ''),
                    'other': alert.get('other', ''),
                    'method': alert.get('method', ''),
                    'evidence': alert.get('evidence', ''),
                    'pluginId': alert.get('pluginId', ''),
                    'cweid': alert.get('cweid', ''),
                    'confidence': alert.get('confidence', ''),
                    'wascid': alert.get('wascid', ''),
                    'description': alert.get('description', ''),
                    'messageId': alert.get('messageId', ''),
                    'inputVector': alert.get('inputVector', ''),
                    'url': alert.get('url', ''),
                    'tags': alert.get('tags', {}),
                    'reference': alert.get('reference', ''),
                    'solution': alert.get('solution', ''),
                    'alert': alert.get('alert', ''),
                    'param': alert.get('param', ''),
                    'attack': alert.get('attack', ''),
                    'name': alert.get('name', ''),
                    'risk': alert.get('risk', ''),
                    'id': alert.get('id', ''),
                    'alertRef': alert.get('alertRef', '')
                }
                alert_entries.append(alert_entry)

            # Append a single entry for all alerts in the row with one timestamp and source
            log_list.append({
                'source': source,
                'timestamp': timestamp,
                'alerts': alert_entries  # List of alerts for this row
            })

    # Render logs to HTML page
    return render_template('threat.html', logs=log_list)

if __name__ == '__main__':
    app.run(debug=True)
