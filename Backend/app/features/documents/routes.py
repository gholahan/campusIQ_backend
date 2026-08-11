import uuid
from fastapi import APIRouter, Depends, status

from app.db.session import SessionDep
from app.features.auth.dependencies import require_student
from app.features.users.models import User
from app.features.documents.schemas import (
    DocumentResponse,
    UploadDocumentRequest,
)
from app.features.documents.service import (
    create_document,
    get_document_by_id,
    get_user_documents,
    delete_document,
)
from app.features.ai.rag.task import upload_document


router = APIRouter(
    prefix="/documents",
    tags=["DOCUMENT"],
)


@router.get(
    "/",
    response_model=list[DocumentResponse],
)
async def get_user_documents_route(
    session: SessionDep,
    current_user: User = Depends(require_student),
) -> list[DocumentResponse]:

    documents = await get_user_documents(
        db=session,
        user_id=current_user.id,
    )

    return [
        DocumentResponse.model_validate(document)
        for document in documents
    ]


@router.post(
    "/",
    response_model=DocumentResponse,
)
async def upload_document_route(
    body: UploadDocumentRequest,
    session: SessionDep,
    current_user: User = Depends(require_student),
) -> DocumentResponse:

    document = await create_document(
        db=session,
        user_id=current_user.id,
        body=body,
    )

    upload_document.delay(
        document_id=str(document.id),
        file_url=document.file_url,
    )

    return DocumentResponse.model_validate(document)


@router.get(
    "/{document_id}",
    response_model=DocumentResponse,
)
async def get_document_route(
    document_id: uuid.UUID,
    session: SessionDep,
    current_user: User = Depends(require_student),
) -> DocumentResponse:

    document = await get_document_by_id(
        db=session,
        document_id=document_id,
    )

    return DocumentResponse.model_validate(document)


@router.delete(
    "/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_document_route(
    document_id: uuid.UUID,
    session: SessionDep,
    current_user: User = Depends(require_student),
) -> None:

    await delete_document(
        db=session,
        document_id=document_id,
        user_id=current_user.id,
    )