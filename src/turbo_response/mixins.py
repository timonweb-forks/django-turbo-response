# Standard Library
import http
from typing import Any, Dict, Iterable, Optional, Union

# Django
from django import forms
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpRequest, HttpResponse
from django.template.engine import Engine

# Third Party Libraries
from typing_extensions import Protocol

# Local
from .renderers import Action
from .response import (
    TurboFrameResponse,
    TurboFrameTemplateResponse,
    TurboStreamResponse,
    TurboStreamTemplateResponse,
)


class SupportsRequest(Protocol):
    request: HttpRequest


class SupportsTemplateEngine(Protocol):
    template_engine: Engine


class SupportsTemplateNames(Protocol):
    def get_template_names(self) -> Iterable[str]:
        ...


class SupportsFormInvalid(Protocol):
    def form_invalid(self, form: forms.Form) -> HttpResponse:
        ...


class TurboStreamResponseMixin:
    """Mixin to handle turbo-stream responses"""

    turbo_stream_action: Optional[Action] = None
    turbo_stream_target: Optional[str] = None

    def get_turbo_stream_action(self) -> Optional[Action]:
        """Returns the turbo-stream action parameter

        :return: turbo-stream action
        :rtype: turbo_response.Action
        """
        return self.turbo_stream_action

    def get_turbo_stream_target(self) -> Optional[str]:
        """Returns the turbo-stream target parameter

        :return: turbo-stream target
        :rtype: str
        """
        return self.turbo_stream_target

    def get_response_content(self) -> Union[bytes, str]:
        """Returns turbo-stream content.

        :rtype: str
        """

        return ""

    def render_turbo_stream_response(self, **response_kwargs) -> TurboStreamResponse:
        """Returns a turbo-stream response.

        :rtype: turbo_response.TurboStreamResponse
        """

        action = self.get_turbo_stream_action()
        target = self.get_turbo_stream_target()

        if action is None:
            raise ValueError("action must be specified")

        if target is None:
            raise ValueError("target must be specified")

        return TurboStreamResponse(
            action=action,
            target=target,
            content=self.get_response_content(),
            **response_kwargs,
        )


class TurboStreamTemplateResponseMixin(
    SupportsRequest,
    SupportsTemplateEngine,
    SupportsTemplateNames,
    TurboStreamResponseMixin,
):
    """Handles turbo-stream template responses."""

    def get_turbo_stream_template_names(self) -> Iterable[str]:
        """Returns list of template names.

        :rtype: list
        """
        return self.get_template_names()

    def render_turbo_stream_template_response(
        self, context: Dict[str, Any], **response_kwargs
    ) -> TurboStreamTemplateResponse:
        """Renders a turbo-stream template response.

        :param context: template context
        :type context: dict

        :rtype: turbo_response.TurboStreamTemplateResponse
        """

        if (target := self.get_turbo_stream_target()) is None:
            raise ImproperlyConfigured("target is None")

        if (action := self.get_turbo_stream_action()) is None:
            raise ImproperlyConfigured("action is None")

        return TurboStreamTemplateResponse(
            request=self.request,
            template=self.get_turbo_stream_template_names(),
            target=target,
            action=action,
            context=context,
            using=self.template_engine,
        )


class TurboFormMixin(SupportsFormInvalid):
    """Mixin for handling form validation. Ensures response
    has 422 status on invalid"""

    def form_invalid(self, form: forms.Form) -> HttpResponse:
        response = super().form_invalid(form)
        response.status_code = http.HTTPStatus.UNPROCESSABLE_ENTITY
        return response


class TurboFrameResponseMixin:
    turbo_frame_dom_id = None

    def get_turbo_frame_dom_id(self) -> Optional[str]:
        return self.turbo_frame_dom_id

    def get_response_content(self) -> Union[bytes, str]:
        return ""

    def render_turbo_frame_response(self, **response_kwargs) -> TurboFrameResponse:

        if (dom_id := self.get_turbo_frame_dom_id()) is None:
            raise ValueError("dom_id must be specified")

        return TurboFrameResponse(
            content=self.get_response_content(), dom_id=dom_id, **response_kwargs,
        )


class TurboFrameTemplateResponseMixin(
    SupportsRequest,
    SupportsTemplateNames,
    SupportsTemplateEngine,
    TurboFrameResponseMixin,
):
    """Handles turbo-frame template responses."""

    def render_turbo_frame_response(self, context, **response_kwargs):
        """Returns a turbo-frame response.

        :param context: template context
        :type context: dict

        :rtype: turbo_response.TurboFrameTemplateResponse
        """
        return TurboFrameTemplateResponse(
            request=self.request,
            template=self.get_template_names(),
            dom_id=self.get_turbo_frame_dom_id(),
            context=context,
            using=self.template_engine,
            **response_kwargs,
        )
