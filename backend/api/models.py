import uuid

from django.core.validators import MaxLengthValidator, URLValidator
from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Category(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True)


class PortfolioImage(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=500, blank=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='images')
    image_url = models.URLField(validators=[URLValidator(schemes=['https'])])
    is_featured = models.BooleanField(default=False)


class AboutPageContent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    headline = models.CharField(max_length=150)
    intro_paragraph = models.TextField(validators=[MaxLengthValidator(1000)])
    artistic_vision = models.TextField(validators=[MaxLengthValidator(2000)])
    experience_credentials = models.TextField(validators=[MaxLengthValidator(2000)])
    cta_text = models.CharField(max_length=50)
    cta_link = models.URLField()
    updated_at = models.DateTimeField(auto_now=True)


class Service(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=500)
    details = models.TextField(blank=True, validators=[MaxLengthValidator(2000)])
    pricing = models.CharField(max_length=2000, blank=True)


class ContactSubmission(models.Model):
    STATUS_NEW = 'new'
    STATUS_READ = 'read'
    STATUS_ARCHIVED = 'archived'
    STATUS_CHOICES = [
        (STATUS_NEW, 'New'),
        (STATUS_READ, 'Read'),
        (STATUS_ARCHIVED, 'Archived'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    message = models.TextField(validators=[MaxLengthValidator(2000)])
    submitted_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_NEW)
