# ComfyUI Integration Ideas - Workflow Brainstorm

## Ecossistema Atual
- **n8n** (localhost:15678) - Orquestração de workflows
- **ComfyUI** (localhost:8188) - Geração de imagens (Qwen-Image + RTX 5080)
- **Ollama** (localhost:11434) - LLMs locais (Llama3.2)
- **Qdrant** (localhost:6333) - Vector store
- **PostgreSQL** - Database persistente
- **Docker Network**: `skynet` (todos conectados)

---

## 1. API REST - ComfyUI → Qualquer Serviço

### Descrição
ComfyUI possui uma API REST nativa que permite enviar workflows JSON via POST para `http://comfyui:8188/prompt`. O sistema retorna um ID de task, permite fazer polling do status e download da imagem gerada.

### Casos de Uso
- n8n chama ComfyUI via HTTP Request node
- Scripts Python externos (FastAPI, Flask) podem integrar
- Webhooks recebem prompts e retornam imagens
- Batch processing de múltiplas imagens em paralelo

### Exemplo de Workflow n8n
```
Trigger (Webhook/Schedule) 
→ HTTP Request (POST to ComfyUI API)
→ Wait/Poll (check status)
→ Download Image
→ Store in PostgreSQL/S3/Local
→ Send notification
```

### Implementação Técnica
```javascript
// POST to ComfyUI API
{
  "prompt": {
    "3": {
      "inputs": {
        "text": "your prompt here"
      },
      "class_type": "CLIPTextEncode"
    }
  },
  "client_id": "unique-client-id"
}

// Response
{
  "prompt_id": "abc123",
  "number": 1
}

// Poll status: GET /history/{prompt_id}
// Download: GET /view?filename=output.png
```

### Complexidade
**Baixa** - API nativa, documentação disponível

### Prioridade
⭐⭐⭐⭐⭐ (Quick Win - 1-2 dias)

---

## 2. n8n como Orquestrador Central

### Descrição
Utilizar n8n como hub central que coordena todos os serviços do ecossistema, criando pipelines complexos que combinam geração de texto (Ollama), busca semântica (Qdrant), geração de imagens (ComfyUI) e persistência (PostgreSQL).

### Workflows Sugeridos

#### A) AI Content Generator
```
1. Trigger: Webhook recebe tópico
2. Ollama: Gera descrição detalhada do conteúdo
3. Ollama: Refina e cria prompt otimizado para imagem
4. ComfyUI: Gera imagem baseada no prompt
5. PostgreSQL: Salva texto + URL da imagem
6. Return: JSON com conteúdo completo
```

**Caso de uso**: Sistema de blog automatizado, geração de conteúdo para redes sociais

#### B) Document Intelligence
```
1. Upload PDF via n8n
2. Ollama: Extrai texto e gera resumo
3. Qdrant: Cria embeddings e indexa documento
4. ComfyUI: Gera thumbnail/visualização do documento
5. PostgreSQL: Salva metadata + links
```

**Caso de uso**: Sistema de gestão de conhecimento, biblioteca digital inteligente

#### C) Social Media Automation
```
1. Schedule/Trigger (diário)
2. Ollama: Gera copy + hashtags relevantes
3. ComfyUI: Gera arte visual alinhada ao texto
4. Post to Twitter/LinkedIn/Instagram API
5. Log metrics em PostgreSQL
```

**Caso de uso**: Automação completa de redes sociais

### Benefícios
- Orquestração visual de pipelines complexos
- Error handling e retry automático
- Logs e monitoramento centralizados
- Fácil manutenção e modificação de workflows

### Complexidade
**Média** - Requer conhecimento dos nodes do n8n

### Prioridade
⭐⭐⭐⭐⭐ (Quick Win - 1-2 dias)

---

## 3. Claude Code → ComfyUI (MCP Integration)

### Descrição
Criar um **MCP (Model Context Protocol) Server** para ComfyUI que permite ao Claude Code (via Copilot) gerar imagens durante conversas, analisar workflows e ajudar a criar custom nodes.

### Funcionalidades
- Claude Code pode executar: "Generate an image of X" → ComfyUI processa
- Upload de workflows para Claude analisar e otimizar
- Claude ajuda a criar e debugar custom nodes
- Integração direta no ambiente de desenvolvimento

### Implementação Exemplo
```python
# comfyui-mcp-server.py
from mcp.server import Server
import requests
import json

server = Server("comfyui-integration")

@server.tool()
async def generate_image(prompt: str, workflow_type: str = "qwen-image"):
    """
    Generate image using ComfyUI
    
    Args:
        prompt: Text description of the image to generate
        workflow_type: Type of workflow (qwen-image, sdxl, etc)
    
    Returns:
        Path to generated image
    """
    workflow = build_workflow(prompt, workflow_type)
    response = requests.post(
        "http://localhost:8188/prompt",
        json={"prompt": workflow}
    )
    prompt_id = response.json()["prompt_id"]
    return await poll_and_download(prompt_id)

@server.tool()
async def list_workflows():
    """List available ComfyUI workflows"""
    return ["qwen-image", "qwen-edit", "sdxl-turbo"]

@server.tool()
async def get_workflow_status(prompt_id: str):
    """Check status of a running workflow"""
    response = requests.get(f"http://localhost:8188/history/{prompt_id}")
    return response.json()
```

### Configuração VSCode (settings.json)
```json
{
  "mcpServers": {
    "comfyui": {
      "command": "python",
      "args": ["D:/Dev/py/comfyui-mcp-server/server.py"],
      "env": {
        "COMFYUI_URL": "http://localhost:8188"
      }
    }
  }
}
```

### Casos de Uso
- Durante código: "Claude, generate a hero image for this landing page"
- Prototyping rápido: "Create 5 variations of this product image"
- Debugging: "Claude, why is this ComfyUI workflow failing?"
- Learning: "Explain this custom node implementation"

### Complexidade
**Média-Alta** - Requer conhecimento de MCP protocol

### Prioridade
⭐⭐⭐⭐ (Medium Term - 1 semana)

---

## 4. File Watching & Auto-Processing

### Descrição
Sistema automatizado que monitora pastas específicas e processa arquivos automaticamente quando detecta novos uploads, combinando análise (Ollama), geração (ComfyUI) e armazenamento (PostgreSQL/Qdrant).

### Opção A: Python + Watchdog
```python
# watch_and_process.py
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import requests
import json

class FileProcessor(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        
        filepath = event.src_path
        
        if filepath.endswith(('.jpg', '.png')):
            # Analyze image with Ollama
            description = analyze_image(filepath)
            
            # Generate variations with ComfyUI
            generate_variations(filepath, description)
            
        elif filepath.endswith('.txt'):
            # Read prompt from file
            with open(filepath, 'r') as f:
                prompt = f.read()
            
            # Generate image
            generate_image_from_prompt(prompt)
            
            # Store in Qdrant for semantic search
            store_in_vector_db(prompt, output_path)

observer = Observer()
observer.schedule(FileProcessor(), "/input_folder", recursive=True)
observer.start()
```

### Opção B: n8n File Trigger
```
File Trigger (watch /shared/input)
→ Read File node
→ Switch node:
   - If image: 
     → Ollama (analyze image)
     → PostgreSQL (store metadata)
   - If text: 
     → ComfyUI (generate image)
     → Move to /shared/output
→ Notification (email/Slack)
```

### Casos de Uso
- Drop zone para geração automática de imagens
- Processing pipeline para datasets
- Auto-categorização de uploads
- Backup e organização automática

### Estrutura de Pastas
```
/shared
  /input          # Drop zone
  /processing     # Arquivos sendo processados
  /output         # Resultados finais
  /archive        # Backup de originais
```

### Complexidade
**Baixa-Média** - Watchdog é simples, n8n tem trigger nativo

### Prioridade
⭐⭐⭐ (Quick Win - 1-2 dias)

---

## 5. RAG Pipeline com Imagens

### Descrição
Sistema de Retrieval-Augmented Generation que combina busca semântica (Qdrant), geração de texto (Ollama) e geração de imagens (ComfyUI) para criar um assistente inteligente que pode responder perguntas e ilustrar respostas visualmente.

### Arquitetura
```
User Query (texto)
↓
Ollama (entende contexto e intenção)
↓
Qdrant (busca imagens similares + documentos relevantes)
↓
Ollama (gera resposta baseada em docs encontrados)
↓
ComfyUI (gera nova imagem se necessário)
↓
Return (resposta + imagens relevantes + nova imagem)
```

### Casos de Uso Avançados

#### A) Sistema de Recomendação Visual
```
User: "Show me designs similar to minimalist tech branding"
↓
1. Qdrant busca embeddings similares
2. Retorna top 10 imagens do database
3. Ollama analisa preferências do usuário
4. ComfyUI gera 3 novas variações
5. Return: 10 similares + 3 novas
```

#### B) Assistente de Design com Memória
```
User: "Create a logo for my coffee shop, rustic style"
↓
1. Qdrant busca logos rusticos anteriores
2. Ollama aprende do histórico do usuário
3. ComfyUI gera logo com estilo consistente
4. Store: embedding do logo + metadata
5. Learning: Sistema aprende o estilo preferido
```

#### C) Chatbot que Ilustra Respostas
```
User: "Explain quantum computing"
↓
1. Ollama gera explicação didática
2. Identifica conceitos que precisam ilustração
3. ComfyUI gera diagramas/ilustrações
4. Return: Texto + imagens explicativas
```

### Implementação Técnica

#### Database Schema (PostgreSQL)
```sql
CREATE TABLE rag_images (
    id SERIAL PRIMARY KEY,
    image_path TEXT NOT NULL,
    prompt TEXT,
    embedding_id TEXT, -- ID no Qdrant
    metadata JSONB,
    tags TEXT[],
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE rag_conversations (
    id SERIAL PRIMARY KEY,
    user_id TEXT,
    query TEXT,
    response TEXT,
    images_used TEXT[],
    images_generated TEXT[],
    timestamp TIMESTAMP DEFAULT NOW()
);
```

#### Python Pipeline
```python
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
import requests

class RAGImagePipeline:
    def __init__(self):
        self.qdrant = QdrantClient("localhost", port=6333)
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
    
    def query(self, user_input: str):
        # 1. Generate embedding
        query_embedding = self.encoder.encode(user_input)
        
        # 2. Search Qdrant
        results = self.qdrant.search(
            collection_name="images",
            query_vector=query_embedding,
            limit=5
        )
        
        # 3. Generate context for Ollama
        context = self.build_context(results)
        
        # 4. Get Ollama response
        ollama_response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3.2",
                "prompt": f"Context: {context}\n\nQuestion: {user_input}"
            }
        )
        
        # 5. Decide if new image needed
        if self.should_generate_image(ollama_response):
            new_image = self.generate_comfyui_image(user_input)
            self.index_new_image(new_image, user_input)
        
        return {
            "text": ollama_response.json()["response"],
            "relevant_images": [r.payload for r in results],
            "new_image": new_image if 'new_image' in locals() else None
        }
```

#### n8n Workflow
```
Webhook (receive query)
→ Qdrant Search node (semantic search)
→ Ollama node (generate response with context)
→ IF node (check if image needed)
  YES →
    → ComfyUI HTTP Request (generate)
    → Qdrant Insert (index new image)
  NO → skip
→ PostgreSQL (log conversation)
→ Respond to Webhook (return JSON)
```

### Benefícios
- Respostas contextualmente relevantes
- Aprendizado contínuo do estilo do usuário
- Reutilização de imagens existentes (economia de GPU)
- Memória de longo prazo via Qdrant

### Otimizações
- Cache de embeddings para queries comuns
- Lazy loading de imagens (só gera se necessário)
- Batch indexing de novas imagens
- Cleanup periódico de embeddings antigos

### Complexidade
**Alta** - Requer integração de múltiplos serviços

### Prioridade
⭐⭐⭐⭐ (Long Term - 2+ semanas)

---

## 6. Batch Processing System

### Descrição
Sistema de fila de jobs robusto que permite processar múltiplas solicitações de geração de imagens de forma controlada, com retry automático, priorização e monitoramento de status.

### Arquitetura

#### Opção A: PostgreSQL como Queue
```sql
CREATE TABLE job_queue (
    id SERIAL PRIMARY KEY,
    status VARCHAR(20) DEFAULT 'pending', -- pending, processing, completed, failed
    priority INTEGER DEFAULT 0,
    prompt TEXT NOT NULL,
    workflow_type VARCHAR(50) DEFAULT 'qwen-image',
    params JSONB,
    result_image_path TEXT,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_by TEXT
);

CREATE INDEX idx_status_priority ON job_queue(status, priority DESC, created_at);
```

