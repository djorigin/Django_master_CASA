"""
Utility functions for handling media uploads in the accounts app.
"""

import os
from datetime import datetime

from django.utils.text import slugify


def profile_photo_upload_path(instance, filename):
    """
    Generate upload path for profile photos.

    Returns path like: staff_ids/2025/10/user_firstname_lastname_timestamp.jpg
    """
    # Get the model name to determine folder
    model_name = instance.__class__.__name__.lower()
    if "staff" in model_name:
        folder = "staff_ids"
    elif "pilot" in model_name:
        folder = "pilot_ids"
    elif "client" in model_name:
        folder = "client_ids"
    else:
        folder = "profile_photos"

    # Get current year and month
    now = datetime.now()
    year = now.strftime("%Y")
    month = now.strftime("%m")

    # Get file extension
    ext = filename.split(".")[-1]

    # Create safe filename
    user_name = f"{instance.user.first_name}_{instance.user.last_name}"
    safe_name = slugify(user_name)
    timestamp = now.strftime("%Y%m%d_%H%M%S")

    new_filename = f"{safe_name}_{timestamp}.{ext}"

    return os.path.join(folder, year, month, new_filename)


def get_media_url(instance):
    """
    Get the full media URL for a profile photo.
    """
    if instance.photo_id:
        return instance.photo_id.url
    return None


def delete_old_photo(instance):
    """
    Delete old photo file when a new one is uploaded.
    """
    if instance.pk:
        try:
            old_instance = instance.__class__.objects.get(pk=instance.pk)
            if old_instance.photo_id and old_instance.photo_id != instance.photo_id:
                if os.path.isfile(old_instance.photo_id.path):
                    os.remove(old_instance.photo_id.path)
        except instance.__class__.DoesNotExist:
            pass
