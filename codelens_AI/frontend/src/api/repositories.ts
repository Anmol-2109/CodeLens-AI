import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

import { getAuthHeaders, API_URL } from './auth';

export interface Repository {
  id: number;
  github_url: string;
  name: string;
  description?: string;
  status: string;
}

export const useRepositories = () => {
  return useQuery({
    queryKey: ['repositories'],
    queryFn: async () => {
      const response = await fetch(`${API_URL}/repositories/`, { headers: getAuthHeaders() });
      if (!response.ok) throw new Error('Network response was not ok');
      return response.json() as Promise<Repository[]>;
    },
    refetchInterval: 5000,
  });
};

export const useConnectRepository = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (githubUrl: string) => {
      const response = await fetch(`${API_URL}/repositories/`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({
          github_url: githubUrl,
          name: githubUrl.split('/').pop()?.replace('.git', ''),
          description: "Connected from UI"
        })
      });
      if (!response.ok) throw new Error('Failed to connect repository');
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['repositories'] });
    }
  });
};

export const useSyncRepository = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (repoId: number) => {
      const response = await fetch(`${API_URL}/repositories/${repoId}/sync`, {
        method: 'POST',
        headers: getAuthHeaders()
      });
      if (!response.ok) throw new Error('Failed to sync repository');
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['repositories'] });
    }
  });
};

export const useFiles = (repoId: number) => {
  return useQuery({
    queryKey: ['files', repoId],
    queryFn: async () => {
      const response = await fetch(`${API_URL}/repositories/${repoId}/files`, {
        headers: getAuthHeaders()
      });
      if (!response.ok) throw new Error('Failed to fetch files');
      return response.json() as Promise<{ file_path: string }[]>;
    }
  });
};

export const useDeleteRepository = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (repoId: number) => {
      const response = await fetch(`${API_URL}/repositories/${repoId}`, {
        method: 'DELETE',
        headers: getAuthHeaders()
      });
      if (!response.ok) throw new Error('Failed to delete repository');
      return true;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['repositories'] });
    }
  });
};
