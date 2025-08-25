import logging
from uuid import UUID
from typing import Annotated, List, Optional, Union, Dict
from fastapi import APIRouter, Depends, HTTPException
from items_app.api.providers import get_company_repo
from items_app.api.schemas import (
    CompanyCreate,
    CompanyResponse,
    CompanyUpdate,
    CompanyUpdateResponse,
)
from items_app.application.application import CompanyApplications
from items_app.application.application_exceptions import CompanyNotFound
from items_app.infrastructure.models import Company
from items_app.infrastructure.repository import CompanyRepo


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/companies", tags=["Companies"])


@router.post("", summary="Создание компании")
async def create_new_company(
    new_company_schema: CompanyCreate,
    company_repo: Annotated[CompanyRepo, Depends(get_company_repo)],
):
    try:
        new_company_data = Company(name=new_company_schema.name)
        new_company = await CompanyApplications.create_company(
            new_company_data, company_repo
        )
        company_response = CompanyResponse.model_validate(new_company)
        return {
            "message": "New company created successfully",
            "company": company_response,
        }
    except Exception as e:
        logger.error(f"Unexpected error: {type(e).__name__} - {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create company")


@router.get(
    "/{company_id}", summary="Вывод компании по ID", response_model=CompanyResponse
)
async def get_company_by_id(
    company_id: UUID,
    company_repo: Annotated[CompanyRepo, Depends(get_company_repo)],
):
    try:
        company = await CompanyApplications.fetch_company_by_id(
            company_id, company_repo
        )
        if not company:
            raise CompanyNotFound(f"Company with company_id={company_id} not found")
        company_response = CompanyResponse.model_validate(company)
        return company_response
    except CompanyNotFound as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch company")


@router.get(
    "", summary="Вывод всех компаний", response_model=Union[List[CompanyResponse], Dict]
)
async def get_all_companies(
    company_repo: Annotated[CompanyRepo, Depends(get_company_repo)],
    offset: Optional[int] = 0,
    limit: Optional[int] = 10,
):
    try:
        companies = await CompanyApplications.fetch_all_companies(
            offset, limit, company_repo
        )
        if companies:
            company_response = [
                CompanyResponse.model_validate(company) for company in companies
            ]
            return company_response
        else:
            return {"message": "No companies in database"}
    except Exception as e:
        logger.error(f"Unexpected error: {type(e).__name__} - {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch companies")


@router.put(
    "/{company_id}",
    summary="Обновление компании по ID",
    response_model=CompanyUpdateResponse,
)
async def update_company_by_id(
    update_data: CompanyUpdate,
    company_repo: Annotated[CompanyRepo, Depends(get_company_repo)],
):
    try:
        update_company_data = Company(id=update_data.id, name=update_data.name)
        updated_company = await CompanyApplications.update_company_data(
            update_company_data, company_repo
        )
        if not updated_company:
            raise CompanyNotFound(f"Company with company_id={update_data.id} not found")
        company_response = CompanyResponse.model_validate(updated_company)
        return {"message": "Company updated successfully", "company": company_response}
    except CompanyNotFound as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Failed to update company")


@router.delete("/{company_id}", summary="Удаление компании по ID")
async def delete_company_by_id(
    company_id: UUID,
    company_repo: Annotated[CompanyRepo, Depends(get_company_repo)],
):
    try:
        result = await CompanyApplications.delete_company(company_id, company_repo)
        if result is None:
            raise CompanyNotFound(f"Company with company_id={company_id} not found")
        elif result is False:
            raise HTTPException(status_code=500, detail="Failed to delete company")
        else:
            return {"message": "Company and its items deleted successfully"}
    except CompanyNotFound as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete company")