#### Worker Container
```python
# worker.py
import psycopg2
import requests
import time

class ComfyUIWorker:
    def __init__(self):
        self.db = psycopg2.connect("postgresql://user:pass@postgres/db")
        self.comfyui_url = "http://comfyui:8188"
    
    def process_jobs(self):
        while True:
            # Fetch next job
            job = self.fetch_next_job()
            
            if not job:
                time.sleep(5)
                continue
            
            try:
                # Mark as processing
                self.update_job_status(job['id'], 'processing')
                
                # Send to ComfyUI
                prompt_id = self.submit_to_comfyui(job)
                
                # Poll until complete
                result = self.wait_for_completion(prompt_id)
                
                # Download and save
                image_path = self.download_result(result)
                
                # Mark as completed
                self.update_job_status(
                    job['id'], 
                    'completed',
                    image_path=image_path
                )
                
            except Exception as e:
                # Handle retry
                if job['retry_count'] < 3:
                    self.retry_job(job['id'])
                else:
                    self.update_job_status(
                        job['id'],
                        'failed',
                        error=str(e)
                    )
    
    def fetch_next_job(self):
        cur = self.db.cursor()
        cur.execute("""
            UPDATE job_queue 
            SET status = 'processing', started_at = NOW()
            WHERE id = (
                SELECT id FROM job_queue 
                WHERE status = 'pending'
                ORDER BY priority DESC, created_at ASC
                LIMIT 1
                FOR UPDATE SKIP LOCKED
            )
            RETURNING *
        """)
        return cur.fetchone()
```

#### Docker Compose Addition
```yaml
comfyui-worker:
  build: ./comfyui-worker
  container_name: comfyui-worker
  networks: ['skynet']
  restart: unless-stopped
  environment:
    - DATABASE_URL=postgresql://user:pass@postgres/db
    - COMFYUI_URL=http://comfyui:8188
    - WORKER_THREADS=2
  depends_on:
    - postgres
    - comfyui
```

### Opção B: Redis Queue
```python
# Using RQ (Redis Queue)
from redis import Redis
from rq import Queue
import requests

redis_conn = Redis(host='redis', port=6379)
queue = Queue('comfyui-jobs', connection=redis_conn)

def process_image(prompt, workflow_type='qwen-image'):
    """Job function"""
    response = requests.post(
        "http://comfyui:8188/prompt",
        json=build_workflow(prompt, workflow_type)
    )
    prompt_id = response.json()["prompt_id"]
    return wait_and_download(prompt_id)

# Enqueue job
job = queue.enqueue(
    process_image,
    args=("beautiful sunset", "qwen-image"),
    job_timeout='10m',
    retry=Retry(max=3)
)
```

### n8n Dashboard Workflow
```
Schedule (every 1 minute)
→ PostgreSQL (count pending jobs)
→ IF (pending > 0)
  → PostgreSQL (get job details)
  → Slack/Email (notify team)
→ PostgreSQL (cleanup old completed jobs)
```

### API para Submissão de Jobs
```python
# FastAPI endpoint
from fastapi import FastAPI
import psycopg2

app = FastAPI()

@app.post("/api/jobs")
async def create_job(prompt: str, priority: int = 0):
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO job_queue (prompt, priority, created_by)
        VALUES (%s, %s, %s)
        RETURNING id
    """, (prompt, priority, "api"))
    job_id = cur.fetchone()[0]
    conn.commit()
    return {"job_id": job_id, "status": "queued"}

@app.get("/api/jobs/{job_id}")
async def get_job_status(job_id: int):
    cur = conn.cursor()
    cur.execute("SELECT * FROM job_queue WHERE id = %s", (job_id,))
    job = cur.fetchone()
    return {
        "id": job[0],
        "status": job[1],
        "result": job[7],
        "created_at": job[9]
    }
```

### Casos de Uso
- Processar 1000 prompts durante a noite
- Geração de dataset para treinamento
- Sistema de requisições para múltiplos usuários
- Batch processing de variações de produto

### Benefícios
- Controle de recursos (não sobrecarrega GPU)
- Retry automático em falhas
- Priorização de jobs urgentes
- Histórico completo de execuções
- Fácil escalabilidade (add more workers)

### Complexidade
**Média** - Requer worker service e queue management

### Prioridade
⭐⭐⭐⭐ (Medium Term - 1 semana)

---

## 7. Multi-Model Pipeline

### Descrição
Sistema avançado que combina múltiplos modelos e workflows do ComfyUI em sequência, criando pipelines complexos de geração de conteúdo visual com diferentes estilos, resoluções e propósitos.

### Exemplo: Product Showcase Generator

#### Pipeline Completo
```
Input: "Create a product showcase for wireless headphones"
↓
Step 1: Ollama (gera especificações)
  Output: {
    "name": "SoundWave Pro",
    "features": ["ANC", "40h battery", "premium leather"],
    "target": "audiophiles",
    "style": "modern minimalist"
  }
↓
Step 2: ComfyUI Workflow 1 - Hero Image
  Model: Qwen-Image (high quality)
  Prompt: "Professional product photography of wireless headphones,
           modern minimalist style, dramatic lighting, 4K, magazine quality"
  Output: hero_image.png
↓
Step 3: ComfyUI Workflow 2 - 4 Lifestyle Variations
  Model: Qwen-Image (batch mode)
  Prompts:
    - "Person wearing headphones in coffee shop, natural lighting"
    - "Headphones on wooden desk with laptop, cozy workspace"
    - "Close-up of headphones texture, premium leather detail"
    - "Headphones in travel case, adventure lifestyle"
  Output: lifestyle_01.png to lifestyle_04.png
↓
Step 4: Ollama (gera descrições para cada)
  For each image: Generate marketing copy
  Output: [
    "Perfect for your daily commute...",
    "Enhance your productivity...",
    ...
  ]
↓
Step 5: PostgreSQL (salva galeria completa)
  Table: product_galleries
  Fields: product_id, hero_image, lifestyle_images[], descriptions[]
```

### Implementação n8n
```
Webhook (receive product brief)
→ Ollama node (generate specs)
→ HTTP Request (ComfyUI hero image)
  - workflow: qwen-image-hq
  - wait for completion
→ Loop node (4 iterations)
  → HTTP Request (ComfyUI lifestyle image)
  → Ollama node (generate caption)
  → Add to array
→ PostgreSQL (insert gallery)
→ Generate HTML gallery
→ Return webhook response
```

### Caso de Uso: E-commerce Automation
```python
class ProductShowcaseGenerator:
    def __init__(self):
        self.ollama = OllamaClient()
        self.comfyui = ComfyUIClient()
        self.db = PostgresClient()
    
    async def generate_showcase(self, product_info):
        # 1. AI-generated specs
        specs = await self.ollama.generate_specs(product_info)
        
        # 2. Hero image (high quality)
        hero = await self.comfyui.generate(
            prompt=specs['hero_prompt'],
            workflow='qwen-image',
            quality='high',
            size='2048x2048'
        )
        
        # 3. Lifestyle images (batch)
        lifestyle_tasks = [
            self.comfyui.generate(
                prompt=prompt,
                workflow='qwen-image',
                quality='medium',
                size='1024x1024'
            )
            for prompt in specs['lifestyle_prompts']
        ]
        lifestyle_images = await asyncio.gather(*lifestyle_tasks)
        
        # 4. Generate captions
        captions = await self.ollama.generate_captions(
            lifestyle_images,
            product_context=specs
        )
        
        # 5. Store complete gallery
        gallery_id = self.db.insert_gallery({
            'product_id': product_info['id'],
            'hero_image': hero,
            'lifestyle_images': lifestyle_images,
            'captions': captions,
            'specs': specs
        })
        
        return gallery_id
```

### Workflows Múltiplos Disponíveis
```json
{
  "workflows": {
    "hero": {
      "model": "qwen-image",
      "quality": "ultra",
      "steps": 50,
      "vram": "12GB"
    },
    "lifestyle": {
      "model": "qwen-image",
      "quality": "high",
      "steps": 30,
      "vram": "8GB"
    },
    "thumbnail": {
      "model": "sdxl-turbo",
      "quality": "fast",
      "steps": 4,
      "vram": "4GB"
    },
    "variation": {
      "model": "qwen-edit",
      "quality": "medium",
      "steps": 20,
      "vram": "6GB"
    }
  }
}
```

### Advanced: Style Transfer Pipeline
```
Original Image
↓
ComfyUI (extract style with Qwen)
↓
Generate 5 variations:
  - Cyberpunk style
  - Watercolor painting
  - 3D render
  - Sketch
  - Pixel art
↓
User selects favorite
↓
ComfyUI (refine selected style)
↓
Generate final 4K version
```

### Benefícios
- Conteúdo completo automatizado
- Consistência de estilo através das imagens
- Economia de tempo (minutos vs horas)
- Experimentação rápida de variações

### Casos de Uso Reais
- **E-commerce**: Gerar todas as imagens de produto
- **Marketing**: Criar campanhas visuais completas
- **Branding**: Explorar identidades visuais
- **Editorial**: Ilustrações para artigos/posts

### Complexidade
**Alta** - Orquestração complexa de múltiplos serviços

### Prioridade
⭐⭐⭐ (Long Term - 2+ semanas)

---

## 8. WebSocket Real-time Integration

### Descrição
Conexão WebSocket direta ao ComfyUI para receber atualizações em tempo real do progresso de geração, preview images intermediários e notificações de conclusão, permitindo criar interfaces web responsivas e interativas.

### Arquitetura

#### Frontend WebSocket Connection
```javascript
// frontend/comfyui-client.js
class ComfyUIWebSocket {
    constructor(serverUrl = 'ws://localhost:8188/ws') {
        this.ws = new WebSocket(serverUrl);
        this.clientId = this.generateClientId();
        this.callbacks = {};
        
        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleMessage(data);
        };
    }
    
    handleMessage(data) {
        const { type, data: payload } = data;
        
        switch(type) {
            case 'progress':
                // Update progress bar
                this.updateProgress(payload.value, payload.max);
                console.log(`Progress: ${payload.value}/${payload.max} steps`);
                break;
                
            case 'executing':
                // Show which node is currently running
                console.log(`Executing node: ${payload.node}`);
                break;
                
            case 'executed':
                // Preview intermediate images
                if (payload.output && payload.output.images) {
                    this.showPreview(payload.output.images);
                }
                break;
                
            case 'execution_complete':
                // Final result ready
                this.onComplete(payload.prompt_id);
                break;
                
            case 'execution_error':
                // Handle error
                this.onError(payload.exception_message);
                break;
        }
    }
    
    updateProgress(current, total) {
        const percent = (current / total) * 100;
        document.getElementById('progress-bar').style.width = `${percent}%`;
        document.getElementById('progress-text').textContent = 
            `${current}/${total} steps (${percent.toFixed(1)}%)`;
    }
    
    showPreview(images) {
        const previewContainer = document.getElementById('preview-container');
        images.forEach(img => {
            const imgElement = document.createElement('img');
            imgElement.src = `/view?filename=${img.filename}`;
            previewContainer.appendChild(imgElement);
        });
    }
    
    async submitPrompt(workflow) {
        const response = await fetch('http://localhost:8188/prompt', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                prompt: workflow,
                client_id: this.clientId
            })
        });
        
        const result = await response.json();
        return result.prompt_id;
    }
}

// Usage
const client = new ComfyUIWebSocket();

document.getElementById('generate-btn').addEventListener('click', async () => {
    const prompt = document.getElementById('prompt-input').value;
    const workflow = buildWorkflow(prompt);
    
    const promptId = await client.submitPrompt(workflow);
    console.log(`Job submitted: ${promptId}`);
    
    // Progress updates happen automatically via WebSocket
});
```

#### React Component Example
```javascript
// components/ImageGenerator.jsx
import { useEffect, useState } from 'react';

function ImageGenerator() {
    const [progress, setProgress] = useState(0);
    const [currentStep, setCurrentStep] = useState('');
    const [previewImages, setPreviewImages] = useState([]);
    const [finalImage, setFinalImage] = useState(null);
    const [isGenerating, setIsGenerating] = useState(false);
    
    useEffect(() => {
        const ws = new WebSocket('ws://localhost:8188/ws');
        
        ws.onmessage = (event) => {
            const { type, data } = JSON.parse(event.data);
            
            if (type === 'progress') {
                setProgress((data.value / data.max) * 100);
            } else if (type === 'executing') {
                setCurrentStep(data.node);
            } else if (type === 'executed') {
                if (data.output?.images) {
                    setPreviewImages(prev => [...prev, ...data.output.images]);
                }
            } else if (type === 'execution_complete') {
                setIsGenerating(false);
                fetchFinalImage(data.prompt_id);
            }
        };
        
        return () => ws.close();
    }, []);
    
    const generateImage = async (prompt) => {
        setIsGenerating(true);
        setProgress(0);
        setPreviewImages([]);
        
        const workflow = buildWorkflow(prompt);
        const response = await fetch('http://localhost:8188/prompt', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt: workflow })
        });
    };
    
    return (
        <div className="image-generator">
            <input type="text" placeholder="Enter prompt..." />
            <button onClick={() => generateImage(...)}>
                {isGenerating ? 'Generating...' : 'Generate'}
            </button>
            
            {isGenerating && (
                <div className="progress-section">
                    <div className="progress-bar">
                        <div style={{ width: `${progress}%` }} />
                    </div>
                    <p>Current step: {currentStep}</p>
                    <p>{progress.toFixed(1)}% complete</p>
                </div>
            )}
            
            {previewImages.length > 0 && (
                <div className="preview-grid">
                    <h3>Preview Images</h3>
                    {previewImages.map((img, i) => (
                        <img key={i} src={`/view?filename=${img.filename}`} />
                    ))}
                </div>
            )}
            
            {finalImage && (
                <div className="final-result">
                    <h2>Final Result</h2>
                    <img src={finalImage} alt="Generated" />
                </div>
            )}
        </div>
    );
}
```

