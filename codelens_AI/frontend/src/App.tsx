import { BrowserRouter as Router, Routes, Route, Link, Navigate, useLocation, useParams } from 'react-router-dom'
import { Code2, Settings, LayoutDashboard, GitBranch, Plus, RefreshCw, LogOut, User as UserIcon, File, Folder, Trash2 } from 'lucide-react'
import React, { useState, useEffect } from 'react'
import ChatPanel from './components/ChatPanel'
import CodeViewer from './components/CodeViewer'
import { FileTree } from './components/FileTree'
import { useRepositories, useConnectRepository, useSyncRepository, useFiles, useDeleteRepository } from './api/repositories'
import { AuthProvider, useAuth } from './context/AuthContext'
import Login from './pages/Login'
import Register from './pages/Register'

function Sidebar() {
  const { user, logout } = useAuth();
  
  return (
    <div className="w-64 bg-gray-900 border-r border-gray-800 h-screen flex flex-col">
      <div className="p-4 flex items-center space-x-2 border-b border-gray-800">
        <Code2 className="text-blue-500 w-8 h-8" />
        <span className="text-xl font-bold text-white">CodeLens</span>
      </div>
      
      <nav className="flex-1 p-4 flex flex-col space-y-2">
        <Link to="/" className="flex items-center space-x-3 text-gray-300 hover:text-white hover:bg-gray-800 p-2 rounded-md">
          <LayoutDashboard className="w-5 h-5" />
          <span>Dashboard</span>
        </Link>
        <Link to="/repositories" className="flex items-center space-x-3 text-gray-300 hover:text-white hover:bg-gray-800 p-2 rounded-md">
          <GitBranch className="w-5 h-5" />
          <span>Repositories</span>
        </Link>
      </nav>

      <div className="p-4 border-t border-gray-800 flex flex-col space-y-2">
        {user && (
          <div className="flex items-center space-x-3 p-2 rounded-md mb-2 text-gray-300">
            <div className="bg-gray-800 p-1.5 rounded-full">
              <UserIcon className="w-4 h-4 text-blue-400" />
            </div>
            <div className="flex flex-col overflow-hidden">
              <span className="text-sm font-medium text-white truncate">{user.full_name || 'User'}</span>
              <span className="text-xs text-gray-500 truncate">{user.email}</span>
            </div>
          </div>
        )}
        <Link to="/settings" className="flex items-center space-x-3 text-gray-300 hover:text-white hover:bg-gray-800 p-2 rounded-md">
          <Settings className="w-5 h-5" />
          <span>Settings</span>
        </Link>
        <button onClick={logout} className="flex items-center space-x-3 text-gray-400 hover:text-red-400 hover:bg-gray-800 p-2 rounded-md transition-colors w-full text-left">
          <LogOut className="w-5 h-5" />
          <span>Sign Out</span>
        </button>
      </div>
    </div>
  )
}

function Dashboard() {
  const { data: repositories } = useRepositories();
  const repoCount = repositories?.length || 0;
  // In a full app, we would have an endpoint for this, but for now we'll derive it from repos
  const indexedRepos = repositories?.filter(r => r.status === 'COMPLETED').length || 0;

  return (
    <div className="p-8 w-full">
      <h1 className="text-3xl font-bold mb-6">Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-gray-800 p-6 rounded-lg border border-gray-700 shadow">
          <h3 className="text-gray-400 font-semibold mb-2">Total Repositories</h3>
          <p className="text-4xl font-bold text-blue-500">{repoCount}</p>
        </div>
        <div className="bg-gray-800 p-6 rounded-lg border border-gray-700 shadow">
          <h3 className="text-gray-400 font-semibold mb-2">Indexed Repositories</h3>
          <p className="text-4xl font-bold text-green-500">{indexedRepos}</p>
        </div>
        <div className="bg-gray-800 p-6 rounded-lg border border-gray-700 shadow">
          <h3 className="text-gray-400 font-semibold mb-2">Total Queries</h3>
          <p className="text-4xl font-bold text-purple-500">0</p>
        </div>
      </div>
    </div>
  )
}

function RepositoryWorkspace() {
  const { id } = useParams();
  const repoId = parseInt(id || '0', 10);
  const [activeFile, setActiveFile] = useState<string | null>(null);
  const { data: files, isLoading } = useFiles(repoId);

  return (
    <div className="flex h-full w-full bg-gray-950">
      <div className="w-64 bg-gray-900 border-r border-gray-800 flex flex-col overflow-hidden">
        <div className="p-4 border-b border-gray-800 font-semibold text-gray-200">
          Files
        </div>
        <div className="flex-1 overflow-y-auto p-2 space-y-1">
          {isLoading ? (
            <div className="text-gray-500 p-2 text-sm">Loading files...</div>
          ) : files?.length === 0 ? (
            <div className="text-gray-500 p-2 text-sm">No files indexed yet.</div>
          ) : (
            <FileTree files={files || []} activeFile={activeFile} onFileSelect={setActiveFile} />
          )}
        </div>
      </div>
      <div className="flex-1 min-w-[400px]">
        <ChatPanel repositoryId={repoId} />
      </div>
      <div className="flex-1 min-w-[400px]">
        <CodeViewer repositoryId={repoId} filePath={activeFile} />
      </div>
    </div>
  )
}

