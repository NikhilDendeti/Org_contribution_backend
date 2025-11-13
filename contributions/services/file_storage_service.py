"""File storage service for handling uploaded files."""
import os
from pathlib import Path
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import hashlib


def save_uploaded_file(file) -> tuple[str, int, str]:
    """
    Save uploaded file to media directory.
    
    Returns:
        Tuple of (storage_path, file_size, checksum)
    """
    # Get filename from file object
    file_name = getattr(file, 'name', None)
    if not file_name:
        # Try to get from request if available
        file_name = 'uploaded_file.xlsx'
    
    # Generate unique filename
    filename = generate_unique_filename(file_name)
    
    # Create uploads directory if it doesn't exist
    upload_dir = Path(settings.MEDIA_ROOT) / 'uploads'
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Save file
    file_path = upload_dir / filename
    
    # Read file content
    file_content = b''
    if hasattr(file, 'read'):
        file.seek(0)  # Reset file pointer
        file_content = file.read()
        file.seek(0)  # Reset again for later use
    elif hasattr(file, 'chunks'):
        for chunk in file.chunks():
            file_content += chunk
    
    # Write to disk
    with open(file_path, 'wb') as f:
        f.write(file_content)
    
    # Calculate file size and checksum
    file_size = file_path.stat().st_size
    checksum = calculate_checksum(file_path)
    
    # Return relative path from MEDIA_ROOT
    relative_path = f"uploads/{filename}"
    
    return relative_path, file_size, checksum


def generate_unique_filename(original_name: str) -> str:
    """Generate unique filename with timestamp prefix."""
    from datetime import datetime
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    name, ext = os.path.splitext(original_name)
    return f"{timestamp}_{name}{ext}"


def calculate_checksum(file_path: Path) -> str:
    """Calculate MD5 checksum of file."""
    hash_md5 = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def get_file_path_by_id(raw_file_id: int) -> Path:
    """Get full file path for a raw file."""
    from contributions.storages import raw_file_storage
    raw_file = raw_file_storage.get_raw_file_by_id(raw_file_id)
    return Path(settings.MEDIA_ROOT) / raw_file.storage_path


def delete_file(file_path: str) -> bool:
    """Delete a file."""
    full_path = Path(settings.MEDIA_ROOT) / file_path
    if full_path.exists():
        full_path.unlink()
        return True
    return False

