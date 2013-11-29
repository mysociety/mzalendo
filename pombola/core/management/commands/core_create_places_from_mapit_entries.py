# This script will copy areas from mapit to core.places, including creating the
# place kind if required.


# import re
# import sys
from django.core.management.base import LabelCommand

from mapit.models import Type
from pombola.core.models import Place, PlaceKind
from django.template.defaultfilters import slugify

class Command(LabelCommand):
    help = 'Copy mapit.areas to core.places'
    args = '<mapit.type.code>'

    def handle_label(self,  mapit_type_code, **options):

        # load the mapit type
        mapit_type = Type.objects.get(code=mapit_type_code)

        # if needed create the core placetype
        placekind, created = PlaceKind.objects.get_or_create(
            name=mapit_type.description,
            defaults={
                'slug': slugify(mapit_type.description)
            }
        )

        # create all the places as needed for all mapit areas of that type
        for area in mapit_type.areas.all():

            # There may be a slug clash as several areas have the same name but
            # are different placekinds. Create the slug and then check to see
            # if the slug is already in use for a placekind other than ours. If
            # it is append the placekind to the slug.
            slug = slugify(area.name)

            if Place.objects.filter(slug=slug).exclude(kind=placekind).exists():
                slug = slug + '-' + placekind.slug

            print "'%s' (%s)" % (area.name, slug)
            place, created = Place.objects.get_or_create(
                name=area.name,
                kind=placekind,
                defaults={
                    'slug': slug,
                }
            )

            place.mapit_area = area
            place.save()
