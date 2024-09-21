# timesheet-v1

## Overview

This project is a FastAPI-based application. It utilizes SQLAlchemy for database interactions, bcrypt for hashing passwords, and Python-Jose for JSON Web Token (JWT) operations.

## Prerequisites

Ensure you have Python 3.x or above installed on your system.

## Setup Instructions

Follow these steps to set up the project on your local machine:

1. **Clone the Repository**

   Clone the project repository from Bitbucket:

   ```bash
   git clone <your-bitbucket-repo-url>
   cd <project-directory>
   ```
2. **Install the Required Dependencies**

   Install the Python dependencies listed in requirements.txt:

   pip install -r requirements.txt
3. **Environment Variables**

   Create a .env file in the project root and define the environment variables. You can use the env.dist file as a template:
   ```bash
   cp env.dist .env
   ```
   Edit the .env file to add your actual credentials:

4. **Run the Application**

   Launch the FastAPI application using Uvicorn:

   ```bash
   uvicorn main:app --reload
   ```
   The application will start running at http://127.0.0.1:8000