### n8n WebSocket Integration
```
Webhook (trigger generation)
→ Set Variable (store client_id)
→ HTTP Request (POST to ComfyUI)
→ WebSocket node (listen for updates)
  - On progress: Update database
  - On complete: Download image
→ PostgreSQL (store final result)
→ Webhook Response (return status)
```

### Real-time Dashboard
```html
<!-- dashboard.html -->
<!DOCTYPE html>
<html>
<head>
    <title>ComfyUI Live Dashboard</title>
    <style>
        .job-card {
            border: 1px solid #ccc;
            padding: 20px;
            margin: 10px;
            border-radius: 8px;
        }
        .progress-bar {
            width: 100%;
            height: 20px;
            background: #f0f0f0;
            border-radius: 10px;
            overflow: hidden;
        }
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #4CAF50, #8BC34A);
            transition: width 0.3s;
        }
    </style>
</head>
<body>
    <h1>ComfyUI Live Dashboard</h1>
    <div id="jobs-container"></div>
    
    <script>
        const ws = new WebSocket('ws://localhost:8188/ws');
        const jobs = new Map();
        
        ws.onmessage = (event) => {
            const { type, data } = JSON.parse(event.data);
            const jobId = data.prompt_id || data.sid;
            
            if (!jobs.has(jobId)) {
                createJobCard(jobId);
            }
            
            updateJobCard(jobId, type, data);
        };
        
        function createJobCard(jobId) {
            const card = document.createElement('div');
            card.className = 'job-card';
            card.id = `job-${jobId}`;
            card.innerHTML = `
                <h3>Job: ${jobId}</h3>
                <p class="status">Status: <span>Queued</span></p>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: 0%"></div>
                </div>
                <p class="progress-text">0%</p>
                <div class="preview-area"></div>
            `;
            document.getElementById('jobs-container').appendChild(card);
            jobs.set(jobId, { status: 'queued', progress: 0 });
        }
        
        function updateJobCard(jobId, type, data) {
            const card = document.getElementById(`job-${jobId}`);
            if (!card) return;
            
            const job = jobs.get(jobId);
            
            if (type === 'progress') {
                const percent = (data.value / data.max) * 100;
                job.progress = percent;
                card.querySelector('.progress-fill').style.width = `${percent}%`;
                card.querySelector('.progress-text').textContent = 
                    `${percent.toFixed(1)}% (${data.value}/${data.max} steps)`;
            } else if (type === 'executing') {
                job.status = 'executing';
                card.querySelector('.status span').textContent = 
                    `Executing node: ${data.node}`;
            } else if (type === 'execution_complete') {
                job.status = 'completed';
                card.querySelector('.status span').textContent = 'Completed ✓';
                card.style.borderColor = '#4CAF50';
            }
        }
    </script>
</body>
</html>
```

### Casos de Uso
- Interface web customizada para ComfyUI
- Monitoramento de múltiplos jobs simultâneos
- Preview em tempo real de imagens intermediárias
- Cancelamento de jobs em andamento
- Dashboard de status para equipe

### Benefícios
- Experiência de usuário muito melhor
- Feedback imediato de progresso
- Possibilidade de cancel jobs
- Debug facilitado (ver qual node está executando)
- Múltiplos clients podem monitorar o mesmo job

### Complexidade
**Média** - Requer conhecimento de WebSockets

### Prioridade
⭐⭐⭐ (Medium Term - 1 semana)

---

## 9. Container Sidecar Pattern - Storage & Queue

### Descrição
Adicionar containers auxiliares ao ecossistema para fornecer funcionalidades de armazenamento escalável (MinIO S3-compatible), sistema de filas (Redis) e cache distribuído, melhorando performance e escalabilidade do sistema.

### Serviços Adicionais

#### A) MinIO - S3-Compatible Object Storage
```yaml
# docker-compose.yml addition
minio:
  image: minio/minio:latest
  container_name: minio
  networks: ['skynet']
  restart: unless-stopped
  ports:
    - "9000:9000"      # API
    - "9001:9001"      # Console
  environment:
    - MINIO_ROOT_USER=admin
    - MINIO_ROOT_PASSWORD=${MINIO_PASSWORD:-minioadmin123}
    - MINIO_BROWSER_REDIRECT_URL=http://localhost:9001
  command: server /data --console-address ":9001"
  volumes:
    - minio_storage:/data
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:9000/minio/health/live"]
    interval: 30s
    timeout: 20s
    retries: 3

volumes:
  minio_storage:
```

**Benefícios do MinIO:**
- Armazenamento ilimitado de imagens geradas
- Interface S3-compatible (fácil integração)
- Buckets organizados por projeto/cliente
- Versionamento de imagens
- Políticas de acesso granulares
- Console web para gerenciamento

**Uso com n8n:**
```
ComfyUI generates image
→ Download image
→ n8n MinIO node:
  - Upload to bucket 'generated-images'
  - Get public URL
→ PostgreSQL: Store URL
→ Return URL to client
```

**Python SDK Example:**
```python
from minio import Minio
from datetime import timedelta

minio_client = Minio(
    "minio:9000",
    access_key="admin",
    secret_key="minioadmin123",
    secure=False
)

# Create bucket if not exists
if not minio_client.bucket_exists("comfyui-outputs"):
    minio_client.make_bucket("comfyui-outputs")

# Upload image
minio_client.fput_object(
    "comfyui-outputs",
    "images/2025/11/hero_image.png",
    "/tmp/generated_image.png",
    content_type="image/png"
)

# Get presigned URL (temporary access)
url = minio_client.presigned_get_object(
    "comfyui-outputs",
    "images/2025/11/hero_image.png",
    expires=timedelta(days=7)
)
```

#### B) Redis - Queue & Cache
```yaml
# docker-compose.yml addition
redis:
  image: redis:7-alpine
  container_name: redis
  networks: ['skynet']
  restart: unless-stopped
  ports:
    - "6379:6379"
  command: redis-server --appendonly yes --maxmemory 2gb --maxmemory-policy allkeys-lru
  volumes:
    - redis_storage:/data
  healthcheck:
    test: ["CMD", "redis-cli", "ping"]
    interval: 10s
    timeout: 3s
    retries: 3

volumes:
  redis_storage:
```

**Benefícios do Redis:**
- Job queue para ComfyUI tasks
- Cache de prompts frequentes
- Rate limiting
- Session storage
- Pub/Sub para eventos

**Job Queue Implementation:**
```python
# comfyui_worker.py
from rq import Worker, Queue, Connection
from redis import Redis

redis_conn = Redis(host='redis', port=6379)

def process_comfyui_job(prompt, workflow_type='qwen-image'):
    """Worker function"""
    import requests
    
    # Submit to ComfyUI
    response = requests.post(
        'http://comfyui:8188/prompt',
        json={'prompt': build_workflow(prompt, workflow_type)}
    )
    
    prompt_id = response.json()['prompt_id']
    
    # Wait and download
    result = wait_for_completion(prompt_id)
    
    # Upload to MinIO
    upload_to_minio(result['image_path'])
    
    return {
        'status': 'completed',
        'image_url': result['url'],
        'prompt_id': prompt_id
    }

# Start worker
if __name__ == '__main__':
    with Connection(redis_conn):
        worker = Worker(['comfyui-queue'])
        worker.work()
```

**Enqueue from n8n:**
```python
# n8n Python code node
from redis import Redis
from rq import Queue

redis_conn = Redis(host='redis', port=6379)
queue = Queue('comfyui-queue', connection=redis_conn)

# Add job
job = queue.enqueue(
    'comfyui_worker.process_comfyui_job',
    args=[item['prompt'], 'qwen-image'],
    job_timeout='15m',
    result_ttl=86400  # Keep result for 24h
)

return {
    'job_id': job.id,
    'status': 'queued'
}
```

**Cache Implementation:**
```python
import hashlib
import json
from redis import Redis

redis_client = Redis(host='redis', port=6379, decode_responses=True)

def get_cached_image(prompt, workflow_type='qwen-image'):
    """Check if prompt was generated before"""
    cache_key = hashlib.md5(
        f"{prompt}:{workflow_type}".encode()
    ).hexdigest()
    
    cached = redis_client.get(f"comfyui:cache:{cache_key}")
    
    if cached:
        return json.loads(cached)
    
    return None

def cache_image(prompt, workflow_type, image_url):
    """Cache generated image URL"""
    cache_key = hashlib.md5(
        f"{prompt}:{workflow_type}".encode()
    ).hexdigest()
    
    redis_client.setex(
        f"comfyui:cache:{cache_key}",
        timedelta(days=7),
        json.dumps({
            'image_url': image_url,
            'generated_at': datetime.now().isoformat()
        })
    )
```

#### C) Redis Commander (Optional - UI)
```yaml
redis-commander:
  image: rediscommander/redis-commander:latest
  container_name: redis-commander
  networks: ['skynet']
  restart: unless-stopped
  ports:
    - "8081:8081"
  environment:
    - REDIS_HOSTS=local:redis:6379
```

### Integrated Workflow Example
```
n8n Webhook receives request
↓
Check Redis cache (prompt hash)
├─ HIT: Return cached URL immediately
└─ MISS: Continue pipeline
    ↓
    Add job to Redis queue
    ↓
    Worker picks up job
    ↓
    ComfyUI generates image
    ↓
    Upload to MinIO
    ↓
    Cache result in Redis
    ↓
    Store metadata in PostgreSQL
    ↓
    Return URL
```

### Complete docker-compose.yml Stack
```yaml
version: '3.8'

services:
  postgres:
    # ... existing config ...
  
  n8n:
    # ... existing config ...
  
  ollama:
    # ... existing config ...
  
  qdrant:
    # ... existing config ...
  
  comfyui:
    # ... existing config with optimizations ...
  
  minio:
    image: minio/minio:latest
    # ... config above ...
  
  redis:
    image: redis:7-alpine
    # ... config above ...
  
  comfyui-worker:
    build: ./comfyui-worker
    container_name: comfyui-worker
    networks: ['skynet']
    restart: unless-stopped
    environment:
      - REDIS_URL=redis://redis:6379
      - COMFYUI_URL=http://comfyui:8188
      - MINIO_ENDPOINT=minio:9000
      - MINIO_ACCESS_KEY=admin
      - MINIO_SECRET_KEY=${MINIO_PASSWORD}
    depends_on:
      - redis
      - comfyui
      - minio
```

### Monitoring Stack
```yaml
  # Optional: Add monitoring
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    networks: ['skynet']
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_storage:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
  
  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    networks: ['skynet']
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_INSTALL_PLUGINS=redis-datasource
    volumes:
      - grafana_storage:/var/lib/grafana
    depends_on:
      - prometheus
```

### Complexidade
**Média** - Requer conhecimento de Docker Compose e APIs

### Prioridade
⭐⭐⭐⭐ (Medium Term - 1 semana)

---

## 10. AI Agent Framework Integration

### Descrição
Integrar ComfyUI como ferramenta (tool) em frameworks de AI Agents como LangChain, AutoGen ou CrewAI, permitindo que agentes inteligentes gerem imagens autonomamente como parte de workflows de decisão complexos.

### LangChain Integration

