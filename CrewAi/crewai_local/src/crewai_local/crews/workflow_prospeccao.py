"""
Workflow E: Property Prospecting / Lead Generation

Crew para prospectar e qualificar listagens de pousadas à venda em Paraty.
Agente: Marina (1 agente, 3 tasks sequenciais)

Output: JSON com lista de propriedades qualificadas (nome, preço, quartos, link, etc)
"""

from crewai import Crew, Process, Task
from ..agents.prospeccao import create_marina_silva
import json


def create_prospecting_crew(llm, constraints: dict = None) -> Crew:
    """
    Cria crew para prospecção de propriedades.

    Args:
        llm: Modelo de linguagem
        constraints: Filtros de busca
            - price_min: Preço mínimo (R$)
            - price_max: Preço máximo (R$)
            - location_filter: Lista de localizações preferidas
            - rooms_min: Número mínimo de quartos
            - rooms_max: Número máximo de quartos

    Returns:
        Crew configurada para prospecção
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
    marina = create_marina_silva(llm)

    # Preparar descrição de constraints para tasks
    constraints_desc = []
    if constraints.get('price_min') or constraints.get('price_max'):
        price_min_fmt = f"R${constraints.get('price_min', 0):,.0f}" if constraints.get('price_min') else "sem limite"
        price_max_fmt = f"R${constraints.get('price_max', 999999999):,.0f}" if constraints.get('price_max') else "sem limite"
        constraints_desc.append(f"Preço: {price_min_fmt} - {price_max_fmt}")
    if constraints.get('location_filter'):
        locations = ', '.join(constraints['location_filter'])
        constraints_desc.append(f"Localização: {locations}")
    if constraints.get('rooms_min') or constraints.get('rooms_max'):
        rooms_min_fmt = constraints.get('rooms_min') if constraints.get('rooms_min') else "sem limite"
        rooms_max_fmt = constraints.get('rooms_max') if constraints.get('rooms_max') else "sem limite"
        constraints_desc.append(f"Quartos: {rooms_min_fmt} - {rooms_max_fmt}")

    constraints_text = '\n'.join([f"   - {c}" for c in constraints_desc]) if constraints_desc else "   - Nenhum filtro (todas as propriedades)"

    # Task 1: Buscar URLs de listagens
    task1_search_listings = Task(
        description=f"""FASE 1: BUSCAR LISTAGENS DE PROPRIEDADES

**MISSÃO:** Encontrar 20-30 URLs de anúncios INDIVIDUAIS de pousadas À VENDA em Paraty.

**PROCESSO DE 2 ETAPAS OBRIGATÓRIO:**

═══════════════════════════════════════════════════════════════════
ETAPA 1.1: ENCONTRAR PÁGINAS DE CATEGORIA (usar search_web)
═══════════════════════════════════════════════════════════════════

Use search_web para encontrar 4-6 páginas de LISTAGEM/CATEGORIA nos sites:

1. **VivaReal.com.br:**
   - Query: "site:vivareal.com.br pousada venda Paraty"
   - Ou: "site:vivareal.com.br hotel venda Paraty"

2. **ZapImóveis.com.br:**
   - Query: "site:zapimoveis.com.br hoteis-moteis-pousadas venda Paraty"
   - Ou: "site:zapimoveis.com.br pousada à venda Paraty"

3. **OLX.com.br:**
   - Query: "site:olx.com.br pousada venda Paraty RJ"

4. **Imovelweb.com.br:**
   - Query: "site:imovelweb.com.br hotel venda Paraty"

**RESULTADO ESPERADO ETAPA 1.1:**
4-6 URLs de páginas de CATEGORIA/LISTAGEM (não anúncios individuais ainda)

═══════════════════════════════════════════════════════════════════
ETAPA 1.2: EXTRAIR LINKS INDIVIDUAIS (usar fetch_with_playwright_fallback)
═══════════════════════════════════════════════════════════════════

Para CADA página de categoria encontrada na Etapa 1.1:

1. **Acessar página:**
   ```
   fetch_with_playwright_fallback(url_da_pagina_categoria)
   ```

2. **Procurar no HTML por links de anúncios individuais:**
   - Tags <a> com href contendo padrões específicos:
     * VivaReal: "/imovel/", "/venda/", com ID único
     * Zap: "/imovel/", com ID único no final
     * OLX: "/vi/", "/imoveis/", com ID numérico
     * Imovelweb: "/imovel/", "/propriedades/"

3. **Extrair 5-10 links únicos de cada página de categoria**

4. **VALIDAR que são anúncios INDIVIDUAIS:**
   ✅ URL VÁLIDA (anúncio individual):
      - https://www.vivareal.com.br/imovel/hotel-venda-300m2-paraty-centro-historico-id-12345/
      - https://www.zapimoveis.com.br/imovel/pousada-venda-paraty-rj-codigo-xyz789/
      - https://www.olx.com.br/vi/imoveis/pousada-15-quartos-paraty-123456789.htm

   ❌ URL INVÁLIDA (página de categoria - REJEITAR):
      - https://www.zapimoveis.com.br/venda/hoteis-moteis-pousadas/rj+paraty/
      - https://www.vivareal.com.br/venda/rj/paraty/hotel/
      - https://www.olx.com.br/imoveis/estado-rj/paraty

   **CRITÉRIO DE VALIDAÇÃO:**
   - URL deve ter ID único (números ou hash)
   - URL deve terminar em slug específico (não em nome de cidade/categoria)
   - URL NÃO deve conter apenas: "/venda/.../rj+paraty/" sem ID final

