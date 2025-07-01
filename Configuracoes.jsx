import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

export default function Configuracoes() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [activeTab, setActiveTab] = useState('empresa')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  
  // Estados para configurações da empresa
  const [empresaConfig, setEmpresaConfig] = useState({
    nome: '',
    logo_url: '',
    cores_personalizadas: {
      primaria: '#3B82F6',
      secundaria: '#10B981',
      texto: '#1F2937'
    }
  })
  
  // Estados para categorias
  const [categorias, setCategorias] = useState([])
  const [novaCategoria, setNovaCategoria] = useState({
    nome: '',
    descricao: '',
    ativa: true
  })
  const [editandoCategoria, setEditandoCategoria] = useState(null)

  useEffect(() => {
    carregarConfiguracoes()
  }, [activeTab])

  const carregarConfiguracoes = async () => {
    try {
      setLoading(true)
      
      if (activeTab === 'empresa') {
        const response = await fetch('/api/configuracoes/empresa')
        if (response.ok) {
          const data = await response.json()
          setEmpresaConfig({
            nome: data.empresa.nome || '',
            logo_url: data.configuracoes.logo_url || '',
            cores_personalizadas: data.configuracoes.cores_personalizadas || {
              primaria: '#3B82F6',
              secundaria: '#10B981',
              texto: '#1F2937'
            }
          })
        }
      } else if (activeTab === 'categorias') {
        const response = await fetch('/api/configuracoes/categorias')
        if (response.ok) {
          const data = await response.json()
          setCategorias(data.categorias || [])
        }
      }
    } catch (err) {
      setError('Erro ao carregar configurações')
    } finally {
      setLoading(false)
    }
  }

  const salvarConfiguracaoEmpresa = async () => {
    try {
      setLoading(true)
      setError('')
      setSuccess('')
      
      const response = await fetch('/api/configuracoes/empresa', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(empresaConfig)
      })
      
      const data = await response.json()
      
      if (response.ok) {
        setSuccess('Configurações salvas com sucesso!')
      } else {
        setError(data.error || 'Erro ao salvar configurações')
      }
    } catch (err) {
      setError('Erro de conexão')
    } finally {
      setLoading(false)
    }
  }

  const criarCategoria = async () => {
    try {
      setLoading(true)
      setError('')
      setSuccess('')
      
      const response = await fetch('/api/configuracoes/categorias', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(novaCategoria)
      })
      
      const data = await response.json()
      
      if (response.ok) {
        setSuccess('Categoria criada com sucesso!')
        setNovaCategoria({ nome: '', descricao: '', ativa: true })
        carregarConfiguracoes()
      } else {
        setError(data.error || 'Erro ao criar categoria')
      }
    } catch (err) {
      setError('Erro de conexão')
    } finally {
      setLoading(false)
    }
  }

  const atualizarCategoria = async (categoriaId, dadosAtualizados) => {
    try {
      setLoading(true)
      setError('')
      setSuccess('')
      
      const response = await fetch(`/api/configuracoes/categorias/${categoriaId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(dadosAtualizados)
      })
      
      const data = await response.json()
      
      if (response.ok) {
        setSuccess('Categoria atualizada com sucesso!')
        setEditandoCategoria(null)
        carregarConfiguracoes()
      } else {
        setError(data.error || 'Erro ao atualizar categoria')
      }
    } catch (err) {
      setError('Erro de conexão')
    } finally {
      setLoading(false)
    }
  }

  const renderTabEmpresa = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-4">Informações da Empresa</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Nome da Empresa
            </label>
            <input
              type="text"
              value={empresaConfig.nome}
              onChange={(e) => setEmpresaConfig({...empresaConfig, nome: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Nome da empresa"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              URL do Logo
            </label>
            <input
              type="url"
              value={empresaConfig.logo_url}
              onChange={(e) => setEmpresaConfig({...empresaConfig, logo_url: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="https://exemplo.com/logo.png"
            />
          </div>
        </div>
      </div>

      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-4">Cores Personalizadas</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Cor Primária
            </label>
            <div className="flex items-center space-x-2">
              <input
                type="color"
                value={empresaConfig.cores_personalizadas.primaria}
                onChange={(e) => setEmpresaConfig({
                  ...empresaConfig,
                  cores_personalizadas: {
                    ...empresaConfig.cores_personalizadas,
                    primaria: e.target.value
                  }
                })}
                className="w-12 h-10 border border-gray-300 rounded cursor-pointer"
              />
              <input
                type="text"
                value={empresaConfig.cores_personalizadas.primaria}
                onChange={(e) => setEmpresaConfig({
                  ...empresaConfig,
                  cores_personalizadas: {
                    ...empresaConfig.cores_personalizadas,
                    primaria: e.target.value
                  }
                })}
                className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Cor Secundária
            </label>
            <div className="flex items-center space-x-2">
              <input
                type="color"
                value={empresaConfig.cores_personalizadas.secundaria}
                onChange={(e) => setEmpresaConfig({
                  ...empresaConfig,
                  cores_personalizadas: {
                    ...empresaConfig.cores_personalizadas,
                    secundaria: e.target.value
                  }
                })}
                className="w-12 h-10 border border-gray-300 rounded cursor-pointer"
              />
              <input
                type="text"
                value={empresaConfig.cores_personalizadas.secundaria}
                onChange={(e) => setEmpresaConfig({
                  ...empresaConfig,
                  cores_personalizadas: {
                    ...empresaConfig.cores_personalizadas,
                    secundaria: e.target.value
                  }
                })}
                className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Cor do Texto
            </label>
            <div className="flex items-center space-x-2">
              <input
                type="color"
                value={empresaConfig.cores_personalizadas.texto}
                onChange={(e) => setEmpresaConfig({
                  ...empresaConfig,
                  cores_personalizadas: {
                    ...empresaConfig.cores_personalizadas,
                    texto: e.target.value
                  }
                })}
                className="w-12 h-10 border border-gray-300 rounded cursor-pointer"
              />
              <input
                type="text"
                value={empresaConfig.cores_personalizadas.texto}
                onChange={(e) => setEmpresaConfig({
                  ...empresaConfig,
                  cores_personalizadas: {
                    ...empresaConfig.cores_personalizadas,
                    texto: e.target.value
                  }
                })}
                className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
        </div>
      </div>

      <div className="flex justify-end">
        <button
          onClick={salvarConfiguracaoEmpresa}
          disabled={loading}
          className="px-6 py-2 bg-blue-600 text-white font-medium rounded-md hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? 'Salvando...' : 'Salvar Configurações'}
        </button>
      </div>
    </div>
  )

  const renderTabCategorias = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-4">Nova Categoria</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <input
            type="text"
            value={novaCategoria.nome}
            onChange={(e) => setNovaCategoria({...novaCategoria, nome: e.target.value})}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Nome da categoria"
          />
          <input
            type="text"
            value={novaCategoria.descricao}
            onChange={(e) => setNovaCategoria({...novaCategoria, descricao: e.target.value})}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Descrição"
          />
          <button
            onClick={criarCategoria}
            disabled={loading || !novaCategoria.nome}
            className="px-4 py-2 bg-green-600 text-white font-medium rounded-md hover:bg-green-700 disabled:opacity-50"
          >
            Criar Categoria
          </button>
        </div>
      </div>

      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-4">Categorias Existentes</h3>
        
        <div className="space-y-4">
          {categorias.map((categoria) => (
            <div key={categoria.id} className="bg-gray-50 rounded-lg p-4">
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  {editandoCategoria === categoria.id ? (
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <input
                        type="text"
                        defaultValue={categoria.nome}
                        className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        onBlur={(e) => {
                          if (e.target.value !== categoria.nome) {
                            atualizarCategoria(categoria.id, { nome: e.target.value })
                          }
                        }}
                      />
                      <input
                        type="text"
                        defaultValue={categoria.descricao}
                        className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        onBlur={(e) => {
                          if (e.target.value !== categoria.descricao) {
                            atualizarCategoria(categoria.id, { descricao: e.target.value })
                          }
                        }}
                      />
                      <div className="flex items-center space-x-2">
                        <label className="flex items-center">
                          <input
                            type="checkbox"
                            checked={categoria.ativa}
                            onChange={(e) => atualizarCategoria(categoria.id, { ativa: e.target.checked })}
                            className="mr-2"
                          />
                          Ativa
                        </label>
                      </div>
                    </div>
                  ) : (
                    <div>
                      <h4 className="font-medium text-gray-900">{categoria.nome}</h4>
                      <p className="text-sm text-gray-600">{categoria.descricao}</p>
                      <div className="flex items-center space-x-4 mt-2">
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                          categoria.ativa ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                        }`}>
                          {categoria.ativa ? 'Ativa' : 'Inativa'}
                        </span>
                        <span className="text-xs text-gray-500">
                          {categoria.subcategorias?.length || 0} subcategorias
                        </span>
                      </div>
                    </div>
                  )}
                </div>
                <button
                  onClick={() => setEditandoCategoria(editandoCategoria === categoria.id ? null : categoria.id)}
                  className="ml-4 px-3 py-1 text-sm text-blue-600 hover:text-blue-800"
                >
                  {editandoCategoria === categoria.id ? 'Cancelar' : 'Editar'}
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )

  if (loading && categorias.length === 0 && !empresaConfig.nome) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Carregando configurações...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold text-sm">M</span>
                </div>
                <span className="text-xl font-bold text-gray-900">Morpheus</span>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600">{user?.nome}</span>
              <span className="px-2 py-1 bg-red-100 text-red-800 text-xs font-medium rounded-full">
                {user?.perfil === 'super_admin' ? 'Super Admin' : user?.perfil}
              </span>
              <button 
                onClick={() => navigate('/dashboard')}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
              >
                Voltar ao Dashboard
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Conteúdo Principal */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Configurações</h1>
          <p className="mt-2 text-gray-600">Gerencie as configurações do sistema e da empresa</p>
        </div>

        {/* Mensagens */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-md p-4 mb-6">
            <p className="text-red-800">{error}</p>
          </div>
        )}
        
        {success && (
          <div className="bg-green-50 border border-green-200 rounded-md p-4 mb-6">
            <p className="text-green-800">{success}</p>
          </div>
        )}

        {/* Tabs */}
        <div className="bg-white rounded-lg shadow-sm border">
          <div className="border-b border-gray-200">
            <nav className="flex space-x-8 px-6">
              <button
                onClick={() => setActiveTab('empresa')}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'empresa'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Empresa
              </button>
              <button
                onClick={() => setActiveTab('categorias')}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'categorias'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Categorias
              </button>
            </nav>
          </div>
          
          <div className="p-6">
            {activeTab === 'empresa' && renderTabEmpresa()}
            {activeTab === 'categorias' && renderTabCategorias()}
          </div>
        </div>
      </div>
    </div>
  )
}

