"""Shared test setup.

The handlers read configuration at import time, so the environment has to be
populated before they are imported. Every value here is fake; nothing in this
suite talks to AWS.
"""

import sys
from pathlib import Path

import pytest

LAMBDA_DIR = Path(__file__).resolve().parent.parent / "lambda"
sys.path.insert(0, str(LAMBDA_DIR))

FAKE_ENV = {
    "DATA_ACCOUNT_ROLE_ARN": "arn:aws:iam::111111111111:role/service-role/sdh-data-read",
    "DATA_ACCOUNT_ROLE_BLUE_ARN": "arn:aws:iam::111111111111:role/service-role/sdh-data-summary",
    "CLIENTS_TABLE_NAME": "ClientsBase",
    "CLIENTS_SUMMARY_TABLE_NAME": "ClientsSummary",
    "KMS_KEY_ALIAS": "alias/DemoKeyClientsBase",
    "AWS_REGION": "us-east-1",
}

TEMP_CREDENTIALS = {
    "AccessKeyId": "ASIAEXAMPLEACCESSKEY",
    "SecretAccessKey": "wJalrEXAMPLEKEY",
    "SessionToken": "FwoGEXAMPLESESSIONTOKEN",
}


@pytest.fixture(autouse=True)
def _env(monkeypatch):
    for key, value in FAKE_ENV.items():
        monkeypatch.setenv(key, value)


@pytest.fixture
def temp_credentials():
    return dict(TEMP_CREDENTIALS)


@pytest.fixture
def repo_root():
    return Path(__file__).resolve().parent.parent
