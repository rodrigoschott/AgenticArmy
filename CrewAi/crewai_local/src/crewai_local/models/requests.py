"""
Pydantic request models for CrewAI workflows.

These models define the input schema for each workflow type,
enabling validation and documentation in the FastAPI interface.
"""

from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


class PropertyEvaluationRequest(BaseModel):
    """
    Request model for property evaluation workflow.

    AUTONOMOUS RESEARCH MODE:
    Agents will automatically research and gather all property details.
    You only need to provide ONE of: property_name OR property_link.
    """

    # REQUIRED: At least one of these must be provided
    property_name: Optional[str] = Field(
        None,
        description="Nome da pousada/propriedade para pesquisa automática"
    )
    property_link: Optional[str] = Field(
        None,
        description="Link direto da propriedade (Airbnb, Booking, OLX, imobiliária, etc.)"
    )

    # OPTIONAL: Location hint to narrow search
    location_hint: Optional[str] = Field(
        None,
        description="Dica de localização opcional (ex: 'Paraty', 'Centro Histórico') para ajudar pesquisa"
    )

    # Optional parameters
    webhook_url: Optional[str] = Field(None, description="URL para webhook de callback (async mode)")
    model_name: Optional[str] = Field(None, description="Nome do modelo Ollama a usar")

    @field_validator('property_name', 'property_link')
    @classmethod
    def validate_at_least_one_identifier(cls, v, info):
        """Ensure at least one identifier is provided."""
        # This will be called for both fields, so we check in model_validator below
        return v

    def model_post_init(self, __context):
        """Validate that at least one identifier is provided."""
        if not self.property_name and not self.property_link:
            raise ValueError(
                "Você deve fornecer pelo menos um identificador: "
                "'property_name' (nome da propriedade) OU 'property_link' (link da propriedade)"
            )

    model_config = ConfigDict(
        json_schema_extra = {
            "examples": [
                {
                    "property_name": "Pousada Vista Mar",
                    "location_hint": "Paraty - RJ",
                    "model_name": "qwen2.5:14b"
                },
                {
                    "property_link": "https://www.airbnb.com.br/rooms/12345678",
                    "model_name": "qwen2.5:14b"
                },
                {
                    "property_link": "https://www.olx.com.br/imoveis/pousada-paraty-venda",
                    "location_hint": "Paraty",
                    "webhook_url": "https://n8n.example.com/webhook/property-eval-complete"
                }
            ]
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
