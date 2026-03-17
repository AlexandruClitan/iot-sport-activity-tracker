# Sport Activity Monitoring System using Strava API and Azure

## Project Overview

This project implements an automated sport activity monitoring system that retrieves activity data from the Strava API, processes it locally, uploads it to Azure Blob Storage, and generates visual analytics.

The system also sends email notifications when certain performance conditions are met.

The project demonstrates the integration of API communication, cloud storage, data processing, visualization, and automated notifications using Python.

## Features

- Authentication with Strava API
- Retrieve user activity data
- Save activity data locally as CSV
- Upload data to Azure Blob Storage
- Generate performance graphs using Matplotlib
- Create gauge charts for heart rate visualization
- Send automatic email notifications based on pace
- Timestamp-based file generation

## Technologies Used

- Python
- Strava API
- Azure Blob Storage
- Matplotlib
- NumPy
- Requests
- SMTP

## How it works

1. Authenticate with Strava API
2. Download activity data
3. Save data to CSV
4. Upload file to Azure Blob Storage
5. Generate performance graphs
6. Send email notification if pace < 8 min/km
7. Display heart rate gauge charts

## Notes

Dataset files and credentials are not included for security reasons.

This project was created for educational and IoT cloud integration purposes.
