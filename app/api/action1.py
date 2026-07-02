import os
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://app.action1.com/api/3.0"


def get_token():
    response = requests.post(
        f"{BASE_URL}/oauth2/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "client_id": os.getenv("ACTION1_CLIENT_ID"),
            "client_secret": os.getenv("ACTION1_CLIENT_SECRET"),
        },
        timeout=30,
    )
    response.raise_for_status()
    return response.json()["access_token"]


def api_get(path, params=None):
    token = get_token()

    response = requests.get(
        f"{BASE_URL}{path}",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        },
        params=params,
        timeout=60,
    )

    if response.status_code >= 400:
        print("URL:", response.url)
        print("STATUS:", response.status_code)
        print("BODY:", response.text)

    response.raise_for_status()
    return response.json()


def get_report_data(report_id, limit=100, start=0):
    org_id = os.getenv("ACTION1_ORG_ID")

    return api_get(
        f"/reportdata/{org_id}/{report_id}/data",
        params={
            "from": start,
            "limit": limit,
        },
    )


def get_all_report_data(report_id, page_size=100):
    all_items = []
    start = 0

    while True:
        data = get_report_data(
            report_id=report_id,
            limit=page_size,
            start=start,
        )

        items = data.get("items", [])
        all_items.extend(items)

        if not data.get("next_page"):
            break

        start += page_size

    return all_items