# SentinelX

## AI-Assisted Security Monitoring & Incident Response Platform

SentinelX is a security monitoring platform designed to help Security
Operations Center (SOC) analysts detect, investigate, prioritize, and
respond to security threats.

It combines rule-based threat detection, threat intelligence, risk
scoring, incident management, machine-learning anomaly detection, MITRE
ATT&CK mapping, alert management, audit logging, and security reporting
in one platform.

------------------------------------------------------------------------

## Problem Statement

Modern organizations generate a large number of security events from
applications, users, networks, and authentication systems.

Manually analyzing these events can be difficult because:

-   Large numbers of security events are generated.
-   Suspicious activities can be missed.
-   Different events may belong to the same incident.
-   Analysts need to prioritize high-risk threats.
-   Security investigations require proper tracking.
-   Security teams need clear reports and audit records.

SentinelX addresses these problems by providing a centralized security
monitoring and incident response platform.

------------------------------------------------------------------------

## Proposed Solution

SentinelX collects security events and analyzes them using multiple
detection mechanisms.

The platform:

1.  Receives security events.
2.  Detects suspicious activity.
3.  Checks threat intelligence indicators.
4.  Calculates risk scores.
5.  Creates security incidents.
6.  Generates alerts.
7.  Correlates related events.
8.  Supports investigation and assignment.
9.  Uses ML to detect anomalous events.
10. Maps detected threats to MITRE ATT&CK.
11. Maintains audit logs.
12. Generates security reports.

------------------------------------------------------------------------

## System Architecture

``` text
                    +----------------------+
                    |      Security Logs   |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    |   Detection Engine   |
                    +----------+-----------+
                               |
                +--------------+--------------+
                |              |              |
                v              v              v
        +-------------+ +-------------+ +-------------+
        | Rule Based  | |   Threat    | |     ML      |
        | Detection   | | Intelligence| | Anomaly     |
        +------+------+ +------+------+ +------+------+
               |               |               |
               +---------------+---------------+
                               |
                               v
                    +----------------------+
                    |    Risk Scoring      |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    | Event Correlation    |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    |      Incident        |
                    |     Management      |
                    +----------+-----------+
                               |
                    +----------+----------+
                    |                     |
                    v                     v
             +-------------+       +-------------+
             |    Alerts   |       | Investigation|
             +-------------+       +-------------+
                    |                     |
                    +----------+----------+
                               |
                               v
                    +----------------------+
                    |   Reports & Audit    |
                    +----------------------+
```

------------------------------------------------------------------------

## Core Workflow

``` text
Security Event
      ↓
Detection
      ↓
Threat Intelligence Check
      ↓
Risk Scoring
      ↓
Event Correlation
      ↓
Incident Creation
      ↓
Alert Generation
      ↓
Investigation
      ↓
Incident Resolution
      ↓
Audit & Reporting
```

------------------------------------------------------------------------

## Key Features

### 1. Authentication & Authorization

-   User registration and login
-   JWT-based authentication
-   Password hashing using Argon2
-   Role-Based Access Control (RBAC)
-   Admin and Analyst roles
-   Protected API endpoints

### 2. Security Event Monitoring

Security events can contain:

-   Event type
-   Source IP
-   IOC type
-   IOC value
-   Username
-   Action
-   Status
-   Severity
-   Message
-   Timestamp

Analysts can view and investigate security events through the SOC
dashboard.

### 3. Detection Engine

SentinelX currently supports rule-based detection for:

#### Brute Force Detection

Detects repeated failed login attempts from the same source IP within a
defined time window.

``` text
5+ failed login attempts
within 10 minutes
        ↓
Brute Force Detection
        ↓
High Risk
```

#### Suspicious Login Detection

Detects login activity from configured suspicious IP addresses.

#### Threat Intelligence Detection

Checks security events against stored Indicators of Compromise (IOCs).

Supported IOC information includes:

-   IP addresses
-   IOC values
-   Threat level
-   Source
-   Description

------------------------------------------------------------------------

## Risk Scoring

SentinelX assigns risk scores to detected threats.

  Threat Level   Risk Score
  -------------- ------------
  Low            30
  Medium         50
  High           70
  Critical       90

Detection rules can also assign specific risk scores based on the
detected behavior.

Risk levels:

``` text
0 - 39    → Low
40 - 69   → Medium
70 - 89   → High
90+       → Critical
```

------------------------------------------------------------------------

## Incident Management

When a threat is detected, SentinelX can automatically create an
incident.

Each incident can contain:

-   Title
-   Description
-   Incident type
-   Detection rule
-   Source IP
-   IOC
-   Username
-   Severity
-   Risk score
-   Status
-   Assigned analyst
-   Investigation notes
-   Related security events
-   Creation/update timestamps

