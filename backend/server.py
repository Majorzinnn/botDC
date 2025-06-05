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

# Stripe payments imports
from emergentintegrations.payments.stripe.checkout import StripeCheckout, CheckoutSessionResponse, CheckoutStatusResponse, CheckoutSessionRequest

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

class PaymentTransaction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    product_id: str
    discord_user_id: str
    amount: float
    currency: str = "brl"
    payment_status: str = "pending"  # pending, paid, failed, expired
    stripe_status: str = "pending"
    metadata: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    delivered: bool = False

class Purchase(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    product_id: str
    discord_user_id: str
    origin_url: str
    quantity: int = 1
    
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
        
        # Check if AI is available (has credits)
        try:
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
            
        except Exception as ai_error:
            # If AI fails (no credits, API issues), provide helpful fallback
            print(f"AI Error: {ai_error}")
            ai_response = await handle_message_without_ai(message.content)
        
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
        await message.channel.send("Desculpe, ocorreu um erro ao processar sua mensagem. Tente novamente ou use os comandos `!produtos` para ver produtos ou `!adicionar_produto` para adicionar produtos.")

async def handle_message_without_ai(message_content):
    """Handle messages when AI is not available"""
    message_lower = message_content.lower()
    
    if "ola" in message_lower or "oi" in message_lower or "hello" in message_lower:
        return "Olá! Sou o assistente do servidor. Como a IA está temporariamente indisponível, use os comandos:\n• `!produtos` - Ver produtos\n• `!adicionar_produto [nome] [preço]` - Adicionar produto\n• `!config_canal_ai` - Configurar canal"
    
    elif "produto" in message_lower and "adicionar" in message_lower:
        return "Para adicionar produtos, use: `!adicionar_produto [nome] [preço] [descrição] [categoria] [estoque]`\nExemplo: `!adicionar_produto Netflix 25.99 'Conta Premium' streaming 5`"
    
    elif "produto" in message_lower and ("mostrar" in message_lower or "listar" in message_lower):
        return "Para ver todos os produtos, use o comando: `!produtos`"
    
    elif "ajuda" in message_lower or "help" in message_lower:
        return """🤖 **Comandos Disponíveis:**
        
• `!produtos` - Lista todos os produtos
• `!adicionar_produto [nome] [preço] [desc] [categoria] [estoque]` - Adiciona produto
• `!config_canal_ai` - Configura este canal para IA

**Exemplos:**
• `!adicionar_produto Netflix 25.99 "Conta Premium" streaming 5`
• `!produtos`

*Nota: IA temporariamente indisponível - use comandos diretos*"""
    
    else:
        return f"Recebi sua mensagem: '{message_content}'\n\nComo a IA está indisponível, use:\n• `!ajuda` - Ver comandos\n• `!produtos` - Ver produtos\n• `!adicionar_produto` - Adicionar produto"

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

@api_router.post("/bot/stop")
async def stop_bot():
    """Stop Discord bot"""
    global bot_running
    if bot_running and bot.is_ready():
        await bot.close()
        bot_running = False
        return {"message": "Bot desligado com sucesso"}
    return {"message": "Bot já está desligado"}

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
    
    # Remove MongoDB ObjectId
    if '_id' in config:
        del config['_id']
    
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

# Payment APIs
@api_router.post("/payments/checkout")
async def create_checkout_session(purchase: Purchase):
    """Create Stripe checkout session for product purchase"""
    try:
        # Get product details
        product = await db.products.find_one({"id": purchase.product_id, "active": True})
        if not product:
            raise HTTPException(status_code=404, detail="Produto não encontrado")
        
        # Check stock
        if product.get("stock", 0) < purchase.quantity:
            raise HTTPException(status_code=400, detail="Estoque insuficiente")
        
        # Calculate total amount
        amount = float(product["price"]) * purchase.quantity
        
        # Initialize Stripe
        stripe_checkout = StripeCheckout(api_key=os.environ.get('STRIPE_API_KEY'))
        
        # Create checkout session
        success_url = f"{purchase.origin_url}?session_id={{CHECKOUT_SESSION_ID}}&payment=success"
        cancel_url = f"{purchase.origin_url}?payment=cancelled"
        
        metadata = {
            "product_id": purchase.product_id,
            "product_name": product["name"],
            "discord_user_id": purchase.discord_user_id,
            "quantity": str(purchase.quantity),
            "bot_purchase": "true"
        }
        
        checkout_request = CheckoutSessionRequest(
            amount=amount,
            currency="brl",
            success_url=success_url,
            cancel_url=cancel_url,
            metadata=metadata
        )
        
        session_response = await stripe_checkout.create_checkout_session(checkout_request)
        
        # Create payment transaction record
        transaction = PaymentTransaction(
            session_id=session_response.session_id,
            product_id=purchase.product_id,
            discord_user_id=purchase.discord_user_id,
            amount=amount,
            currency="brl",
            metadata=metadata
        )
        
        await db.payment_transactions.insert_one(transaction.dict())
        
        return {
            "url": session_response.url,
            "session_id": session_response.session_id
        }
        
    except Exception as e:
        print(f"Erro ao criar checkout: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao criar checkout: {str(e)}")

@api_router.get("/payments/status/{session_id}")
async def get_payment_status(session_id: str):
    """Check payment status and update transaction"""
    try:
        # Get transaction from database
        transaction = await db.payment_transactions.find_one({"session_id": session_id})
        if not transaction:
            raise HTTPException(status_code=404, detail="Transação não encontrada")
        
        # If already processed as paid, return status
        if transaction.get("payment_status") == "paid":
            return {
                "payment_status": "paid",
                "stripe_status": transaction.get("stripe_status"),
                "delivered": transaction.get("delivered", False)
            }
        
        # Check with Stripe
        stripe_checkout = StripeCheckout(api_key=os.environ.get('STRIPE_API_KEY'))
        stripe_status = await stripe_checkout.get_checkout_status(session_id)
        
        # Update transaction
        update_data = {
            "stripe_status": stripe_status.status,
            "updated_at": datetime.utcnow()
        }
        
        # If payment is complete, process delivery
        if stripe_status.payment_status == "paid" and transaction.get("payment_status") != "paid":
            update_data["payment_status"] = "paid"
            
            # Process delivery (deliver product to Discord user)
            delivery_success = await deliver_product_to_user(transaction)
            update_data["delivered"] = delivery_success
            
            # Update product stock
            if delivery_success:
                quantity = int(transaction.get("metadata", {}).get("quantity", 1))
                await db.products.update_one(
                    {"id": transaction["product_id"]},
                    {"$inc": {"stock": -quantity}}
                )
        
        elif stripe_status.status == "expired":
            update_data["payment_status"] = "expired"
        
        # Update transaction in database
        await db.payment_transactions.update_one(
            {"session_id": session_id},
            {"$set": update_data}
        )
        
        return {
            "payment_status": update_data.get("payment_status", transaction.get("payment_status")),
            "stripe_status": stripe_status.status,
            "delivered": update_data.get("delivered", transaction.get("delivered", False))
        }
        
    except Exception as e:
        print(f"Erro ao verificar status: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao verificar status: {str(e)}")

@api_router.get("/payments/transactions")
async def get_payment_transactions():
    """Get all payment transactions"""
    transactions = await db.payment_transactions.find().sort("created_at", -1).limit(100).to_list(100)
    # Remove sensitive data
    for transaction in transactions:
        if '_id' in transaction:
            del transaction['_id']
    return transactions

async def deliver_product_to_user(transaction):
    """Deliver product to Discord user via DM or channel"""
    try:
        discord_user_id = transaction.get("discord_user_id")
        product_id = transaction.get("product_id")
        
        # Get product details
        product = await db.products.find_one({"id": product_id})
        if not product:
            return False
        
        # Get Discord user
        try:
            user = await bot.fetch_user(int(discord_user_id))
        except:
            print(f"Usuário Discord {discord_user_id} não encontrado")
            return False
        
        # Create delivery message
        embed = discord.Embed(
            title="🎉 Compra Realizada com Sucesso!",
            description=f"Obrigado por comprar **{product['name']}**!",
            color=0x00ff00
        )
        embed.add_field(name="Produto", value=product['name'], inline=True)
        embed.add_field(name="Preço", value=f"R$ {product['price']:.2f}", inline=True)
        embed.add_field(name="Descrição", value=product.get('description', 'N/A'), inline=False)
        
        # Add delivery instructions based on product type
        if product.get('category') == 'streaming':
            embed.add_field(
                name="📧 Entrega",
                value="Suas credenciais de acesso foram enviadas por email. Verifique também a caixa de spam.",
                inline=False
            )
        else:
            embed.add_field(
                name="📦 Entrega",
                value="Seu produto foi processado. Em caso de dúvidas, entre em contato com o suporte.",
                inline=False
            )
        
        embed.set_footer(text=f"ID da Transação: {transaction.get('session_id')[:8]}...")
        
        # Send DM to user
        try:
            await user.send(embed=embed)
            print(f"Produto entregue via DM para {user.name}")
            return True
        except discord.Forbidden:
            # If DM fails, try to send in configured channel
            print(f"Não foi possível enviar DM para {user.name}, tentando canal público")
            
            guild_id = os.environ.get('DISCORD_GUILD_ID')
            config = await get_bot_config(guild_id)
            
            if config and config.get('shop_channel_id'):
                try:
                    channel = bot.get_channel(int(config['shop_channel_id']))
                    if channel:
                        await channel.send(f"<@{discord_user_id}>", embed=embed)
                        return True
                except:
                    pass
            
            return False
            
    except Exception as e:
        print(f"Erro ao entregar produto: {e}")
        return False

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
