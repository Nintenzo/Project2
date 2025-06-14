import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from twocaptcha import TwoCaptcha

api_key = 'b8daffbe8e5b36e71f496f43ad9fc2a7'
solver = TwoCaptcha(api_key)

try:
    result = solver.funcaptcha(
        sitekey='2CB16598-CB82-4CF7-B332-5990DB66F3AB',
        url='https://iframe.arkoselabs.com',
        surl='https://client-api.arkoselabs.com',
        funcaptchaApiJSSubdomain='https://client-api.arkoselabs.com'
        )
    
except Exception as e:
    sys.exit(e)

else:
    sys.exit('result: ' + str(result))
