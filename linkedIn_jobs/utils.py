import time
import random
import requests


def requests_with_retry(url, session, params=[], retries=3, backoff_factor=0.3):
    for attempt in range(retries):
        try:
            response = session.get(url, timeout=30, params=params)

            # Retry on rate limit
            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", 10))
                print(f"Rate limited. Retrying after {retry_after} seconds...")
                time.sleep(retry_after)
                continue

            # Retry on server errors
            if response.status_code >= 500:
                raise requests.RequestException(f"Server error: {response.status_code}")

            response.raise_for_status()
            return response

        except requests.RequestException as e:
            if attempt == retries - 1:
                raise e

            sleep_time = backoff_factor * (2 ** attempt)
            sleep_time += random.uniform(0, 0.5)  # jitter
            time.sleep(sleep_time)
