from postonline import PochtaRuOnline

login, password = 'pmmos@rosan.ru', '!qUeen-PR'
token = "IQXgXpRloNnX2f36f0Jxy5FMBg9_Xx_7"
key = "cG1tb3NAcm9zYW4ucnU6IXFVZWVuLVBS"

attrs = {'id':'addr1', 'original-address':"107564,Москва г,,,,Миллионная ул,13,2,57"}

p = PochtaRuOnline(token, key) #, login, password
code, address = p.cleanAddress(attrs)

print(code)
print(address)
