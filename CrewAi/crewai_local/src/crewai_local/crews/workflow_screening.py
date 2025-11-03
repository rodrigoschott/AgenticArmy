"""
Workflow F: Batch Property Screening & Ranking

Crew para fazer screening rápido de múltiplas propriedades (do Workflow E)
e ranquear por scores objetivos para seleção de top candidates.

Agente: Sofia Mendes (1 agente, 1 task)

Input: JSON do Workflow E com array de propriedades
Output: JSON ranqueado com top N propriedades + scores + justificativas
"""

from crewai import Crew, Process, Task
from ..agents.screening import create_sofia_mendes
import json


def create_screening_crew(llm, json_data: dict, constraints: dict = None, top_n: int = 10) -> Crew:
    """
    Cria crew para screening em lote de propriedades.

    Args:
        llm: Modelo de linguagem
        json_data: Dict com dados do JSON do Workflow E
            Estrutura esperada:
            {
                "data": {
                    "properties": [
                        {
                            "id": "PROP-001",
                            "name": "...",
                            "price": 2800000,
                            "bedrooms": 15,
                            "location_type": "praia",
                            "condition": "excelente",
                            "data_quality": "complete",
                            "url": "..."
                        },
                        ...
                    ]
                }
            }
        constraints: Filtros originais do Workflow E (para investment_fit_score)
            - price_min: Preço mínimo desejado
            - price_max: Preço máximo desejado
            - location_filter: Lista de localizações preferidas
            - rooms_min: Quartos mínimo
            - rooms_max: Quartos máximo
        top_n: Número de propriedades top para retornar (default: 10)

    Returns:
        Crew configurada para screening
    """

    if constraints is None:
        constraints = {
            'price_min': None,
            'price_max': None,
            'location_filter': [],
            'rooms_min': None,
            'rooms_max': None
        }

    # Criar agente
    sofia = create_sofia_mendes(llm)

    # Extrair propriedades do JSON
    properties = json_data.get('data', {}).get('properties', [])
    total_properties = len(properties)

    # Preparar descrição de constraints para a task
    constraints_desc = []
    if constraints.get('price_min') or constraints.get('price_max'):
        price_min_fmt = f"R${constraints.get('price_min', 0):,.0f}" if constraints.get('price_min') else "sem limite"
        price_max_fmt = f"R${constraints.get('price_max', 999999999):,.0f}" if constraints.get('price_max') else "sem limite"
        constraints_desc.append(f"Preço: {price_min_fmt} - {price_max_fmt}")
    if constraints.get('location_filter'):
        locations = ', '.join(constraints['location_filter'])
        constraints_desc.append(f"Localização preferida: {locations}")
    if constraints.get('rooms_min') or constraints.get('rooms_max'):
        rooms_min_fmt = constraints.get('rooms_min') if constraints.get('rooms_min') else "sem limite"
        rooms_max_fmt = constraints.get('rooms_max') if constraints.get('rooms_max') else "sem limite"
        constraints_desc.append(f"Quartos: {rooms_min_fmt} - {rooms_max_fmt}")

    constraints_text = '\n'.join([f"   - {c}" for c in constraints_desc]) if constraints_desc else "   - Nenhum filtro específico (investment_fit_score = 8.0 para todas)"

    # Serializar propriedades para inclusão na task description
    properties_json_str = json.dumps(properties, indent=2, ensure_ascii=False)

    # Task única: Screening e ranqueamento
    task_screening = Task(
        description=f"""MISSÃO: Analise e ranqueie {total_properties} propriedades de investimento usando metodologia de scoring multi-dimensional.

**DADOS DE ENTRADA (JSON):**

```json
{properties_json_str}
```

**CONSTRAINTS DO INVESTIDOR (para investment_fit_score):**
{constraints_text}

**SUA TAREFA:**

1. **Para CADA propriedade no array acima:**

   Calcule 5 scores individuais (escala 0-10):

   a) **PRICE/ROOM RATIO SCORE (peso 30%):**
      - Calcule: price / bedrooms = R$/quarto
      - Benchmark ideal: R$100k-200k/quarto
      - Scoring:
        * R$120k-180k: 10 pts
        * R$100k-120k ou R$180k-200k: 8-9 pts
        * R$80k-100k ou R$200k-250k: 6-7 pts
        * <R$80k: 3-5 pts (suspeito)
        * >R$250k: 2-4 pts (caro demais)
      - Se price null: score = 0
      - Se bedrooms null: assume 10 quartos, penaliza data_quality

   b) **LOCATION SCORE (peso 25%):**
      - location_type:
        * "praia": 10 pts
        * "centro_historico": 9 pts
        * "outras": 6 pts
        * null: 6 pts
      - Ajustes pela description (se disponível):
        * Menciona "vista mar", "pé na areia": +0.5
        * Menciona "acesso difícil": -1

   c) **DATA QUALITY SCORE (peso 15%):**
      - data_quality field:
        * "complete": 10 pts
        * "partial": 7 pts
        * "minimal": 4 pts
        * null: 5 pts
      - Penalidade se price null: -2 pts
      - Penalidade se bedrooms null: -2 pts

   d) **CONDITION SCORE (peso 20%):**
      - condition field:
        * "excelente": 10 pts
        * "bom": 8 pts
        * "regular": 6 pts
        * "ruim": 3 pts
        * null: 5 pts (assume regular)

   e) **INVESTMENT FIT SCORE (peso 10%):**
      - Baseado nos constraints:
        * Price dentro do range (price_min-price_max): 10 pts
        * Price 10% fora do range: 7 pts
        * Price 20%+ fora do range: 3 pts
        * Se sem constraint de preço: 8 pts (neutro)
      - Similar para bedrooms (se constraint definido)

2. **Calcule SCORE FINAL para cada propriedade:**

   final_score = (price_room × 0.30) + (location × 0.25) + (data_quality × 0.15) + (condition × 0.20) + (investment_fit × 0.10)

   Arredondar para 1 casa decimal (ex: 8.7)

3. **Classifique cada propriedade:**

   - final_score >= 8.5: "STRONGLY RECOMMENDED"
   - final_score >= 7.0: "RECOMMENDED"
   - final_score >= 5.5: "CONSIDER"
   - final_score < 5.5: "SKIP"

4. **Gere justificativa para cada uma:**

   Template: "Score X.X: [Ponto forte principal] + [Segundo ponto forte]. [Ressalva se houver]. Price/room R$XXXk [vs benchmark]. [Recomendação]."

   Exemplo: "Score 9.1: Excelente localização centro histórico + condição impecável. Price/room R$193k (sweet spot vs benchmark R$100k-200k). STRONGLY RECOMMENDED."

5. **Ordenar todas por final_score (decrescente)**

6. **Selecionar TOP {top_n} propriedades**

7. **Retornar JSON estruturado conforme schema abaixo**

**SCHEMA JSON (FORMATO EXATO OBRIGATÓRIO):**

```json
{{
  "metadata": {{
    "source_file": "[nome do arquivo JSON fonte se disponível]",
    "source_workflow": "property_prospecting",
    "total_properties_analyzed": {total_properties},
    "top_n_selected": {top_n},
    "screening_date": "[ISO 8601 timestamp]",
    "criteria_weights": {{
      "price_per_room": 0.30,
      "location": 0.25,
      "data_quality": 0.15,
      "condition": 0.20,
      "investment_fit": 0.10
    }},
    "constraints_applied": {{
      "price_min": {constraints.get('price_min') or 'null'},
      "price_max": {constraints.get('price_max') or 'null'},
      "rooms_min": {constraints.get('rooms_min') or 'null'},
      "rooms_max": {constraints.get('rooms_max') or 'null'}
    }}
  }},
  "ranked_properties": [
    {{
      "rank": 1,
      "property_id": "PROP-XXX",
      "name": "Nome da Propriedade",
      "price": 2700000,
      "bedrooms": 14,
      "location_type": "centro_historico",
      "condition": "excelente",
      "data_quality": "complete",
      "url": "https://...",
      "scores": {{
        "price_per_room": 9.5,
        "price_per_room_value": 193000,
        "location": 9.0,
        "data_quality": 10.0,
        "condition": 10.0,
        "investment_fit": 8.0,
        "final_score": 9.1
      }},
      "recommendation": "STRONGLY RECOMMENDED",
      "justification": "Score 9.1: Excelente localização centro histórico + condição impecável. Price/room R$193k (sweet spot vs benchmark R$100k-200k). STRONGLY RECOMMENDED."
    }},
    {{
      "rank": 2,
      ...
    }}
  ]
}}
```

**IMPORTANTE:**
- Retorne APENAS o JSON (sem markdown code fences, sem explicações)
- Use sintaxe JSON válida (aspas duplas, sem vírgulas finais)
- Analise TODAS as {total_properties} propriedades
- Retorne apenas top {top_n} no array ranked_properties
- NUNCA invente dados - use exatamente o que está no JSON de entrada
- Se algum campo for null, aplique regra de fallback documentada acima
- Scores devem ser numéricos (não strings)
- Timestamp no formato ISO 8601 (YYYY-MM-DDTHH:MM:SSZ)
""",

        expected_output=f"""Objeto JSON válido seguindo schema exato especificado acima.

REQUISITOS OBRIGATÓRIOS:
- Deve ser parseável por json.loads() sem erros
- Metadata completa com {total_properties} analyzed e {top_n} selected
- Array ranked_properties ordenado por final_score decrescente
- Cada propriedade com todos os 5 scores calculados
- Justificativa clara e objetiva para cada uma
- Apenas JSON puro (sem markdown code fences)

VALIDAÇÃO:
- total_properties_analyzed == {total_properties}
- len(ranked_properties) <= {top_n}
- ranked_properties[0].scores.final_score >= ranked_properties[1].scores.final_score (ordenado)
- Todos os property_ids presentes no input devem estar analisados (top N selecionadas)""",

        agent=sofia
    )

    # Criar crew
    crew = Crew(
        agents=[sofia],
        tasks=[task_screening],
        process=Process.sequential,
        verbose=True
    )

    return crew
