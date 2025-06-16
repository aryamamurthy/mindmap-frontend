# Mind Map Explorer Frontend Plan (Minimal)

## Overview
This document outlines a minimal Next.js frontend for the Mind Map Explorer API. The focus is on core functionality only with the easiest possible implementation.

---

## Technology Stack

### Minimal Dependencies
- **Next.js 14+** (App Router) - Main framework
- **TypeScript** - Type safety
- **Basic CSS** - Simple styling (no framework needed)
- **useState hooks** - Basic state management
- **fetch API** - API calls

---

## Folder Structure (3 levels max)
```
src/
├── app/
│   ├── page.tsx           # Home page
│   ├── layout.tsx         # Root layout
│   └── spaces/
│       ├── page.tsx       # Spaces list
│       └── [id]/page.tsx  # Space viewer
├── lib/
│   └── api.ts             # All API calls
└── styles/
    └── globals.css        # All styles
```

---

## Pages (3 total)

### 1. Home (`/`)
- Title "Mind Map Explorer"
- Button "View Spaces" → go to `/spaces`

### 2. Spaces List (`/spaces`)
- List of spaces as cards
- "Create Space" button (uses prompt() dialog)
- Click space → go to `/spaces/[id]`

### 3. Space Viewer (`/spaces/[id]`)
- Space name as title
- Simple text list of nodes
- "Add Node" button (uses prompt() dialog)
- Click node → show content below

---

## User Actions (Simple)

### Create Space
1. Click "Create Space"
2. prompt() asks for name
3. API call creates space
4. Page refreshes

### Add Node
1. Click "Add Node"
2. prompt() asks for title
3. API creates node (AI generates content)
4. Page refreshes

### View Content
1. Click node in list
2. Content shows below
3. "AI generating..." if not ready

---

## Implementation

### API Client (lib/api.ts)
```typescript
const API_BASE = 'https://your-api.com';

export async function getSpaces() {
  const response = await fetch(`${API_BASE}/spaces`);
  return response.json();
}

export async function createSpace(name: string) {
  const response = await fetch(`${API_BASE}/spaces`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, ownerId: 'user1' })
  });
  return response.json();
}

export async function getSpace(spaceId: string) {
  const response = await fetch(`${API_BASE}/spaces/${spaceId}`);
  return response.json();
}

export async function addNode(spaceId: string, title: string) {
  const response = await fetch(`${API_BASE}/spaces/${spaceId}/nodes`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title })
  });
  return response.json();
}
```

### Home Page (app/page.tsx)
```typescript
import Link from 'next/link';

export default function Home() {
  return (
    <div style={{ padding: '20px', textAlign: 'center' }}>
      <h1>Mind Map Explorer</h1>
      <p>Create mind maps with AI content.</p>
      <Link href="/spaces">
        <button style={{ 
          padding: '12px 24px', 
          backgroundColor: '#007bff', 
          color: 'white', 
          border: 'none', 
          borderRadius: '4px' 
        }}>
          View Spaces
        </button>
      </Link>
    </div>
  );
}
```

### Spaces List (app/spaces/page.tsx)
```typescript
'use client';
import { useState, useEffect } from 'react';
import Link from 'next/link';
import { getSpaces, createSpace } from '../../lib/api';

export default function Spaces() {
  const [spaces, setSpaces] = useState([]);

  useEffect(() => {
    loadSpaces();
  }, []);

  async function loadSpaces() {
    const data = await getSpaces();
    setSpaces(data);
  }

  async function handleCreate() {
    const name = prompt('Space name:');
    if (name) {
      await createSpace(name);
      loadSpaces();
    }
  }

  return (
    <div style={{ padding: '20px' }}>
      <h1>My Spaces</h1>
      <button onClick={handleCreate} style={{ marginBottom: '20px' }}>
        Create Space
      </button>
      
      {spaces.map((space: any) => (
        <Link key={space.spaceId} href={`/spaces/${space.spaceId}`}>
          <div style={{ 
            border: '1px solid #ddd', 
            padding: '16px', 
            margin: '8px 0',
            cursor: 'pointer' 
          }}>
            <h3>{space.name}</h3>
          </div>
        </Link>
      ))}
    </div>
  );
}
```

### Space Viewer (app/spaces/[id]/page.tsx)
```typescript
'use client';
import { useState, useEffect } from 'react';
import { getSpace, addNode } from '../../../lib/api';

export default function SpaceViewer({ params }: { params: { id: string } }) {
  const [space, setSpace] = useState<any>(null);
  const [selectedNode, setSelectedNode] = useState<any>(null);

  useEffect(() => {
    loadSpace();
  }, []);

  async function loadSpace() {
    const data = await getSpace(params.id);
    setSpace(data);
  }

  async function handleAddNode() {
    const title = prompt('Node title:');
    if (title) {
      await addNode(params.id, title);
      loadSpace();
    }
  }

  if (!space) return <div>Loading...</div>;

  return (
    <div style={{ padding: '20px' }}>
      <h1>{space.name}</h1>
      
      <button onClick={handleAddNode} style={{ marginBottom: '20px' }}>
        Add Node
      </button>

      <div style={{ display: 'flex', gap: '20px' }}>
        <div style={{ flex: 1 }}>
          <h3>Nodes</h3>
          {space.nodes?.map((node: any) => (
            <div 
              key={node.nodeId}
              onClick={() => setSelectedNode(node)}
              style={{ 
                padding: '8px', 
                border: '1px solid #eee',
                margin: '4px 0',
                cursor: 'pointer',
                backgroundColor: selectedNode?.nodeId === node.nodeId ? '#f0f0f0' : 'white'
              }}
            >
              {node.title}
            </div>
          ))}
        </div>

        <div style={{ flex: 2 }}>
          {selectedNode && (
            <div>
              <h3>{selectedNode.title}</h3>
              <div style={{ 
                padding: '16px', 
                border: '1px solid #ddd',
                backgroundColor: '#f9f9f9' 
              }}>
                {selectedNode.content || 'AI generating content...'}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
```

### Basic Styles (styles/globals.css)
```css
body {
  font-family: Arial, sans-serif;
  margin: 0;
  padding: 0;
}

button {
  padding: 8px 16px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

button:hover {
  background-color: #0056b3;
}

a {
  text-decoration: none;
  color: inherit;
}
```

---

## Setup Instructions

1. **Create Next.js app:**
   ```bash
   npx create-next-app@latest mindmap-frontend --typescript --app --eslint
   cd mindmap-frontend
   ```

2. **Add API base URL to `.env.local`:**
   ```
   NEXT_PUBLIC_API_BASE_URL=https://your-api-url.com
   ```

3. **Create the files above in their respective folders**

4. **Run:**
   ```bash
   npm run dev
   ```

---

## Key Features

✅ **3 simple pages only**  
✅ **No external libraries** (except Next.js)  
✅ **prompt() dialogs** instead of complex modals  
✅ **Basic inline styles** instead of CSS frameworks  
✅ **Simple state management** with useState  
✅ **Easy to understand** code structure  
✅ **Mobile friendly** basic responsive design  

---

This is the absolute minimum viable frontend that connects to your Mind Map Explorer API with core functionality only.