#### Setup
```python
# langchain_comfyui_integration.py
from langchain.tools import Tool
from langchain.agents import initialize_agent, AgentType
from langchain_community.llms import Ollama
import requests
import json
from typing import Optional

class ComfyUITool:
    def __init__(self, base_url: str = "http://localhost:8188"):
        self.base_url = base_url
    
    def generate_image(self, prompt: str, workflow_type: str = "qwen-image") -> str:
        """
        Generate an image using ComfyUI
        
        Args:
            prompt: Text description of the image
            workflow_type: Type of workflow to use
        
        Returns:
            URL or path to the generated image
        """
        try:
            # Build workflow
            workflow = self._build_workflow(prompt, workflow_type)
            
            # Submit to ComfyUI
            response = requests.post(
                f"{self.base_url}/prompt",
                json={"prompt": workflow}
            )
            response.raise_for_status()
            
            prompt_id = response.json()["prompt_id"]
            
            # Wait for completion
            image_path = self._wait_for_completion(prompt_id)
            
            return f"Image generated successfully: {image_path}"
        
        except Exception as e:
            return f"Error generating image: {str(e)}"
    
    def _build_workflow(self, prompt: str, workflow_type: str) -> dict:
        """Build ComfyUI workflow JSON"""
        # Load workflow template
        with open(f"./workflows/{workflow_type}.json", "r") as f:
            workflow = json.load(f)
        
        # Inject prompt into workflow
        # This varies based on workflow structure
        for node_id, node in workflow.items():
            if node.get("class_type") == "CLIPTextEncode":
                if "positive" in node.get("_meta", {}).get("title", "").lower():
                    node["inputs"]["text"] = prompt
        
        return workflow
    
    def _wait_for_completion(self, prompt_id: str, timeout: int = 300) -> str:
        """Poll ComfyUI until generation completes"""
        import time
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            response = requests.get(f"{self.base_url}/history/{prompt_id}")
            history = response.json()
            
            if prompt_id in history:
                outputs = history[prompt_id].get("outputs", {})
                for node_output in outputs.values():
                    if "images" in node_output:
                        images = node_output["images"]
                        if images:
                            return images[0]["filename"]
            
            time.sleep(2)
        
        raise TimeoutError("Image generation timed out")

# Create LangChain tool
comfyui_tool = ComfyUITool()

image_generator_tool = Tool(
    name="ImageGenerator",
    func=comfyui_tool.generate_image,
    description="""
    Useful for generating images from text descriptions.
    Input should be a detailed text description of the image you want to create.
    Example: 'a beautiful sunset over mountains with dramatic clouds'
    Returns the path to the generated image file.
    """
)

# Initialize LLM
llm = Ollama(
    model="llama3.2",
    base_url="http://localhost:11434"
)

# Create agent with ComfyUI tool
agent = initialize_agent(
    tools=[image_generator_tool],
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    max_iterations=5
)

# Use the agent
if __name__ == "__main__":
    response = agent.run(
        "I need a professional product photo of wireless headphones "
        "with dramatic lighting for my e-commerce store"
    )
    print(response)
```

#### Advanced Multi-Tool Agent
```python
# advanced_agent.py
from langchain.tools import Tool
from langchain.agents import initialize_agent
from langchain_community.llms import Ollama
from langchain_community.vectorstores import Qdrant
from langchain_community.embeddings import HuggingFaceEmbeddings

class MultiModalAgent:
    def __init__(self):
        self.comfyui = ComfyUITool()
        self.embeddings = HuggingFaceEmbeddings()
        self.qdrant = Qdrant(
            client=qdrant_client,
            collection_name="images",
            embeddings=self.embeddings
        )
    
    def search_similar_images(self, description: str) -> str:
        """Search for similar images in vector DB"""
        results = self.qdrant.similarity_search(description, k=3)
        return "\n".join([r.page_content for r in results])
    
    def generate_new_image(self, prompt: str) -> str:
        """Generate new image with ComfyUI"""
        return self.comfyui.generate_image(prompt)
    
    def analyze_image_with_ollama(self, image_path: str) -> str:
        """Analyze image using Ollama vision model"""
        # Implementation depends on Ollama vision support
        pass

# Create tools
tools = [
    Tool(
        name="SearchSimilarImages",
        func=agent.search_similar_images,
        description="Search for similar images in the database"
    ),
    Tool(
        name="GenerateImage",
        func=agent.generate_new_image,
        description="Generate a new image from text description"
    ),
    Tool(
        name="AnalyzeImage",
        func=agent.analyze_image_with_ollama,
        description="Analyze an existing image"
    )
]

llm = Ollama(model="llama3.2", base_url="http://localhost:11434")

agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# Complex query
result = agent.run("""
I need images for my coffee shop website. 
First, search for existing coffee-related images we have.
Then generate 3 new images:
1. Interior shot of cozy coffee shop
2. Close-up of latte art
3. Outdoor seating area
""")
```

### AutoGen Integration

```python
# autogen_comfyui.py
import autogen
from autogen import AssistantAgent, UserProxyAgent
import json

# Configure LLM
config_list = [{
    "model": "llama3.2",
    "base_url": "http://localhost:11434/v1",
    "api_key": "ollama"  # dummy key
}]

llm_config = {
    "config_list": config_list,
    "temperature": 0.7
}

# Create ComfyUI tool function
def generate_image_with_comfyui(prompt: str) -> dict:
    """
    Generate image using ComfyUI
    
    Args:
        prompt: Description of image to generate
    
    Returns:
        dict with status and image_path
    """
    comfyui = ComfyUITool()
    result = comfyui.generate_image(prompt)
    return {
        "status": "success",
        "message": result
    }

# Register function
autogen.register_function(
    generate_image_with_comfyui,
    caller=assistant,
    executor=user_proxy,
    description="Generate an image from a text description using ComfyUI"
)

# Create agents
assistant = AssistantAgent(
    name="DesignAssistant",
    llm_config=llm_config,
    system_message="""
    You are a creative design assistant that can generate images.
    When asked to create visuals, use the generate_image_with_comfyui function.
    Provide detailed, creative prompts to get the best results.
    """
)

user_proxy = UserProxyAgent(
    name="User",
    human_input_mode="NEVER",
    code_execution_config={
        "work_dir": "generated_images",
        "use_docker": False
    }
)

# Run conversation
user_proxy.initiate_chat(
    assistant,
    message="""
    Create a series of 3 images for a tech startup's landing page:
    1. Hero image with futuristic theme
    2. Team collaboration scene
    3. Product showcase
    """
)
```

### CrewAI Integration

```python
# crewai_comfyui.py
from crewai import Agent, Task, Crew
from langchain.tools import Tool
from langchain_community.llms import Ollama

# ComfyUI Tool
comfyui_tool = Tool(
    name="generate_image",
    func=ComfyUITool().generate_image,
    description="Generate images from text descriptions"
)

# Create specialized agents
visual_designer = Agent(
    role='Visual Designer',
    goal='Create stunning visual content',
    backstory="""
    You are an expert visual designer with years of experience
    in creating compelling imagery for brands and marketing campaigns.
    """,
    tools=[comfyui_tool],
    llm=Ollama(model="llama3.2", base_url="http://localhost:11434"),
    verbose=True
)

content_strategist = Agent(
    role='Content Strategist',
    goal='Plan and coordinate visual content strategy',
    backstory="""
    You excel at understanding brand needs and creating
    comprehensive visual content strategies.
    """,
    llm=Ollama(model="llama3.2", base_url="http://localhost:11434"),
    verbose=True
)

# Create tasks
planning_task = Task(
    description="""
    Analyze the client's request for a product launch campaign.
    Plan what types of images are needed and create detailed prompts.
    Client: Tech startup launching AI-powered productivity tool.
    """,
    agent=content_strategist,
    expected_output="Detailed list of required images with prompts"
)

generation_task = Task(
    description="""
    Based on the content strategy, generate all required images
    using the image generation tool. Ensure high quality and
    consistency across all visuals.
    """,
    agent=visual_designer,
    expected_output="Confirmation of all images generated with paths",
    context=[planning_task]
)

# Create and run crew
crew = Crew(
    agents=[content_strategist, visual_designer],
    tasks=[planning_task, generation_task],
    verbose=2
)

result = crew.kickoff()
print(result)
```

### Use Cases

#### Automated Content Creation Pipeline
```python
# Agent decides when to generate images
agent.run("""
Create a complete blog post about sustainable living with:
- Title and introduction
- 3 main sections with text
- Generate 1 header image and 3 section images
- Conclusion
- Meta description
""")
# Agent autonomously generates text AND images
```

#### Smart Product Catalog
```python
# Agent processes product data and generates visuals
agent.run("""
We have 50 new products without images.
For each product:
1. Read the product description from database
2. Generate appropriate product image
3. Create 2 lifestyle variations
4. Store all images with proper metadata
""")
```

#### A/B Testing Assistant
```python
# Agent generates variations for testing
agent.run("""
Create 5 variations of our landing page hero image:
- Different color schemes
- Different compositions
- Different moods
Optimize for conversion
""")
```

### Benefits
- Agents make intelligent decisions about when to generate images
- Autonomous multi-step workflows
- Natural language interface to ComfyUI
- Easy integration with other tools (web scraping, APIs, databases)
- Self-correcting (agent can retry with better prompts)

### Complexidade
**Alta** - Requer conhecimento de AI agent frameworks

### Prioridade
⭐⭐⭐ (Long Term - 2 semanas)

---

## 11. Prompt Management System

### Descrição
Sistema completo de gerenciamento de prompts que permite salvar, versionar, organizar, testar e compartilhar prompts e workflows do ComfyUI, incluindo A/B testing, analytics e recomendação de prompts baseado em histórico.

### Database Schema

```sql
-- Prompt Templates Table
CREATE TABLE prompt_templates (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100),
    positive_prompt TEXT NOT NULL,
    negative_prompt TEXT,
    workflow_json JSONB NOT NULL,
    workflow_type VARCHAR(50) DEFAULT 'qwen-image',
    
    -- Parameters
    parameters JSONB, -- {"steps": 30, "cfg": 7.5, "size": "1024x1024"}
    
    -- Metadata
    tags TEXT[],
    author VARCHAR(100),
    is_public BOOLEAN DEFAULT false,
    is_favorite BOOLEAN DEFAULT false,
    
    -- Analytics
    usage_count INTEGER DEFAULT 0,
    success_rate FLOAT DEFAULT 0.0,
    avg_rating FLOAT,
    
    -- Versioning
    parent_template_id INTEGER REFERENCES prompt_templates(id),
    version INTEGER DEFAULT 1,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_used_at TIMESTAMP
);

-- Prompt Executions Table
CREATE TABLE prompt_executions (
    id SERIAL PRIMARY KEY,
    template_id INTEGER REFERENCES prompt_templates(id),
    prompt_used TEXT,
    workflow_used JSONB,
    
    -- Results
    status VARCHAR(20), -- 'success', 'failed', 'cancelled'
    image_path TEXT,
    image_url TEXT,
    comfyui_prompt_id TEXT,
    
    -- Performance
    generation_time_seconds FLOAT,
    vram_used_gb FLOAT,
    
    -- Quality feedback
    user_rating INTEGER CHECK (user_rating BETWEEN 1 AND 5),
    user_feedback TEXT,
    
    -- Metadata
    user_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);

-- A/B Test Campaigns
CREATE TABLE ab_test_campaigns (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    base_prompt_id INTEGER REFERENCES prompt_templates(id),
    
    -- Variants
    variant_prompts INTEGER[], -- Array of template IDs
    
    -- Status
    status VARCHAR(20) DEFAULT 'draft', -- 'draft', 'running', 'completed'
    target_executions INTEGER DEFAULT 100,
    current_executions INTEGER DEFAULT 0,
    
    -- Results
    winner_template_id INTEGER,
    
    -- Timestamps
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Prompt Collections (Categories/Projects)
CREATE TABLE prompt_collections (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    template_ids INTEGER[],
    is_shared BOOLEAN DEFAULT false,
    created_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_templates_category ON prompt_templates(category);
CREATE INDEX idx_templates_tags ON prompt_templates USING GIN(tags);
CREATE INDEX idx_templates_usage ON prompt_templates(usage_count DESC);
CREATE INDEX idx_executions_template ON prompt_executions(template_id);
CREATE INDEX idx_executions_created ON prompt_executions(created_at DESC);
```

### API Implementation (FastAPI)

