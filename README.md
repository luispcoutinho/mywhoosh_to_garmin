# MyWhoosh to Garmin Sync Activities

A script that automates synchronization of activites from MyWhoosh to Garmin Connect.

## Installation and Setup

### Clone the repository
```bash
git clone https://github.com/mvace/mywhoosh_to_garmin.git
```

### Navigate to project folder
```bash
cd .\mywhoosh_to_garmin\
```

### Create virtual environment
```bash
python -m venv .venv
```

### Activate virtual environment
```bash
.\.venv\Scripts\activate
```

### Install dependencies
```bash
pip install -r requirements.txt
```

```bash
playwright install
```


### Configure environment variables
1. Rename `.env.example` to `.env`
2. Open `.env` file and fill in your credentials:
  - MYWHOOSH_EMAIL: Your MyWhoosh account email
  - MYWHOOSH_PASSWORD: Your MyWhoosh account password
  - GARMIN_EMAIL: Your Garmin Connect email
  - GARMIN_PASSWORD: Your Garmin Connect password

### Security Notice
Your credentials are stored locally in the `.env` file on your machine only. These credentials are used solely for authentication with MyWhoosh and Garmin Connect websites. The script does not transmit, store, or log your credentials anywhere else. As this is a client-side application, the repository owner and contributors have no access to your personal login information. We recommend reviewing the source code for transparency about credential handling.

### Run the script

#### Option 1: Command Line
```bash
python main.py
```

#### Option 2: Using Batch File (Windows)
Simply double-click the `run_script.bat` file in the project folder to execute the script. 

## Prerequisites

* Python (I used Python 3.11.)
* Git

