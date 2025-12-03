"""  # pragma: no cover
ASGI config for backend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os  # pragma: no cover

from django.core.asgi import get_asgi_application  # pragma: no cover

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")  # pragma: no cover

application = get_asgi_application()  # pragma: no cover