```python
# prompt_manager_api.py
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
import psycopg2
from datetime import datetime

app = FastAPI(title="ComfyUI Prompt Manager")

# Models
class PromptTemplate(BaseModel):
    name: str
    description: Optional[str]
    category: str
    positive_prompt: str
    negative_prompt: Optional[str]
    workflow_json: dict
    workflow_type: str = "qwen-image"
    parameters: Optional[dict]
    tags: List[str] = []
    is_public: bool = False

class PromptExecution(BaseModel):
    template_id: int
    user_id: Optional[str]
    rating: Optional[int]
    feedback: Optional[str]

# Endpoints
@app.post("/api/prompts")
async def create_prompt(prompt: PromptTemplate):
    """Create new prompt template"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        INSERT INTO prompt_templates 
        (name, description, category, positive_prompt, negative_prompt,
         workflow_json, workflow_type, parameters, tags, is_public)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
    """, (
        prompt.name, prompt.description, prompt.category,
        prompt.positive_prompt, prompt.negative_prompt,
        json.dumps(prompt.workflow_json), prompt.workflow_type,
        json.dumps(prompt.parameters), prompt.tags, prompt.is_public
    ))
    
    template_id = cur.fetchone()[0]
    conn.commit()
    
    return {"id": template_id, "status": "created"}

@app.get("/api/prompts")
async def list_prompts(
    category: Optional[str] = None,
    tags: Optional[List[str]] = Query(None),
    sort_by: str = "created_at",
    limit: int = 50
):
    """List prompt templates with filters"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    query = "SELECT * FROM prompt_templates WHERE 1=1"
    params = []
    
    if category:
        query += " AND category = %s"
        params.append(category)
    
    if tags:
        query += " AND tags && %s"
        params.append(tags)
    
    query += f" ORDER BY {sort_by} DESC LIMIT %s"
    params.append(limit)
    
    cur.execute(query, params)
    results = cur.fetchall()
    
    return {"prompts": [dict(zip([d[0] for d in cur.description], r)) for r in results]}

@app.get("/api/prompts/{template_id}")
async def get_prompt(template_id: int):
    """Get specific prompt template"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT p.*, 
               COUNT(e.id) as total_executions,
               AVG(e.user_rating) as avg_rating,
               AVG(e.generation_time_seconds) as avg_time
        FROM prompt_templates p
        LEFT JOIN prompt_executions e ON e.template_id = p.id
        WHERE p.id = %s
        GROUP BY p.id
    """, (template_id,))
    
    result = cur.fetchone()
    
    if not result:
        raise HTTPException(status_code=404, detail="Template not found")
    
    return dict(zip([d[0] for d in cur.description], result))

@app.post("/api/prompts/{template_id}/execute")
async def execute_prompt(template_id: int, variables: Optional[dict] = None):
    """Execute a prompt template"""
    # Get template
    template = await get_prompt(template_id)
    
    # Apply variables to prompt
    prompt = template['positive_prompt']
    if variables:
        for key, value in variables.items():
            prompt = prompt.replace(f"{{{key}}}", value)
    
    # Submit to ComfyUI
    comfyui_response = requests.post(
        "http://localhost:8188/prompt",
        json={"prompt": template['workflow_json']}
    )
    
    prompt_id = comfyui_response.json()['prompt_id']
    
    # Log execution
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO prompt_executions 
        (template_id, prompt_used, workflow_used, comfyui_prompt_id, status)
        VALUES (%s, %s, %s, %s, 'running')
        RETURNING id
    """, (template_id, prompt, json.dumps(template['workflow_json']), prompt_id))
    
    execution_id = cur.fetchone()[0]
    conn.commit()
    
    # Update template usage
    cur.execute("""
        UPDATE prompt_templates 
        SET usage_count = usage_count + 1,
            last_used_at = NOW()
        WHERE id = %s
    """, (template_id,))
    conn.commit()
    
    return {
        "execution_id": execution_id,
        "comfyui_prompt_id": prompt_id,
        "status": "submitted"
    }

@app.put("/api/executions/{execution_id}/feedback")
async def add_feedback(execution_id: int, rating: int, feedback: Optional[str] = None):
    """Add rating and feedback to execution"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        UPDATE prompt_executions
        SET user_rating = %s, user_feedback = %s
        WHERE id = %s
    """, (rating, feedback, execution_id))
    
    conn.commit()
    
    # Recalculate template avg rating
    cur.execute("""
        UPDATE prompt_templates
        SET avg_rating = (
            SELECT AVG(user_rating)
            FROM prompt_executions
            WHERE template_id = (
                SELECT template_id FROM prompt_executions WHERE id = %s
            )
        )
        WHERE id = (SELECT template_id FROM prompt_executions WHERE id = %s)
    """, (execution_id, execution_id))
    
    conn.commit()
    
    return {"status": "feedback recorded"}

@app.get("/api/prompts/recommend")
async def recommend_prompts(user_id: str, limit: int = 10):
    """Recommend prompts based on user history"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Get user's favorite categories and tags
    cur.execute("""
        WITH user_prefs AS (
            SELECT 
                p.category,
                unnest(p.tags) as tag,
                COUNT(*) as usage
            FROM prompt_executions e
            JOIN prompt_templates p ON p.id = e.template_id
            WHERE e.user_id = %s AND e.user_rating >= 4
            GROUP BY p.category, tag
        )
        SELECT DISTINCT p.*
        FROM prompt_templates p
        JOIN user_prefs up ON (
            p.category = up.category OR
            up.tag = ANY(p.tags)
        )
        WHERE p.id NOT IN (
            SELECT template_id FROM prompt_executions WHERE user_id = %s
        )
        ORDER BY p.avg_rating DESC NULLS LAST, p.usage_count DESC
        LIMIT %s
    """, (user_id, user_id, limit))
    
    results = cur.fetchall()
    return {"recommendations": [dict(zip([d[0] for d in cur.description], r)) for r in results]}

@app.post("/api/ab-tests")
async def create_ab_test(
    name: str,
    base_prompt_id: int,
    variant_prompt_ids: List[int],
    target_executions: int = 100
):
    """Create A/B test campaign"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        INSERT INTO ab_test_campaigns
        (name, base_prompt_id, variant_prompts, target_executions, status)
        VALUES (%s, %s, %s, %s, 'running')
        RETURNING id
    """, (name, base_prompt_id, variant_prompt_ids, target_executions))
    
    campaign_id = cur.fetchone()[0]
    conn.commit()
    
    return {"campaign_id": campaign_id, "status": "created"}

@app.get("/api/ab-tests/{campaign_id}/results")
async def get_ab_test_results(campaign_id: int):
    """Get A/B test results"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT 
            p.id,
            p.name,
            COUNT(e.id) as executions,
            AVG(e.user_rating) as avg_rating,
            AVG(e.generation_time_seconds) as avg_time,
            COUNT(CASE WHEN e.user_rating >= 4 THEN 1 END)::FLOAT / COUNT(e.id) as success_rate
        FROM ab_test_campaigns c
        CROSS JOIN unnest(ARRAY[c.base_prompt_id] || c.variant_prompts) as variant_id
        JOIN prompt_templates p ON p.id = variant_id
        LEFT JOIN prompt_executions e ON e.template_id = p.id
        WHERE c.id = %s
        GROUP BY p.id, p.name
        ORDER BY success_rate DESC
    """, (campaign_id,))
    
    results = cur.fetchall()
    return {"variants": [dict(zip([d[0] for d in cur.description], r)) for r in results]}
```

### n8n Integration Workflow

```
Cron (daily)
→ PostgreSQL (get top performing prompts from last week)
→ Email/Slack (send report)

Webhook (user rates image)
→ PostgreSQL (update prompt_executions)
→ PostgreSQL (recalculate template avg_rating)
→ IF (rating >= 4)
  → PostgreSQL (add to user favorites)
```

### Web UI (Simple Example)

```html
<!-- prompt_library.html -->
<!DOCTYPE html>
<html>
<head>
    <title>ComfyUI Prompt Library</title>
    <style>
        .prompt-card {
            border: 1px solid #ddd;
            padding: 20px;
            margin: 10px;
            border-radius: 8px;
        }
        .prompt-card:hover {
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        .tags {
            display: flex;
            gap: 5px;
            margin-top: 10px;
        }
        .tag {
            background: #e0e0e0;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
        }
        .rating {
            color: #ffa500;
        }
    </style>
</head>
<body>
    <h1>ComfyUI Prompt Library</h1>
    
    <div class="filters">
        <select id="category-filter">
            <option value="">All Categories</option>
            <option value="product">Product Photography</option>
            <option value="landscape">Landscape</option>
            <option value="portrait">Portrait</option>
        </select>
        
        <input type="text" id="search" placeholder="Search prompts..." />
        
        <select id="sort">
            <option value="usage_count">Most Used</option>
            <option value="avg_rating">Highest Rated</option>
            <option value="created_at">Newest</option>
        </select>
    </div>
    
    <div id="prompts-container"></div>
    
    <script>
        async function loadPrompts() {
            const category = document.getElementById('category-filter').value;
            const sort = document.getElementById('sort').value;
            
            const response = await fetch(
                `/api/prompts?category=${category}&sort_by=${sort}`
            );
            const data = await response.json();
            
            const container = document.getElementById('prompts-container');
            container.innerHTML = data.prompts.map(prompt => `
                <div class="prompt-card">
                    <h3>${prompt.name}</h3>
                    <p>${prompt.description || ''}</p>
                    <p class="rating">★ ${prompt.avg_rating?.toFixed(1) || 'N/A'}</p>
                    <p>Used ${prompt.usage_count} times</p>
                    <div class="tags">
                        ${prompt.tags.map(tag => `
                            <span class="tag">${tag}</span>
                        `).join('')}
                    </div>
                    <button onclick="usePrompt(${prompt.id})">
                        Use This Prompt
                    </button>
                </div>
            `).join('');
        }
        
        async function usePrompt(templateId) {
            const response = await fetch(`/api/prompts/${templateId}/execute`, {
                method: 'POST'
            });
            const data = await response.json();
            alert(`Image generation started! Execution ID: ${data.execution_id}`);
        }
        
        // Load on page load
        loadPrompts();
        
        // Update on filter change
        document.getElementById('category-filter').addEventListener('change', loadPrompts);
        document.getElementById('sort').addEventListener('change', loadPrompts);
    </script>
</body>
</html>
```

### Benefits
- Organize and discover successful prompts
- Learn what works best over time
- A/B test different approaches
- Share prompts with team
- Track ROI of different prompts
- Version control for iterations

### Complexidade
**Média-Alta** - Requer full-stack development

### Prioridade
⭐⭐⭐ (Medium-Long Term - 1-2 semanas)

---

## 12. Model Hot-Swapping & Dynamic Resource Management

### Descrição
Sistema inteligente que permite trocar modelos dinamicamente baseado em requisitos de qualidade, velocidade e recursos disponíveis. O sistema monitora VRAM, tempo de resposta e qualidade desejada para escolher automaticamente o melhor modelo/configuração.

### Model Configuration Database

```json
// models_config.json
{
  "models": {
    "qwen-image-ultra": {
      "path": "qwen_image_edit_2509_fp8_e4m3fn.safetensors",
      "type": "diffusion",
      "quality": "ultra",
      "vram_required_gb": 14,
      "avg_time_seconds": 100,
      "recommended_steps": 50,
      "max_resolution": "2048x2048",
      "use_cases": ["hero_images", "print_quality", "professional"],
      "cost_per_image": 0.05
    },
    "qwen-image-standard": {
      "path": "qwen_image_edit_2509_fp8_e4m3fn.safetensors",
      "type": "diffusion",
      "quality": "high",
      "vram_required_gb": 8,
      "avg_time_seconds": 60,
      "recommended_steps": 30,
      "max_resolution": "1024x1024",
      "use_cases": ["web_images", "social_media", "general"],
      "cost_per_image": 0.02
    },
    "qwen-image-fast": {
      "path": "qwen_image_edit_2509_fp8_e4m3fn.safetensors",
      "type": "diffusion",
      "quality": "medium",
      "vram_required_gb": 6,
      "avg_time_seconds": 30,
      "recommended_steps": 15,
      "max_resolution": "512x512",
      "use_cases": ["thumbnails", "previews", "batch_processing"],
      "cost_per_image": 0.01
    },
    "sdxl-turbo": {
      "path": "sd_xl_turbo_1.0_fp16.safetensors",
      "type": "diffusion",
      "quality": "fast",
      "vram_required_gb": 4,
      "avg_time_seconds": 10,
      "recommended_steps": 4,
      "max_resolution": "1024x1024",
      "use_cases": ["rapid_prototyping", "iterations", "testing"],
      "cost_per_image": 0.005
    }
  },
  "routing_rules": {
    "by_urgency": {
      "immediate": "sdxl-turbo",
      "standard": "qwen-image-standard",
      "flexible": "qwen-image-ultra"
    },
    "by_purpose": {
      "hero_image": "qwen-image-ultra",
      "social_media": "qwen-image-standard",
      "thumbnail": "qwen-image-fast",
      "preview": "sdxl-turbo"
    },
    "by_available_vram": {
      "low": "qwen-image-fast",      // < 8GB
      "medium": "qwen-image-standard", // 8-12GB
      "high": "qwen-image-ultra"      // > 12GB
    }
  }
}
```

### Smart Router Implementation

