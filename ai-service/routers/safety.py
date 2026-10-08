# -*- coding: utf-8 -*-
"""安全拦截：POST /ai/safety-check"""
from fastapi import APIRouter
from pydantic import BaseModel

from services import safety as safety_service

router = APIRouter()


class SafetyReq(BaseModel):
    advice: str


class SafetyResp(BaseModel):
    safe: bool
    reason: str


@router.post("/ai/safety-check", response_model=SafetyResp)
def safety_check(req: SafetyReq):
    result = safety_service.check(req.advice)
    return {"safe": result["safe"], "reason": result["reason"]}
