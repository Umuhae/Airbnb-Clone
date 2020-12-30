import random

from django.contrib.admin.utils import flatten
from django.core.management import BaseCommand
from django_seed import Seed
from lists.models import List
from rooms.models import Room
from users.models import User

class Command(BaseCommand):

    help = "This command create lists"

    def add_arguments(self, parser):
        parser.add_argument(
            "--number", type=int, default=2, help="How many lists you want to create"
        )

    def handle(self, *args, **options):
        number = options.get("number")
        seeder = Seed.seeder()
        all_rooms = Room.objects.all()
        all_users = User.objects.all()
        seeder.add_entity(
            List,
            number,
            {

                "user": lambda x: random.choice(all_users),
            },
        )
        create_list = seeder.execute()
        lists_pk = flatten(list(create_list.values()))
        for pk in lists_pk:
            list_model = List.objects.get(pk=pk)
            to_add = all_rooms[random.randint(0, 5): random.randint(6,30)]
            list_model.rooms.add(*to_add)

        self.stdout.write(self.style.SUCCESS("lists created!"))