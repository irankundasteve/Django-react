import json
import os
import re
import time
from collections import defaultdict, deque
from functools import wraps
from uuid import UUID

from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.http import HttpResponseNotAllowed, JsonResponse
from django.utils.html import strip_tags
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from .models import AboutPageContent, Category, ContactSubmission, PortfolioImage, Service

EMAIL_RE = re.compile(r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*"
                      r'|^"([!#-[\\]-~]|(\\[ -~]))+")@([A-Z0-9-]+\.)+[A-Z]{2,}$', re.IGNORECASE)

REQUEST_BUCKETS = defaultdict(deque)
ADMIN_TOKEN = os.getenv('NANOX_ADMIN_TOKEN', 'nanox-admin-token')
HTTPS_ONLY_URL_VALIDATOR = URLValidator(schemes=['https'])


def parse_json(request):
    try:
        return json.loads(request.body or '{}')
    except json.JSONDecodeError:
        raise ValidationError('Invalid JSON payload.')


def sanitize_text(value, max_len=None, required=False, field_name='field'):
    value = strip_tags((value or '').strip())
    if required and not value:
        raise ValidationError(f'{field_name} is required.')
    if max_len is not None and len(value) > max_len:
        raise ValidationError(f'{field_name} exceeds maximum length of {max_len}.')
    return value


def parse_uuid(value, field='id'):
    try:
        return UUID(str(value))
    except Exception as exc:  # noqa: BLE001
        raise ValidationError(f'Invalid {field}.') from exc


def get_client_ip(request):
    return (request.META.get('HTTP_X_FORWARDED_FOR') or request.META.get('REMOTE_ADDR') or 'unknown').split(',')[0].strip()


def rate_limited(limit_per_minute):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            ip = get_client_ip(request)
            bucket_key = f'{ip}:{view_func.__name__}'
            now = time.time()
            bucket = REQUEST_BUCKETS[bucket_key]
            while bucket and now - bucket[0] > 60:
                bucket.popleft()
            if len(bucket) >= limit_per_minute:
                return JsonResponse({'error': 'Rate limit exceeded.'}, status=429)
            bucket.append(now)
            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator


def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        token = request.headers.get('X-Admin-Token', '')
        if token != ADMIN_TOKEN:
            return JsonResponse({'error': 'Unauthorized.'}, status=401)
        return view_func(request, *args, **kwargs)

    return wrapper


def serialize_portfolio(item):
    return {
        'id': str(item.id),
        'title': item.title,
        'description': item.description,
        'category': item.category.name,
        'categoryId': str(item.category.id),
        'imageUrl': item.image_url,
        'isFeatured': item.is_featured,
        'createdAt': item.created_at.isoformat(),
        'updatedAt': item.updated_at.isoformat(),
    }


def serialize_category(item):
    return {
        'id': str(item.id),
        'name': item.name,
        'createdAt': item.created_at.isoformat(),
        'updatedAt': item.updated_at.isoformat(),
    }


def serialize_service(item):
    return {
        'id': str(item.id),
        'title': item.title,
        'description': item.description,
        'details': item.details,
        'pricing': item.pricing,
        'createdAt': item.created_at.isoformat(),
        'updatedAt': item.updated_at.isoformat(),
    }


def serialize_contact(item):
    return {
        'id': str(item.id),
        'name': item.name,
        'email': item.email,
        'phone': item.phone,
        'message': item.message,
        'submittedAt': item.submitted_at.isoformat(),
        'status': item.status,
    }


@require_GET
def site_content(_request):
    return JsonResponse(
        {
            'name': 'Nanox',
            'headline': 'Capturing Moments, Creating Stories',
            'contact': {
                'email': 'irankundasteve22@gmail.com',
                'phone': '+25767622353',
                'facebook': 'https://www.facebook.com/profile.php?id=61551810645067',
            },
        }
    )


@require_GET
def portfolio_images(request):
    category = (request.GET.get('category') or '').strip()
    queryset = PortfolioImage.objects.select_related('category').all().order_by('-created_at')
    if category:
        queryset = queryset.filter(category__name=category)
    return JsonResponse({'images': [serialize_portfolio(item) for item in queryset]})


