"""Storage layer for RawFile entities."""
from contributions.models import RawFile
from .storage_dto import RawFileDTO
from ..exceptions import EntityNotFoundException, DuplicateUploadException


def get_raw_file_by_checksum(checksum: str) -> RawFileDTO:
    """Get raw file by checksum if exists."""
    try:
        raw_file = RawFile.objects.get(checksum=checksum)
        return RawFileDTO(
            id=raw_file.id,
            file_name=raw_file.file_name,
            uploaded_by_id=raw_file.uploaded_by_id,
            uploaded_at=raw_file.uploaded_at,
            storage_path=raw_file.storage_path,
            file_size=raw_file.file_size,
            checksum=raw_file.checksum,
            parse_summary=raw_file.parse_summary,
        )
    except RawFile.DoesNotExist:
        return None


def create_raw_file(
    file_name: str,
    storage_path: str,
    uploaded_by_id: int = None,
    file_size: int = 0,
    checksum: str = None,
    parse_summary: dict = None,
    check_duplicate: bool = True
) -> RawFileDTO:
    """
    Create a raw file record.
    
    Args:
        check_duplicate: If True, check for existing file with same checksum
    """
    # Check for duplicate if checksum provided
    if check_duplicate and checksum:
        existing = get_raw_file_by_checksum(checksum)
        if existing:
            raise DuplicateUploadException(
                f"File with same checksum already exists: {existing.file_name} (uploaded at {existing.uploaded_at})"
            )
    
    raw_file = RawFile.objects.create(
        file_name=file_name,
        storage_path=storage_path,
        uploaded_by_id=uploaded_by_id,
        file_size=file_size,
        checksum=checksum,
        parse_summary=parse_summary or {},
    )
    return RawFileDTO(
        id=raw_file.id,
        file_name=raw_file.file_name,
        uploaded_by_id=raw_file.uploaded_by_id,
        uploaded_at=raw_file.uploaded_at,
        storage_path=raw_file.storage_path,
        file_size=raw_file.file_size,
        checksum=raw_file.checksum,
        parse_summary=raw_file.parse_summary,
    )


def get_raw_file_by_id(raw_file_id: int) -> RawFileDTO:
    """Get raw file by ID."""
    try:
        raw_file = RawFile.objects.select_related('uploaded_by').get(id=raw_file_id)
        return RawFileDTO(
            id=raw_file.id,
            file_name=raw_file.file_name,
            uploaded_by_id=raw_file.uploaded_by_id,
            uploaded_at=raw_file.uploaded_at,
            storage_path=raw_file.storage_path,
            file_size=raw_file.file_size,
            checksum=raw_file.checksum,
            parse_summary=raw_file.parse_summary,
        )
    except RawFile.DoesNotExist:
        raise EntityNotFoundException(f"RawFile with id {raw_file_id} not found")


def update_raw_file_summary(raw_file_id: int, parse_summary: dict) -> RawFileDTO:
    """Update raw file parse summary."""
    try:
        raw_file = RawFile.objects.get(id=raw_file_id)
        raw_file.parse_summary = parse_summary
        raw_file.save()
        return RawFileDTO(
            id=raw_file.id,
            file_name=raw_file.file_name,
            uploaded_by_id=raw_file.uploaded_by_id,
            uploaded_at=raw_file.uploaded_at,
            storage_path=raw_file.storage_path,
            file_size=raw_file.file_size,
            checksum=raw_file.checksum,
            parse_summary=raw_file.parse_summary,
        )
    except RawFile.DoesNotExist:
        raise EntityNotFoundException(f"RawFile with id {raw_file_id} not found")

