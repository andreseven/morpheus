import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

export default function Relatorios() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [activeTab, setActiveTab] = useState('dashboard')
  
  // Estados para relatório dashboard
  const [dashboardData, setDashboardData] = useState(null)
  
  // Estados para relatório detalhado
  const [filtros, setFiltros] = useState({
    data_inicio: '',
    data_fim: '',
    categoria: '',
    status: '',
    prioridade: ''
  })
  const [relatorioDetalhado, setRelatorioDetalhado] = useState(null)
  
  // Estados para métricas de empresa (Super Admin)
  const [metricasEmpresas, setMetricasEmpresas] = useState([])

  useEffect(() => {
    if (activeTab === 'dashboard') {
      carregarDashboard()
    } else if (activeTab === 'metricas' && user?.perfil === 'super_admin') {
      carregarMetricasEmpresas()
    }
  }, [activeTab])

  const carregarDashboard = async () => {
    try {
      setLoading(true)
      setError('')
      
      const response = await fetch('/api/relatorios/dashboard')
      const data = await response.json()
      
      if (response.ok) {
        setDashboardData(data)
      } else {
        setError(data.error || 'Erro ao carregar relatório')
      }
    } catch (err) {
      setError('Erro de conexão')
    } finally {
      setLoading(false)
    }
  }

  const carregarRelatorioDetalhado = async () => {
    try {
      setLoading(true)
      setError('')
      
      const params = new URLSearchParams()
      Object.entries(filtros).forEach(([key, value]) => {
        if (value) params.append(key, value)
      })
      
      const response = await fetch(`/api/relatorios/detalhado?${params}`)
      const data = await response.json()
      
      if (response.ok) {
        setRelatorioDetalhado(data)
      } else {
        setError(data.error || 'Erro ao carregar relatório detalhado')
      }
    } catch (err) {
      setError('Erro de conexão')
    } finally {
      setLoading(false)
    }
  }

  const carregarMetricasEmpresas = async () => {
    try {
      setLoading(true)
      setError('')
      
      const response = await fetch('/api/relatorios/metricas-empresa')
      const data = await response.json()
      
      if (response.ok) {
        setMetricasEmpresas(data.metricas_empresas || [])
      } else {
        setError(data.error || 'Erro ao carregar métricas das empresas')
      }
    } catch (err) {
      setError('Erro de conexão')
    } finally {
      setLoading(false)
    }
  }

  const exportarRelatorio = async (formato) => {
    try {
      setLoading(true)
      setError('')
      
      const response = await fetch('/api/relatorios/exportar', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          formato: formato,
          filtros: filtros
        })
      })
      
      const data = await response.json()
      
      if (response.ok) {
        if (formato === 'csv') {
          // Converter para CSV e fazer download
          const csvContent = convertToCSV(data.dados)
          downloadFile(csvContent, `relatorio_denuncias_${new Date().toISOString().split('T')[0]}.csv`, 'text/csv')
        } else {
          // JSON
          const jsonContent = JSON.stringify(data, null, 2)
          downloadFile(jsonContent, `relatorio_denuncias_${new Date().toISOString().split('T')[0]}.json`, 'application/json')
        }
      } else {
        setError(data.error || 'Erro ao exportar relatório')
      }
    } catch (err) {
      setError('Erro de conexão')
    } finally {
      setLoading(false)
    }
  }

  const convertToCSV = (data) => {
    if (!data || data.length === 0) return ''
    
    const headers = Object.keys(data[0])
    const csvHeaders = headers.join(',')
    
    const csvRows = data.map(row => 
      headers.map(header => {
        const value = row[header] || ''
        // Escapar aspas e vírgulas
        return `"${value.toString().replace(/"/g, '""')}"`
      }).join(',')
    )
    
    return [csvHeaders, ...csvRows].join('\n')
  }

  const downloadFile = (content, filename, contentType) => {
    const blob = new Blob([content], { type: contentType })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  }

  const renderDashboard = () => (
    <div className="space-y-6">
      {dashboardData && (
        <>
          {/* Estatísticas Gerais */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="bg-white rounded-lg shadow-sm border p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-2">Total de Denúncias</h3>
              <p className="text-3xl font-bold text-blue-600">{dashboardData.total_denuncias}</p>
            </div>
            
            <div className="bg-white rounded-lg shadow-sm border p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-2">Recebidas</h3>
              <p className="text-3xl font-bold text-orange-600">{dashboardData.por_status.recebida || 0}</p>
            </div>
            
            <div className="bg-white rounded-lg shadow-sm border p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-2">Em Análise</h3>
              <p className="text-3xl font-bold text-blue-600">{dashboardData.por_status.em_analise || 0}</p>
            </div>
            
            <div className="bg-white rounded-lg shadow-sm border p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-2">Concluídas</h3>
              <p className="text-3xl font-bold text-green-600">{dashboardData.por_status.concluida || 0}</p>
            </div>
          </div>

          {/* Distribuição por Categoria */}
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Distribuição por Categoria</h3>
            <div className="space-y-3">
              {Object.entries(dashboardData.por_categoria || {}).map(([categoria, count]) => (
                <div key={categoria} className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">{categoria}</span>
                  <div className="flex items-center space-x-2">
                    <div className="w-32 bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-blue-600 h-2 rounded-full" 
                        style={{ width: `${(count / dashboardData.total_denuncias) * 100}%` }}
                      ></div>
                    </div>
                    <span className="text-sm font-medium text-gray-900">{count}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Distribuição por Prioridade */}
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Distribuição por Prioridade</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {Object.entries(dashboardData.por_prioridade || {}).map(([prioridade, count]) => {
                const colors = {
                  'baixa': 'bg-green-100 text-green-800',
                  'media': 'bg-yellow-100 text-yellow-800',
                  'alta': 'bg-orange-100 text-orange-800',
                  'critica': 'bg-red-100 text-red-800'
                }
                return (
                  <div key={prioridade} className={`rounded-lg p-4 ${colors[prioridade] || 'bg-gray-100 text-gray-800'}`}>
                    <p className="text-sm font-medium capitalize">{prioridade}</p>
                    <p className="text-2xl font-bold">{count}</p>
                  </div>
                )
              })}
            </div>
          </div>
        </>
      )}
    </div>
  )

  const renderDetalhado = () => (
    <div className="space-y-6">
      {/* Filtros */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Filtros</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Data Início</label>
            <input
              type="date"
              value={filtros.data_inicio}
              onChange={(e) => setFiltros({...filtros, data_inicio: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Data Fim</label>
            <input
              type="date"
              value={filtros.data_fim}
              onChange={(e) => setFiltros({...filtros, data_fim: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Categoria</label>
            <select
              value={filtros.categoria}
              onChange={(e) => setFiltros({...filtros, categoria: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Todas</option>
              <option value="Segurança da Informação">Segurança da Informação</option>
              <option value="Fraudes e Integridade Corporativa">Fraudes e Integridade</option>
              <option value="Conduta, Compliance e Recursos Humanos">Conduta e RH</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Status</label>
            <select
              value={filtros.status}
              onChange={(e) => setFiltros({...filtros, status: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Todos</option>
              <option value="recebida">Recebida</option>
              <option value="em_analise">Em Análise</option>
              <option value="concluida">Concluída</option>
              <option value="arquivada">Arquivada</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Prioridade</label>
            <select
              value={filtros.prioridade}
              onChange={(e) => setFiltros({...filtros, prioridade: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Todas</option>
              <option value="baixa">Baixa</option>
              <option value="media">Média</option>
              <option value="alta">Alta</option>
              <option value="critica">Crítica</option>
            </select>
          </div>
        </div>
        
        <div className="flex justify-between items-center mt-4">
          <button
            onClick={carregarRelatorioDetalhado}
            disabled={loading}
            className="px-4 py-2 bg-blue-600 text-white font-medium rounded-md hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? 'Carregando...' : 'Gerar Relatório'}
          </button>
          
          <div className="flex space-x-2">
            <button
              onClick={() => exportarRelatorio('json')}
              disabled={loading || !relatorioDetalhado}
              className="px-4 py-2 bg-green-600 text-white font-medium rounded-md hover:bg-green-700 disabled:opacity-50"
            >
              Exportar JSON
            </button>
            <button
              onClick={() => exportarRelatorio('csv')}
              disabled={loading || !relatorioDetalhado}
              className="px-4 py-2 bg-purple-600 text-white font-medium rounded-md hover:bg-purple-700 disabled:opacity-50"
            >
              Exportar CSV
            </button>
          </div>
        </div>
      </div>

      {/* Resultados */}
      {relatorioDetalhado && (
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Resultados</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-blue-600">{relatorioDetalhado.estatisticas.total_denuncias}</p>
              <p className="text-sm text-gray-600">Total de Denúncias</p>
            </div>
            
            {relatorioDetalhado.estatisticas.tempo_medio_resolucao_dias && (
              <div className="text-center">
                <p className="text-2xl font-bold text-green-600">
                  {Math.round(relatorioDetalhado.estatisticas.tempo_medio_resolucao_dias)}
                </p>
                <p className="text-sm text-gray-600">Dias Médios de Resolução</p>
              </div>
            )}
          </div>
          
          <div className="text-sm text-gray-600">
            <p>Período: {relatorioDetalhado.filtros_aplicados.data_inicio || 'Início'} até {relatorioDetalhado.filtros_aplicados.data_fim || 'Fim'}</p>
            <p>Filtros aplicados: {Object.values(relatorioDetalhado.filtros_aplicados).filter(v => v).length}</p>
          </div>
        </div>
      )}
    </div>
  )

  const renderMetricasEmpresas = () => (
    <div className="space-y-6">
      {metricasEmpresas.map((metrica) => (
        <div key={metrica.empresa.id} className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium text-gray-900">{metrica.empresa.nome}</h3>
            <span className={`px-2 py-1 text-xs font-medium rounded-full ${
              metrica.empresa.status === 'ativa' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
            }`}>
              {metrica.empresa.status}
            </span>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="text-center">
              <p className="text-2xl font-bold text-blue-600">{metrica.estatisticas.total_denuncias}</p>
              <p className="text-sm text-gray-600">Total Denúncias</p>
            </div>
            
            <div className="text-center">
              <p className="text-2xl font-bold text-green-600">{metrica.estatisticas.total_usuarios}</p>
              <p className="text-sm text-gray-600">Usuários Ativos</p>
            </div>
            
            <div className="text-center">
              <p className="text-2xl font-bold text-orange-600">{metrica.estatisticas.denuncias_30_dias}</p>
              <p className="text-sm text-gray-600">Últimos 30 Dias</p>
            </div>
            
            <div className="text-center">
              <p className="text-2xl font-bold text-purple-600">
                {Object.values(metrica.estatisticas.por_status).reduce((a, b) => a + b, 0)}
              </p>
              <p className="text-sm text-gray-600">Total por Status</p>
            </div>
          </div>
        </div>
      ))}
    </div>
  )

  if (loading && !dashboardData && !relatorioDetalhado && metricasEmpresas.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Carregando relatórios...</p>
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
          <h1 className="text-3xl font-bold text-gray-900">Relatórios e Análises</h1>
          <p className="mt-2 text-gray-600">Visualize estatísticas e gere relatórios detalhados</p>
        </div>

        {/* Mensagens */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-md p-4 mb-6">
            <p className="text-red-800">{error}</p>
          </div>
        )}

        {/* Tabs */}
        <div className="bg-white rounded-lg shadow-sm border">
          <div className="border-b border-gray-200">
            <nav className="flex space-x-8 px-6">
              <button
                onClick={() => setActiveTab('dashboard')}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'dashboard'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Dashboard
              </button>
              <button
                onClick={() => setActiveTab('detalhado')}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'detalhado'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Relatório Detalhado
              </button>
              {user?.perfil === 'super_admin' && (
                <button
                  onClick={() => setActiveTab('metricas')}
                  className={`py-4 px-1 border-b-2 font-medium text-sm ${
                    activeTab === 'metricas'
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  Métricas por Empresa
                </button>
              )}
            </nav>
          </div>
          
          <div className="p-6">
            {activeTab === 'dashboard' && renderDashboard()}
            {activeTab === 'detalhado' && renderDetalhado()}
            {activeTab === 'metricas' && user?.perfil === 'super_admin' && renderMetricasEmpresas()}
          </div>
        </div>
      </div>
    </div>
  )
}

