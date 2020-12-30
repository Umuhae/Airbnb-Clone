import random

from django.contrib.admin.utils import flatten
from django.core.management import BaseCommand
from rooms.models import Amenity
from django_seed import Seed
from rooms.models import Room, RoomType, Photo, Amenity, Facility, HouseRule
from users.models import User

class Command(BaseCommand):

    help = "This command tells me that he loves me"

    def add_arguments(self, parser):
        parser.add_argument(
            "--number", type=int, default=2, help="How many rooms you want to create"
        )

    def handle(self, *args, **options):
        number = options.get("number")
        seeder = Seed.seeder()
        all_users = User.objects.all()
        roomtypes = RoomType.objects.all()
        seeder.add_entity(Room, number, {
            'name': lambda x: seeder.faker.address(),
            'host': lambda x: random.choice(all_users),
            'room_type': lambda x: random.choice(roomtypes),
            "guests": lambda x: random.randint(1,20),
            "price": lambda x: random.randint(100,3000)*100,
            "beds": lambda x: random.randint(1,10),
            "bedrooms": lambda x: random.randint(1,5),
            "baths": lambda x: random.randint(1,5),
        })
        create_rooms = seeder.execute()
        rooms_pk = flatten(list(create_rooms.values()))
        amenities = Amenity.objects.all()
        facilities = Facility.objects.all()
        rules = HouseRule.objects.all()
        for pk in rooms_pk:
            roompk = Room.objects.get(pk=pk)
            for i in range(random.randint(7,47)):
                Photo.objects.create(
                    caption=seeder.faker.sentence(),
                    room=roompk,
                    file=f"room_photos/{random.randint(1,31)}.webp"
                )
            for a in amenities:
                magic_number = random.randint(0,15)
                if magic_number % 2 == 0:
                    roompk.amenities.add(a)
            for f in facilities:
                magic_number = random.randint(0,15)
                if magic_number % 2 == 0:
                    roompk.facilities.add(f)
            for r in rules:
                magic_number = random.randint(0,15)
                if magic_number % 2 == 0:
                    roompk.house_rules.add(r)

        self.stdout.write(self.style.SUCCESS("Rooms created!"))