Incident statuses include:

``` text
Open
Investigating
Resolved
Closed
```

------------------------------------------------------------------------

## Event Correlation

Multiple security events can be associated with the same incident.

This helps analysts understand the complete activity behind a security
threat instead of investigating every event independently.

``` text
Event 1 ─┐
Event 2 ─┼──→ Incident
Event 3 ─┤
Event 4 ─┘
```

------------------------------------------------------------------------

## Alert Management

SentinelX automatically generates alerts for detected incidents.

Alert information includes:

-   Alert title
-   Message
-   Severity
-   Risk score
-   Status
-   Related incident
-   Acknowledged user
-   Resolved user
-   Timestamp

Alert states:

``` text
New
Acknowledged
Resolved
```

------------------------------------------------------------------------

## Machine Learning Anomaly Detection

SentinelX uses **Isolation Forest** for anomaly detection.

The ML model analyzes security-event characteristics such as:

-   Severity
-   Failed/success status
-   Source IP availability
-   IOC availability
-   Username availability
-   Message length
-   Event type characteristics

The system identifies unusual security events that may not be detected
by predefined rules.

### ML Workflow

``` text
Security Events
      ↓
Feature Extraction
      ↓
Isolation Forest
      ↓
Anomaly Detection
      ↓
Risk Classification
      ↓
Incident Creation
      ↓
Alert Generation
```

High-confidence anomalies can receive higher risk scores and
automatically generate incidents and alerts.

------------------------------------------------------------------------

## MITRE ATT&CK Integration

SentinelX maps detected security behaviors to the **MITRE ATT&CK**
framework.

Current mappings include:

  Detection Rule      Technique        ID      Tactic
  ------------------- ---------------- ------- -------------------
  Brute Force Login   Brute Force      T1110   Credential Access
  Suspicious Login    Valid Accounts   T1078   Initial Access

This helps analysts understand the attacker behavior associated with a
detected event.

------------------------------------------------------------------------

## Investigation

Analysts can investigate incidents using:

-   Incident details
-   Related security events
-   Threat intelligence
-   MITRE ATT&CK mapping
-   Risk score
-   Severity
-   Investigation notes
-   Analyst assignment
-   Incident status

------------------------------------------------------------------------

## Audit Logging

Important security actions are recorded in audit logs.

Examples include:

-   Incident assignment
-   Incident status changes
-   Investigation updates
-   Alert status changes

Audit logs help provide accountability and traceability of analyst
activities.

Administrative access is protected using RBAC.

------------------------------------------------------------------------

## Security Features

SentinelX includes several security controls:

-   JWT authentication
-   Argon2 password hashing
-   Role-Based Access Control
-   API rate limiting
-   CORS configuration
-   Security headers
-   Input validation
-   Global error handling
-   Protected API endpoints
-   Audit logging

Security headers include:

``` text
X-Content-Type-Options
X-Frame-Options
X-XSS-Protection
Referrer-Policy
Permissions-Policy
```

------------------------------------------------------------------------

## SOC Dashboard

The SentinelX dashboard provides a centralized security overview.

It displays:

-   Total security events
-   Total incidents
-   Total alerts
-   Open incidents
-   Incident status
-   Incident severity
-   Alert status
-   Risk overview
-   Recent security activity
-   API status
-   Last updated time

------------------------------------------------------------------------

## Reports

SentinelX provides security reports in multiple formats.

### Summary Report

Provides an overview of:

-   Security events
-   Incidents
-   Alerts
-   Risk levels
-   Incident status
-   Alert status

### CSV Report

Security information can be exported as CSV for further analysis.

### PDF Report

Security information can also be generated as a PDF report.

------------------------------------------------------------------------

## Technology Stack

### Backend

-   Python
-   FastAPI
-   SQLAlchemy
-   SQLite
-   Pydantic
-   JWT
-   Argon2
-   Scikit-learn
-   ReportLab

### Frontend

-   HTML5
-   CSS3
-   JavaScript

### Machine Learning

-   Scikit-learn
-   Isolation Forest

### Security Framework

-   MITRE ATT&CK

### Database

-   SQLite

### Development Tools

-   Visual Studio Code
-   Git
-   GitHub
-   Swagger / OpenAPI

------------------------------------------------------------------------

## Project Structure

