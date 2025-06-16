// API utility functions for Mind Map Explorer

// Use local proxy for development to bypass CORS
const API_BASE = process.env.NODE_ENV === 'production' 
  ? (process.env.NEXT_PUBLIC_MAIN_API_BASE || "https://ozqiu4g1m7.execute-api.us-east-1.amazonaws.com/Prod")
  : "/api/proxy";

export interface User {
  Id: string;
  email: string;
  name: string;
  createdAt: string;
}

export interface Space {
  spaceId: string;
  name: string;
  description?: string;
  ownerId?: string;
  createdAt: string;
  updatedAt?: string;
  nodes?: TreeNode[];
}

export interface TreeNode extends Node {
  children: TreeNode[];
}

export interface Node {
  nodeId: string;
  spaceId: string;
  title: string;
  content?: string;
  contentHTML?: string;
  orderIndex: number;
  parentNodeId?: string;
  depth?: number;
  createdAt: string;
  updatedAt: string;
  s3Key?: string;
}

export interface NodeWithContent extends Node {
  contentHTML?: string;
}

// User API functions
export const userAPI = {
  async create(email: string, name: string): Promise<User> {
    const response = await fetch(`${API_BASE}/users`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, name })
    });
    if (!response.ok) throw new Error(`Failed to create user: ${response.statusText}`);
    return response.json();
  },

  async get(userId: string): Promise<User> {
    const response = await fetch(`${API_BASE}/users/${userId}`);
    if (!response.ok) throw new Error(`Failed to get user: ${response.statusText}`);
    return response.json();
  },

  async list(): Promise<User[]> {
    const response = await fetch(`${API_BASE}/users`);
    if (!response.ok) throw new Error(`Failed to list users: ${response.statusText}`);
    return response.json();
  },

  async update(userId: string, email: string, name: string): Promise<User> {
    const response = await fetch(`${API_BASE}/users/${userId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, name })
    });
    if (!response.ok) throw new Error(`Failed to update user: ${response.statusText}`);
    return response.json();
  },

  async delete(userId: string): Promise<void> {
    const response = await fetch(`${API_BASE}/users/${userId}`, {
      method: 'DELETE'
    });
    if (!response.ok) throw new Error(`Failed to delete user: ${response.statusText}`);
  }
};

// Spaces API functions
export const spacesAPI = {
  async list(): Promise<Space[]> {
    const url = `${API_BASE}/spaces`;
    console.log('🔍 Making request to:', url);
    console.log('🔍 API_BASE:', API_BASE);
    
    const response = await fetch(url);
    console.log('📡 Response status:', response.status);
    console.log('📡 Response headers:', Object.fromEntries(response.headers.entries()));
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error('❌ Error response:', errorText);
      throw new Error(`Failed to list spaces: ${response.status} ${response.statusText} - ${errorText}`);
    }
    return response.json();
  },

  async create(name: string, description?: string, ownerId?: string): Promise<Space> {
    const response = await fetch(`${API_BASE}/spaces`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, description, ownerId })
    });
    if (!response.ok) throw new Error(`Failed to create space: ${response.statusText}`);
    return response.json();
  },

  async get(spaceId: string): Promise<Space> {
    const response = await fetch(`${API_BASE}/spaces/${spaceId}`);
    if (!response.ok) throw new Error(`Failed to get space: ${response.statusText}`);
    return response.json();
  },

  async update(spaceId: string, name?: string, description?: string): Promise<Space> {
    const response = await fetch(`${API_BASE}/spaces/${spaceId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, description })
    });
    if (!response.ok) throw new Error(`Failed to update space: ${response.statusText}`);
    return response.json();
  },

  async delete(spaceId: string): Promise<void> {
    const response = await fetch(`${API_BASE}/spaces/${spaceId}`, {
      method: 'DELETE'
    });
    if (!response.ok) throw new Error(`Failed to delete space: ${response.statusText}`);
  }
};
// Nodes API functions
export const nodesAPI = {
  async create(spaceId: string, title: string, parentNodeId?: string, contentHTML?: string): Promise<Node> {
    const response = await fetch(`${API_BASE}/spaces/${spaceId}/nodes`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title, parentNodeId, orderIndex: 0, contentHTML })
    });
    if (!response.ok) throw new Error(`Failed to create node: ${response.statusText}`);
    return response.json();
  },

  async get(spaceId: string, nodeId: string): Promise<NodeWithContent> {
    const response = await fetch(`${API_BASE}/spaces/${spaceId}/nodes/${nodeId}`);
    if (!response.ok) throw new Error(`Failed to get node: ${response.statusText}`);
    return response.json();
  },

  async update(spaceId: string, nodeId: string, title?: string, contentHTML?: string): Promise<Node> {
    const response = await fetch(`${API_BASE}/spaces/${spaceId}/nodes/${nodeId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title, contentHTML })
    });
    if (!response.ok) throw new Error(`Failed to update node: ${response.statusText}`);
    return response.json();
  },

  async delete(spaceId: string, nodeId: string): Promise<void> {
    const response = await fetch(`${API_BASE}/spaces/${spaceId}/nodes/${nodeId}`, {
      method: 'DELETE'
    });
    if (!response.ok) throw new Error(`Failed to delete node: ${response.statusText}`);
  },

  async reorder(spaceId: string, nodeOrders: Array<{ nodeId: string; newOrderIndex: number }>): Promise<void> {
    const response = await fetch(`${API_BASE}/spaces/${spaceId}/nodes/reorder`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(nodeOrders)
    });
    if (!response.ok) throw new Error(`Failed to reorder nodes: ${response.statusText}`);
  }
};

// Utility function to poll for AI content generation completion
export async function pollForContent(spaceId: string, nodeId: string, maxAttempts = 30, interval = 2000): Promise<NodeWithContent> {
  for (let attempt = 0; attempt < maxAttempts; attempt++) {
    const node = await nodesAPI.get(spaceId, nodeId);
    if (node.contentHTML && node.contentHTML.trim()) {
      return node;
    }
    await new Promise(resolve => setTimeout(resolve, interval));
  }
  throw new Error('Content generation timeout');
}

// Simplified functions for the minimal frontend - No user management needed for demo
export const api = {
  // Spaces
  async getSpaces(): Promise<Space[]> {
    return spacesAPI.list();
  },

  async createSpace(name: string, description?: string): Promise<Space> {
    return spacesAPI.create(name, description);
  },

  async getSpace(spaceId: string): Promise<Space> {
    return spacesAPI.get(spaceId);
  },

  async getSpaceTree(spaceId: string): Promise<Space> {
    // According to Final_API_Docs.md, GET /spaces/{spaceId} returns the space with full node tree
    return spacesAPI.get(spaceId);
  },

  // Nodes
  async createNode(spaceId: string, title: string, parentNodeId?: string): Promise<Node> {
    return nodesAPI.create(spaceId, title, parentNodeId);
  },

  async getNode(spaceId: string, nodeId: string): Promise<NodeWithContent> {
    return nodesAPI.get(spaceId, nodeId);
  },

  async updateNode(spaceId: string, nodeId: string, title?: string, contentHTML?: string): Promise<Node> {
    return nodesAPI.update(spaceId, nodeId, title, contentHTML);
  },

  async deleteNode(spaceId: string, nodeId: string): Promise<void> {
    return nodesAPI.delete(spaceId, nodeId);
  },

  // Utility
  async pollForContent(spaceId: string, nodeId: string): Promise<NodeWithContent> {
    return pollForContent(spaceId, nodeId);
  }
};
