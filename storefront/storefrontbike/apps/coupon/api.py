from django.http import JsonResponse

from .models import Coupon

def api_can_use(request):
    json_response = {}

    coupon_code_get = request.GET.get('coupon_code_get', '')
    print('Coupon get before fetching')

    try:
        coupon = Coupon.objects.get(coupon_code = coupon_code_get)

        if coupon.can_use():
            json_response = {'amount': coupon.coupon_value}
            print('Fetched')
        else:
            json_response = {'amount': 0}
    
    except Exception:
        json_response = {'amount': 0}

    return JsonResponse(json_response)