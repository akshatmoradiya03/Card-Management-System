"""
Utility functions for the cards app.
"""
from django.core.exceptions import ValidationError
from decouple import config
import boto3
from botocore.exceptions import ClientError
from datetime import datetime
import os


ALLOWED_IMAGE_FORMATS = ['JPEG', 'JPG', 'PNG']
ALLOWED_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png']


def validate_image_format(image_file):
    """
    Validate that the uploaded image is in an allowed format.
    
    Args:
        image_file: The uploaded image file
        
    Raises:
        ValidationError: If the image format is not allowed
    """
    # Check file extension
    file_name = image_file.name.lower()
    file_extension = os.path.splitext(file_name)[1]
    
    if file_extension not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValidationError(
            f'Invalid image format. Allowed formats: {", ".join(ALLOWED_IMAGE_EXTENSIONS)}'
        )
    
    # Check file content type
    try:
        from PIL import Image
        image = Image.open(image_file)
        image_format = image.format
        
        if image_format not in ALLOWED_IMAGE_FORMATS:
            raise ValidationError(
                f'Invalid image format. Allowed formats: {", ".join(ALLOWED_IMAGE_FORMATS)}'
            )
    except Exception as e:
        raise ValidationError(f'Invalid image file: {str(e)}')


def upload_to_s3(image_file, card_id):
    """
    Upload image to Amazon S3 and return the public URL.
    
    Args:
        image_file: The image file to upload
        card_id: The ID of the card this image belongs to
        
    Returns:
        str: The public URL of the uploaded image
    """
    use_s3 = config('USE_S3', default=False, cast=bool)
    
    if not use_s3:
        # For development, save locally and return local URL
        from django.core.files.storage import default_storage
        from django.conf import settings
        
        # Generate unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_extension = os.path.splitext(image_file.name)[1]
        file_name = f'cards/{card_id}/{timestamp}{file_extension}'
        
        # Save file
        saved_path = default_storage.save(file_name, image_file)
        return f'{settings.MEDIA_URL}{saved_path}'
    
    # Upload to S3
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=config('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=config('AWS_SECRET_ACCESS_KEY'),
            region_name=config('AWS_S3_REGION_NAME', default='us-east-1')
        )
        
        bucket_name = config('AWS_STORAGE_BUCKET_NAME')
        
        # Generate unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_extension = os.path.splitext(image_file.name)[1]
        file_name = f'cards/{card_id}/{timestamp}{file_extension}'
        
        # Upload file
        s3_client.upload_fileobj(
            image_file,
            bucket_name,
            file_name,
            ExtraArgs={
                'ContentType': image_file.content_type,
                'ACL': 'public-read'
            }
        )
        
        # Generate public URL
        custom_domain = config('AWS_S3_CUSTOM_DOMAIN', default='')
        if custom_domain:
            image_url = f'https://{custom_domain}/{file_name}'
        else:
            image_url = f'https://{bucket_name}.s3.amazonaws.com/{file_name}'
        
        return image_url
        
    except ClientError as e:
        raise ValidationError(f'Failed to upload image to S3: {str(e)}')
    except Exception as e:
        raise ValidationError(f'Error uploading image: {str(e)}')


