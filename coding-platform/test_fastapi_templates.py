from fastapi.templating import Jinja2Templates
from fastapi import Request
import asyncio

async def test():
    t = Jinja2Templates(directory="frontend/templates")
    req = Request(scope={"type": "http", "method": "GET", "headers": []})
    
    print("Testing Signature 1: t.TemplateResponse(req, 'index.html', {'request': req})")
    try:
        resp = t.TemplateResponse(req, "index.html", {"request": req})
        print("Signature 1 worked")
    except Exception as e:
        print("Signature 1 failed:", type(e), e)

    print("\nTesting Signature 3: t.TemplateResponse(request=req, name='index.html', context={'request': req})")
    try:
        resp = t.TemplateResponse(request=req, name="index.html", context={"request": req})
        print("Signature 3 worked")
    except Exception as e:
        print("Signature 3 failed:", type(e), e)

asyncio.run(test())
