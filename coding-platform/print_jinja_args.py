from fastapi.templating import Jinja2Templates
import inspect

print("Signature:", inspect.signature(Jinja2Templates.TemplateResponse))
