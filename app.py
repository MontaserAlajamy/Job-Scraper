from flask import Flask, render_template, jsonify, send_file, request
from scraper import JobScraper
import os
import threading
import pandas as pd
from email_sender import send_email
import json
from datetime import datetime

app = Flask(__name__)

# Global variables
job_scraper = JobScraper()
scraping_in_progress = False
latest_jobs = []

@app.route('/')
def index():
    return render_template('index.html')



@app.route('/scrape', methods=['POST'])
def scrape():
    global scraping_in_progress, latest_jobs
    if not scraping_in_progress:
        scraping_in_progress = True
        data = request.json
        threading.Thread(target=run_scraper, args=(data['keywords'], data['location'], data['time_filter'])).start()
        return jsonify({"status": "Scraping started"}), 202
    else:
        return jsonify({"status": "Scraping already in progress"}), 409

def run_scraper(keywords, location, time_filter):
    global scraping_in_progress, latest_jobs
    try:
        latest_jobs = job_scraper.scrape_jobs(keywords, location, time_filter)
        print(f"Scraping completed. Found {len(latest_jobs)} jobs.")
        save_results_to_file(latest_jobs)
    except Exception as e:
        print(f"Error during scraping: {e}")
        latest_jobs = []
    finally:
        scraping_in_progress = False



def run_scraper(keywords, location, time_filter):
    global scraping_in_progress, latest_jobs
    try:
        latest_jobs = job_scraper.scrape_jobs(keywords, location, time_filter)
        print(f"Scraping completed. Found {len(latest_jobs)} jobs.")
        save_results_to_file(latest_jobs)
    except Exception as e:
        print(f"Error during scraping: {e}")
        latest_jobs = []
    finally:
        scraping_in_progress = False

def save_results_to_file(jobs):
    filename = f"job_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(jobs, f)
    print(f"Results saved to {filename}")

@app.route('/results')
def get_results():
    global latest_jobs
    return jsonify(latest_jobs)

@app.route('/download/<filetype>')
def download(filetype):
    if filetype not in ['excel', 'csv']:
        return "Invalid file type", 400
    
    df = pd.DataFrame(latest_jobs)
    filename = f"it_jobs_uae_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{'xlsx' if filetype == 'excel' else 'csv'}"
    
    if filetype == 'excel':
        df.to_excel(filename, index=False)
    else:
        df.to_csv(filename, index=False)
    
    return send_file(filename, as_attachment=True)

@app.route('/status')
def get_status():
    return jsonify({"scraping": scraping_in_progress})

@app.route('/send-email', methods=['POST'])
def send_results_email():
    recipient_email = request.json.get('email')
    email_body = request.json.get('body', '')
    if not recipient_email:
        return jsonify({"status": "Error", "message": "Email address is required"}), 400

    try:
        df = pd.DataFrame(latest_jobs)
        csv_file = f"job_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(csv_file, index=False)
        
        if send_email(recipient_email, csv_file, email_body):
            os.remove(csv_file)  # Remove the temporary CSV file after sending
            return jsonify({"status": "Success", "message": "Email sent successfully"}), 200
        else:
            return jsonify({"status": "Error", "message": "Failed to send email"}), 500
    except Exception as e:
        return jsonify({"status": "Error", "message": str(e)}), 500
    
# @app.route('/send-email', methods=['POST'])
# def send_results_email():
#     recipient_email = request.json.get('email')
#     email_body = request.json.get('body', '')
#     if not recipient_email:
#         return jsonify({"status": "Error", "message": "Email address is required"}), 400

#     try:
#         df = pd.DataFrame(latest_jobs)
#         csv_file = f"job_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
#         df.to_csv(csv_file, index=False)
        
#         if send_email(recipient_email, csv_file, email_body):
#             os.remove(csv_file)  # Remove the temporary CSV file after sending
#             return jsonify({"status": "Success", "message": "Email sent successfully"}), 200
#         else:
#             return jsonify({"status": "Error", "message": "Failed to send email"}), 500
#     except Exception as e:
#         return jsonify({"status": "Error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)