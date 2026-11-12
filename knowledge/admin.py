from django.contrib import admin

from .models import Chunk, Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("title",)


@admin.register(Chunk)
class ChunkAdmin(admin.ModelAdmin):
    list_display = ("__str__", "document")
    search_fields = ("text",)