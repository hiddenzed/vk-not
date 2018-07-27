import json
import requests as r
import time

captchalink     = 'http://rucaptcha.com/'
rucaptcha_token = 'fb60bad56d50420c14c340a00adbe230'


def main(imglink):
	getimage(imglink)
	

	captchakey = getresult(sendcaptcha())

	return captchakey


def getimage(imagelink):
	im = r.get(imagelink)
	jpegimage = open('cp.jpg', 'wb')
	jpegimage.write(im.content)
	jpegimage.close()

def sendcaptcha():
	files         = {'file': open('cp.jpg', 'rb')}
	captha_params = {
		'key'    : rucaptcha_token,
		'method' : 'post',
		'json'   : 1
	} 

	cid = r.post(captchalink + 'in.php', files=files, params=captha_params).json()['request']
	time.sleep (7)
	return cid

def getresult(cid):
	getresultparams = {
		'key'    : rucaptcha_token,
		'action' : 'get',
		'json'   : 1,
		'id'     : cid
	}

	answer = 'CAPCHA_NOT_READY'

	while answer == 'CAPCHA_NOT_READY':

		time.sleep (1)
		answer = r.get(captchalink + 'res.php', params=getresultparams).json()['request']
	

	return answer

if __name__ == '__main__':
	main()