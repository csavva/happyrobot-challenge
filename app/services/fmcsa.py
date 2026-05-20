import re
from typing import Any

import httpx

from app.config import settings
from app.schemas.fmcsa import FMCSAValidateResponse

FMCSA_BASE_URL = "https://mobile.fmcsa.dot.gov/qc/services"
MC_NUMBER_PATTERN = re.compile(r"^\d{1,8}$")


class FMCSAError(Exception):
    def __init__(self, message: str, status_code: int = 502) -> None:
        super().__init__(message)
        self.status_code = status_code


def normalize_mc_number(raw: str) -> str:
    cleaned = raw.strip().upper()
    cleaned = re.sub(r"^MC[-\s]*", "", cleaned)
    digits = re.sub(r"\D", "", cleaned)
    return digits


def _yn_to_bool(value: Any) -> bool | None:
    if value is None:
        return None
    if isinstance(value, str):
        normalized = value.strip().upper()
        if normalized in ("Y", "YES", "TRUE"):
            return True
        if normalized in ("N", "NO", "FALSE"):
            return False
        return None
    return bool(value)


def _extract_carrier(payload: dict[str, Any]) -> dict[str, Any] | None:
    content = payload.get("content")
    if isinstance(content, dict):
        carrier = content.get("carrier")
        if isinstance(carrier, dict):
            return carrier
        if any(key in content for key in ("legalName", "legal_name", "dotNumber", "dot_number")):
            return content
    if isinstance(content, list) and content:
        first = content[0]
        if isinstance(first, dict):
            carrier = first.get("carrier", first)
            if isinstance(carrier, dict):
                return carrier
    carrier = payload.get("carrier")
    if isinstance(carrier, dict):
        return carrier
    return None


def _carrier_display_name(carrier: dict[str, Any]) -> str | None:
    legal_name = carrier.get("legalName") or carrier.get("legal_name")
    dba_name = carrier.get("dbaName") or carrier.get("dba_name")
    if legal_name:
        return str(legal_name)
    if dba_name:
        return str(dba_name)
    return None


def _build_eligibility(carrier: dict[str, Any], mc_number: str) -> FMCSAValidateResponse:
    allow_to_operate = _yn_to_bool(carrier.get("allowedToOperate") or carrier.get("allowed_to_operate"))
    out_of_service = _yn_to_bool(carrier.get("outOfService") or carrier.get("out_of_service"))

    legal_name = carrier.get("legalName") or carrier.get("legal_name")
    dba_name = carrier.get("dbaName") or carrier.get("dba_name")
    dot_raw = carrier.get("dotNumber") or carrier.get("dot_number")
    dot_number = int(dot_raw) if dot_raw is not None else None

    reason: str | None = None
    eligible = True

    if allow_to_operate is False:
        eligible = False
        reason = "Carrier is not authorized to operate."
    elif out_of_service is True:
        eligible = False
        reason = "Carrier has an out-of-service order."
    elif allow_to_operate is None and out_of_service is None:
        eligible = False
        reason = "Unable to determine carrier operating status from FMCSA."

    return FMCSAValidateResponse(
        eligible=eligible,
        mc_number=mc_number,
        legal_name=str(legal_name) if legal_name else None,
        dba_name=str(dba_name) if dba_name else None,
        dot_number=dot_number,
        allow_to_operate=allow_to_operate,
        out_of_service=out_of_service,
        reason=reason,
    )


def validate_mc_number(raw_mc_number: str) -> FMCSAValidateResponse:
    mc_number = normalize_mc_number(raw_mc_number)
    if not mc_number or not MC_NUMBER_PATTERN.match(mc_number):
        raise ValueError("mc_number must contain 1–8 digits (optional MC prefix is accepted).")

    if not settings.fmcsa_web_key:
        raise FMCSAError(
            "FMCSA_WEB_KEY is not configured. Register at https://mobile.fmcsa.dot.gov/QCDevsite/",
            status_code=503,
        )

    url = f"{FMCSA_BASE_URL}/carriers/docket-number/{mc_number}"
    try:
        with httpx.Client(timeout=15.0) as client:
            response = client.get(url, params={"webKey": settings.fmcsa_web_key})
    except httpx.RequestError as exc:
        raise FMCSAError(f"FMCSA API request failed: {exc}") from exc

    if response.status_code == 404:
        return FMCSAValidateResponse(
            eligible=False,
            mc_number=mc_number,
            reason="No carrier found for this MC number.",
        )
    if response.status_code == 401:
        raise FMCSAError("FMCSA API rejected the web key (unauthorized).", status_code=502)
    if response.status_code >= 400:
        raise FMCSAError(
            f"FMCSA API returned status {response.status_code}.",
            status_code=502,
        )

    try:
        payload = response.json()
    except ValueError as exc:
        raise FMCSAError("FMCSA API returned invalid JSON.") from exc

    carrier = _extract_carrier(payload)
    if not carrier:
        return FMCSAValidateResponse(
            eligible=False,
            mc_number=mc_number,
            reason="No carrier found for this MC number.",
        )

    if not _carrier_display_name(carrier):
        return FMCSAValidateResponse(
            eligible=False,
            mc_number=mc_number,
            reason="Carrier record found but missing a legal or DBA name.",
        )

    return _build_eligibility(carrier, mc_number)
