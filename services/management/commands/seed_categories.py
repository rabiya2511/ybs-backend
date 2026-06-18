from django.core.management.base import BaseCommand
from services.models import ServiceCategory

class Command(BaseCommand):
    help = 'Seed service categories'

    def handle(self, *args, **kwargs):
        categories = [
            {"name": "Legal", "slug": "legal"},
            {"name": "Design", "slug": "design"},
            {"name": "Tech", "slug": "tech"},
            {"name": "Finance", "slug": "finance"},
            {"name": "Food & ISO", "slug": "food-iso"},
        ]
        for c in categories:
            obj, created = ServiceCategory.objects.get_or_create(
                name=c["name"],
                defaults={"slug": c["slug"], "icon": "x"}
            )
            if created:
                self.stdout.write(f"Added: {c['name']}")
            else:
                self.stdout.write(f"Already exists: {c['name']}")
        self.stdout.write("Done!")