``` text
SentinelX/
│
├── backend/
│   ├── app/
│   │   ├── detection/
│   │   │   ├── rules.py
│   │   │   ├── engine.py
│   │   │   └── risk.py
│   │   │
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── security_event.py
│   │   │   ├── incident.py
│   │   │   ├── threat_intelligence.py
│   │   │   ├── audit_log.py
│   │   │   ├── incident_event.py
│   │   │   └── alert.py
│   │   │
│   │   ├── routes/
│   │   │   ├── auth.py
│   │   │   ├── security_events.py
│   │   │   ├── incident.py
│   │   │   ├── threat_intelligence.py
│   │   │   ├── audit_logs.py
│   │   │   ├── alerts.py
│   │   │   ├── dashboard.py
│   │   │   ├── mitre.py
│   │   │   ├── anomaly.py
│   │   │   └── reports.py
│   │   │
│   │   ├── security/
│   │   ├── services/
│   │   ├── database.py
│   │   └── main.py
│   │
│   └── requirements.txt
│
├── frontend/
│   ├── login.html
│   ├── dashboard.html
│   ├── security-events.html
│   ├── incidents.html
│   ├── incident-details.html
│   ├── alerts.html
│   ├── ml-anomalies.html
│   ├── mitre.html
│   ├── reports.html
│   ├── audit-logs.html
│   │
│   ├── css/
│   │   └── style.css
│   │
│   └── js/
│       ├── auth.js
│       ├── dashboard.js
│       ├── security-events.js
│       ├── incidents.js
│       ├── incident-details.js
│       ├── alerts.js
│       ├── ml-anomalies.js
│       ├── mitre.js
│       ├── reports.js
│       └── audit-logs.js
│
├── tests/
├── data/
├── docs/
├── .gitignore
├── README.md
└── requirements.txt
```

------------------------------------------------------------------------

## Installation

### 1. Clone the Repository

``` bash
git clone https://github.com/rajkumar020605/SentinelX.git
```

``` bash
cd SentinelX
```

### 2. Create Virtual Environment

``` bash
cd backend
python -m venv venv
```

### 3. Activate Virtual Environment

Windows:

``` bash
venv\Scripts\activate
```

### 4. Install Dependencies

``` bash
pip install -r requirements.txt
```

### 5. Start Backend

``` bash
uvicorn app.main:app --reload
```

Backend:

``` text
http://127.0.0.1:8000
```

Swagger API documentation:

``` text
http://127.0.0.1:8000/docs
```

------------------------------------------------------------------------

## Start Frontend

Open another terminal:

``` bash
cd frontend
```

Run:

``` bash
python -m http.server 5500
```

Open:

``` text
http://127.0.0.1:5500/login.html
```

------------------------------------------------------------------------

## API Documentation

SentinelX provides interactive API documentation using Swagger.

``` text
http://127.0.0.1:8000/docs
```

Major API areas include:

``` text
Authentication
Security Events
Incidents
Threat Intelligence
Alerts
Dashboard
MITRE ATT&CK
ML Anomalies
Reports
Audit Logs
```

------------------------------------------------------------------------

## Example Detection

A sequence of failed login attempts can trigger brute-force detection.

``` text
Failed Login 1
Failed Login 2
Failed Login 3
Failed Login 4
Failed Login 5
       ↓
Brute Force Detection
       ↓
Risk Score: 80
       ↓
High Severity Incident
       ↓
Alert Generated
```

------------------------------------------------------------------------

## Advantages

-   Centralized security monitoring
-   Automated threat detection
-   Risk-based prioritization
-   ML-based anomaly detection
-   Threat intelligence integration
-   Incident correlation
-   MITRE ATT&CK mapping
-   Alert management
-   Investigation tracking
-   Audit logging
-   Security reporting
-   Role-based access control

------------------------------------------------------------------------

## Future Enhancements

Possible future improvements include:

-   Real-time log streaming
-   SIEM integrations
-   Email/SMS notifications
-   More ML detection models
-   Advanced threat intelligence feeds
-   Network traffic analysis
-   Automated response actions
-   Cloud deployment
-   Docker containerization
-   PostgreSQL production database
-   Real-time SOC dashboards
-   More MITRE ATT&CK techniques
-   Advanced correlation rules

------------------------------------------------------------------------

## Project Status

**Status: Completed Core Platform**

Current SentinelX platform includes:

-   Authentication
-   RBAC
-   Security Event Monitoring
-   Detection Engine
-   Threat Intelligence
-   Risk Scoring
-   Incident Management
-   Event Correlation
-   Alert Management
-   Investigation
-   ML Anomaly Detection
-   MITRE ATT&CK
-   Audit Logging
-   SOC Dashboard
-   CSV/PDF Reporting

------------------------------------------------------------------------

## Author

**Rajkumar**

B.Tech Computer Science & Engineering

------------------------------------------------------------------------

## Disclaimer

SentinelX is an educational and security research project developed for
learning, demonstration, and SOC workflow simulation.

It should be properly secured and configured before being used in a real
production environment.
