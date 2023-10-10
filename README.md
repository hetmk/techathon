# Smart Attendance System

The Smart Attendance System is an innovative solution to manage attendance using advanced technologies including face comparison, database querying with Language Models, and more. This repository will guide you through the setup and execution process.

## Table of Contents
- [Installation](#installation)
  - [Prerequisites](#prerequisites)
  - [Steps](#steps)
- [Execution](#execution)

## Installation

### Prerequisites
Before getting started, ensure you have the following:
- Anaconda for managing virtual environments.
- Docker for running the face compare API.
- Node.js and npm for the React app.

### Steps

1. **Setup Conda Virtual Environment**: 
   - Navigate to both the `Anti-spoofing` and `Server` folders and install the necessary dependencies using the `requirements.txt` file:
     ```bash
     conda create --name smart-attendance python=3.7
     conda activate smart-attendance
     pip install -r Anti-spoofing/requirements.txt
     pip install -r Server/requirements.txt
     ```

2. **Docker Environment**:
   - Install Docker from the official [Docker website](https://www.docker.com/).
   - Create an environment to run the face comparison API.

3. **React App Dependencies**:
   - Navigate to the React app folder and install its requirements:
     ```bash
     cd ReactApp
     npm install
     ```

4. **DB-GPT & LLM Setup**:
   - Follow the instructions on [this link](https://github.com/hetmk/techathon/tree/main/LLM%20using%20DB-GPT) to install and setup `db-gpt` and `llm`.

5. **Firebase & Google Sheet API**:
   - Setup Firebase for your project.
   - Activate the Google Sheet API for your Firebase project.
    
6. **Update Credentials**:
   - In the server code, replace any instances of `{your-credentials}` or `{api-key}` with your actual credentials.

## Execution

1. **Anti-Spoofing**:
   - Activate the conda environment and run `test.py` in the `Anti-spoofing` folder:
     ```bash
     conda activate smart-attendance
     python Anti-spoofing/test.py
     ```

2. **Start the Server**:
   - While still in the virtual environment, navigate to the `Server` folder and run `RestApi.py`:
     ```bash
     python Server/RestApi.py
     ```

3. **React App**:
   - Navigate to the React app directory and start the app:
     ```bash
     cd ReactApp
     npm start
     ```

4. **Face Comparison with Docker**:
   - Start your Docker container.
   - Navigate to the compare face UI in your web browser.
   - Login, and then either train the dataset or compare faces.

5. **DB-GPT Server for LLM**:
   - Start the `db-gpt` server. This will allow the Language Model to communicate with your database.
   - Ensure your database is uploaded and properly configured with the server.