@require_GET
def portfolio_image_detail(_request, image_id):
    image = PortfolioImage.objects.select_related('category').filter(id=parse_uuid(image_id)).first()
    if not image:
        return JsonResponse({'error': 'Image not found.'}, status=404)
    return JsonResponse(serialize_portfolio(image))


@require_GET
def about_content(_request):
    content = AboutPageContent.objects.first()
    if not content:
        return JsonResponse(
            {
                'headline': 'Capturing Moments, Creating Stories',
                'introParagraph': 'Nanox is the creative portfolio of Steve Irankunda, an artistic photographer passionate about capturing moments that speak to the heart.',
                'artisticVision': 'Photography is more than just a picture—it’s a feeling frozen in time.',
                'experienceCredentials': 'With over 5 years of experience in portrait, event, and artistic photography.',
                'ctaText': 'Book a Shoot',
                'ctaLink': 'https://nanox.example/contact',
            }
        )

    return JsonResponse(
        {
            'id': str(content.id),
            'headline': content.headline,
            'introParagraph': content.intro_paragraph,
            'artisticVision': content.artistic_vision,
            'experienceCredentials': content.experience_credentials,
            'ctaText': content.cta_text,
            'ctaLink': content.cta_link,
            'updatedAt': content.updated_at.isoformat(),
        }
    )


@require_GET
def services_list(_request):
    data = [serialize_service(item) for item in Service.objects.all().order_by('-created_at')]
    return JsonResponse({'services': data})


@require_GET
def privacy_policy(_request):
    return JsonResponse(
        {
            'Introduction': 'We respect your privacy. Any personal information collected on this website is used solely to respond to inquiries and provide services.',
            'Information Collection': 'We may collect your name, email address, and phone number through contact forms or newsletter sign-ups.',
            'Use of Information': 'Collected information is only used to contact you regarding your inquiries, bookings, or services.',
            'Data Protection': 'We take reasonable measures to protect your information from unauthorized access.',
            'Third-Party Services': 'Links to social media or third-party platforms may collect data independently.',
            'Cookies': 'This website may use cookies to enhance user experience. No personal data is sold or shared with third parties.',
        }
    )


@require_GET
def terms_of_service(_request):
    return JsonResponse(
        {
            'Scope of Services': 'Nanox provides artistic photography services as described on this website. All services are subject to availability and confirmation.',
            'Booking & Payment': 'Clients are responsible for confirming bookings and fulfilling any agreed payments.',
            'Intellectual Property': 'All photographs displayed on this website are the property of Nanox. Unauthorized use is prohibited.',
            'Liability': 'Nanox is not liable for any damages arising from the use of this website or its content.',
            'Governing Law': 'These terms are governed by the laws of your country of residence.',
        }
    )


@csrf_exempt
@require_POST
@rate_limited(10)
def contact_submit(request):
    try:
        payload = parse_json(request)
        name = sanitize_text(payload.get('name'), 100, required=True, field_name='name')
        email = sanitize_text(payload.get('email'), 254, required=True, field_name='email')
        phone = sanitize_text(payload.get('phone'), 20, required=False, field_name='phone')
        message = sanitize_text(payload.get('message'), 2000, required=True, field_name='message')
    except ValidationError as exc:
        return JsonResponse({'error': str(exc)}, status=400)

    if not EMAIL_RE.match(email):
        return JsonResponse({'error': 'Invalid email format.'}, status=400)

    submission = ContactSubmission.objects.create(name=name, email=email, phone=phone, message=message)
    return JsonResponse({'id': str(submission.id), 'message': 'Submission received'}, status=201)


@csrf_exempt
@admin_required
@rate_limited(10)
def admin_portfolio_collection(request):
    if request.method == 'POST':
        try:
            payload = parse_json(request)
            title = sanitize_text(payload.get('title'), 100, True, 'title')
            description = sanitize_text(payload.get('description'), 500, False, 'description')
            category_id = parse_uuid(payload.get('categoryId'), 'categoryId')
            image_url = sanitize_text(payload.get('imageUrl'), 2000, True, 'imageUrl')
            HTTPS_ONLY_URL_VALIDATOR(image_url)
            is_featured = bool(payload.get('isFeatured', False))
            category = Category.objects.filter(id=category_id).first()
            if not category:
                return JsonResponse({'error': 'Category not found.'}, status=404)
            image = PortfolioImage.objects.create(
                title=title,
                description=description,
                category=category,
                image_url=image_url,
                is_featured=is_featured,
            )
            return JsonResponse(serialize_portfolio(image), status=201)
        except ValidationError as exc:
            return JsonResponse({'error': str(exc)}, status=400)

    return HttpResponseNotAllowed(['POST'])


