"""Screening service for business logic and caching"""

import hashlib
import json
import time
from typing import Any, Dict

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import CacheManager
from app.repositories.screening_repository import ScreeningRepository
from app.schemas.screening import (ScreenedStock, ScreeningFilters,
                                   ScreeningMetadata, ScreeningRequest,
                                   ScreeningResponse, ScreeningTemplate,
                                   ScreeningTemplateList)


class ScreeningService:
    """Service for stock screening operations with caching"""

    # Cache TTL (seconds)
    SCREENING_TTL = 5 * 60  # 5 minutes
    TEMPLATES_TTL = 60 * 60  # 1 hour

    def __init__(self, session: AsyncSession, cache: CacheManager):
        """Initialize service with database session and cache"""
        self.session = session
        self.cache = cache
        self.screening_repo = ScreeningRepository(session)

    async def execute_screening(self, request: ScreeningRequest) -> ScreeningResponse:
        """
        Execute stock screening with filters and caching

        Args:
            request: ScreeningRequest with filters and pagination

        Returns:
            ScreeningResponse with matching stocks and metadata
        """
        # Record start time
        start_time = time.time()

        # Validate pagination
        page = max(1, request.page)
        per_page = min(200, max(1, request.per_page))
        offset = (page - 1) * per_page

        # Build cache key from filters hash
        cache_key = self._build_cache_key(request)

        # Check cache
        cached = await self.cache.get(cache_key)
        if cached:
            # Update query time
            cached["query_time_ms"] = (time.time() - start_time) * 1000
            return ScreeningResponse(**cached)

        # Execute screening query
        results, total = await self.screening_repo.screen_stocks(
            filters=request.filters,
            sort_by=request.sort_by,
            order=request.order,
            offset=offset,
            limit=per_page,
        )

        # Transform results to ScreenedStock objects
        stocks = [ScreenedStock(**row) for row in results]

        # Calculate metadata
        total_pages = (total + per_page - 1) // per_page if total > 0 else 0
        metadata = ScreeningMetadata(
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages,
        )

        # Build filters summary
        filters_applied = self._build_filters_summary(request.filters)

        # Calculate query time
        query_time_ms = (time.time() - start_time) * 1000

        # Create response
        response = ScreeningResponse(
            stocks=stocks,
            meta=metadata,
            query_time_ms=query_time_ms,
            filters_applied=filters_applied,
        )

        # Cache response
        await self.cache.set(
            cache_key,
            response.model_dump(),
            ttl=self.SCREENING_TTL,
        )

        return response

    async def get_templates(self) -> ScreeningTemplateList:
        """
        Get available screening templates

        Returns:
            ScreeningTemplateList with predefined templates
        """
        # Check cache
        cache_key = "screening:templates"
        cached = await self.cache.get(cache_key)
        if cached:
            return ScreeningTemplateList(**cached)

        # Get templates from repository
        templates_data = await self.screening_repo.get_screening_templates()

        # Transform to ScreeningTemplate objects
        templates = []
        for template_data in templates_data:
            # Convert filters dict to ScreeningFilters
            filters_dict = template_data["filters"]
            filters = ScreeningFilters(**filters_dict)

            template = ScreeningTemplate(
                id=template_data["id"],
                name=template_data["name"],
                description=template_data["description"],
                filters=filters,
                sort_by=template_data.get("sort_by", "overall_score"),
                order=template_data.get("order", "desc"),
            )
            templates.append(template)

        # Create response
        response = ScreeningTemplateList(templates=templates)

        # Cache response
        await self.cache.set(
            cache_key,
            response.model_dump(),
            ttl=self.TEMPLATES_TTL,
        )

        return response

    async def apply_template(
        self, template_id: str, page: int = 1, per_page: int = 50
    ) -> ScreeningResponse:
        """
        Apply a predefined screening template

        Args:
            template_id: Template ID to apply
            page: Page number
            per_page: Results per page

        Returns:
            ScreeningResponse with template results
        """
        # Get templates
        templates_list = await self.get_templates()

        # Find template by ID
        template = next(
            (t for t in templates_list.templates if t.id == template_id),
            None,
        )

        if not template:
            from app.core.exceptions import NotFoundException

            raise NotFoundException(f"Template not found: {template_id}")

        # Create screening request from template
        request = ScreeningRequest(
            filters=template.filters,
            sort_by=template.sort_by,
            order=template.order,
            page=page,
            per_page=per_page,
        )

        # Execute screening
        return await self.execute_screening(request)

    def _build_cache_key(self, request: ScreeningRequest) -> str:
        """
        Build cache key from request parameters

        Args:
            request: ScreeningRequest

        Returns:
            Cache key string
        """
        # Create a deterministic hash of filters
        filters_dict = request.filters.model_dump(exclude_none=True)
        filters_json = json.dumps(filters_dict, sort_keys=True)
        filters_hash = hashlib.md5(filters_json.encode()).hexdigest()

        # Build cache key
        cache_key = (
            f"screening:{filters_hash}:"
            f"{request.sort_by}:{request.order}:"
            f"{request.page}:{request.per_page}"
        )

        return cache_key

    def _build_filters_summary(self, filters: ScreeningFilters) -> Dict[str, Any]:
        """
        Build a summary of applied filters for response

        Args:
            filters: ScreeningFilters

        Returns:
            Dictionary of applied filters
        """
        summary = {}

        # Convert to dict and filter out None values
        filters_dict = filters.model_dump(exclude_none=True)

        # Count number of active filters
        active_count = 0
        for key, value in filters_dict.items():
            if value is not None:
                if key in ("market", "sector", "industry"):
                    summary[key] = value
                    if key == "market" and value != "ALL":
                        active_count += 1
                    elif key in ("sector", "industry"):
                        active_count += 1
                elif isinstance(value, dict):
                    # FilterRange
                    if value.get("min") is not None or value.get("max") is not None:
                        summary[key] = value
                        active_count += 1

        summary["_count"] = active_count

        return summary

    async def invalidate_screening_cache(self) -> None:
        """
        Invalidate all screening cache

        Should be called after daily indicator calculation completes
        """
        # In Redis, we would use KEYS screening:* and DEL
        # For now, we rely on TTL expiration
        # TODO: Implement cache invalidation by pattern
