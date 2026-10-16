import React, { useState } from 'react';
import { File, Folder, ChevronRight, ChevronDown } from 'lucide-react';

interface FileTreeProps {
  files: { file_path: string }[];
  activeFile: string | null;
  onFileSelect: (filePath: string) => void;
}

type TreeNode = {
  name: string;
  path: string;
  type: 'file' | 'folder';
  children: { [key: string]: TreeNode };
};

const buildTree = (files: { file_path: string }[]) => {
  const root: TreeNode = { name: 'root', path: '', type: 'folder', children: {} };

  files.forEach((file) => {
    const parts = file.file_path.split(/[\/\\]/);
    let currentNode = root;

    parts.forEach((part, index) => {
      if (!currentNode.children[part]) {
        const isFile = index === parts.length - 1;
        currentNode.children[part] = {
          name: part,
          path: parts.slice(0, index + 1).join('/'),
          type: isFile ? 'file' : 'folder',
          children: {},
        };
      }
      currentNode = currentNode.children[part];
    });
  });

  return root;
};

const FileTreeNode: React.FC<{ node: TreeNode; activeFile: string | null; onSelect: (path: string) => void; level: number }> = ({ node, activeFile, onSelect, level }) => {
  const [isOpen, setIsOpen] = useState(false);

  if (node.type === 'file') {
    const isActive = activeFile === node.path;
    return (
      <button
        onClick={() => onSelect(node.path)}
        style={{ paddingLeft: `${level * 12 + 8}px` }}
        className={`flex items-center space-x-2 w-full text-left py-1.5 rounded text-sm truncate ${
          isActive ? 'bg-blue-600/20 text-blue-400' : 'text-gray-400 hover:text-gray-200 hover:bg-gray-800'
        }`}
        title={node.path}
      >
        <File className="w-4 h-4 flex-shrink-0" />
        <span className="truncate">{node.name}</span>
      </button>
    );
  }

  const children = Object.values(node.children).sort((a, b) => {
    if (a.type === b.type) return a.name.localeCompare(b.name);
    return a.type === 'folder' ? -1 : 1;
  });

  return (
    <div>
      <button
        onClick={() => setIsOpen(!isOpen)}
        style={{ paddingLeft: `${level * 12 + 8}px` }}
        className="flex items-center space-x-2 w-full text-left py-1.5 rounded text-sm truncate text-gray-300 hover:text-white hover:bg-gray-800"
      >
        {isOpen ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
        <Folder className="w-4 h-4 flex-shrink-0 text-blue-400" />
        <span className="truncate">{node.name}</span>
      </button>
      {isOpen && (
        <div className="flex flex-col">
          {children.map((child) => (
            <FileTreeNode key={child.path} node={child} activeFile={activeFile} onSelect={onSelect} level={level + 1} />
          ))}
        </div>
      )}
    </div>
  );
};

export const FileTree: React.FC<FileTreeProps> = ({ files, activeFile, onFileSelect }) => {
  const tree = buildTree(files);
  const children = Object.values(tree.children).sort((a, b) => {
    if (a.type === b.type) return a.name.localeCompare(b.name);
    return a.type === 'folder' ? -1 : 1;
  });

  return (
    <div className="flex flex-col space-y-0.5">
      {children.map((child) => (
        <FileTreeNode key={child.path} node={child} activeFile={activeFile} onSelect={onFileSelect} level={0} />
      ))}
    </div>
  );
};
