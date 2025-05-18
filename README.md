![Completed](https://img.shields.io/badge/✓%20Completed-brightgreen)


# VectorShift Integrations Technical Assessment  

This project is a full-stack application that integrates with **HubSpot** using OAuth 2.0. It demonstrates a working implementation of both frontend (React) and backend (FastAPI) services with Redis support.  

### 📄 Assignment Instructions

[View VectorShift Technical Assessment Instructions (PDF)](./integrations_technical_assessment/VectorShift%20-%20Integrations%20Technical%20Assessment%20Instructions.pdf)




## 🗂️ Project Structure

- /frontend # React frontend for integrations  
- /backend # FastAPI backend with integration logic

/backend  

├── main.py  
├── redis_client.py  
└── requirements.txt  

/backend/integrations

├── airtable.py  
├── notion.py  
└── hubspot.py # <- Implemented in this assignment  


## 🚀 Part 1: HubSpot OAuth Integration

### ✅ Backend (`/backend/integrations/hubspot.py`)
Implemented the following functions:
- `authorize_hubspot`: Generates HubSpot OAuth 2.0 URL and redirects the user.
- `oauth2callback_hubspot`: Handles the OAuth callback and exchanges the code for access/refresh tokens.
- `get_hubspot_credentials`: Retrieves and stores the tokens for authenticated requests.

### ✅ Frontend (`/frontend/src/integrations/hubspot.js`)
- Handles OAuth initiation and token exchange.
- Integrated with UI alongside Airtable and Notion.
- Registered in global integration routes and dropdown menus.

---

## 📦 Part 2: Loading HubSpot Items

### ✅ Backend (`get_items_hubspot` in `hubspot.py`)
- Authenticated API calls using retrieved OAuth credentials.
- Fetched data (e.g., CRM Contacts, Deals).
- Converted data into `IntegrationItem` objects with dynamic fields.
- Logged the fetched items to the console.

---

## 🛠️ Setup Instructions

### Prerequisites
- Node.js + npm
- Python 3.9+
- Redis server
- HubSpot Developer Account (for OAuth credentials)

### Clone the repository
```bash
git clone https://github.com/vaibhavxom/Assignment_Vectorshift.git
cd Assignment_Vectorshift
```

## 2. Backend Setup  
```bash  
cd backend  
python -m venv venv  
source venv/bin/activate  # or venv\Scripts\activate on Windows  
pip install -r requirements.txt  
uvicorn main:app --reload
```
  
Make sure Redis is running:  
``redis-server``  
## 3.Forntend Setup
```bash
cd frontend
npm install
npm run start
```

## 🔐 OAuth Setup
  
#### 1. Go to [HubSpot Developer](https://developers.hubspot.com/).

#### 2. Create an app and get:  
  - Client ID  
  - Client Secret  
  - Redirect URI (e.g., `http://localhost:8000/oauth2callback/hubspot`)

#### 4. Update the credentials in the backend as needed (can use .`env` file).  

### 🧪 Testing

- Initiate the OAuth flow by clicking "Connect HubSpot" in the UI.
- Authorize and get redirected back.
- Fetch and display integration items (printed to backend logs or console).

### 📄 Notes
- Airtable and Notion integrations are non-functional due to redacted credentials.
- Focused only on HubSpot integration for this task.
- Safe to modify, add, or remove files as necessary.




