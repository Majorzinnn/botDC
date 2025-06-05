import React, { useEffect, useState } from "react";
import "./App.css";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Dashboard = () => {
  const [botStatus, setBotStatus] = useState({ running: false, bot_user: null });
  const [products, setProducts] = useState([]);
  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(false);
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
  }, []);

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
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
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
              <div className="flex items-center text-green-600">
                <span className="w-3 h-3 bg-green-500 rounded-full animate-pulse mr-2"></span>
                Bot rodando
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
