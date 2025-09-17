"""Pydantic models for horse data schema validation."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class InjuryRecord(BaseModel):
    """Model for injury/health records."""
    
    date: str = Field(default="", description="Injury date")
    description: str = Field(default="", description="Injury description")


class PastRunRecord(BaseModel):
    """Model for past performance records."""
    
    race_date: str = Field(default="", description="Race date")
    venue: str = Field(default="", description="Race venue")
    distance: str = Field(default="", description="Race distance")
    barrier: str = Field(default="", description="Barrier position")
    weight: str = Field(default="", description="Carried weight")
    jockey: str = Field(default="", description="Jockey name")
    position: str = Field(default="", description="Finishing position")
    time: str = Field(default="", description="Race time")
    equipment: str = Field(default="", description="Equipment used")
    rating: str = Field(default="", description="Rating")
    odds: str = Field(default="", description="Win odds")
    
    # Additional comprehensive fields
    track_condition: str = Field(default="", description="Track condition")
    race_class: str = Field(default="", description="Race class")
    distance_to_winner: str = Field(default="", description="Distance to winner")
    running_position: str = Field(default="", description="Running position during race")
    barrier_weight: str = Field(default="", description="Barrier weight")
    trainer: str = Field(default="", description="Trainer name")


class ToplineData(BaseModel):
    """Model for top-line race data from the main table."""
    
    馬號: str = Field(default="", description="Horse number")
    馬匹ID: str = Field(default="", description="Horse ID")
    馬名: str = Field(default="", description="Horse name")
    馬匹編號: str = Field(default="", description="Horse code")
    最近6輪: str = Field(default="", description="Recent 6 runs")
    排位: str = Field(default="", description="Barrier position")
    負磅: str = Field(default="", description="Carried weight")
    騎師: str = Field(default="", description="Jockey")
    練馬師: str = Field(default="", description="Trainer")
    獨贏: str = Field(default="", description="Win odds")
    位置: str = Field(default="", description="Place odds")
    當前評分: str = Field(default="", description="Current rating")
    國際評分: str = Field(default="", description="International rating")
    配備: str = Field(default="", description="Equipment")
    讓磅: str = Field(default="", description="Weight allowance")
    練馬師喜好: str = Field(default="1", description="Trainer preference")
    馬齡: str = Field(default="", description="Horse age")
    
    # Detail page data
    傷病記錄: List[InjuryRecord] = Field(default_factory=list, description="Injury records")
    往績紀錄: List[PastRunRecord] = Field(default_factory=list, description="Past performance records")
    馬匹基本資料: str = Field(default="", description="Horse basic information")
    
    # Additional fields for internal use
    detail_url: Optional[str] = Field(default=None, description="Horse detail page URL")
    
    @field_validator("*", mode="before")
    @classmethod
    def convert_to_string(cls, v: Any) -> str:
        """Convert all values to strings except lists and None."""
        if v is None:
            return ""
        if isinstance(v, (list, dict)):
            return v
        return str(v)
    
    @classmethod
    def from_topline_and_detail(
        cls, 
        topline: Dict[str, Any], 
        detail: Dict[str, Any]
    ) -> "ToplineData":
        """Merge topline race data with detail page data."""
        merged_data = topline.copy()
        merged_data.update(detail)
        return cls(**merged_data)


class HorseRecord(BaseModel):
    """Final horse record model matching the exact output schema."""
    
    馬號: str = Field(default="", description="Horse number")
    馬匹ID: str = Field(default="", description="Horse ID")
    馬名: str = Field(default="", description="Horse name")
    馬匹編號: str = Field(default="", description="Horse code")
    最近6輪: str = Field(default="", description="Recent 6 runs")
    排位: str = Field(default="", description="Barrier position")
    負磅: str = Field(default="", description="Carried weight")
    騎師: str = Field(default="", description="Jockey")
    練馬師: str = Field(default="", description="Trainer")
    獨贏: str = Field(default="", description="Win odds")
    位置: str = Field(default="", description="Place odds")
    當前評分: str = Field(default="", description="Current rating")
    國際評分: str = Field(default="", description="International rating")
    配備: str = Field(default="", description="Equipment")
    讓磅: str = Field(default="", description="Weight allowance")
    練馬師喜好: str = Field(default="1", description="Trainer preference")
    馬齡: str = Field(default="", description="Horse age")
    傷病記錄: List[InjuryRecord] = Field(default_factory=list, description="Injury records")
    往績紀錄: List[PastRunRecord] = Field(default_factory=list, description="Past performance records")
    馬匹基本資料: str = Field(default="", description="Horse basic information")
    
    @field_validator("*", mode="before")
    @classmethod
    def convert_to_string(cls, v: Any) -> str:
        """Convert all values to strings except lists and None."""
        if v is None:
            return ""
        if isinstance(v, (list, dict)):
            return v
        return str(v)
    
    @classmethod
    def from_topline_data(cls, topline_data: ToplineData) -> "HorseRecord":
        """Convert ToplineData to HorseRecord."""
        return cls(**topline_data.model_dump())
