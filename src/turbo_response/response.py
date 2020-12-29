# Django
from django.http import HttpResponse, StreamingHttpResponse
from django.template.response import TemplateResponse

# Local
from .utils import render_turbo_frame, render_turbo_stream


class TurboStreamResponseMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(
            content_type="text/html; turbo-stream; charset=utf-8", *args, **kwargs
        )


class TurboStreamStreamingResponse(TurboStreamResponseMixin, StreamingHttpResponse):
    ...


class TurboStreamResponse(TurboStreamResponseMixin, HttpResponse):
    def __init__(self, content=b"", *, action, target, **kwargs):
        super().__init__(
            render_turbo_stream(action, target, content), **kwargs,
        )


class TurboStreamTemplateResponse(TurboStreamResponseMixin, TemplateResponse):
    is_turbo_stream = True

    def __init__(self, request, template, context, *, action, target, **kwargs):

        super().__init__(
            request,
            template,
            {
                **context,
                "turbo_stream_action": action.value,
                "turbo_stream_target": target,
                "is_turbo_stream": True,
            },
            **kwargs,
        )

        self._target = target
        self._action = action

    @property
    def rendered_content(self):
        return render_turbo_stream(
            action=self._action, target=self._target, content=super().rendered_content
        )


class TurboFrameResponse(HttpResponse):
    def __init__(self, content=b"", *, dom_id, **kwargs):
        super().__init__(
            render_turbo_frame(dom_id, content), **kwargs,
        )


class TurboFrameTemplateResponse(TemplateResponse):
    is_turbo_frame = True

    def __init__(self, request, template, context, *, dom_id, **kwargs):

        super().__init__(
            request,
            template,
            {**context, "turbo_frame_dom_id": dom_id, "is_turbo_frame": True},
            **kwargs,
        )

        self._dom_id = dom_id

    @property
    def rendered_content(self):
        return render_turbo_frame(self._dom_id, super().rendered_content)
