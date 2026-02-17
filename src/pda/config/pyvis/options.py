from pydantic import Field

from pda.config.base import BaseConfig


class PDAOptions(BaseConfig):
    auto_adjust_spacing: bool = Field(
        default=True,
        description="""Whether to automatically adjust spacing between nodes in the visualization
        for a given ratio.""",
    )
    ratio: float = Field(
        default=1.0,
        description="""Aspect ratio (height/width) to maintain when auto-adjusting spacing.
        Only applied if `auto_adjust_spacing` is True.""",
    )
