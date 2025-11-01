"""
Pydantic request models for CrewAI workflows.

These models define the input schema for each workflow type,
enabling validation and documentation in the FastAPI interface.
"""

from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


class PropertyEvaluationRequest(BaseModel):
    """Request model for property evaluation workflow."""

    name: str = Field(..., description="Nome da pousada/propriedade")
    location: str = Field(..., description="Localização (ex: 'Centro Histórico de Paraty')")
    price: float = Field(..., description="Preço de compra em R$", gt=0)
    rooms: int = Field(..., description="Número de quartos/UHs", gt=0)
    capex_estimated: float = Field(..., description="CAPEX estimado para reformas em R$", ge=0)
    adr_target: float = Field(..., description="ADR (diária média) alvo em R$", gt=0)
    occupancy_target: float = Field(..., description="Taxa de ocupação alvo (%)", gt=0, le=100)

    # Optional parameters
    webhook_url: Optional[str] = Field(None, description="URL para webhook de callback (async mode)")
    model_name: Optional[str] = Field(None, description="Nome do modelo Ollama a usar")

    model_config = ConfigDict(
        json_schema_extra = {
            "example": {
                "name": "Pousada Vista Mar",
                "location": "Centro Histórico de Paraty",
                "price": 2200000,
                "rooms": 12,
                "capex_estimated": 280000,
                "adr_target": 320,
                "occupancy_target": 60,
                "webhook_url": "https://n8n.example.com/webhook/property-eval-complete",
                "model_name": "qwen2.5:14b"
            }
        }
    )


class PositioningStrategyRequest(BaseModel):
    """Request model for positioning strategy workflow."""

    name: str = Field(..., description="Nome da pousada")
    location: str = Field(..., description="Localização")
    target_audience: str = Field(
        ...,
        description="Público-alvo principal (ex: 'Casais românticos', 'Famílias')"
    )
    differentiators: list[str] = Field(
        ...,
        description="Diferenciais da propriedade",
        min_length=1
    )
    budget_marketing: float = Field(
        ...,
        description="Orçamento de marketing disponível em R$",
        ge=0
    )

    # Optional parameters
    webhook_url: Optional[str] = Field(None, description="URL para webhook de callback")
    model_name: Optional[str] = Field(None, description="Nome do modelo Ollama")

    model_config = ConfigDict(
        json_schema_extra = {
            "example": {
                "name": "Pousada Vista Mar",
                "location": "Paraty - RJ",
                "target_audience": "Casais românticos 30-50 anos",
                "differentiators": [
                    "Vista panorâmica do mar",
                    "Arquitetura colonial preservada",
                    "Gastronomia local autêntica"
                ],
                "budget_marketing": 50000
            }
        }
    )


class OpeningPreparationRequest(BaseModel):
    """Request model for opening preparation workflow."""

    name: str = Field(..., description="Nome da pousada")
    location: str = Field(..., description="Localização")
    opening_date: str = Field(..., description="Data prevista de abertura (YYYY-MM-DD)")
    total_staff_needed: int = Field(..., description="Número total de funcionários necessários", gt=0)
    budget_setup: float = Field(..., description="Orçamento para setup operacional em R$", ge=0)
    priority_areas: list[str] = Field(
        ...,
        description="Áreas prioritárias de preparação",
        min_length=1
    )

    # Optional parameters
    webhook_url: Optional[str] = Field(None, description="URL para webhook de callback")
    model_name: Optional[str] = Field(None, description="Nome do modelo Ollama")

    @field_validator('opening_date')
    @classmethod
    def validate_date_format(cls, v: str) -> str:
        """Validate date format is YYYY-MM-DD."""
        from datetime import datetime
        try:
            datetime.strptime(v, '%Y-%m-%d')
            return v
        except ValueError:
            raise ValueError('Data deve estar no formato YYYY-MM-DD')

    model_config = ConfigDict(
        json_schema_extra = {
            "example": {
                "name": "Pousada Vista Mar",
                "location": "Paraty - RJ",
                "opening_date": "2025-12-01",
                "total_staff_needed": 15,
                "budget_setup": 150000,
                "priority_areas": [
                    "Contratação e treinamento",
                    "Fornecedores de alimentos",
                    "Sistemas de reserva",
                    "Marketing de lançamento"
                ]
            }
        }
    )


class Planning30DaysRequest(BaseModel):
    """Request model for 30-day planning workflow."""

    name: str = Field(..., description="Nome da pousada")
    location: str = Field(..., description="Localização")
    start_date: str = Field(..., description="Data de início do plano (YYYY-MM-DD)")
    focus_areas: list[str] = Field(
        ...,
        description="Áreas de foco para os 30 dias",
        min_length=1
    )
    current_status: str = Field(
        ...,
        description="Status atual do negócio (ex: 'Em reforma', 'Recém inaugurado', 'Operacional')"
    )
    key_goals: list[str] = Field(
        ...,
        description="Objetivos principais para os 30 dias",
        min_length=1
    )

    # Optional parameters
    webhook_url: Optional[str] = Field(None, description="URL para webhook de callback")
    model_name: Optional[str] = Field(None, description="Nome do modelo Ollama")

    @field_validator('start_date')
    @classmethod
    def validate_date_format(cls, v: str) -> str:
        """Validate date format is YYYY-MM-DD."""
        from datetime import datetime
        try:
            datetime.strptime(v, '%Y-%m-%d')
            return v
        except ValueError:
            raise ValueError('Data deve estar no formato YYYY-MM-DD')

    model_config = ConfigDict(
        json_schema_extra = {
            "example": {
                "name": "Pousada Vista Mar",
                "location": "Paraty - RJ",
                "start_date": "2025-02-01",
                "focus_areas": [
                    "Operações",
                    "Marketing",
                    "Qualidade do serviço",
                    "Finanças"
                ],
                "current_status": "Recém inaugurado - primeira temporada",
                "key_goals": [
                    "Atingir 40% de ocupação",
                    "Estabelecer processos operacionais",
                    "Construir presença digital",
                    "Conquistar primeiras avaliações 5 estrelas"
                ]
            }
        }
    )


# Union type for any workflow request
WorkflowRequest = PropertyEvaluationRequest | PositioningStrategyRequest | OpeningPreparationRequest | Planning30DaysRequest