@csrf_exempt
@admin_required
@rate_limited(10)
def admin_portfolio_detail(request, image_id):
    image = PortfolioImage.objects.select_related('category').filter(id=parse_uuid(image_id)).first()
    if not image:
        return JsonResponse({'error': 'Image not found.'}, status=404)

    if request.method == 'DELETE':
        image.delete()
        return JsonResponse({'message': 'Deleted.'})

    if request.method == 'PUT':
        try:
            payload = parse_json(request)
            if 'title' in payload:
                image.title = sanitize_text(payload.get('title'), 100, True, 'title')
            if 'description' in payload:
                image.description = sanitize_text(payload.get('description'), 500, False, 'description')
            if 'imageUrl' in payload:
                image.image_url = sanitize_text(payload.get('imageUrl'), 2000, True, 'imageUrl')
                HTTPS_ONLY_URL_VALIDATOR(image.image_url)
            if 'isFeatured' in payload:
                image.is_featured = bool(payload.get('isFeatured'))
            if 'categoryId' in payload:
                category = Category.objects.filter(id=parse_uuid(payload.get('categoryId'), 'categoryId')).first()
                if not category:
                    return JsonResponse({'error': 'Category not found.'}, status=404)
                image.category = category
            image.save()
            return JsonResponse(serialize_portfolio(image))
        except ValidationError as exc:
            return JsonResponse({'error': str(exc)}, status=400)

    return HttpResponseNotAllowed(['PUT', 'DELETE'])


@csrf_exempt
@admin_required
@rate_limited(10)
def admin_categories_collection(request):
    if request.method == 'GET':
        categories = Category.objects.all().order_by('name')
        return JsonResponse({'categories': [serialize_category(item) for item in categories]})

    if request.method == 'POST':
        try:
            payload = parse_json(request)
            name = sanitize_text(payload.get('name'), 50, True, 'name')
            category = Category.objects.create(name=name)
            return JsonResponse(serialize_category(category), status=201)
        except ValidationError as exc:
            return JsonResponse({'error': str(exc)}, status=400)
        except Exception:  # noqa: BLE001
            return JsonResponse({'error': 'Category name must be unique.'}, status=400)

    return HttpResponseNotAllowed(['GET', 'POST'])


@csrf_exempt
@admin_required
@rate_limited(10)
def admin_category_detail(request, category_id):
    category = Category.objects.filter(id=parse_uuid(category_id, 'categoryId')).first()
    if not category:
        return JsonResponse({'error': 'Category not found.'}, status=404)

    if request.method == 'PUT':
        try:
            payload = parse_json(request)
            category.name = sanitize_text(payload.get('name'), 50, True, 'name')
            category.save()
            return JsonResponse(serialize_category(category))
        except ValidationError as exc:
            return JsonResponse({'error': str(exc)}, status=400)
        except Exception:  # noqa: BLE001
            return JsonResponse({'error': 'Category name must be unique.'}, status=400)

    if request.method == 'DELETE':
        if category.images.exists():
            return JsonResponse({'error': 'Cannot delete category with assigned images.'}, status=400)
        category.delete()
        return JsonResponse({'message': 'Deleted.'})

    return HttpResponseNotAllowed(['PUT', 'DELETE'])