5. **Adicionar à lista final:**
   - Meta: 20-30 URLs de anúncios individuais no total
   - 5-10 links por página de categoria × 4-6 páginas = 20-60 links
   - Remover duplicatas

**FILTROS A CONSIDERAR:**
{constraints_text}

═══════════════════════════════════════════════════════════════════
EXEMPLO DE FLUXO COMPLETO:
═══════════════════════════════════════════════════════════════════

1. search_web("site:vivareal.com.br pousada venda Paraty")
   → Retorna: https://www.vivareal.com.br/venda/rj/paraty/hotel/

2. fetch_with_playwright_fallback("https://www.vivareal.com.br/venda/rj/paraty/hotel/")
   → HTML contém 10 links de anúncios:
      - https://www.vivareal.com.br/imovel/hotel-venda-paraty-centro-id-abc123/
      - https://www.vivareal.com.br/imovel/pousada-praia-paraty-id-def456/
      - [... mais 8 links ...]

3. Validar cada link (tem ID? não é categoria?)
   → 10 links válidos extraídos

4. Repetir para Zap, OLX, Imovelweb...

5. Total final: 25 URLs de anúncios individuais

═══════════════════════════════════════════════════════════════════
FORMATO DE SAÍDA OBRIGATÓRIO:
═══════════════════════════════════════════════════════════════════

### VivaReal (10 anúncios individuais)
1. https://www.vivareal.com.br/imovel/hotel-venda-300m2-paraty-centro-historico-id-12345/
2. https://www.vivareal.com.br/imovel/pousada-15-quartos-praia-paraty-id-67890/
[... lista completa ...]

### Zap Imóveis (8 anúncios individuais)
1. https://www.zapimoveis.com.br/imovel/pousada-venda-paraty-rj-codigo-abc123/
2. https://www.zapimoveis.com.br/imovel/hotel-boutique-centro-paraty-codigo-def456/
[... lista completa ...]

### OLX (5 anúncios individuais)
1. https://www.olx.com.br/vi/imoveis/pousada-15-quartos-paraty-123456789.htm
[... lista completa ...]

**Total de URLs encontradas: 23**

**IMPORTANTE:**
- TODAS as URLs devem ser de anúncios INDIVIDUAIS (com ID único)
- NÃO incluir páginas de categoria/listagem na lista final
- Se não conseguir extrair links de uma página, documente o problema e tente outra fonte
""",

        expected_output="""Lista em markdown de 20-30 URLs de anúncios INDIVIDUAIS agrupadas por site.

REQUISITOS OBRIGATÓRIOS:
- Cada URL DEVE ser um link direto para anúncio ESPECÍFICO (não página de busca/categoria)
- Cada URL DEVE ter ID único (hash, código, número)
- URLs de categoria (ex: /venda/hoteis-moteis-pousadas/rj+paraty/) são INVÁLIDAS
- Mínimo 20 URLs, máximo 40 URLs
- Incluir contagem por fonte e total ao final

FORMATO:
### [Nome do Site] (X anúncios individuais)
1. [URL com ID]
2. [URL com ID]
...

**Total de URLs encontradas: X**""",

        agent=marina
    )

    # Task 2: Extrair e validar dados
    task2_extract_validate = Task(
        description=f"""FASE 2: EXTRAIR E VALIDAR DADOS DAS PROPRIEDADES

**MISSÃO:** Extrair dados detalhados de cada URL e validar contra filtros.

**ESTRATÉGIA DE EXTRAÇÃO:**

1. **Para cada URL da Fase 1:**
   - Use fetch_with_playwright_fallback(url) para obter conteúdo
   - Extraia os seguintes campos:
     * Nome da propriedade (ou gere a partir da localização)
     * Endereço completo
     * Preço (R$) - CRÍTICO se filtro de preço está ativo
     * Número de quartos/unidades
     * Área construída (m²)
     * Área do terreno (m²) se disponível
     * Condição (excelente/bom/regular/ruim)
     * Descrição completa
     * Número de fotos/imagens
     * Tipo de localização (praia/centro_historico/outras)

2. **Regras de Validação:**
   - PULAR se falta preço E filtro de preço está ativo
   - PULAR se localização não corresponde ao filtro (se especificado)
   - PULAR se quartos fora da faixa do filtro (se especificado)
   - MARCAR qualidade dos dados:
     * "complete": Todos os campos presentes
     * "partial": Faltando 1-2 campos não-críticos
     * "minimal": Apenas informações básicas (nome, preço, URL)

