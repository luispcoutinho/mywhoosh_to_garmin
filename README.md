# MyWhoosh to Garmin Converter

A tool to convert MyWhoosh workout data to Garmin format.

## Installation and Setup

### Clone the repository
`git clone https://github.com/mvace/mywhoosh_to_garmin.git`

### Navigate to project folder
`cd .\mywhoosh_to_garmin\`

### Create virtual environment
`python -m venv .venv`

### Activate virtual environment
`.\.venv\Scripts\activate`

### Install dependencies
`pip install -r requirements.txt`

### Configure environment variables
1. Rename `.env.example` to `.env`
2. Open `.env` file and fill in your credentials:
  - MYWHOOSH_EMAIL: Your MyWhoosh account email
  - MYWHOOSH_PASSWORD: Your MyWhoosh account password
  - GARMIN_EMAIL: Your Garmin Connect email
  - GARMIN_PASSWORD: Your Garmin Connect password

### Run the script
`python main.py`

## Prerequisites

* Python 3.6 or higher
* Git