@csrf_exempt
@admin_required
@rate_limited(5)
def admin_about(request):
    if request.method != 'PUT':
        return HttpResponseNotAllowed(['PUT'])

    try:
        payload = parse_json(request)
        headline = sanitize_text(payload.get('headline'), 150, True, 'headline')
        intro = sanitize_text(payload.get('introParagraph'), 1000, True, 'introParagraph')
        vision = sanitize_text(payload.get('artisticVision'), 2000, True, 'artisticVision')
        experience = sanitize_text(payload.get('experienceCredentials'), 2000, True, 'experienceCredentials')
        cta_text = sanitize_text(payload.get('ctaText'), 50, True, 'ctaText')
        cta_link = sanitize_text(payload.get('ctaLink'), 2000, True, 'ctaLink')
        URLValidator()(cta_link)

        content = AboutPageContent.objects.first()
        if not content:
            content = AboutPageContent.objects.create(
                headline=headline,
                intro_paragraph=intro,
                artistic_vision=vision,
                experience_credentials=experience,
                cta_text=cta_text,
                cta_link=cta_link,
            )
        else:
            content.headline = headline
            content.intro_paragraph = intro
            content.artistic_vision = vision
            content.experience_credentials = experience
            content.cta_text = cta_text
            content.cta_link = cta_link
            content.save()

        return JsonResponse({'message': 'About content updated.', 'id': str(content.id)})
    except ValidationError as exc:
        return JsonResponse({'error': str(exc)}, status=400)


@csrf_exempt
@admin_required
@rate_limited(10)
def admin_services_collection(request):
    if request.method == 'POST':
        try:
            payload = parse_json(request)
            title = sanitize_text(payload.get('title'), 100, True, 'title')
            description = sanitize_text(payload.get('description'), 500, True, 'description')
            details = sanitize_text(payload.get('details'), 2000, False, 'details')
            pricing = sanitize_text(payload.get('pricing'), 2000, False, 'pricing')
            service = Service.objects.create(title=title, description=description, details=details, pricing=pricing)
            return JsonResponse(serialize_service(service), status=201)
        except ValidationError as exc:
            return JsonResponse({'error': str(exc)}, status=400)

    return HttpResponseNotAllowed(['POST'])


@csrf_exempt
@admin_required
@rate_limited(10)
def admin_service_detail(request, service_id):
    service = Service.objects.filter(id=parse_uuid(service_id, 'serviceId')).first()
    if not service:
        return JsonResponse({'error': 'Service not found.'}, status=404)

    if request.method == 'DELETE':
        service.delete()
        return JsonResponse({'message': 'Deleted.'})

    if request.method == 'PUT':
        try:
            payload = parse_json(request)
            if 'title' in payload:
                service.title = sanitize_text(payload.get('title'), 100, True, 'title')
            if 'description' in payload:
                service.description = sanitize_text(payload.get('description'), 500, True, 'description')
            if 'details' in payload:
                service.details = sanitize_text(payload.get('details'), 2000, False, 'details')
            if 'pricing' in payload:
                service.pricing = sanitize_text(payload.get('pricing'), 2000, False, 'pricing')
            service.save()
            return JsonResponse(serialize_service(service))
        except ValidationError as exc:
            return JsonResponse({'error': str(exc)}, status=400)

    return HttpResponseNotAllowed(['PUT', 'DELETE'])


@csrf_exempt
@admin_required
@rate_limited(10)
def admin_contact_collection(request):
    if request.method != 'GET':
        return HttpResponseNotAllowed(['GET'])
    submissions = ContactSubmission.objects.all().order_by('-submitted_at')
    return JsonResponse({'submissions': [serialize_contact(item) for item in submissions]})


@csrf_exempt
@admin_required
@rate_limited(10)
def admin_contact_detail(request, submission_id):
    submission = ContactSubmission.objects.filter(id=parse_uuid(submission_id, 'submissionId')).first()
    if not submission:
        return JsonResponse({'error': 'Submission not found.'}, status=404)

    if request.method == 'DELETE':
        submission.delete()
        return JsonResponse({'message': 'Deleted.'})

    if request.method == 'PUT':
        try:
            payload = parse_json(request)
            status = sanitize_text(payload.get('status'), 20, True, 'status')
            if status not in {ContactSubmission.STATUS_NEW, ContactSubmission.STATUS_READ, ContactSubmission.STATUS_ARCHIVED}:
                return JsonResponse({'error': 'Invalid status.'}, status=400)
            submission.status = status
            submission.save()
            return JsonResponse(serialize_contact(submission))
        except ValidationError as exc:
            return JsonResponse({'error': str(exc)}, status=400)

    return HttpResponseNotAllowed(['PUT', 'DELETE'])
