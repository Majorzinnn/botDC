import React, { useEffect, useState } from "react";
import "./App.css";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const FeaturesTab = () => {
  return (
    <div className="space-y-8">
      {/* AI Features */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-6 border border-blue-200">
        <h3 className="text-2xl font-bold text-indigo-800 mb-4 flex items-center">
          🧠 Inteligência Artificial
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-white p-4 rounded-lg shadow-sm">
            <h4 className="font-semibold text-gray-800 mb-2">Comandos Naturais</h4>
            <p className="text-sm text-gray-600 mb-2">Converse naturalmente com o bot:</p>
            <ul className="text-xs text-gray-600 space-y-1">
              <li>• "adicionar produto Netflix com preço 25"</li>
              <li>• "mostrar todos os produtos"</li>
              <li>• "remover produto Netflix"</li>
              <li>• "configurar loja"</li>
            </ul>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm">
            <h4 className="font-semibold text-gray-800 mb-2">Configuração</h4>
            <p className="text-sm text-gray-600 mb-2">Configure o canal de IA:</p>
            <code className="text-xs bg-gray-100 px-2 py-1 rounded">!config_canal_ai</code>
          </div>
        </div>
      </div>

      {/* Shop Features */}
      <div className="bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg p-6 border border-green-200">
        <h3 className="text-2xl font-bold text-emerald-800 mb-4 flex items-center">
          🛒 Sistema de Loja
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white p-4 rounded-lg shadow-sm">
            <h4 className="font-semibold text-gray-800 mb-2">Produtos</h4>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• Gestão completa de produtos</li>
              <li>• Categorias personalizadas</li>
              <li>• Controle de estoque</li>
              <li>• Preços flexíveis</li>
            </ul>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm">
            <h4 className="font-semibold text-gray-800 mb-2">Comandos Slash</h4>
            <ul className="text-sm text-gray-600 space-y-1">
              <li><code className="text-xs bg-gray-100 px-1 rounded">!produtos</code> - Lista produtos</li>
              <li><code className="text-xs bg-gray-100 px-1 rounded">!adicionar_produto</code> - Adiciona</li>
            </ul>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm">
            <h4 className="font-semibold text-gray-800 mb-2">Futuras Funcionalidades</h4>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• Integração com pagamentos</li>
              <li>• Sistema de carrinho</li>
              <li>• Cupons de desconto</li>
              <li>• Afiliados</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Bot Commands */}
      <div className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg p-6 border border-purple-200">
        <h3 className="text-2xl font-bold text-purple-800 mb-4 flex items-center">
          ⚡ Comandos do Bot
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 className="font-semibold text-gray-800 mb-3">Comandos Básicos</h4>
            <div className="space-y-2">
              <div className="bg-white p-3 rounded border-l-4 border-purple-400">
                <code className="text-sm font-mono text-purple-600">!config_canal_ai</code>
                <p className="text-xs text-gray-600 mt-1">Configura o canal onde a IA responde</p>
              </div>
              <div className="bg-white p-3 rounded border-l-4 border-purple-400">
                <code className="text-sm font-mono text-purple-600">!produtos</code>
                <p className="text-xs text-gray-600 mt-1">Lista todos os produtos da loja</p>
              </div>
              <div className="bg-white p-3 rounded border-l-4 border-purple-400">
                <code className="text-sm font-mono text-purple-600">!adicionar_produto [nome] [preço] [desc] [categoria] [estoque]</code>
                <p className="text-xs text-gray-600 mt-1">Adiciona um novo produto</p>
              </div>
            </div>
          </div>
          <div>
            <h4 className="font-semibold text-gray-800 mb-3">Exemplos de Uso</h4>
            <div className="space-y-2">
              <div className="bg-white p-3 rounded border-l-4 border-green-400">
                <code className="text-sm font-mono text-green-600">!adicionar_produto "Netflix Premium" 25.99 "Conta Netflix" streaming 5</code>
              </div>
              <div className="bg-white p-3 rounded border-l-4 border-blue-400">
                <p className="text-sm text-blue-600">Via IA: "adicionar produto Netflix com preço 25"</p>
              </div>
              <div className="bg-white p-3 rounded border-l-4 border-orange-400">
                <p className="text-sm text-orange-600">Via IA: "mostrar todos os produtos disponíveis"</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Setup Instructions */}
      <div className="bg-gradient-to-r from-red-50 to-orange-50 rounded-lg p-6 border border-red-200">
        <h3 className="text-2xl font-bold text-red-800 mb-4 flex items-center">
          ⚙️ Configuração Inicial
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 className="font-semibold text-gray-800 mb-3">Passo a Passo</h4>
            <ol className="space-y-2 text-sm text-gray-600">
              <li className="flex items-start">
                <span className="bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs mr-3 mt-0.5 font-bold">1</span>
                <div>
                  <p className="font-medium text-gray-800">Ativar Privileged Intents</p>
                  <p>Vá em <a href="https://discord.com/developers/applications" target="_blank" rel="noopener noreferrer" className="text-blue-600 underline">Discord Developer Portal</a></p>
                  <p>Ative "Server Members Intent" e "Message Content Intent"</p>
                </div>
              </li>
              <li className="flex items-start">
                <span className="bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs mr-3 mt-0.5 font-bold">2</span>
                <div>
                  <p className="font-medium text-gray-800">Iniciar o Bot</p>
                  <p>Clique em "🚀 Iniciar Bot" acima</p>
                </div>
              </li>
              <li className="flex items-start">
                <span className="bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs mr-3 mt-0.5 font-bold">3</span>
                <div>
                  <p className="font-medium text-gray-800">Configurar Canal</p>
                  <p>No Discord: <code className="bg-gray-100 px-1 rounded">!config_canal_ai</code></p>
                </div>
              </li>
              <li className="flex items-start">
                <span className="bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs mr-3 mt-0.5 font-bold">4</span>
                <div>
                  <p className="font-medium text-gray-800">Começar a Usar</p>
                  <p>Converse naturalmente com o bot!</p>
                </div>
              </li>
            </ol>
          </div>
          <div>
            <h4 className="font-semibold text-gray-800 mb-3">Problemas Comuns</h4>
            <div className="space-y-3">
              <div className="bg-white p-3 rounded border border-yellow-300">
                <p className="font-medium text-yellow-800">❌ Bot não responde</p>
                <p className="text-sm text-yellow-700">Verifique se as privileged intents estão ativadas</p>
              </div>
              <div className="bg-white p-3 rounded border border-yellow-300">
                <p className="font-medium text-yellow-800">❌ Erro ao processar mensagem</p>
                <p className="text-sm text-yellow-700">Verifique se a chave OpenAI tem créditos</p>
              </div>
              <div className="bg-white p-3 rounded border border-yellow-300">
                <p className="font-medium text-yellow-800">❌ Comandos não funcionam</p>
                <p className="text-sm text-yellow-700">Configure o canal primeiro com !config_canal_ai</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Future Features */}
      <div className="bg-gradient-to-r from-gray-50 to-slate-50 rounded-lg p-6 border border-gray-200">
        <h3 className="text-2xl font-bold text-gray-800 mb-4 flex items-center">
          🚀 Funcionalidades Futuras
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white p-4 rounded-lg shadow-sm">
            <h4 className="font-semibold text-gray-800 mb-2">🛡️ Moderação</h4>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• Anti-spam automático</li>
              <li>• Sistema de warns</li>
              <li>• Auto-ban/kick</li>
              <li>• Logs de moderação</li>
            </ul>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm">
            <h4 className="font-semibold text-gray-800 mb-2">💳 Pagamentos</h4>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• Integração Stripe</li>
              <li>• PIX automático</li>
              <li>• Carrinho de compras</li>
              <li>• Sistema de tickets</li>
            </ul>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm">
            <h4 className="font-semibold text-gray-800 mb-2">🎯 Marketing</h4>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• Sorteios automáticos</li>
              <li>• Sistema de levels</li>
              <li>• Cupons de desconto</li>
              <li>• Programa de afiliados</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

