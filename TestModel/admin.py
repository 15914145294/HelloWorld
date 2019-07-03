from django.contrib import admin

from .models import Test, Contact, Tag


# Register your models here.

# Register your models here.
# Register your models here.
# Register your models here.
class TagInline(admin.TabularInline):
	model = Tag


class ContactAdmin(admin.ModelAdmin):
	search_fields = ('name',)
	list_display = ('name', 'age',"email")  # list
	inlines = [TagInline]
	fieldsets = (
		['The main fields', {
			'fields': ('name', 'email'),
		}],
		['Advance', {
			'classes': ('collapse',),  # CSS
			'fields': ('age',),
		}]
	)


admin.site.register(Contact, ContactAdmin)
admin.site.register([Test, Tag])