function RepositoryList() {
  const { data: repositories, isLoading } = useRepositories();
  const connectMutation = useConnectRepository();
  const syncMutation = useSyncRepository();
  const deleteMutation = useDeleteRepository();
  const [url, setUrl] = useState('');

  const handleConnect = (e: React.FormEvent) => {
    e.preventDefault();
    if (url) {
      connectMutation.mutate(url, {
        onSuccess: () => setUrl('')
      });
    }
  };

  return (
    <div className="p-8 w-full">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Repositories</h1>
      </div>

      <div className="bg-gray-800 p-6 rounded-lg border border-gray-700 shadow mb-8">
        <h2 className="text-xl font-semibold mb-4">Connect New Repository</h2>
        <form onSubmit={handleConnect} className="flex space-x-4">
          <input 
            type="text" 
            placeholder="https://github.com/username/repo.git" 
            className="flex-1 bg-gray-900 border border-gray-700 rounded-md py-2 px-4 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
          />
          <button 
            type="submit" 
            disabled={connectMutation.isPending || !url}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md font-medium flex items-center space-x-2 disabled:opacity-50"
          >
            {connectMutation.isPending ? <RefreshCw className="w-5 h-5 animate-spin" /> : <Plus className="w-5 h-5" />}
            <span>Connect</span>
          </button>
        </form>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {isLoading ? (
          <p className="text-gray-400">Loading repositories...</p>
        ) : repositories?.length === 0 ? (
          <p className="text-gray-400 col-span-3">No repositories connected yet.</p>
        ) : (
          repositories?.map(repo => (
            <div key={repo.id} className="bg-gray-800 p-6 rounded-lg border border-gray-700 shadow flex flex-col justify-between">
              <div>
                <div className="flex justify-between items-start mb-2">
                  <h3 className="text-lg font-bold text-white truncate">{repo.name}</h3>
                  <span className={`px-2 py-1 rounded text-xs font-semibold uppercase ${repo.status === 'COMPLETED' ? 'bg-green-900 text-green-300' : repo.status === 'INDEXING' ? 'bg-yellow-900 text-yellow-300' : 'bg-gray-700 text-gray-300'}`}>
                    {repo.status || 'PENDING'}
                  </span>
                </div>
                <p className="text-sm text-gray-400 mb-4 truncate">{repo.github_url}</p>
              </div>
              <div className="flex space-x-2 border-t border-gray-700 pt-4 mt-2">
                <Link to={`/repositories/${repo.id}/chat`} className="flex-1 bg-gray-700 hover:bg-gray-600 text-white text-center px-3 py-2 rounded-md text-sm font-medium">
                  Open Workspace
                </Link>
                <button 
                  onClick={() => syncMutation.mutate(repo.id)}
                  disabled={syncMutation.isPending || repo.status === 'INDEXING'}
                  className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-2 rounded-md text-sm font-medium disabled:opacity-50"
                  title="Re-index codebase"
                >
                  <RefreshCw className={`w-4 h-4 ${syncMutation.isPending && 'animate-spin'}`} />
                </button>
                <button 
                  onClick={() => {
                    if (window.confirm('Are you sure you want to delete this repository?')) {
                      deleteMutation.mutate(repo.id);
                    }
                  }}
                  disabled={deleteMutation.isPending}
                  className="bg-red-600 hover:bg-red-700 text-white px-3 py-2 rounded-md text-sm font-medium disabled:opacity-50"
                  title="Delete repository"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}

const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const { isAuthenticated, isLoading } = useAuth();
  const location = useLocation();

  if (isLoading) {
    return <div className="h-screen w-full flex items-center justify-center bg-gray-950 text-white">Loading...</div>;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return <>{children}</>;
};

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/*" element={
            <ProtectedRoute>
              <div className="flex h-screen bg-gray-950 text-gray-100 font-sans">
                <Sidebar />
                <main className="flex-1 overflow-auto">
                  <Routes>
                    <Route path="/" element={<Dashboard />} />
                    <Route path="/repositories" element={<RepositoryList />} />
                    <Route path="/repositories/:id/chat" element={<RepositoryWorkspace />} />
                    <Route path="/settings" element={<div className="p-8"><h1 className="text-3xl font-bold mb-6">Settings</h1><p className="text-gray-400">Configuration panel goes here.</p></div>} />
                  </Routes>
                </main>
              </div>
            </ProtectedRoute>
          } />
        </Routes>
      </Router>
    </AuthProvider>
  )
}

export default App
