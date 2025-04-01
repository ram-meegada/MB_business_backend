def fetch_serializer_error(serializer_errors: dict) -> str:
    data = dict(serializer_errors)
    key = list(data.keys())[0]
    return data[key][0]
