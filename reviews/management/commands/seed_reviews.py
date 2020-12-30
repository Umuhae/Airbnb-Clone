import random

from django.contrib.admin.utils import flatten
from django.core.management import BaseCommand
from django_seed import Seed
from reviews.models import Review
from reviews.models import Review
from users.models import User
from rooms.models import Room

class Command(BaseCommand):

    help = "This command tells me that he loves me"

    def add_arguments(self, parser):
        parser.add_argument(
            "--number", type=int, default=2, help="How many users you want to create"
        )

    def handle(self, *args, **options):
        number = options.get("number")
        seeder = Seed.seeder()
        all_rooms = Room.objects.all()
        all_users = User.objects.all()
        seeder.add_entity(
            Review,
            number,
            {
                "accuracy": lambda x: random.randint(0, 6),
                "communication": lambda x: random.randint(0, 6),
                "cleanliness": lambda x: random.randint(0, 6),
                "location": lambda x: random.randint(0, 6),
                "check_in": lambda x: random.randint(0, 6),
                "value": lambda x: random.randint(0, 6),
                "room": lambda x: random.choice(all_rooms),
                "user": lambda x: random.choice(all_users),
            },
        )
        seeder.execute()

        self.stdout.write(self.style.SUCCESS("reviews created!"))