3. **Verificações de Qualidade:**
   - Verificar preço realista (> R$500k, < R$50M para pousadas)
   - Verificar quartos realista (3-50 para pousadas)
   - Checar se anúncio é realmente À VENDA (não aluguel)
   - Marcar anúncios suspeitos (muito barato, sem fotos, endereço incompleto)

**FILTROS PARA VALIDAR:**
{constraints_text}

**DEDUPLICAÇÃO:**
- Se mesmo endereço aparece múltiplas vezes: manter versão com dados mais completos
- Anotar fontes duplicadas no registro da propriedade

**FORMATO DE SAÍDA:**
Retorne dados estruturados para cada propriedade validada:

```
PROPRIEDADE 1:
- ID: PROP-001
- Nome: [nome ou gerado]
- Endereço: [endereço completo]
- Preço: R$ X.XXX.XXX
- Quartos: X
- Área: X m²
- Terreno: X m² (ou "não informado")
- Condição: [excelente/bom/regular/ruim/não informado]
- Descrição: [primeiros 150 caracteres]
- Tipo Localização: [praia/centro_historico/outras]
- Fotos: X fotos
- Fonte: [domínio do site]
- Qualidade Dados: [complete/partial/minimal]
- URL Anúncio: [URL original]

PROPRIEDADE 2:
[...]

---
RESUMO:
- Total URLs processadas: X
- Propriedades validadas: X
- Propriedades puladas (fora dos filtros): X
- Propriedades puladas (outras razões): X
```
""",

        expected_output="""Listagem estruturada em texto de todas as propriedades validadas com detalhes completos.
Incluir estatísticas resumidas ao final mostrando total processado vs validado vs pulado.""",

        agent=marina,
        context=[task1_search_listings]
    )

    # Task 3: Compilar JSON final
    task3_compile_json = Task(
        description=f"""FASE 3: COMPILAR JSON FINAL

**MISSÃO:** Criar arquivo JSON final com todas as propriedades qualificadas e metadata.

**ESTRUTURA JSON:**

1. **Seção Metadata:**
   - search_date: timestamp ISO 8601
   - workflow: "property_prospecting"
   - location: "Paraty - RJ"
   - constraints: {{filtros usados}}
   - total_found: X (da Fase 1)
   - total_qualified: X (da Fase 2)
   - sources: [lista de sites únicos]

2. **Array Properties:**
   - Converter cada propriedade da Fase 2 para objeto JSON
   - Auto-gerar IDs (PROP-001, PROP-002, ...)
   - Formatar preços como número E string formatada
   - Incluir timestamp scraped_date para cada propriedade
   - Garantir que todos os campos seguem schema exatamente

3. **Garantia de Qualidade:**
   - Verificar que todas as propriedades têm campos obrigatórios
   - Checar IDs ou URLs duplicadas
   - Validar que preços e quartos são numéricos
   - Garantir datas no formato ISO 8601

**FILTROS USADOS:**
{constraints_text}

**SCHEMA JSON (FORMATO EXATO OBRIGATÓRIO):**

```json
{{
  "metadata": {{
    "search_date": "2025-11-02T14:30:00Z",
    "workflow": "property_prospecting",
    "location": "Paraty - RJ",
    "constraints": {{
      "price_min": {constraints.get('price_min') or 'null'},
      "price_max": {constraints.get('price_max') or 'null'},
      "location_filter": {json.dumps(constraints.get('location_filter', []))},
      "rooms_min": {constraints.get('rooms_min') or 'null'},
      "rooms_max": {constraints.get('rooms_max') or 'null'}
    }},
    "total_found": 0,
    "total_qualified": 0,
    "sources": []
  }},
  "properties": [
    {{
      "id": "PROP-001",
      "name": "Nome da Propriedade",
      "address": "Endereço Completo",
      "price": 2800000,
      "price_formatted": "R$ 2.800.000",
      "rooms": 12,
      "area_m2": 450,
      "land_area_m2": 800,
      "condition": "bom",
      "listing_url": "https://...",
      "source_site": "vivareal.com.br",
      "scraped_date": "2025-11-02T14:35:12Z",
      "description_snippet": "Primeiros 150 caracteres...",
      "location_type": "centro_historico",
      "images_count": 15,
      "data_quality": "complete"
    }}
  ]
}}
```

**IMPORTANTE:**
- Retorne APENAS o JSON (sem code fences markdown, sem explicações)
- Use sintaxe JSON apropriada (sem vírgulas finais)
- Todas as strings devem usar aspas duplas
- Números devem estar sem aspas
- Valores nulos devem ser JSON null (não string "null")

**ARQUIVO SERÁ SALVO EM:**
outputs/property_prospecting/{{YYYY-MM-DD}}/pousadas_paraty_leads_{{timestamp}}.json
""",

        expected_output="""Objeto JSON válido seguindo schema exato especificado acima.
Deve ser parseável por json.loads() sem erros.
Incluir header metadata e array properties completo.""",

        agent=marina,
        context=[task1_search_listings, task2_extract_validate]
    )

    # Criar crew
    crew = Crew(
        agents=[marina],
        tasks=[task1_search_listings, task2_extract_validate, task3_compile_json],
        process=Process.sequential,
        verbose=True
    )

    return crew
