from django.urls import path

from api.views import (
    about_content,
    admin_about,
    admin_categories_collection,
    admin_category_detail,
    admin_contact_collection,
    admin_contact_detail,
    admin_portfolio_collection,
    admin_portfolio_detail,
    admin_service_detail,
    admin_services_collection,
    contact_submit,
    portfolio_image_detail,
    portfolio_images,
    privacy_policy,
    services_list,
    site_content,
    terms_of_service,
)

urlpatterns = [
    path('api/site-content/', site_content, name='site-content'),
    path('api/portfolio/', portfolio_images, name='portfolio'),
    path('api/portfolio/<uuid:image_id>/', portfolio_image_detail, name='portfolio-detail'),
    path('api/about/', about_content, name='about-content'),
    path('api/services/', services_list, name='services'),
    path('api/contact/', contact_submit, name='contact-submit'),
    path('api/privacy-policy/', privacy_policy, name='privacy-policy'),
    path('api/terms-of-service/', terms_of_service, name='terms-of-service'),

    path('api/admin/portfolio/', admin_portfolio_collection, name='admin-portfolio-collection'),
    path('api/admin/portfolio/<uuid:image_id>/', admin_portfolio_detail, name='admin-portfolio-detail'),
    path('api/admin/categories/', admin_categories_collection, name='admin-categories-collection'),
    path('api/admin/categories/<uuid:category_id>/', admin_category_detail, name='admin-category-detail'),
    path('api/admin/about/', admin_about, name='admin-about'),
    path('api/admin/services/', admin_services_collection, name='admin-services-collection'),
    path('api/admin/services/<uuid:service_id>/', admin_service_detail, name='admin-service-detail'),
    path('api/admin/contact/', admin_contact_collection, name='admin-contact-collection'),
    path('api/admin/contact/<uuid:submission_id>/', admin_contact_detail, name='admin-contact-detail'),
]
