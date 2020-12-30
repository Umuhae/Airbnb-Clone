import random
from datetime import datetime, timedelta
from django.utils import timezone
from django.core.management import BaseCommand
from django_seed import Seed
from rooms.models import Room
from reservations.models import Reservation
from users.models import User

class Command(BaseCommand):

    help = "This command create reservations"

    def add_arguments(self, parser):
        parser.add_argument(
            "--number", type=int, default=2, help="How many reservations you want to create"
        )

    def handle(self, *args, **options):
        number = options.get("number")
        seeder = Seed.seeder()
        all_rooms = Room.objects.all()
        all_users = User.objects.all()
        seeder.add_entity(
            Reservation,
            number,
            {
                "guest": lambda x: random.choice(all_users),
                "room": lambda x: random.choice(all_rooms),
                "check_in": lambda x: timezone.now().date(),
                "check_out": lambda x: datetime.now()
                                       + timedelta(days=random.randint(3, 25)),
            },
        )
        seeder.execute()
        self.stdout.write(self.style.SUCCESS(str(number)+" reservations created!"))