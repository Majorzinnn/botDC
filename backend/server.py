from fastapi import FastAPI, APIRouter, HTTPException, BackgroundTasks
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime
import asyncio
import json

# Discord and AI imports
import discord
from discord.ext import commands
from emergentintegrations.llm.chat import LlmChat, UserMessage

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Discord Bot Setup
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.guild_messages = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Global variables for bot state
bot_running = False
ai_chat_sessions = {}

# Pydantic Models
class Product(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    price: float
    description: Optional[str] = ""
    category: Optional[str] = "general"
    stock: int = 0
    active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ProductCreate(BaseModel):
    name: str
    price: float
    description: Optional[str] = ""
    category: Optional[str] = "general"
    stock: int = 0

class BotConfig(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    guild_id: str
    ai_channel_id: Optional[str] = None
    shop_channel_id: Optional[str] = None
    welcome_message: Optional[str] = "Bem-vindo ao servidor!"
    ai_enabled: bool = True
    shop_enabled: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Conversation(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    channel_id: str
    message: str
    ai_response: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    session_id: str

class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str

# Discord Bot Events
@bot.event
async def on_ready():
    global bot_running
    bot_running = True
    print(f'Bot conectado como {bot.user}')
    
    # Initialize AI for configured guild
    guild_id = os.environ.get('DISCORD_GUILD_ID')
    if guild_id:
        await setup_guild_ai(guild_id)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    # Check if message is in AI channel
    config = await get_bot_config(str(message.guild.id))
    if not config or not config.get('ai_enabled', False):
        return
    
    ai_channel_id = config.get('ai_channel_id')
    if ai_channel_id and str(message.channel.id) == ai_channel_id:
        await process_ai_message(message)
    
    await bot.process_commands(message)

async def process_ai_message(message):
    """Process message with AI and respond"""
    try:
        user_id = str(message.author.id)
        channel_id = str(message.channel.id)
        session_id = f"{user_id}_{channel_id}"
        
        # Get or create AI chat session
        if session_id not in ai_chat_sessions:
            ai_chat_sessions[session_id] = LlmChat(
                api_key=os.environ.get('OPENAI_API_KEY'),
                session_id=session_id,
                system_message="""Você é um assistente inteligente para um servidor Discord com sistema de loja.
                
                Você pode ajudar com:
                - Adicionar produtos: "adicionar produto [nome] com preço [valor]"
                - Listar produtos: "mostrar produtos" ou "listar produtos"
                - Remover produtos: "remover produto [nome]"
                - Configurar loja: "configurar loja"
                - Responder perguntas gerais
                
                Sempre responda em português de forma amigável e útil. Quando um usuário quiser adicionar um produto, 
                você deve fazer perguntas para coletar todos os detalhes necessários como nome, preço, descrição, categoria e estoque.
                
                Responda sempre de forma clara e direta."""
            ).with_model("openai", "gpt-4o")
        
        # Send message to AI
        user_message = UserMessage(text=message.content)
        ai_response = await ai_chat_sessions[session_id].send_message(user_message)
        
        # Check if AI wants to perform an action
        if "adicionar produto" in message.content.lower():
            await handle_product_creation(message, ai_response)
        elif "listar produtos" in message.content.lower() or "mostrar produtos" in message.content.lower():
            await handle_product_listing(message)
        else:
            # Send AI response
            await message.channel.send(ai_response)
        
        # Store conversation
        conversation = Conversation(
            user_id=user_id,
            channel_id=channel_id,
            message=message.content,
            ai_response=ai_response,
            session_id=session_id
        )
        await db.conversations.insert_one(conversation.dict())
        
    except Exception as e:
        print(f"Erro ao processar mensagem AI: {e}")
        await message.channel.send("Desculpe, ocorreu um erro ao processar sua mensagem.")

async def handle_product_creation(message, ai_response):
    """Handle product creation from AI conversation"""
    try:
        # Extract product info from message (basic parsing)
        content = message.content.lower()
        
        # Send AI response first
        await message.channel.send(ai_response)
        
        # Ask for more details if needed
        await message.channel.send("Para adicionar o produto, preciso de mais algumas informações. Use o comando completo: `!adicionar_produto nome preço descrição categoria estoque`")
        
    except Exception as e:
        print(f"Erro ao criar produto: {e}")
        await message.channel.send("Erro ao processar criação do produto.")

async def handle_product_listing(message):
    """Handle product listing"""
    try:
        products = await db.products.find({"active": True}).to_list(100)
        
        if not products:
            await message.channel.send("Nenhum produto cadastrado ainda.")
            return
        
        embed = discord.Embed(title="🛒 Produtos Disponíveis", color=0x00ff00)
        
        for product in products:
            embed.add_field(
                name=f"{product['name']} - R$ {product['price']:.2f}",
                value=f"{product.get('description', 'Sem descrição')}\nEstoque: {product.get('stock', 0)}",
                inline=False
            )
        
        await message.channel.send(embed=embed)
        
    except Exception as e:
        print(f"Erro ao listar produtos: {e}")
        await message.channel.send("Erro ao listar produtos.")

# Bot Commands
@bot.command(name='adicionar_produto')
async def add_product_command(ctx, nome: str, preco: float, *, resto: str = ""):
    """Comando para adicionar produto"""
    try:
        parts = resto.split(" ", 2) if resto else []
        descricao = parts[0] if len(parts) > 0 else ""
        categoria = parts[1] if len(parts) > 1 else "geral"
        estoque = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 0
        
        product = Product(
            name=nome,
            price=preco,
            description=descricao,
            category=categoria,
            stock=estoque
        )
        
        await db.products.insert_one(product.dict())
        
        embed = discord.Embed(title="✅ Produto Adicionado", color=0x00ff00)
        embed.add_field(name="Nome", value=nome, inline=True)
        embed.add_field(name="Preço", value=f"R$ {preco:.2f}", inline=True)
        embed.add_field(name="Categoria", value=categoria, inline=True)
        embed.add_field(name="Estoque", value=estoque, inline=True)
        if descricao:
            embed.add_field(name="Descrição", value=descricao, inline=False)
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        await ctx.send(f"Erro ao adicionar produto: {e}")

@bot.command(name='produtos')
async def list_products_command(ctx):
    """Comando para listar produtos"""
    await handle_product_listing(ctx.message)

@bot.command(name='config_canal_ai')
async def config_ai_channel(ctx, channel_id: str = None):
    """Configure AI channel"""
    if not channel_id:
        channel_id = str(ctx.channel.id)
    
    guild_id = str(ctx.guild.id)
    
    # Update bot config
    await db.bot_configs.update_one(
        {"guild_id": guild_id},
        {"$set": {"ai_channel_id": channel_id}},
        upsert=True
    )
    
    await ctx.send(f"Canal de IA configurado para <#{channel_id}>")

# Helper functions
async def setup_guild_ai(guild_id: str):
    """Setup AI for a guild"""
    try:
        # Check if config exists
        config = await db.bot_configs.find_one({"guild_id": guild_id})
        if not config:
            bot_config = BotConfig(guild_id=guild_id)
            await db.bot_configs.insert_one(bot_config.dict())
    except Exception as e:
        print(f"Erro ao configurar guild: {e}")

async def get_bot_config(guild_id: str):
    """Get bot configuration for guild"""
    try:
        config = await db.bot_configs.find_one({"guild_id": guild_id})
        return config
    except Exception as e:
        print(f"Erro ao buscar config: {e}")
        return None

# API Routes
@api_router.get("/")
async def root():
    return {"message": "Discord Bot API funcionando!"}

@api_router.get("/bot/status")
async def get_bot_status():
    return {"running": bot_running, "bot_user": str(bot.user) if bot.user else None}

@api_router.post("/bot/start")
async def start_bot(background_tasks: BackgroundTasks):
    """Start Discord bot"""
    if not bot_running:
        discord_token = os.environ.get('DISCORD_BOT_TOKEN')
        if not discord_token:
            raise HTTPException(status_code=400, detail="Discord token não configurado")
        
        background_tasks.add_task(run_bot, discord_token)
        return {"message": "Bot iniciando..."}
    return {"message": "Bot já está rodando"}

async def run_bot(token: str):
    """Run Discord bot in background"""
    try:
        await bot.start(token)
    except Exception as e:
        print(f"Erro ao iniciar bot: {e}")

@api_router.get("/products", response_model=List[Product])
async def get_products():
    """Get all products"""
    products = await db.products.find({"active": True}).to_list(100)
    return [Product(**product) for product in products]

@api_router.post("/products", response_model=Product)
async def create_product(product: ProductCreate):
    """Create new product"""
    product_obj = Product(**product.dict())
    await db.products.insert_one(product_obj.dict())
    return product_obj

@api_router.delete("/products/{product_id}")
async def delete_product(product_id: str):
    """Delete product"""
    result = await db.products.update_one(
        {"id": product_id},
        {"$set": {"active": False}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return {"message": "Produto removido"}

@api_router.get("/conversations")
async def get_conversations():
    """Get recent conversations"""
    conversations = await db.conversations.find().sort("timestamp", -1).limit(50).to_list(50)
    return conversations

@api_router.get("/bot/config/{guild_id}")
async def get_guild_config(guild_id: str):
    """Get bot configuration for guild"""
    config = await get_bot_config(guild_id)
    if not config:
        raise HTTPException(status_code=404, detail="Configuração não encontrada")
    return config

@api_router.put("/bot/config/{guild_id}")
async def update_guild_config(guild_id: str, config_data: dict):
    """Update bot configuration"""
    await db.bot_configs.update_one(
        {"guild_id": guild_id},
        {"$set": config_data},
        upsert=True
    )
    return {"message": "Configuração atualizada"}

# Legacy routes
@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    _ = await db.status_checks.insert_one(status_obj.dict())
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**status_check) for status_check in status_checks]

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    """Startup event"""
    # Auto-start bot if tokens are available
    discord_token = os.environ.get('DISCORD_BOT_TOKEN')
    if discord_token and not bot_running:
        asyncio.create_task(run_bot(discord_token))

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
    if bot.is_ready():
        await bot.close()