```python
# smart_model_router.py
import json
import requests
from typing import Dict, Optional
from enum import Enum

class Urgency(Enum):
    IMMEDIATE = "immediate"    # < 30s
    STANDARD = "standard"      # < 2min
    FLEXIBLE = "flexible"      # Best quality

class Purpose(Enum):
    HERO_IMAGE = "hero_image"
    SOCIAL_MEDIA = "social_media"
    THUMBNAIL = "thumbnail"
    PREVIEW = "preview"
    GENERAL = "general"

class ModelRouter:
    def __init__(self, config_path="models_config.json"):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
    
    def get_available_vram(self) -> float:
        """Query ComfyUI for available VRAM"""
        try:
            response = requests.get("http://localhost:8188/system_stats")
            stats = response.json()
            return stats['devices'][0]['vram_free'] / (1024**3)  # Convert to GB
        except:
            return 8.0  # Default fallback
    
    def select_model(
        self,
        purpose: Optional[Purpose] = None,
        urgency: Optional[Urgency] = None,
        min_quality: Optional[str] = None,
        max_vram: Optional[float] = None
    ) -> Dict:
        """
        Intelligently select best model based on requirements
        
        Priority:
        1. Available VRAM (hard constraint)
        2. Urgency (if specified)
        3. Purpose (if specified)
        4. Quality requirement
        """
        available_vram = self.get_available_vram()
        
        # Filter models by VRAM availability
        eligible_models = {
            name: config
            for name, config in self.config['models'].items()
            if config['vram_required_gb'] <= (max_vram or available_vram)
        }
        
        if not eligible_models:
            raise RuntimeError("No models available with current VRAM constraints")
        
        # Apply urgency routing
        if urgency:
            urgency_model = self.config['routing_rules']['by_urgency'][urgency.value]
            if urgency_model in eligible_models:
                return {
                    'model_name': urgency_model,
                    **eligible_models[urgency_model],
                    'selection_reason': f'urgency:{urgency.value}'
                }
        
        # Apply purpose routing
        if purpose:
            purpose_model = self.config['routing_rules']['by_purpose'].get(
                purpose.value,
                'qwen-image-standard'
            )
            if purpose_model in eligible_models:
                return {
                    'model_name': purpose_model,
                    **eligible_models[purpose_model],
                    'selection_reason': f'purpose:{purpose.value}'
                }
        
        # Filter by quality if specified
        if min_quality:
            quality_order = ['fast', 'medium', 'high', 'ultra']
            min_quality_idx = quality_order.index(min_quality)
            eligible_models = {
                name: config
                for name, config in eligible_models.items()
                if quality_order.index(config['quality']) >= min_quality_idx
            }
        
        # Default: best quality within constraints
        best_model = max(
            eligible_models.items(),
            key=lambda x: ['fast', 'medium', 'high', 'ultra'].index(x[1]['quality'])
        )
        
        return {
            'model_name': best_model[0],
            **best_model[1],
            'selection_reason': 'best_available_quality'
        }
    
    def build_workflow(
        self,
        prompt: str,
        model_config: Dict,
        negative_prompt: Optional[str] = None
    ) -> Dict:
        """Build ComfyUI workflow with selected model configuration"""
        
        # Load base workflow template
        with open(f"./workflow_templates/{model_config['type']}.json", 'r') as f:
            workflow = json.load(f)
        
        # Inject model path
        for node in workflow.values():
            if node.get('class_type') == 'CheckpointLoaderSimple':
                node['inputs']['ckpt_name'] = model_config['path']
        
        # Inject prompts
        for node in workflow.values():
            if node.get('class_type') == 'CLIPTextEncode':
                if 'positive' in node.get('_meta', {}).get('title', '').lower():
                    node['inputs']['text'] = prompt
                elif negative_prompt:
                    node['inputs']['text'] = negative_prompt
        
        # Set recommended steps
        for node in workflow.values():
            if node.get('class_type') == 'KSampler':
                node['inputs']['steps'] = model_config['recommended_steps']
        
        return workflow

# Usage examples
router = ModelRouter()

# Example 1: Fast preview needed
model = router.select_model(urgency=Urgency.IMMEDIATE)
print(f"Selected: {model['model_name']} - {model['selection_reason']}")
# Output: "sdxl-turbo - urgency:immediate"

# Example 2: Hero image for website
model = router.select_model(purpose=Purpose.HERO_IMAGE)
print(f"Selected: {model['model_name']} - Estimated time: {model['avg_time_seconds']}s")
# Output: "qwen-image-ultra - Estimated time: 100s"

# Example 3: Limited VRAM scenario
model = router.select_model(max_vram=6.0, min_quality='medium')
print(f"Selected: {model['model_name']} - VRAM: {model['vram_required_gb']}GB")
# Output: "qwen-image-fast - VRAM: 6GB"
```

### n8n Smart Router Workflow

```
Webhook (receive generation request)
→ Function node (calculate requirements):
    - Parse request parameters
    - Determine urgency from SLA
    - Identify purpose from metadata
→ HTTP Request (query ComfyUI VRAM):
    GET http://comfyui:8188/system_stats
→ Python code node (run ModelRouter):
    model = router.select_model(
        purpose=purpose,
        urgency=urgency,
        max_vram=available_vram
    )
    workflow = router.build_workflow(prompt, model)
→ HTTP Request (submit to ComfyUI):
    POST /prompt with optimized workflow
→ PostgreSQL (log model selection):
    INSERT INTO model_usage_log
→ Wait for completion
→ Respond with result + metadata:
    {
        "image_url": "...",
        "model_used": "qwen-image-standard",
        "generation_time": 62,
        "selection_reason": "purpose:social_media"
    }
```

### Dynamic VRAM Monitoring

```python
# vram_monitor.py
import requests
import time
from datetime import datetime
import psycopg2

class VRAMMonitor:
    def __init__(self, check_interval=30):
        self.check_interval = check_interval
        self.db = psycopg2.connect(DB_URL)
    
    def get_vram_stats(self) -> dict:
        """Get current VRAM usage from ComfyUI"""
        try:
            response = requests.get("http://localhost:8188/system_stats")
            stats = response.json()
            device = stats['devices'][0]
            
            return {
                'vram_total_gb': device['vram_total'] / (1024**3),
                'vram_free_gb': device['vram_free'] / (1024**3),
                'vram_used_gb': (device['vram_total'] - device['vram_free']) / (1024**3),
                'vram_used_percent': ((device['vram_total'] - device['vram_free']) / device['vram_total']) * 100
            }
        except:
            return None
    
    def log_vram_usage(self, stats: dict):
        """Log VRAM stats to database"""
        cur = self.db.cursor()
        cur.execute("""
            INSERT INTO vram_usage_log
            (timestamp, vram_total_gb, vram_free_gb, vram_used_gb, vram_used_percent)
            VALUES (NOW(), %s, %s, %s, %s)
        """, (
            stats['vram_total_gb'],
            stats['vram_free_gb'],
            stats['vram_used_gb'],
            stats['vram_used_percent']
        ))
        self.db.commit()
    
    def monitor_loop(self):
        """Continuous monitoring loop"""
        while True:
            stats = self.get_vram_stats()
            if stats:
                self.log_vram_usage(stats)
                
                # Alert if VRAM is critically low
                if stats['vram_free_gb'] < 2.0:
                    self.send_alert(f"Low VRAM: {stats['vram_free_gb']:.2f}GB free")
            
            time.sleep(self.check_interval)
    
    def send_alert(self, message: str):
        """Send alert via webhook/Slack"""
        requests.post(
            "http://localhost:15678/webhook/vram-alert",
            json={"message": message, "timestamp": datetime.now().isoformat()}
        )

# Run as background service
if __name__ == "__main__":
    monitor = VRAMMonitor(check_interval=30)
    monitor.monitor_loop()
```

### Auto-Scaling Workflow Quality

```python
# adaptive_quality.py
class AdaptiveQualityManager:
    def __init__(self):
        self.router = ModelRouter()
        self.performance_history = []
    
    def generate_with_adaptive_quality(
        self,
        prompt: str,
        target_time_seconds: Optional[int] = None,
        min_acceptable_quality: str = 'medium'
    ):
        """
        Try to generate image meeting time constraint
        If fails, automatically downgrade quality
        """
        quality_levels = ['ultra', 'high', 'medium', 'fast']
        min_quality_idx = quality_levels.index(min_acceptable_quality)
        
        for quality in quality_levels[min_quality_idx:]:
            model = self.router.select_model(min_quality=quality)
            
            if target_time_seconds and model['avg_time_seconds'] > target_time_seconds:
                continue  # Skip if too slow
            
            # Attempt generation
            start_time = time.time()
            try:
                result = self.generate_image(prompt, model)
                actual_time = time.time() - start_time
                
                # Log performance
                self.performance_history.append({
                    'model': model['model_name'],
                    'expected_time': model['avg_time_seconds'],
                    'actual_time': actual_time,
                    'quality': quality
                })
                
                return {
                    'success': True,
                    'result': result,
                    'model_used': model['model_name'],
                    'quality': quality,
                    'time_seconds': actual_time
                }
            
            except Exception as e:
                print(f"Failed with quality={quality}: {e}")
                continue
        
        raise RuntimeError("Could not generate image within constraints")
```

### Cost-Based Routing

```python
# cost_optimizer.py
class CostOptimizer:
    def __init__(self):
        self.router = ModelRouter()
    
    def select_cost_optimal_model(
        self,
        prompt: str,
        max_cost: float = 0.05,
        min_quality: str = 'medium'
    ):
        """Select model that meets quality requirements at lowest cost"""
        
        # Get all eligible models
        models = [
            (name, config)
            for name, config in self.router.config['models'].items()
            if config['cost_per_image'] <= max_cost
            and self._quality_meets_requirement(config['quality'], min_quality)
        ]
        
        # Sort by cost (ascending)
        models.sort(key=lambda x: x[1]['cost_per_image'])
        
        if not models:
            raise ValueError("No models available within cost constraint")
        
        # Select cheapest that meets requirements
        selected = models[0]
        
        return {
            'model_name': selected[0],
            **selected[1],
            'cost_savings': max_cost - selected[1]['cost_per_image']
        }
    
    def batch_generation_cost_analysis(
        self,
        num_images: int,
        quality_distribution: dict  # {'ultra': 10, 'high': 50, 'medium': 40}
    ):
        """Calculate cost for batch generation with mixed quality"""
        
        total_cost = 0
        breakdown = {}
        
        for quality, count in quality_distribution.items():
            model = self.router.select_model(min_quality=quality)
            cost = model['cost_per_image'] * count
            total_cost += cost
            breakdown[quality] = {
                'count': count,
                'cost_per_image': model['cost_per_image'],
                'total_cost': cost,
                'model': model['model_name']
            }
        
        return {
            'total_images': num_images,
            'total_cost': total_cost,
            'avg_cost_per_image': total_cost / num_images,
            'breakdown': breakdown
        }
```

### Dashboard Metrics

```sql
-- Track model usage and performance
CREATE TABLE model_usage_log (
    id SERIAL PRIMARY KEY,
    model_name VARCHAR(100),
    quality_level VARCHAR(20),
    vram_used_gb FLOAT,
    generation_time_seconds FLOAT,
    cost FLOAT,
    success BOOLEAN,
    selection_reason VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);

-- VRAM monitoring
CREATE TABLE vram_usage_log (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT NOW(),
    vram_total_gb FLOAT,
    vram_free_gb FLOAT,
    vram_used_gb FLOAT,
    vram_used_percent FLOAT
);

-- Analytics queries
-- Average generation time by model
SELECT 
    model_name,
    AVG(generation_time_seconds) as avg_time,
    COUNT(*) as usage_count,
    SUM(cost) as total_cost
FROM model_usage_log
WHERE created_at > NOW() - INTERVAL '7 days'
GROUP BY model_name
ORDER BY usage_count DESC;

-- VRAM usage patterns
SELECT 
    DATE_TRUNC('hour', timestamp) as hour,
    AVG(vram_used_percent) as avg_usage,
    MAX(vram_used_percent) as peak_usage
FROM vram_usage_log
WHERE timestamp > NOW() - INTERVAL '24 hours'
GROUP BY hour
ORDER BY hour;
```

### Benefits
- Automatic adaptation to resource availability
- Cost optimization for batch operations
- Quality/speed trade-offs managed automatically
- Prevents VRAM OOM errors
- Optimizes for SLA requirements
- Provides cost transparency

### Complexidade
**Alta** - Requer system monitoring e decision logic

### Prioridade
⭐⭐⭐⭐ (Long Term - 2 semanas)

---

## 13. Monitoring & Analytics Stack

### Descrição
Stack completo de monitoramento e observabilidade que coleta métricas de performance, traces de execução, logs estruturados e dashboards em tempo real para todo o ecossistema ComfyUI.

### Architecture

```
ComfyUI + n8n + Ollama
↓ (metrics export)
Prometheus (time-series database)
↓ (visualization)
Grafana (dashboards)
↓ (alerting)
Alertmanager → Slack/Email
```

### Docker Compose Stack

