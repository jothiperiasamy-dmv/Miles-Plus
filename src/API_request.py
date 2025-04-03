import requests
import pandas as pd

def call_query_api(query):
    """
    Call a Cloud Run API with a query and return the result as a pandas DataFrame.

    Args:
        query (str): The query to send.
        api_url (str): The full Cloud Run API endpoint (e.g., https://your-api-url/run-query)

    Returns:
        pd.DataFrame: Response data as a DataFrame (or empty DataFrame on error).
    """
    try:
        print("API CALL STARTING..")
        api_url = "https://miles-webautomation-398219119144.us-east1.run.app/run-query"
        payload = {"query": query}
        headers = {"Content-Type": "application/json"}
        response = requests.post(api_url, json=payload, headers=headers)
        response.raise_for_status()
        print("API CALLED..")
        data = response.json()

        if data.get("status") == "success":
            df = pd.DataFrame(data["data"])
            print(f"✅ Success: {len(df)} rows received.")
            return df
        else:
            print(f"❌ API error: {data.get('message')}")
            return pd.DataFrame()

    except requests.exceptions.RequestException as e:
        print(f"💥 HTTP request failed: {e}")
        return pd.DataFrame()