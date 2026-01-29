from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel


class CbrUsd(BaseModel):
    Value: Decimal


class CbrValute(BaseModel):
    USD: CbrUsd


class CbrDailyRates(BaseModel):
    Valute: CbrValute
