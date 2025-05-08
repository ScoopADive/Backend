from django.contrib import admin
from .models import Log, Equipment, DiveCenter

@admin.register(Log)
class LogAdmin(admin.ModelAdmin):
    list_display = (
        'dive_title', 'dive_site', 'dive_date', 'buddy',
        'max_depth', 'bottom_time', 'start_pressure', 'end_pressure'
    )
    list_filter = (
        'dive_date', 'weather', 'type_of_dive', 'dive_center',
    )
    search_fields = (
        'dive_title', 'dive_site', 'buddy', 'feeling',
    )
    filter_horizontal = ('equipment',)  # ManyToManyField 용
    readonly_fields = ('bottom_time',)  # 선택적으로 읽기 전용 처리

    fieldsets = (
        ('기본 정보', {
            'fields': ('dive_title', 'dive_site', 'dive_date', 'buddy', 'feeling', 'dive_image')
        }),
        ('다이브 상세', {
            'fields': ('max_depth', 'bottom_time', 'start_pressure', 'end_pressure', 'weight')
        }),
        ('환경 및 장비', {
            'fields': ('weather', 'type_of_dive', 'equipment', 'dive_center')
        }),
    )

    def formatted_bottom_time(self, obj):
        if obj.bottom_time:
            minutes = obj.bottom_time.total_seconds() // 60
            return f"{int(minutes)} min"
        return "-"


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(DiveCenter)
class DiveCenterAdmin(admin.ModelAdmin):
    list_display = ('name',)