```yaml
# Add to docker-compose.yml
prometheus:
  image: prom/prometheus:latest
  container_name: prometheus
  networks: ['skynet']
  restart: unless-stopped
  ports:
    - "9090:9090"
  volumes:
    - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
    - prometheus_storage:/prometheus
  command:
    - '--config.file=/etc/prometheus/prometheus.yml'
    - '--storage.tsdb.path=/prometheus'
    - '--storage.tsdb.retention.time=30d'
    - '--web.enable-lifecycle'
  healthcheck:
    test: ["CMD", "wget", "--spider", "-q", "http://localhost:9090/-/healthy"]
    interval: 30s
    timeout: 10s
    retries: 3

grafana:
  image: grafana/grafana:latest
  container_name: grafana
  networks: ['skynet']
  restart: unless-stopped
  ports:
    - "3000:3000"
  environment:
    - GF_SECURITY_ADMIN_USER=admin
    - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD:-admin}
    - GF_INSTALL_PLUGINS=redis-datasource,postgres-datasource
    - GF_SERVER_ROOT_URL=http://localhost:3000
  volumes:
    - grafana_storage:/var/lib/grafana
    - ./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards
    - ./monitoring/grafana/datasources:/etc/grafana/provisioning/datasources
  depends_on:
    - prometheus
  healthcheck:
    test: ["CMD", "wget", "--spider", "-q", "http://localhost:3000/api/health"]
    interval: 30s
    timeout: 10s
    retries: 3

node-exporter:
  image: prom/node-exporter:latest
  container_name: node-exporter
  networks: ['skynet']
  restart: unless-stopped
  ports:
    - "9100:9100"
  command:
    - '--path.procfs=/host/proc'
    - '--path.sysfs=/host/sys'
    - '--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)'
  volumes:
    - /proc:/host/proc:ro
    - /sys:/host/sys:ro
    - /:/rootfs:ro

nvidia-gpu-exporter:
  image: utkuozdemir/nvidia_gpu_exporter:latest
  container_name: nvidia-gpu-exporter
  networks: ['skynet']
  restart: unless-stopped
  ports:
    - "9835:9835"
  runtime: nvidia
  environment:
    - NVIDIA_VISIBLE_DEVICES=all

volumes:
  prometheus_storage:
  grafana_storage:
```

### Prometheus Configuration

```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    monitor: 'comfyui-ecosystem'

scrape_configs:
  # System metrics
  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']
  
  # GPU metrics
  - job_name: 'nvidia-gpu'
    static_configs:
      - targets: ['nvidia-gpu-exporter:9835']
  
  # ComfyUI metrics (if exposed)
  - job_name: 'comfyui'
    static_configs:
      - targets: ['comfyui:8188']
    metrics_path: '/metrics'
  
  # PostgreSQL metrics
  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:9187']
  
  # Redis metrics
  - job_name: 'redis'
    static_configs:
      - targets: ['redis:9121']
  
  # n8n metrics (if available)
  - job_name: 'n8n'
    static_configs:
      - targets: ['n8n:5678']
    metrics_path: '/metrics'

alerting:
  alertmanagers:
    - static_configs:
        - targets: ['alertmanager:9093']

rule_files:
  - 'alerts.yml'
```

### Custom Metrics Exporter for ComfyUI

```python
# comfyui_metrics_exporter.py
from prometheus_client import start_http_server, Gauge, Counter, Histogram
import requests
import time
import psycopg2
from datetime import datetime, timedelta

# Define metrics
vram_usage = Gauge('comfyui_vram_usage_bytes', 'VRAM usage in bytes')
vram_total = Gauge('comfyui_vram_total_bytes', 'Total VRAM in bytes')
generation_time = Histogram(
    'comfyui_generation_duration_seconds',
    'Time to generate image',
    buckets=[10, 30, 60, 120, 300, 600]
)
generations_total = Counter(
    'comfyui_generations_total',
    'Total number of generations',
    ['status', 'model']
)
queue_size = Gauge('comfyui_queue_size', 'Number of jobs in queue')
active_generations = Gauge('comfyui_active_generations', 'Currently running generations')

class ComfyUIMetricsExporter:
    def __init__(self, comfyui_url='http://localhost:8188', db_url=None):
        self.comfyui_url = comfyui_url
        self.db = psycopg2.connect(db_url) if db_url else None
    
    def collect_vram_metrics(self):
        """Collect VRAM usage from ComfyUI"""
        try:
            response = requests.get(f"{self.comfyui_url}/system_stats")
            stats = response.json()
            device = stats['devices'][0]
            
            vram_total.set(device['vram_total'])
            vram_usage.set(device['vram_total'] - device['vram_free'])
            
        except Exception as e:
            print(f"Error collecting VRAM metrics: {e}")
    
    def collect_queue_metrics(self):
        """Collect queue statistics from database"""
        if not self.db:
            return
        
        try:
            cur = self.db.cursor()
            
            # Queue size
            cur.execute("""
                SELECT COUNT(*) FROM job_queue WHERE status = 'pending'
            """)
            queue_size.set(cur.fetchone()[0])
            
            # Active generations
            cur.execute("""
                SELECT COUNT(*) FROM job_queue WHERE status = 'processing'
            """)
            active_generations.set(cur.fetchone()[0])
            
            # Generation stats (last hour)
            cur.execute("""
                SELECT 
                    status,
                    COUNT(*) as count,
                    AVG(EXTRACT(EPOCH FROM (completed_at - started_at))) as avg_time
                FROM job_queue
                WHERE created_at > NOW() - INTERVAL '1 hour'
                AND completed_at IS NOT NULL
                GROUP BY status
            """)
            
            for row in cur.fetchall():
                status, count, avg_time = row
                generations_total.labels(status=status, model='qwen').inc(count)
                if avg_time:
                    generation_time.observe(avg_time)
            
        except Exception as e:
            print(f"Error collecting queue metrics: {e}")
    
    def run_exporter(self, port=8000, interval=15):
        """Start metrics HTTP server and collection loop"""
        start_http_server(port)
        print(f"Metrics server started on port {port}")
        
        while True:
            self.collect_vram_metrics()
            self.collect_queue_metrics()
            time.sleep(interval)

if __name__ == '__main__':
    exporter = ComfyUIMetricsExporter(
        comfyui_url='http://localhost:8188',
        db_url='postgresql://user:pass@localhost/db'
    )
    exporter.run_exporter(port=8000)
```

### Alert Rules

```yaml
# monitoring/alerts.yml
groups:
  - name: comfyui_alerts
    interval: 30s
    rules:
      # VRAM alerts
      - alert: HighVRAMUsage
        expr: (comfyui_vram_usage_bytes / comfyui_vram_total_bytes) > 0.9
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High VRAM usage detected"
          description: "VRAM usage is above 90% for 5 minutes"
      
      - alert: VRAMCritical
        expr: (comfyui_vram_usage_bytes / comfyui_vram_total_bytes) > 0.95
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Critical VRAM usage"
          description: "VRAM usage is above 95%"
      
      # Queue alerts
      - alert: LargeQueue
        expr: comfyui_queue_size > 100
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Large job queue"
          description: "Queue has {{ $value }} pending jobs"
      
      # Generation performance
      - alert: SlowGenerations
        expr: rate(comfyui_generation_duration_seconds_sum[5m]) / rate(comfyui_generation_duration_seconds_count[5m]) > 120
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Slow generation times"
          description: "Average generation time is {{ $value }}s"
      
      # Failure rate
      - alert: HighFailureRate
        expr: (rate(comfyui_generations_total{status="failed"}[15m]) / rate(comfyui_generations_total[15m])) > 0.1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High generation failure rate"
          description: "Failure rate is {{ $value | humanizePercentage }}"
      
      # System health
      - alert: HostHighCPU
        expr: 100 - (avg by (instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage"
          description: "CPU usage is {{ $value }}%"
      
      - alert: HostOutOfMemory
        expr: node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes * 100 < 10
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Host out of memory"
          description: "Available memory is {{ $value }}%"
```

### Grafana Dashboards

#### Dashboard 1: ComfyUI Overview
```json
{
  "dashboard": {
    "title": "ComfyUI Performance Overview",
    "panels": [
      {
        "title": "VRAM Usage",
        "targets": [
          {
            "expr": "comfyui_vram_usage_bytes / comfyui_vram_total_bytes * 100"
          }
        ],
        "type": "gauge"
      },
      {
        "title": "Generation Time (p95)",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, comfyui_generation_duration_seconds_bucket)"
          }
        ],
        "type": "graph"
      },
      {
        "title": "Queue Size",
        "targets": [
          {
            "expr": "comfyui_queue_size"
          }
        ],
        "type": "stat"
      },
      {
        "title": "Success Rate",
        "targets": [
          {
            "expr": "rate(comfyui_generations_total{status='success'}[5m]) / rate(comfyui_generations_total[5m]) * 100"
          }
        ],
        "type": "gauge"
      },
      {
        "title": "Generations per Minute",
        "targets": [
          {
            "expr": "rate(comfyui_generations_total[1m]) * 60"
          }
        ],
        "type": "graph"
      }
    ]
  }
}
```

#### Dashboard 2: GPU Metrics
```json
{
  "dashboard": {
    "title": "RTX 5080 GPU Metrics",
    "panels": [
      {
        "title": "GPU Utilization",
        "targets": [
          {
            "expr": "nvidia_gpu_duty_cycle"
          }
        ],
        "type": "graph"
      },
      {
        "title": "GPU Temperature",
        "targets": [
          {
            "expr": "nvidia_gpu_temperature_celsius"
          }
        ],
        "type": "graph"
      },
      {
        "title": "GPU Power Usage",
        "targets": [
          {
            "expr": "nvidia_gpu_power_usage_milliwatts / 1000"
          }
        ],
        "type": "graph"
      },
      {
        "title": "GPU Memory Usage",
        "targets": [
          {
            "expr": "nvidia_gpu_memory_used_bytes / nvidia_gpu_memory_total_bytes * 100"
          }
        ],
        "type": "gauge"
      }
    ]
  }
}
```

### n8n Integration for Monitoring

```
Schedule (every 5 minutes)
→ HTTP Request (query Prometheus):
    GET http://prometheus:9090/api/v1/query?query=comfyui_queue_size
→ IF (queue_size > 50)
  → Slack notification: "Queue backlog detected"
  → PostgreSQL: Log alert

Schedule (daily)
→ HTTP Request (query Prometheus):
    Range query for daily statistics
→ Generate PDF report
→ Email to team
```

### Log Aggregation with Loki (Optional)

```yaml
# Add Loki for log aggregation
loki:
  image: grafana/loki:latest
  container_name: loki
  networks: ['skynet']
  restart: unless-stopped
  ports:
    - "3100:3100"
  command: -config.file=/etc/loki/local-config.yaml
  volumes:
    - loki_storage:/loki

promtail:
  image: grafana/promtail:latest
  container_name: promtail
  networks: ['skynet']
  restart: unless-stopped
  volumes:
    - /var/log:/var/log:ro
    - ./monitoring/promtail-config.yml:/etc/promtail/config.yml
  command: -config.file=/etc/promtail/config.yml
  depends_on:
    - loki
```

### Benefits
- Real-time visibility into system performance
- Proactive alerting before issues occur
- Historical data for trend analysis
- Capacity planning insights
- Performance regression detection
- Cost tracking (GPU usage → electricity costs)

### Key Metrics to Track
1. **Performance**: Generation time, throughput, queue depth
2. **Resources**: VRAM, RAM, CPU, GPU utilization
3. **Quality**: Success rate, error rate, retry count
4. **Business**: Cost per image, revenue per generation
5. **User Experience**: Wait time, SLA compliance

### Complexidade
**Média-Alta** - Requer DevOps knowledge

### Prioridade
⭐⭐⭐⭐ (Long Term - 2 semanas)

---

## 14. Multi-User Setup & Resource Quotas

### Descrição
Sistema de autenticação, autorização e quotas que permite múltiplos usuários compartilharem o ComfyUI com limites de uso individualizados, priorização de jobs e isolamento de recursos.

### Architecture Components

1. **Authentication Layer** - JWT tokens
2. **Authorization Service** - Role-based access control (RBAC)
3. **Quota Manager** - Track and enforce usage limits
4. **Resource Scheduler** - Fair queue management
5. **Reverse Proxy** - Route requests with auth

### User Database Schema

```sql
-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'user', -- 'admin', 'power_user', 'user', 'trial'
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    last_login_at TIMESTAMP
);

-- User quotas
CREATE TABLE user_quotas (
    user_id INTEGER PRIMARY KEY REFERENCES users(id),
    
    -- Generation limits
    max_generations_per_day INTEGER DEFAULT 100,
    max_generations_per_month INTEGER DEFAULT 1000,
    max_concurrent_jobs INTEGER DEFAULT 3,
    
    -- Resource limits
    max_vram_gb FLOAT DEFAULT 8.0,
    max_generation_time_seconds INTEGER DEFAULT 300,
    max_image_resolution INTEGER DEFAULT 1024,
    
    -- Quality/Model access
    allowed_models TEXT[] DEFAULT ARRAY['qwen-image-standard'],
    max_quality_level VARCHAR(20) DEFAULT 'high', -- 'fast', 'medium', 'high', 'ultra'
    
    -- Priority
    job_priority INTEGER DEFAULT 0, -- Higher = more priority
    
    -- Storage
    max_storage_mb INTEGER DEFAULT 5000,
    
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Usage tracking
CREATE TABLE user_usage (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    date DATE DEFAULT CURRENT_DATE,
    
    generations_count INTEGER DEFAULT 0,
    total_generation_time_seconds FLOAT DEFAULT 0,
    total_vram_used_gb FLOAT DEFAULT 0,
    storage_used_mb FLOAT DEFAULT 0,
    
    UNIQUE(user_id, date)
);

-- API keys
CREATE TABLE api_keys (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    key_hash VARCHAR(255) NOT NULL,
    name VARCHAR(100),
    permissions JSONB, -- {"generate": true, "view": true, "delete": false}
    expires_at TIMESTAMP,
    last_used_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT true
);
```

