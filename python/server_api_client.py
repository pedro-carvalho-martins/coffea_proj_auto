"""Minimal HTTPS client for the Coffea Pag device API."""

import json
from urllib import error, parse, request


DEVICE_API_BASE_URL = "https://controle.coffeapag.com.br/device-api/v1"


class DeviceApiError(RuntimeError):
    pass


def _send(http_request, timeout):
    try:
        with request.urlopen(http_request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        details = exc.read().decode("utf-8", errors="replace")
        raise DeviceApiError(f"HTTP {exc.code}: {details}") from exc
    except (error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise DeviceApiError(str(exc)) from exc


def post_json(path, payload, token, timeout=10):
    body = json.dumps(payload).encode("utf-8")
    http_request = request.Request(
        f"{DEVICE_API_BASE_URL}{path}",
        data=body,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )

    return _send(http_request, timeout)


def get_json(path, query, token, timeout=10):
    query_string = parse.urlencode(query)
    http_request = request.Request(
        f"{DEVICE_API_BASE_URL}{path}?{query_string}",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        },
        method="GET",
    )
    return _send(http_request, timeout)
