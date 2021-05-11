from django.contrib import admin
from coin_spider import models


@admin.register(models.CoinTrick)
class CoinTrickAdmin(admin.ModelAdmin):

    list_per_page = 50
    list_filter = ('product_id','timestamp')
    list_display = ('product_id','last_qty','last','best_ask','best_ask_size','best_bid','best_bid_size','open_utc0','open_utc8','timestamp')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
