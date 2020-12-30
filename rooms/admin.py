from django.contrib import admin
from django.utils.html import mark_safe
from . import models


@admin.register(models.RoomType, models.Amenity, models.Facility, models.HouseRule)
class ItemAdmin(admin.ModelAdmin):
    """ Item Admin Definition """

    list_display = ("name", "used_by")

    def used_by(self, obj):
        return obj.rooms.count()

class Photoinline(admin.TabularInline):
    model = models.Photo

@admin.register(models.Room)
class RoomAdmin(admin.ModelAdmin):
    """ RoomAdmin Admin Definition """
    inlines = (Photoinline,)

    fieldsets = (
        (
            "Basic Info",
            {"fields": ("name", "description", "country", "address", "city","price")},
        ),
        ("Times", {"fields": ("check_in", "check_out", "instant_book")}),
        ("Spaces", {"fields": ("guests", "beds", "bedrooms", "baths")}),
        (
            "More About the Space",
            {
                "classes": ("collapse",),
                "fields": ("amenities", "facilities", "house_rules"),
            },
        ),
        ("Last Details", {"fields": ("host",)}),
    )

    list_display = (
        "name",
        "description",
        "country",
        "city",
        "price",
        "guests",
        "beds",
        "bedrooms",
        "baths",
        "check_in",
        "check_out",
        "instant_book",
        "count_amenities",
        "count_photos",
        "total_rating",
    )

    list_filter = (
        "instant_book",
        "room_type",
        "amenities",
        "facilities",
        "house_rules",
        "city",
        "country",
    )
    search_fields = ("name", "city" , "^host__username")

    filter_horizontal = ("amenities",
        "facilities",
        "house_rules",)

    ordering = ('name', 'price')

    def count_amenities(self, obj):
        return obj.amenities.count()

    def count_photos(self, obj):
        return obj.photos.count()

    count_photos.short_description = 'Photo Count'

@admin.register(models.Photo)
class PhotoAdmin(admin.ModelAdmin):
    """ PhotoAdmin Admin Definition """

    list_display = ("__str__", 'get_thumbnail')

    def get_thumbnail(self, obj):
        print(dir(obj.file))
        return mark_safe(f'<img width="50px" src="{obj.file.url}" />')

    get_thumbnail.short_description = "thumbnail"