### Authentication Service (FastAPI)

```python
# auth_service.py
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import jwt
import bcrypt
from datetime import datetime, timedelta
import psycopg2

app = FastAPI(title="ComfyUI Auth Service")
security = HTTPBearer()

SECRET_KEY = "your-secret-key-here"
ALGORITHM = "HS256"

class UserLogin(BaseModel):
    username: str
    password: str

class UserRegister(BaseModel):
    username: str
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

def get_db():
    return psycopg2.connect(DB_URL)

def create_access_token(user_id: int, username: str, role: str):
    """Generate JWT token"""
    expiration = datetime.utcnow() + timedelta(hours=24)
    payload = {
        "user_id": user_id,
        "username": username,
        "role": role,
        "exp": expiration
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.post("/api/auth/register")
async def register(user: UserRegister):
    """Register new user"""
    db = get_db()
    cur = db.cursor()
    
    # Check if user exists
    cur.execute("SELECT id FROM users WHERE username = %s OR email = %s", 
                (user.username, user.email))
    if cur.fetchone():
        raise HTTPException(status_code=400, detail="User already exists")
    
    # Hash password
    password_hash = bcrypt.hashpw(user.password.encode(), bcrypt.gensalt()).decode()
    
    # Create user
    cur.execute("""
        INSERT INTO users (username, email, password_hash, role)
        VALUES (%s, %s, %s, 'user')
        RETURNING id
    """, (user.username, user.email, password_hash))
    
    user_id = cur.fetchone()[0]
    
    # Create default quotas
    cur.execute("""
        INSERT INTO user_quotas (user_id) VALUES (%s)
    """, (user_id,))
    
    db.commit()
    
    return {"message": "User created successfully", "user_id": user_id}

@app.post("/api/auth/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    """Login and get JWT token"""
    db = get_db()
    cur = db.cursor()
    
    cur.execute("""
        SELECT id, username, password_hash, role, is_active
        FROM users
        WHERE username = %s
    """, (credentials.username,))
    
    user = cur.fetchone()
    
    if not user or not bcrypt.checkpw(credentials.password.encode(), user[2].encode()):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not user[4]:  # is_active
        raise HTTPException(status_code=403, detail="Account is disabled")
    
    # Update last login
    cur.execute("UPDATE users SET last_login_at = NOW() WHERE id = %s", (user[0],))
    db.commit()
    
    # Generate token
    token = create_access_token(user[0], user[1], user[3])
    
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=86400  # 24 hours
    )

@app.get("/api/auth/me")
async def get_current_user(payload: dict = Depends(verify_token)):
    """Get current user info"""
    db = get_db()
    cur = db.cursor()
    
    cur.execute("""
        SELECT u.id, u.username, u.email, u.role, q.*
        FROM users u
        JOIN user_quotas q ON q.user_id = u.id
        WHERE u.id = %s
    """, (payload['user_id'],))
    
    user = cur.fetchone()
    
    return {
        "id": user[0],
        "username": user[1],
        "email": user[2],
        "role": user[3],
        "quotas": {
            # ... quota details
        }
    }
```

### Quota Enforcement Middleware

```python
# quota_middleware.py
from fastapi import HTTPException
import psycopg2
from datetime import date

class QuotaManager:
    def __init__(self, db_url):
        self.db = psycopg2.connect(db_url)
    
    def check_quota(self, user_id: int, requested_resources: dict) -> bool:
        """
        Check if user has quota available
        
        requested_resources: {
            'vram_gb': 8.0,
            'quality': 'high',
            'model': 'qwen-image',
            'resolution': 1024
        }
        """
        cur = self.db.cursor()
        
        # Get user quotas
        cur.execute("""
            SELECT 
                q.max_generations_per_day,
                q.max_concurrent_jobs,
                q.max_vram_gb,
                q.allowed_models,
                q.max_quality_level
            FROM user_quotas q
            WHERE q.user_id = %s
        """, (user_id,))
        
        quotas = cur.fetchone()
        
        if not quotas:
            raise HTTPException(status_code=403, detail="No quota configured")
        
        # Get today's usage
        cur.execute("""
            SELECT generations_count
            FROM user_usage
            WHERE user_id = %s AND date = CURRENT_DATE
        """, (user_id,))
        
        usage = cur.fetchone()
        today_generations = usage[0] if usage else 0
        
        # Check daily limit
        if today_generations >= quotas[0]:
            raise HTTPException(
                status_code=429,
                detail=f"Daily generation limit reached ({quotas[0]})"
            )
        
        # Check concurrent jobs
        cur.execute("""
            SELECT COUNT(*)
            FROM job_queue
            WHERE created_by = %s AND status IN ('pending', 'processing')
        """, (user_id,))
        
        concurrent = cur.fetchone()[0]
        if concurrent >= quotas[1]:
            raise HTTPException(
                status_code=429,
                detail=f"Maximum concurrent jobs reached ({quotas[1]})"
            )
        
        # Check VRAM limit
        if requested_resources.get('vram_gb', 0) > quotas[2]:
            raise HTTPException(
                status_code=403,
                detail=f"Requested VRAM exceeds limit ({quotas[2]}GB)"
            )
        
        # Check model access
        if requested_resources.get('model') not in quotas[3]:
            raise HTTPException(
                status_code=403,
                detail=f"No access to model: {requested_resources['model']}"
            )
        
        return True
    
    def record_usage(self, user_id: int, metrics: dict):
        """Record usage metrics"""
        cur = self.db.cursor()
        
        cur.execute("""
            INSERT INTO user_usage (user_id, date, generations_count, total_generation_time_seconds)
            VALUES (%s, CURRENT_DATE, 1, %s)
            ON CONFLICT (user_id, date) DO UPDATE
            SET generations_count = user_usage.generations_count + 1,
                total_generation_time_seconds = user_usage.total_generation_time_seconds + %s
        """, (user_id, metrics.get('time_seconds', 0), metrics.get('time_seconds', 0)))
        
        self.db.commit()
```

### Priority Queue Scheduler

```python
# priority_scheduler.py
class PriorityScheduler:
    def __init__(self, db_url):
        self.db = psycopg2.connect(db_url)
    
    def enqueue_job(self, user_id: int, job_data: dict):
        """Add job to queue with user priority"""
        cur = self.db.cursor()
        
        # Get user priority
        cur.execute("""
            SELECT job_priority FROM user_quotas WHERE user_id = %s
        """, (user_id,))
        
        user_priority = cur.fetchone()[0] or 0
        
        # Insert with priority
        cur.execute("""
            INSERT INTO job_queue 
            (created_by, prompt, workflow_type, priority, status)
            VALUES (%s, %s, %s, %s, 'pending')
            RETURNING id
        """, (user_id, job_data['prompt'], job_data['workflow_type'], user_priority))
        
        job_id = cur.fetchone()[0]
        self.db.commit()
        
        return job_id
    
    def get_next_job(self):
        """Get highest priority pending job"""
        cur = self.db.cursor()
        
        cur.execute("""
            SELECT j.*, u.username
            FROM job_queue j
            JOIN users u ON u.id = j.created_by
            WHERE j.status = 'pending'
            ORDER BY j.priority DESC, j.created_at ASC
            LIMIT 1
            FOR UPDATE SKIP LOCKED
        """)
        
        return cur.fetchone()
```

### Traefik Reverse Proxy (with auth)

```yaml
# docker-compose.yml
traefik:
  image: traefik:v2.10
  container_name: traefik
  networks: ['skynet']
  restart: unless-stopped
  ports:
    - "80:80"
    - "8080:8080"  # Traefik dashboard
  command:
    - "--api.insecure=true"
    - "--providers.docker=true"
    - "--providers.docker.exposedbydefault=false"
    - "--entrypoints.web.address=:80"
  volumes:
    - /var/run/docker.sock:/var/run/docker.sock:ro

auth-service:
  build: ./auth-service
  container_name: auth-service
  networks: ['skynet']
  restart: unless-stopped
  environment:
    - DATABASE_URL=postgresql://user:pass@postgres/db
    - JWT_SECRET=${JWT_SECRET}
  depends_on:
    - postgres

comfyui-proxy:
  build: ./comfyui-proxy
  container_name: comfyui-proxy
  networks: ['skynet']
  restart: unless-stopped
  labels:
    - "traefik.enable=true"
    - "traefik.http.routers.comfyui.rule=Host(`comfyui.local`)"
    - "traefik.http.middlewares.auth.forwardauth.address=http://auth-service:8000/api/auth/verify"
    - "traefik.http.routers.comfyui.middlewares=auth"
  environment:
    - COMFYUI_URL=http://comfyui:8188
    - AUTH_SERVICE_URL=http://auth-service:8000
  depends_on:
    - auth-service
    - comfyui
```

### Benefits
- Multi-tenancy support
- Fair resource allocation
- Usage tracking per user
- Prevent abuse
- Billing integration ready
- Role-based features
- Enterprise-ready

### Complexidade
**Alta** - Requer auth, RBAC, quota management

### Prioridade
⭐⭐⭐ (Long Term - 2-3 semanas)

---

## 15. Comprehensive Integration Roadmap

### Phase 1: Foundation (Week 1-2)
**Goal**: Basic integrations working

✅ **Priority Tasks**:
1. API REST - n8n → ComfyUI integration
2. PostgreSQL storage for outputs
3. Basic webhook triggers
4. File watching system

**Deliverables**:
- n8n workflow templates
- Database schema
- API documentation
- Basic monitoring

### Phase 2: Enhancement (Week 3-4)
**Goal**: Advanced workflows and optimization

✅ **Priority Tasks**:
1. RAG pipeline with Qdrant
2. Batch processing queue (Redis)
3. MinIO storage integration
4. Prompt management system

**Deliverables**:
- Complete RAG implementation
- Queue worker service
- S3-compatible storage
- Prompt library UI

### Phase 3: Intelligence (Week 5-6)
**Goal**: AI-powered automation

✅ **Priority Tasks**:
1. Model hot-swapping system
2. AI Agent framework integration (LangChain)
3. MCP server for Claude Code
4. Dynamic resource management

**Deliverables**:
- Smart model router
- LangChain/AutoGen integration
- MCP server running
- Adaptive quality system

### Phase 4: Production (Week 7-8)
**Goal**: Enterprise-ready platform

✅ **Priority Tasks**:
1. Monitoring stack (Prometheus + Grafana)
2. Multi-user system
3. WebSocket real-time updates
4. Complete documentation

**Deliverables**:
- Full observability
- Auth & quota system
- Real-time dashboards
- Production deployment guide

---

## Summary & Next Steps

### Ecosystem Overview

```
                    ┌─────────────┐
                    │   Claude    │
                    │    Code     │ (MCP Integration)
                    └──────┬──────┘
                           │
      ┌────────────────────┼────────────────────┐
      │                    │                    │
┌─────▼─────┐       ┌─────▼─────┐       ┌─────▼─────┐
│   n8n     │◄─────►│  ComfyUI  │◄─────►│  Ollama   │
│(Workflow) │       │  (Image)  │       │   (LLM)   │
└─────┬─────┘       └─────┬─────┘       └─────┬─────┘
      │                   │                   │
      │            ┌──────▼──────┐           │
      │            │    Redis    │           │
      │            │   (Queue)   │           │
      │            └──────┬──────┘           │
      │                   │                  │
      └───────┬───────────┴──────────┬───────┘
              │                      │
        ┌─────▼──────┐        ┌─────▼──────┐
        │ PostgreSQL │        │   Qdrant   │
        │ (Storage)  │        │  (Vector)  │
        └────────────┘        └────────────┘
              │
        ┌─────▼──────┐
        │   MinIO    │
        │    (S3)    │
        └────────────┘
              │
        ┌─────▼──────┐
        │ Prometheus │
        │  Grafana   │
        └────────────┘
```

### Quick Wins (Start Here!)

1. **n8n → ComfyUI API** (1 day)
   - Create HTTP Request workflow
   - Test with Qwen-Image
   - Store results in PostgreSQL

2. **File Drop Zone** (1 day)
   - Setup watched folder
   - Auto-process uploads
   - Output to shared folder

3. **Prompt Library** (2 days)
   - Create database schema
   - Simple CRUD API
   - Basic web UI

4. **MinIO Storage** (1 day)
   - Add to docker-compose
   - Configure n8n nodes
   - Setup buckets

### Resources Created

Este documento fornece:
- ✅ 15 ideias de integração detalhadas
- ✅ Código de exemplo para cada
- ✅ Priorização e complexidade
- ✅ Roadmap de implementação
- ✅ Arquitetura completa

### Recomendação Final

**Comece por**: 
1. API REST (n8n → ComfyUI)
2. MinIO storage
3. Batch queue system

**Depois expanda para**:
4. MCP Server (Claude integration)
5. RAG pipeline
6. Monitoring stack

Isso cria uma base sólida que pode crescer progressivamente! 🚀

