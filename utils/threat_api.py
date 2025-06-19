import requests
import os

# VirusTotal lookup
def check_ip_virustotal(ip):
    api_key = os.getenv("VT_API_KEY")
    headers = {"x-apikey": api_key}
    url = f"https://www.virustotal.com/api/v3/ip_addresses/{ip}"

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        stats = data.get("data", {}).get("attributes", {}).get("last_analysis_stats", {})
        return stats
    else:
        return f"VirusTotal Error: {response.status_code} - {response.text}"

# AbuseIPDB lookup
def check_ip_abuseipdb(ip):
    api_key = os.getenv("ABUSEIPDB_API_KEY")
    url = "https://api.abuseipdb.com/api/v2/check"
    headers = {
        "Accept": "application/json",
        "Key": api_key
    }
    params = {
        "ipAddress": ip,
        "maxAgeInDays": 90
    }

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json().get("data", {})
        return {
            "abuseConfidenceScore": data.get("abuseConfidenceScore"),
            "countryCode": data.get("countryCode"),
            "usageType": data.get("usageType"),
            "domain": data.get("domain")
        }
    else:
        return f"AbuseIPDB Error: {response.status_code} - {response.text}"
