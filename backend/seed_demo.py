from datetime import datetime, timedelta, timezone

from app.database import Base, engine, SessionLocal
from app import models

from app.models.security_event import SecurityEvent
from app.models.incident import Incident
from app.models.alert import Alert
from app.models.threat_intelligence import ThreatIntelligence
from app.models.incident_event import IncidentEvent


# Make sure all tables exist
Base.metadata.create_all(bind=engine)

db = SessionLocal()

try:
    # ---------------------------------------------------------
    # SAFETY CHECK
    # Do not create duplicate demo data
    # ---------------------------------------------------------
    existing_events = db.query(SecurityEvent).count()

    if existing_events > 0:
        print("Seed skipped.")
        print(f"Security events already exist: {existing_events}")
        print("No existing data was changed.")
        raise SystemExit(0)

    now = datetime.now(timezone.utc)

    # ---------------------------------------------------------
    # 1. SECURITY EVENTS - 35
    # ---------------------------------------------------------

    event_data = [
        # Brute force events
        ("login_failure", "185.220.101.10", "ip", "185.220.101.10",
         "admin", "login", "failed", "high",
         "Multiple failed login attempts detected"),

        ("login_failure", "185.220.101.10", "ip", "185.220.101.10",
         "admin", "login", "failed", "high",
         "Failed login attempt"),

        ("login_failure", "185.220.101.10", "ip", "185.220.101.10",
         "admin", "login", "failed", "high",
         "Failed login attempt"),

        ("login_failure", "185.220.101.10", "ip", "185.220.101.10",
         "admin", "login", "failed", "high",
         "Failed login attempt"),

        ("login_failure", "185.220.101.10", "ip", "185.220.101.10",
         "admin", "login", "failed", "critical",
         "Brute force threshold exceeded"),

        # Suspicious login
        ("suspicious_login", "45.155.205.33", "ip", "45.155.205.33",
         "rajkumar", "login", "failed", "high",
         "Login from suspicious source IP"),

        ("suspicious_login", "45.155.205.33", "ip", "45.155.205.33",
         "rajkumar", "login", "failed", "high",
         "Suspicious authentication activity"),

        ("suspicious_login", "45.155.205.33", "ip", "45.155.205.33",
         "rajkumar", "login", "success", "medium",
         "Successful login from suspicious IP"),

        # Malware / IOC
        ("malware_detected", "103.91.190.12", "ip", "103.91.190.12",
         "user1", "file_access", "detected", "critical",
         "Known malicious IP detected"),

        ("malware_detected", "103.91.190.12", "ip", "103.91.190.12",
         "user1", "file_access", "detected", "critical",
         "Malicious activity detected"),

        ("ioc_match", "91.240.118.172", "ip", "91.240.118.172",
         "user2", "network_connection", "blocked", "high",
         "Threat intelligence IOC match"),

        ("ioc_match", "91.240.118.172", "ip", "91.240.118.172",
         "user2", "network_connection", "blocked", "high",
         "Known malicious indicator detected"),

        # Privilege / account activity
        ("privilege_change", "10.0.0.15", None, None,
         "admin1", "role_change", "success", "medium",
         "Administrative privilege change"),

        ("account_activity", "10.0.0.25", None, None,
         "user3", "password_change", "success", "low",
         "Password changed successfully"),

        ("account_activity", "10.0.0.26", None, None,
         "user4", "account_unlock", "success", "low",
         "User account unlocked"),

        # Web attacks
        ("sql_injection", "172.16.10.45", "ip", "172.16.10.45",
         "webuser", "request", "blocked", "critical",
         "Possible SQL injection attempt blocked"),

        ("sql_injection", "172.16.10.45", "ip", "172.16.10.45",
         "webuser", "request", "blocked", "critical",
         "Repeated SQL injection pattern detected"),

        ("xss_attempt", "172.16.10.50", "ip", "172.16.10.50",
         "webuser", "request", "blocked", "high",
         "Cross-site scripting attempt detected"),

        ("xss_attempt", "172.16.10.50", "ip", "172.16.10.50",
         "webuser", "request", "blocked", "high",
         "Malicious script payload detected"),

        # Network activity
        ("port_scan", "192.168.1.55", "ip", "192.168.1.55",
         "scanner", "network_scan", "detected", "high",
         "Port scanning activity detected"),

        ("port_scan", "192.168.1.55", "ip", "192.168.1.55",
         "scanner", "network_scan", "detected", "high",
         "Repeated port scanning detected"),

        ("network_anomaly", "192.168.1.77", None, None,
         "user5", "network_connection", "detected", "medium",
         "Unusual network behavior detected"),

        ("network_anomaly", "192.168.1.78", None, None,
         "user6", "network_connection", "detected", "medium",
         "Abnormal outbound traffic detected"),

        # Data access
        ("data_access", "10.0.0.40", None, None,
         "user7", "database_query", "success", "medium",
         "Unusual database access detected"),

        ("data_access", "10.0.0.41", None, None,
         "user8", "database_query", "success", "medium",
         "Sensitive table access detected"),

        ("file_access", "10.0.0.42", None, None,
         "user9", "file_read", "success", "low",
         "Sensitive file accessed"),

        ("file_access", "10.0.0.43", None, None,
         "user10", "file_download", "success", "medium",
         "Large file download detected"),

        # Authentication
        ("login_success", "10.0.0.50", None, None,
         "user11", "login", "success", "low",
         "Normal successful login"),

        ("login_success", "10.0.0.51", None, None,
         "user12", "login", "success", "low",
         "Normal successful login"),

        ("login_failure", "10.0.0.52", None, None,
         "user13", "login", "failed", "medium",
         "Failed login attempt"),

        ("login_failure", "10.0.0.53", None, None,
         "user14", "login", "failed", "medium",
         "Failed login attempt"),

        # Additional anomalies
        ("process_anomaly", "10.0.0.60", None, None,
         "user15", "process_start", "detected", "high",
         "Unusual process execution detected"),

        ("process_anomaly", "10.0.0.61", None, None,
         "user16", "process_start", "detected", "high",
         "Suspicious process behavior detected"),

        ("configuration_change", "10.0.0.70", None, None,
         "admin1", "configuration", "success", "medium",
         "Security configuration changed"),

        ("configuration_change", "10.0.0.71", None, None,
         "admin1", "configuration", "success", "low",
         "System configuration updated"),
    ]

    events = []

    for index, item in enumerate(event_data):
        event_type, source_ip, ioc_type, ioc_value, username, action, status, severity, message = item

        event = SecurityEvent(
            event_type=event_type,
            source_ip=source_ip,
            ioc_type=ioc_type,
            ioc_value=ioc_value,
            username=username,
            action=action,
            status=status,
            severity=severity,
            message=message,
            created_at=now - timedelta(minutes=(index * 7))
        )

        db.add(event)
        events.append(event)

    db.flush()

    print(f"Created {len(events)} security events.")

    # ---------------------------------------------------------
    # 2. THREAT INTELLIGENCE - 6
    # ---------------------------------------------------------

    threat_data = [
        ("ip", "185.220.101.10", "high", "SentinelX Demo Feed",
         "Known brute-force source"),
        ("ip", "45.155.205.33", "high", "SentinelX Demo Feed",
         "Suspicious authentication source"),
        ("ip", "103.91.190.12", "critical", "SentinelX Demo Feed",
         "Known malicious infrastructure"),
        ("ip", "91.240.118.172", "critical", "SentinelX Demo Feed",
         "Known malicious IOC"),
        ("ip", "172.16.10.45", "high", "SentinelX Demo Feed",
         "Web attack source"),
        ("ip", "192.168.1.55", "medium", "SentinelX Demo Feed",
         "Network scanning source"),
    ]

    threats = []

    for item in threat_data:
        ioc_type, ioc_value, threat_level, source, description = item

        threat = ThreatIntelligence(
            ioc_type=ioc_type,
            ioc_value=ioc_value,
            threat_level=threat_level,
            source=source,
            description=description,
            created_at=now
        )

        db.add(threat)
        threats.append(threat)

    db.flush()

    print(f"Created {len(threats)} threat intelligence records.")

    # ---------------------------------------------------------
    # 3. INCIDENTS - 19
    # ---------------------------------------------------------

    incident_data = [
        ("Brute Force Attack", "Repeated failed login attempts detected",
         "brute_force", "Brute Force Detection", "185.220.101.10",
         "ip", "185.220.101.10", "admin", "critical", 95, "open"),

        ("Suspicious Login Activity", "Login from suspicious IP address",
         "suspicious_login", "Suspicious Login Detection", "45.155.205.33",
         "ip", "45.155.205.33", "rajkumar", "high", 80, "investigating"),

        ("Malicious IP Detected", "Known malicious source detected",
         "malware", "Threat Intelligence Detection", "103.91.190.12",
         "ip", "103.91.190.12", "user1", "critical", 95, "open"),

        ("Threat Intelligence Match", "IOC matched known malicious indicator",
         "ioc_match", "Threat Intelligence Detection", "91.240.118.172",
         "ip", "91.240.118.172", "user2", "high", 85, "investigating"),

        ("SQL Injection Attempt", "Possible SQL injection attack blocked",
         "web_attack", "SQL Injection Detection", "172.16.10.45",
         "ip", "172.16.10.45", "webuser", "critical", 95, "open"),

        ("XSS Attack Attempt", "Cross-site scripting attempt detected",
         "web_attack", "XSS Detection", "172.16.10.50",
         "ip", "172.16.10.50", "webuser", "high", 80, "resolved"),

        ("Port Scan Detected", "Repeated port scanning activity",
         "network_scan", "Port Scan Detection", "192.168.1.55",
         "ip", "192.168.1.55", "scanner", "high", 75, "investigating"),

        ("Network Anomaly", "Unusual outbound traffic detected",
         "network_anomaly", "ML Anomaly Detection", "192.168.1.77",
         None, None, "user5", "medium", 60, "open"),

        ("Database Access Anomaly", "Unusual database activity detected",
         "data_access", "ML Anomaly Detection", "10.0.0.40",
         None, None, "user7", "medium", 55, "open"),

        ("Sensitive Data Access", "Sensitive database table accessed",
         "data_access", "Data Access Detection", "10.0.0.41",
         None, None, "user8", "medium", 50, "resolved"),

        ("Suspicious File Download", "Large file download detected",
         "file_access", "File Access Detection", "10.0.0.43",
         None, None, "user10", "medium", 55, "investigating"),

        ("Process Anomaly", "Unusual process execution detected",
         "process_anomaly", "ML Anomaly Detection", "10.0.0.60",
         None, None, "user15", "high", 72, "open"),

        ("Suspicious Process", "Suspicious process behavior detected",
         "process_anomaly", "ML Anomaly Detection", "10.0.0.61",
         None, None, "user16", "high", 78, "open"),

        ("Privilege Change", "Administrative privilege change detected",
         "privilege_change", "Privilege Monitoring", "10.0.0.15",
         None, None, "admin1", "medium", 55, "resolved"),

        ("Failed Login Pattern", "Repeated failed login activity",
         "authentication", "Authentication Monitoring", "10.0.0.52",
         None, None, "user13", "medium", 50, "closed"),

        ("Failed Login Pattern", "Repeated failed login activity",
         "authentication", "Authentication Monitoring", "10.0.0.53",
         None, None, "user14", "medium", 50, "resolved"),

        ("Configuration Change", "Security configuration changed",
         "configuration", "Configuration Monitoring", "10.0.0.70",
         None, None, "admin1", "medium", 55, "closed"),

        ("Security Configuration Update", "System configuration updated",
         "configuration", "Configuration Monitoring", "10.0.0.71",
         None, None, "admin1", "low", 35, "resolved"),

        ("Abnormal Network Activity", "Abnormal outbound network behavior",
         "network_anomaly", "ML Anomaly Detection", "192.168.1.78",
         None, None, "user6", "medium", 65, "open"),
    ]

    incidents = []

    for index, item in enumerate(incident_data):
        (
            title,
            description,
            incident_type,
            detection_rule,
            source_ip,
            ioc_type,
            ioc_value,
            username,
            severity,
            risk_score,
            status
        ) = item

        incident = Incident(
            title=title,
            description=description,
            incident_type=incident_type,
            detection_rule=detection_rule,
            source_ip=source_ip,
            ioc_type=ioc_type,
            ioc_value=ioc_value,
            event_id=events[index].id,
            username=username,
            severity=severity,
            risk_score=risk_score,
            status=status,
            assigned_to=1,
            investigation_notes="Demo investigation record for SentinelX SOC dashboard.",
            created_at=now - timedelta(hours=index),
            updated_at=now - timedelta(hours=index)
        )

        db.add(incident)
        incidents.append(incident)

    db.flush()

    print(f"Created {len(incidents)} incidents.")

    # ---------------------------------------------------------
    # 4. INCIDENT ↔ EVENT CORRELATION
    # ---------------------------------------------------------

    correlation_count = 0

    for incident_index, incident in enumerate(incidents):
        # Attach the main event
        link = IncidentEvent(
            incident_id=incident.id,
            event_id=events[incident_index].id,
            created_at=now
        )

        db.add(link)
        correlation_count += 1

        # Attach extra events to first two incidents
        if incident_index == 0:
            for event_index in range(1, 5):
                db.add(
                    IncidentEvent(
                        incident_id=incident.id,
                        event_id=events[event_index].id,
                        created_at=now
                    )
                )
                correlation_count += 1

        if incident_index == 1:
            for event_index in range(5, 8):
                db.add(
                    IncidentEvent(
                        incident_id=incident.id,
                        event_id=events[event_index].id,
                        created_at=now
                    )
                )
                correlation_count += 1

    db.flush()

    print(f"Created {correlation_count} incident-event relationships.")

    # ---------------------------------------------------------
    # 5. ALERTS - 14
    # ---------------------------------------------------------

    alert_data = [
        ("Critical Brute Force Alert",
         "Multiple failed login attempts exceeded the detection threshold.",
         "critical", 95, "new"),

        ("Suspicious Login Alert",
         "Login activity detected from a suspicious IP address.",
         "high", 80, "new"),

        ("Malicious IP Alert",
         "Known malicious IP detected by threat intelligence.",
         "critical", 95, "new"),

        ("IOC Match Alert",
         "Security event matched a known malicious indicator.",
         "high", 85, "acknowledged"),

        ("SQL Injection Alert",
         "Possible SQL injection attack was detected and blocked.",
         "critical", 95, "new"),

        ("XSS Attack Alert",
         "Cross-site scripting attempt detected.",
         "high", 80, "resolved"),

        ("Port Scan Alert",
         "Repeated network scanning activity detected.",
         "high", 75, "acknowledged"),

        ("Network Anomaly Alert",
         "ML anomaly detection identified unusual network behavior.",
         "medium", 60, "new"),

        ("Database Anomaly Alert",
         "Unusual database access pattern detected.",
         "medium", 55, "new"),

        ("File Access Alert",
         "Suspicious large file download detected.",
         "medium", 55, "acknowledged"),

        ("Process Anomaly Alert",
         "Unusual process execution detected by ML analysis.",
         "high", 72, "new"),

        ("Privilege Change Alert",
         "Administrative privilege change detected.",
         "medium", 55, "resolved"),

        ("Authentication Alert",
         "Repeated failed login pattern detected.",
         "medium", 50, "resolved"),

        ("Configuration Change Alert",
         "Security configuration change detected.",
         "medium", 55, "acknowledged"),
    ]

    alerts = []

    for index, item in enumerate(alert_data):
        title, message, severity, risk_score, status = item

        alert = Alert(
            incident_id=incidents[index].id,
            title=title,
            message=message,
            severity=severity,
            risk_score=risk_score,
            status=status,
            acknowledged_by=1 if status == "acknowledged" else None,
            resolved_by=1 if status == "resolved" else None,
            created_at=now - timedelta(hours=index),
            updated_at=now - timedelta(hours=index)
        )

        db.add(alert)
        alerts.append(alert)

    db.flush()

    print(f"Created {len(alerts)} alerts.")

    # ---------------------------------------------------------
    # COMMIT
    # ---------------------------------------------------------

    db.commit()

    print()
    print("========================================")
    print("SentinelX demo seed completed")
    print("========================================")
    print(f"Security Events : {len(events)}")
    print(f"Incidents       : {len(incidents)}")
    print(f"Alerts          : {len(alerts)}")
    print(f"Threat Intel    : {len(threats)}")
    print(f"Correlations    : {correlation_count}")
    print("========================================")

finally:
    db.close()