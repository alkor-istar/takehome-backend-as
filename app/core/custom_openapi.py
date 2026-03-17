from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi


# This is a workaround to document validation errors as 400 to match our exception handler.
# While probably at this point it should be considered to just use port 422 as FastAPI
# devs intended, I'm leaving this workaround to demostrate how can the documentation be
# customized programmatically.
def get_custom_openapi(app: FastAPI):
    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema
        openapi_schema = get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            routes=app.routes,
        )
        for path_item in openapi_schema.get("paths", {}).values():
            for method in ("get", "post", "put", "patch", "delete", "head", "options"):
                op = path_item.get(method)
                if isinstance(op, dict):
                    responses = op.get("responses", {})
                    if "422" in responses:
                        responses["400"] = responses.pop("422")
                        responses["400"]["description"] = "Invalid request parameters"
        app.openapi_schema = openapi_schema
        return app.openapi_schema

    return custom_openapi
