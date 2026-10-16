import React, { useState, useEffect } from 'react';
import Editor from '@monaco-editor/react';
import { FileCode, Loader2 } from 'lucide-react';
import { getAuthHeaders, API_URL } from '../api/auth';

interface CodeViewerProps {
  repositoryId: number;
  filePath: string | null;
  highlightLine?: number;
}

export default function CodeViewer({ repositoryId, filePath, highlightLine }: CodeViewerProps) {
  const [code, setCode] = useState<string>('// Select a file to view its contents');
  const [loading, setLoading] = useState(false);
  const [language, setLanguage] = useState('javascript');

  useEffect(() => {
    if (!filePath) return;

    // Basic language detection based on extension
    const ext = filePath.split('.').pop()?.toLowerCase();
    const langMap: Record<string, string> = {
      'ts': 'typescript', 'tsx': 'typescript',
      'js': 'javascript', 'jsx': 'javascript',
      'py': 'python', 'java': 'java', 'go': 'go',
      'cpp': 'cpp', 'c': 'c', 'cs': 'csharp',
      'rs': 'rust', 'html': 'html', 'css': 'css',
      'json': 'json', 'md': 'markdown'
    };
    setLanguage(langMap[ext || ''] || 'plaintext');

    const fetchFile = async () => {
      setLoading(true);
      try {
        const response = await fetch(`${API_URL}/repositories/${repositoryId}/files/content?file_path=${encodeURIComponent(filePath)}`, {
          headers: getAuthHeaders(),
        });
        if (response.ok) {
          const data = await response.json();
          setCode(data.content);
        } else {
          setCode(`// Failed to load ${filePath}`);
        }
      } catch (err) {
        setCode(`// Error connecting to backend`);
      } finally {
        setLoading(false);
      }
    };

    fetchFile();
  }, [repositoryId, filePath]);

  return (
    <div className="flex flex-col h-[calc(100vh-2rem)] border border-gray-700 rounded-lg bg-gray-900 overflow-hidden m-4">
      <div className="bg-gray-800 p-4 border-b border-gray-700 font-semibold flex justify-between items-center text-gray-200">
        <div className="flex items-center space-x-2">
          <FileCode className="w-5 h-5 text-blue-400" />
          <span>{filePath || 'No file selected'}</span>
        </div>
      </div>
      
      <div className="flex-1 relative bg-gray-950">
        {loading ? (
          <div className="absolute inset-0 flex items-center justify-center bg-gray-900/50 z-10">
            <Loader2 className="w-8 h-8 text-blue-500 animate-spin" />
          </div>
        ) : null}
        
        <Editor
          height="100%"
          language={language}
          theme="vs-dark"
          value={code}
          options={{
            readOnly: true,
            minimap: { enabled: true },
            scrollBeyondLastLine: false,
            fontSize: 14,
            lineNumbers: 'on',
            renderLineHighlight: 'all',
          }}
          onMount={(editor, monaco) => {
            if (highlightLine) {
              editor.revealLineInCenter(highlightLine);
              editor.setPosition({ lineNumber: highlightLine, column: 1 });
            }
          }}
        />
      </div>
    </div>
  );
}