const Dashboard = () => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [botStatus, setBotStatus] = useState({ running: false, bot_user: null });
  const [products, setProducts] = useState([]);
  const [conversations, setConversations] = useState([]);
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [paymentLoading, setPaymentLoading] = useState(false);
  const [newProduct, setNewProduct] = useState({
    name: "",
    price: "",
    description: "",
    category: "geral",
    stock: "0"
  });

  useEffect(() => {
    fetchBotStatus();
    fetchProducts();
    fetchConversations();
    fetchTransactions();
    
    // Check for payment return
    checkPaymentReturn();
  }, []);

  const checkPaymentReturn = () => {
    const urlParams = new URLSearchParams(window.location.search);
    const sessionId = urlParams.get('session_id');
    const paymentStatus = urlParams.get('payment');
    
    if (sessionId && paymentStatus === 'success') {
      pollPaymentStatus(sessionId);
      // Clean URL
      window.history.replaceState({}, document.title, window.location.pathname);
    }
  };

  const pollPaymentStatus = async (sessionId, attempts = 0) => {
    const maxAttempts = 5;
    const pollInterval = 2000;

    if (attempts >= maxAttempts) {
      alert('Verificação de pagamento expirou. Verifique o histórico de transações.');
      return;
    }

    try {
      const response = await axios.get(`${API}/payments/status/${sessionId}`);
      const data = response.data;
      
      if (data.payment_status === 'paid') {
        alert('Pagamento realizado com sucesso! O produto foi entregue.');
        fetchTransactions();
        return;
      } else if (data.stripe_status === 'expired') {
        alert('Sessão de pagamento expirou.');
        return;
      }

      // Continue polling
      setTimeout(() => pollPaymentStatus(sessionId, attempts + 1), pollInterval);
    } catch (error) {
      console.error('Erro ao verificar pagamento:', error);
      if (attempts < maxAttempts - 1) {
        setTimeout(() => pollPaymentStatus(sessionId, attempts + 1), pollInterval);
      }
    }
  };

  const fetchTransactions = async () => {
    try {
      const response = await axios.get(`${API}/payments/transactions`);
      setTransactions(response.data);
    } catch (error) {
      console.error("Erro ao buscar transações:", error);
    }
  };

  const purchaseProduct = async (productId) => {
    if (!window.confirm('Deseja comprar este produto?')) return;
    
    try {
      setPaymentLoading(true);
      
      const discordUserId = prompt('Digite seu Discord User ID:');
      if (!discordUserId) return;
      
      const response = await axios.post(`${API}/payments/checkout`, {
        product_id: productId,
        discord_user_id: discordUserId,
        origin_url: window.location.origin,
        quantity: 1
      });
      
      if (response.data.url) {
        window.location.href = response.data.url;
      }
    } catch (error) {
      console.error("Erro ao processar compra:", error);
      alert(`Erro ao processar compra: ${error.response?.data?.detail || error.message}`);
    } finally {
      setPaymentLoading(false);
    }
  };

  const fetchBotStatus = async () => {
    try {
      const response = await axios.get(`${API}/bot/status`);
      setBotStatus(response.data);
    } catch (error) {
      console.error("Erro ao buscar status do bot:", error);
    }
  };

  const fetchProducts = async () => {
    try {
      const response = await axios.get(`${API}/products`);
      setProducts(response.data);
    } catch (error) {
      console.error("Erro ao buscar produtos:", error);
    }
  };

  const fetchConversations = async () => {
    try {
      const response = await axios.get(`${API}/conversations`);
      setConversations(response.data);
    } catch (error) {
      console.error("Erro ao buscar conversas:", error);
    }
  };

  const startBot = async () => {
    try {
      setLoading(true);
      await axios.post(`${API}/bot/start`);
      setTimeout(fetchBotStatus, 2000);
    } catch (error) {
      console.error("Erro ao iniciar bot:", error);
      alert("Erro ao iniciar bot");
    } finally {
      setLoading(false);
    }
  };

  const stopBot = async () => {
    try {
      setLoading(true);
      await axios.post(`${API}/bot/stop`);
      setTimeout(fetchBotStatus, 1000);
    } catch (error) {
      console.error("Erro ao parar bot:", error);
      alert("Erro ao parar bot");
    } finally {
      setLoading(false);
    }
  };

  const createProduct = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/products`, {
        ...newProduct,
        price: parseFloat(newProduct.price),
        stock: parseInt(newProduct.stock)
      });
      setNewProduct({ name: "", price: "", description: "", category: "geral", stock: "0" });
      fetchProducts();
      alert("Produto criado com sucesso!");
    } catch (error) {
      console.error("Erro ao criar produto:", error);
      alert("Erro ao criar produto");
    }
  };

  const deleteProduct = async (productId) => {
    try {
      await axios.delete(`${API}/products/${productId}`);
      fetchProducts();
      alert("Produto removido com sucesso!");
    } catch (error) {
      console.error("Erro ao remover produto:", error);
      alert("Erro ao remover produto");
    }
  };

  const DashboardContent = () => (
    <div>
      {/* Bot Control */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">🔧 Controle do Bot</h2>
        <div className="flex items-center space-x-4">
          {!botStatus.running ? (
            <button
              onClick={startBot}
              disabled={loading}
              className="bg-green-500 hover:bg-green-600 text-white px-6 py-2 rounded-lg font-medium disabled:opacity-50"
            >
              {loading ? "Iniciando..." : "🚀 Iniciar Bot"}
            </button>
          ) : (
            <div className="flex items-center space-x-4">
              <div className="flex items-center text-green-600">
                <span className="w-3 h-3 bg-green-500 rounded-full animate-pulse mr-2"></span>
                Bot rodando
              </div>
              <button
                onClick={stopBot}
                disabled={loading}
                className="bg-red-500 hover:bg-red-600 text-white px-6 py-2 rounded-lg font-medium disabled:opacity-50"
              >
                {loading ? "Parando..." : "🛑 Parar Bot"}
              </button>
            </div>
          )}
          <button
            onClick={fetchBotStatus}
            className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg"
          >
            🔄 Atualizar
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Products Section */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">🛒 Produtos da Loja</h2>
          
          {/* Add Product Form */}
          <form onSubmit={createProduct} className="bg-gray-50 p-4 rounded-lg mb-6">
            <h3 className="text-lg font-semibold mb-3">Adicionar Produto</h3>
            <div className="space-y-3">
              <input
                type="text"
                placeholder="Nome do produto"
                value={newProduct.name}
                onChange={(e) => setNewProduct({...newProduct, name: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                required
              />
              <div className="grid grid-cols-2 gap-3">
                <input
                  type="number"
                  step="0.01"
                  placeholder="Preço"
                  value={newProduct.price}
                  onChange={(e) => setNewProduct({...newProduct, price: e.target.value})}
                  className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                  required
                />
                <input
                  type="number"
                  placeholder="Estoque"
                  value={newProduct.stock}
                  onChange={(e) => setNewProduct({...newProduct, stock: e.target.value})}
                  className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                />
              </div>
              <select
                value={newProduct.category}
                onChange={(e) => setNewProduct({...newProduct, category: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
              >
                <option value="geral">Geral</option>
                <option value="streaming">Streaming</option>
                <option value="jogos">Jogos</option>
                <option value="software">Software</option>
              </select>
              <textarea
                placeholder="Descrição (opcional)"
                value={newProduct.description}
                onChange={(e) => setNewProduct({...newProduct, description: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                rows="2"
              />
              <button
                type="submit"
                className="w-full bg-indigo-600 hover:bg-indigo-700 text-white py-2 rounded-lg font-medium"
              >
                ➕ Adicionar Produto
              </button>
            </div>
          </form>

          {/* Products List */}
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {products.length === 0 ? (
              <p className="text-gray-500 text-center py-4">Nenhum produto cadastrado</p>
            ) : (
              products.map((product) => (
                <div key={product.id} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <h4 className="font-semibold text-gray-900">{product.name}</h4>
                      <p className="text-green-600 font-bold">R$ {product.price.toFixed(2)}</p>
                      <p className="text-sm text-gray-600">{product.description}</p>
                      <div className="flex items-center mt-2 space-x-4">
                        <span className="text-xs bg-gray-100 px-2 py-1 rounded">
                          {product.category}
                        </span>
                        <span className="text-xs text-gray-500">
                          Estoque: {product.stock}
                        </span>
                      </div>
                      <div className="flex items-center mt-3 space-x-2">
                        <button
                          onClick={() => purchaseProduct(product.id)}
                          disabled={paymentLoading || product.stock <= 0}
                          className="bg-green-500 hover:bg-green-600 text-white px-3 py-1 rounded text-sm font-medium disabled:opacity-50"
                        >
                          {paymentLoading ? "..." : product.stock <= 0 ? "Esgotado" : "💳 Comprar"}
                        </button>
                      </div>
                    </div>
                    <button
                      onClick={() => deleteProduct(product.id)}
                      className="text-red-500 hover:text-red-700 ml-4"
                    >
                      🗑️
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Conversations Section */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">💬 Conversas Recentes</h2>
          <div className="space-y-4 max-h-96 overflow-y-auto">
            {conversations.length === 0 ? (
              <p className="text-gray-500 text-center py-4">Nenhuma conversa ainda</p>
            ) : (
              conversations.map((conv) => (
                <div key={conv.id} className="border-l-4 border-blue-500 pl-4 py-2">
                  <div className="text-sm text-gray-500 mb-1">
                    Usuário: {conv.user_id} | {new Date(conv.timestamp).toLocaleString()}
                  </div>
                  <div className="bg-gray-100 p-2 rounded mb-2">
                    <strong>Usuário:</strong> {conv.message}
                  </div>
                  <div className="bg-blue-50 p-2 rounded">
                    <strong>IA:</strong> {conv.ai_response}
                  </div>
                </div>
              ))
            )}
          </div>
          <button
            onClick={fetchConversations}
            className="mt-4 w-full bg-blue-500 hover:bg-blue-600 text-white py-2 rounded-lg"
          >
            🔄 Atualizar Conversas
          </button>
        </div>
      </div>

      {/* Transactions Section */}
      <div className="bg-white rounded-lg shadow-md p-6 mt-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">💳 Transações de Pagamento</h2>
        <div className="space-y-3 max-h-96 overflow-y-auto">
          {transactions.length === 0 ? (
            <p className="text-gray-500 text-center py-4">Nenhuma transação ainda</p>
          ) : (
            transactions.map((transaction) => (
              <div key={transaction.id} className="border border-gray-200 rounded-lg p-4">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <h4 className="font-semibold text-gray-900">
                      {transaction.metadata?.product_name || 'Produto'}
                    </h4>
                    <p className="text-sm text-gray-600">
                      Discord User: {transaction.discord_user_id}
                    </p>
                    <p className="text-green-600 font-bold">
                      R$ {transaction.amount.toFixed(2)}
                    </p>
                    <div className="flex items-center mt-2 space-x-4">
                      <span className={`text-xs px-2 py-1 rounded ${
                        transaction.payment_status === 'paid' 
                          ? 'bg-green-100 text-green-800' 
                          : transaction.payment_status === 'pending'
                          ? 'bg-yellow-100 text-yellow-800'
                          : 'bg-red-100 text-red-800'
                      }`}>
                        {transaction.payment_status}
                      </span>
                      <span className="text-xs text-gray-500">
                        {new Date(transaction.created_at).toLocaleString()}
                      </span>
                      {transaction.delivered && (
                        <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                          Entregue
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
        <button
          onClick={fetchTransactions}
          className="mt-4 w-full bg-purple-500 hover:bg-purple-600 text-white py-2 rounded-lg"
        >
          🔄 Atualizar Transações
        </button>
      </div>

      {/* Instructions */}
      <div className="bg-yellow-50 border-l-4 border-yellow-400 p-6 mt-8">
        <h3 className="text-lg font-semibold text-yellow-800 mb-2">📝 Como usar:</h3>
        <div className="text-yellow-700 space-y-2">
          <p><strong>1.</strong> Inicie o bot clicando em "Iniciar Bot"</p>
          <p><strong>2.</strong> No Discord, use <code>!config_canal_ai</code> no canal onde quer que a IA responda</p>
          <p><strong>3.</strong> Converse naturalmente com a IA no canal configurado</p>
          <p><strong>4.</strong> Use comandos como:</p>
          <ul className="ml-4 space-y-1">
            <li>• "adicionar produto Netflix com preço 20"</li>
            <li>• "mostrar produtos"</li>
            <li>• <code>!adicionar_produto Netflix 20.00 Conta Premium streaming 5</code></li>
            <li>• <code>!produtos</code></li>
          </ul>
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <div className="bg-indigo-600 text-white shadow-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <div className="w-8 h-8 bg-white rounded-full flex items-center justify-center mr-3">
                <span className="text-indigo-600 font-bold">🤖</span>
              </div>
              <h1 className="text-3xl font-bold">Discord Bot Dashboard</h1>
            </div>
            <div className="flex items-center space-x-4">
              <div className={`px-3 py-1 rounded-full text-sm font-medium ${
                botStatus.running ? 'bg-green-500' : 'bg-red-500'
              }`}>
                {botStatus.running ? 'Online' : 'Offline'}
              </div>
              {botStatus.bot_user && (
                <span className="text-sm">Bot: {botStatus.bot_user}</span>
              )}
            </div>
          </div>
          
          {/* Tabs */}
          <div className="flex space-x-8 pb-4">
            <button
              onClick={() => setActiveTab('dashboard')}
              className={`pb-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'dashboard'
                  ? 'border-white text-white'
                  : 'border-transparent text-indigo-200 hover:text-white hover:border-indigo-300'
              }`}
            >
              📊 Dashboard
            </button>
            <button
              onClick={() => setActiveTab('features')}
              className={`pb-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'features'
                  ? 'border-white text-white'
                  : 'border-transparent text-indigo-200 hover:text-white hover:border-indigo-300'
              }`}
            >
              ⚡ Funcionalidades
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'dashboard' ? <DashboardContent /> : <FeaturesTab />}
      </div>
    </div>
  );
};

function App() {
  return (
    <div className="App">
      <Dashboard />
    </div>
  );
}

export default App;
