"""File storage utilities for local and cloud storage."""
import os
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import current_app


def save_uploaded_files(files, allowed_file_func):
    """
    Save uploaded files to local storage or Google Cloud Storage.
    Returns comma-separated paths/URLs.
    """
    if not files:
        return None
    
    saved_paths = []
    use_gcs = current_app.config.get('USE_GCS', False)
    
    if use_gcs:
        # Use Google Cloud Storage
        saved_paths = _save_to_gcs(files, allowed_file_func)
    else:
        # Use local storage (for development)
        saved_paths = _save_to_local(files, allowed_file_func)
    
    return ','.join(saved_paths) if saved_paths else None


def _save_to_local(files, allowed_file_func):
    """Save files to local filesystem."""
    saved_paths = []
    upload_folder = current_app.config['UPLOAD_FOLDER']
    os.makedirs(upload_folder, exist_ok=True)
    
    for file in files:
        if file and allowed_file_func(file.filename):
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
            filename = timestamp + filename
            filepath = os.path.join(upload_folder, filename)
            file.save(filepath)
            saved_paths.append(f'/static/uploads/{filename}')
    
    return saved_paths


def _save_to_gcs(files, allowed_file_func):
    """Save files to Google Cloud Storage."""
    saved_paths = []
    bucket_name = current_app.config.get('GCS_BUCKET_NAME')
    project_id = current_app.config.get('GCS_PROJECT_ID')
    
    if not bucket_name:
        raise ValueError("GCS_BUCKET_NAME must be set when USE_GCS=true")
    
    try:
        # Initialize GCS client
        # Cloud Run automatically provides credentials via service account
        from google.cloud import storage
        client = storage.Client(project=project_id) if project_id else storage.Client()
        bucket = client.bucket(bucket_name)
        
        for file in files:
            if file and allowed_file_func(file.filename):
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
                filename = timestamp + filename
                
                # Upload to GCS
                blob = bucket.blob(f'uploads/{filename}')
                # Reset file pointer to beginning
                file.seek(0)
                blob.upload_from_file(file, content_type=file.content_type or 'image/jpeg')
                
                # Make blob publicly readable (or use signed URLs for private)
                blob.make_public()
                
                # Return public URL
                saved_paths.append(blob.public_url)
    except ImportError:
        current_app.logger.error("google-cloud-storage not installed. Falling back to local storage.")
        return _save_to_local(files, allowed_file_func)
    except Exception as e:
        current_app.logger.error(f"Error uploading to GCS: {e}")
        # Fallback to local storage on error
        return _save_to_local(files, allowed_file_func)
    
    return saved_paths


def delete_file_from_storage(file_path):
    """Delete a file from local or GCS storage."""
    use_gcs = current_app.config.get('USE_GCS', False)
    
    if use_gcs:
        _delete_from_gcs(file_path)
    else:
        _delete_from_local(file_path)


def _delete_from_local(file_path):
    """Delete file from local filesystem."""
    if file_path.startswith('/static/uploads/'):
        filename = os.path.basename(file_path)
        upload_folder = current_app.config['UPLOAD_FOLDER']
        filepath = os.path.join(upload_folder, filename)
        if os.path.exists(filepath):
            os.remove(filepath)


def _delete_from_gcs(file_path):
    """Delete file from Google Cloud Storage."""
    bucket_name = current_app.config.get('GCS_BUCKET_NAME')
    if not bucket_name:
        return
    
    try:
        from google.cloud import storage
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        
        # Extract blob name from URL
        if 'uploads/' in file_path:
            blob_name = file_path.split('uploads/')[-1]
            blob = bucket.blob(f'uploads/{blob_name}')
            blob.delete()
    except Exception as e:
        # Log error but don't fail
        current_app.logger.error(f"Error deleting file from GCS: {e}")

