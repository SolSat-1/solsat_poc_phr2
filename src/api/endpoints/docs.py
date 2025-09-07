"""
Documentation endpoints
"""

from fastapi import APIRouter
from fastapi.responses import Response
import yaml

router = APIRouter(tags=["Documentation"])


@router.get("/openapi.yaml", response_class=Response)
async def get_openapi_yaml():
    """
    Get OpenAPI documentation in YAML format

    This endpoint returns the complete API documentation in YAML format,
    which can be imported into tools like Postman, Insomnia, or used
    for code generation with tools like OpenAPI Generator.
    """
    from src.api.main import app

    openapi_json = app.openapi()
    yaml_str = yaml.dump(openapi_json, default_flow_style=False, sort_keys=False)

    return Response(content=yaml_str, media_type="text/plain; charset=utf-8")
