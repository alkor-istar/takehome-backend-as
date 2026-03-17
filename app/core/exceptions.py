from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from slowapi.errors import RateLimitExceeded


class NotFoundError(Exception):
    pass


def not_found_exception_handler(request: Request, exc: NotFoundError):
    return JSONResponse(status_code=404, content={"detail": str(exc)})


def internal_exception_handler(request: Request, exc: Exception):
    # log the exception here
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


def db_exception_handler(request: Request, exc: SQLAlchemyError):
    # log the exception here
    return JSONResponse(status_code=500, content={"detail": "Database error"})


# This custom exception handler is needed because by default FastAPI returns a 422 status code
# for validation errors. The requirements specify 400, still 422 is more specific.
def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content={
            "detail": "Invalid request parameters",
            "errors": exc.errors(),
        },
    )


# Rate limit exception handler
def rate_limit_exception_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={
            "detail": "Rate limit exceeded",
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(NotFoundError, not_found_exception_handler)
    app.add_exception_handler(Exception, internal_exception_handler)
    app.add_exception_handler(SQLAlchemyError, db_exception_handler)
    app.add_exception_handler(RateLimitExceeded, rate_limit_exception_handler)
