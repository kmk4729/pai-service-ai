from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

from application.port.inbound.vqa_use_case import VQAUseCase
from application.port.outbound.llm_port import LLMPort
from application.port.outbound.language_detection_port import LanguageDetectionPort
from domain.model.vqa_model import VQARequest, VQAResponse
from domain.util.text_utils import extract_keywords_from_text
from adapter.inbound.web.dependencies import get_vqa_service, get_llm_adapter, get_language_detection_adapter


class VQARequestDTO(BaseModel):
    media_id: Optional[str] = None
    question: str
    child_name: Optional[str] = None


vqa_router = APIRouter()


@vqa_router.post("/", response_class=JSONResponse)
async def handle_vqa(
    request_dto: VQARequestDTO,
    vqa_service: VQAUseCase = Depends(get_vqa_service),
    llm_port: LLMPort = Depends(get_llm_adapter),
    language_detection_port: LanguageDetectionPort = Depends(get_language_detection_adapter)
):
    """
    이미지(media) 없으면 LLM 직접 질의, 있으면 VQA → LLM 설명 생성
    """
    # Extract keywords from question
    keywords = extract_keywords_from_text(request_dto.question)
    lang = language_detection_port.detect_language(request_dto.question)

    # If no media_id, use simple LLM response
    if not request_dto.media_id:
        answer = await llm_port.ask_simple(request_dto.question, request_dto.child_name or "아이", lang)
        return JSONResponse(content={
            "answer": answer,
            "keywords": keywords
        })

    # If media_id provided, use VQA service
    try:
        request = VQARequest(
            image_url=request_dto.media_id,
            question=request_dto.question,
            child_name=request_dto.child_name
        )
        response: VQAResponse = await vqa_service.handle_vqa(request)

        # Return simplified response with answer and keywords
        return JSONResponse(content={
            "answer": response.answer,
            "keywords": response.keywords
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"VQA 처리 중 오류: {str(e)}")
