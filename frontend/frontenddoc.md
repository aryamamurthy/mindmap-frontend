# Mind Map Explorer - End-to-End Frontend Functional Documentation

**Last Updated:** December 19, 2024  
**Version:** 1.0  
**Technology Stack:** Next.js 14.2.5, React 18.3.1, TypeScript, Plain CSS

## Table of Contents
1. [System Overview](#1-system-overview)
2. [Architecture & Data Flow](#2-architecture--data-flow)
3. [User Journey & Functional Flows](#3-user-journey--functional-flows)
4. [Core Components Deep Dive](#4-core-components-deep-dive)
5. [API Integration & Data Management](#5-api-integration--data-management)
6. [Error Handling & User Experience](#6-error-handling--user-experience)
7. [Development vs Production Configuration](#7-development-vs-production-configuration)
8. [Logging & Monitoring Strategy](#8-logging--monitoring-strategy)
9. [Deployment Architecture](#9-deployment-architecture)

---

## 1. System Overview

### 1.1. Application Purpose
The Mind Map Explorer is a web-based application that enables users to create, organize, and explore hierarchical mind maps. It provides an intuitive interface for managing spaces (mind map containers) and nodes (individual ideas/concepts) with AI-powered content generation capabilities.

### 1.2. Key Features
- **Space Management**: Create, view, and manage mind map spaces
- **Hierarchical Node System**: Add, edit, and organize nodes in tree structures
- **AI Content Generation**: Automatic content generation for nodes (backend-driven)
- **Interactive Tree Visualization**: Visual representation of mind map hierarchies
- **Real-time Updates**: Dynamic content loading and state management
- **Responsive Design**: Works across desktop and mobile devices

### 1.3. Technology Stack
```
Frontend Framework:    Next.js 14.2.5 (App Router)
UI Library:           React 18.3.1
Type Safety:          TypeScript
Styling:              Plain CSS (no external dependencies)
State Management:     React Hooks (useState, useEffect)
HTTP Client:          Native Fetch API
Development Server:   localhost:3001
Production Hosting:   AWS Amplify
```

---

## 2. Architecture & Data Flow

### 2.1. High-Level Architecture
```
┌─────────────────────┐    ┌──────────────────────┐    ┌─────────────────────┐
│   User Browser      │    │   Frontend (Next.js) │    │   Backend API       │
│                     │    │                      │    │                     │
│ • User Interactions │◄──►│ • UI Components      │◄──►│ • AWS API Gateway   │
│ • DOM Rendering     │    │ • State Management   │    │ • Lambda Functions  │
│ • Event Handling    │    │ • API Calls          │    │ • DynamoDB          │
└─────────────────────┘    └──────────────────────┘    └─────────────────────┘
```

### 2.2. Data Flow Patterns

#### 2.2.1. Development Environment
```
User Action → React Component → API Client (api.ts) → Next.js Proxy (/api/proxy/*) → AWS API Gateway → Lambda → DynamoDB
                                                                    ↓
User Interface ← State Update ← Component Re-render ← API Response ← Next.js Proxy ← API Gateway Response
```

#### 2.2.2. Production Environment
```
User Action → React Component → API Client (api.ts) → Direct HTTPS → AWS API Gateway → Lambda → DynamoDB
                                                                    ↓
User Interface ← State Update ← Component Re-render ← API Response ← Direct HTTPS ← API Gateway Response
```

### 2.3. Component Hierarchy
```
RootLayout (layout.js)
├── Header (Global Navigation)
├── Main Content Area
    ├── Home Page (page.tsx)
    ├── Spaces List (/spaces/page.tsx)
    │   ├── Space Cards
    │   ├── Create Space Modal
    │   └── Loading/Error States
    └── Space Viewer (/spaces/[id]/page.tsx)
        ├── Space Info Panel
        ├── Node Tree Visualization
        ├── Node Content Panel
        ├── Add Node Form
        └── Loading/Error States
```

---

## 3. User Journey & Functional Flows

### 3.1. Primary User Flows

#### 3.1.1. First-Time User Journey
1. **Landing** → User visits home page (`/`)
2. **Discovery** → Reads feature overview and value proposition
3. **Navigation** → Clicks "Browse Spaces" or "Create New Space"
4. **Space Creation** → Creates first mind map space
5. **Node Addition** → Adds initial nodes to organize thoughts
6. **Content Exploration** → Views generated content and expands mind map

#### 3.1.2. Returning User Journey
1. **Entry** → Direct navigation to spaces list (`/spaces`)
2. **Space Selection** → Chooses existing space from list
3. **Mind Map Interaction** → Views/edits nodes, adds new content
4. **Space Management** → Creates new spaces or manages existing ones

### 3.2. Detailed Functional Flows

#### 3.2.1. Space Creation Flow
```
1. User clicks "Create New Space" button
2. Modal opens with form fields (name, description)
3. User fills in space details
4. Form validation occurs (name required)
5. API call to POST /spaces
6. Success: Modal closes, user redirected to new space
7. Error: Error message displayed, form remains open
```

#### 3.2.2. Node Management Flow
```
1. User selects a space from the list
2. Space tree structure loads and displays
3. User clicks "Add Node" button
4. Node creation form appears
5. User enters node title
6. API call to POST /spaces/{id}/nodes
7. Tree refreshes with new node
8. AI content generation triggers (backend)
9. User can click node to view generated content
```

#### 3.2.3. Content Viewing Flow
```
1. User clicks on a node in the tree
2. Loading state shows in content panel
3. API call to GET /spaces/{spaceId}/nodes/{nodeId}
4. Node content loads (including AI-generated content)
5. Content displays in formatted HTML
6. User can interact with content or navigate to other nodes
```

---

## 4. Core Components Deep Dive

### 4.1. Root Layout (`src/app/layout.js`)

**Purpose**: Provides the foundational HTML structure and global layout for all pages.

**Key Functionalities**:
- Imports global CSS styles
- Sets HTML metadata (title, description)
- Renders consistent header navigation
- Provides main content area for page-specific content

**Code Structure**:
```javascript
export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <header className="header">
          <nav className="nav">
            <h1 className="title">Mind Map Explorer</h1>
          </nav>
        </header>
        <main className="main">{children}</main>
      </body>
    </html>
  )
}
```

**State Management**: None (stateless layout component)

### 4.2. Home Page (`src/app/page.tsx`)

**Purpose**: Landing page that introduces the application and provides navigation entry points.

**Key Functionalities**:
- Feature showcase with visual cards
- Primary navigation buttons
- Application value proposition
- Responsive grid layout

**User Interactions**:
- Click "Browse Spaces" → Navigate to `/spaces`
- Click "Create New Space" → Navigate to `/spaces/new` (or trigger modal)

**State Management**: None (static content page)

### 4.3. Spaces List Page (`src/app/spaces/page.tsx`)

**Purpose**: Displays all available mind map spaces and enables space creation.

**Key Functionalities**:
- Fetches and displays spaces list
- Space creation modal/form
- Loading and error states
- Real-time space list updates

**State Variables**:
```typescript
const [spaces, setSpaces] = useState<Space[]>([])           // Spaces data
const [loading, setLoading] = useState(true)                // Loading state
const [error, setError] = useState<string | null>(null)     // Error messages
const [createModalOpen, setCreateModalOpen] = useState(false) // Modal state
const [newSpaceName, setNewSpaceName] = useState('')        // Form input
const [newSpaceDescription, setNewSpaceDescription] = useState('') // Form input
const [creating, setCreating] = useState(false)             // Creation state
```

**API Interactions**:
- `loadSpaces()` → GET `/spaces` (retrieves all spaces)
- `handleCreateSpace()` → POST `/spaces` (creates new space)

**User Interactions**:
- View spaces list
- Click space card → Navigate to `/spaces/{id}`
- Click "Create Space" → Open creation modal
- Fill form and submit → Create new space

### 4.4. Space Viewer (`src/app/spaces/[id]/page.tsx`)

**Purpose**: Displays individual space with tree visualization and node management.

**Key Functionalities**:
- Loads space with hierarchical node structure
- Interactive node tree visualization
- Node content display panel
- Node creation and management
- Real-time content loading

**State Variables**:
```typescript
const [spaceId, setSpaceId] = useState<string>('')                    // Route param
const [space, setSpace] = useState<Space | null>(null)               // Space data
const [selectedNode, setSelectedNode] = useState<TreeNode | null>(null) // Selected node
const [selectedNodeContent, setSelectedNodeContent] = useState<NodeWithContent | null>(null) // Node content
const [loading, setLoading] = useState(true)                         // Loading state
const [error, setError] = useState<string | null>(null)              // Error messages
const [loadingContent, setLoadingContent] = useState(false)          // Content loading
const [newNodeTitle, setNewNodeTitle] = useState('')                 // Form input
const [showAddNode, setShowAddNode] = useState(false)                // Form visibility
const [addingNode, setAddingNode] = useState(false)                  // Creation state
```

**API Interactions**:
- `loadSpace()` → GET `/spaces/{id}/tree` (loads space with nodes)
- `handleNodeClick()` → GET `/spaces/{spaceId}/nodes/{nodeId}` (loads node content)
- `handleAddNode()` → POST `/spaces/{spaceId}/nodes` (creates new node)

**User Interactions**:
- View hierarchical node tree
- Click node → Load and display content
- Click "Add Node" → Show creation form
- Submit node form → Create new node
- Navigate node hierarchy

### 4.5. API Client (`src/lib/api.ts`)

**Purpose**: Centralized API communication layer with type safety and error handling.

**Key Features**:
- TypeScript interfaces for all data types
- Environment-aware API base URL configuration
- Comprehensive error handling
- Support for all CRUD operations

**Configuration**:
```typescript
const API_BASE = process.env.NODE_ENV === 'production' 
  ? (process.env.NEXT_PUBLIC_MAIN_API_BASE || "https://ozqiu4g1m7.execute-api.us-east-1.amazonaws.com/Prod")
  : "/api/proxy";
```

**Core Interfaces**:
```typescript
interface Space {
  spaceId: string;
  name: string;
  description?: string;
  ownerId?: string;
  createdAt: string;
  updatedAt?: string;
  nodes?: TreeNode[];
}

interface Node {
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
```

**Main API Functions**:
- `api.getSpaces()` → List all spaces
- `api.createSpace(name, description)` → Create new space
- `api.getSpaceTree(spaceId)` → Get space with node tree
- `api.createNode(spaceId, title, parentNodeId)` → Create new node
- `api.getNode(spaceId, nodeId)` → Get node with content

### 4.6. Development Proxy (`src/app/api/proxy/[...path]/route.ts`)

**Purpose**: CORS bypass proxy for local development environment.

**Functionality**:
- Intercepts all `/api/proxy/*` requests
- Forwards requests to actual AWS API Gateway
- Adds CORS headers to responses
- Supports all HTTP methods (GET, POST, PUT, DELETE, OPTIONS)

**Request Flow**:
```
Frontend Request → /api/proxy/spaces → AWS API Gateway/spaces → Lambda Handler
Frontend Response ← CORS Headers Added ← API Gateway Response ← Lambda Response
```

---

## 5. API Integration & Data Management

### 5.1. API Architecture

**Base URL Configuration**:
- **Development**: `/api/proxy` (routes through Next.js proxy)
- **Production**: `https://ozqiu4g1m7.execute-api.us-east-1.amazonaws.com/Prod`

**Authentication**: Currently none implemented (future enhancement)

### 5.2. Data Types & Relationships

```
User (1) ──── Has Many ────► Space (N)
                                │
                                │ Contains
                                ▼
                            TreeNode (N)
                                │
                                │ Has Children
                                ▼
                            TreeNode (N) [Recursive]
```

### 5.3. API Endpoints Used

| Method | Endpoint | Purpose | Frontend Usage |
|--------|----------|---------|----------------|
| GET | `/spaces` | List all spaces | Spaces list page |
| POST | `/spaces` | Create new space | Space creation |
| GET | `/spaces/{id}/tree` | Get space with nodes | Space viewer |
| POST | `/spaces/{id}/nodes` | Create node | Node creation |
| GET | `/spaces/{spaceId}/nodes/{nodeId}` | Get node content | Content viewing |

### 5.4. Error Handling Strategy

**API Client Level**:
```typescript
try {
  const response = await fetch(url, options);
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
  }
  return await response.json();
} catch (error) {
  console.error('API Error:', error);
  throw error;
}
```

**Component Level**:
```typescript
try {
  const data = await api.getSpaces();
  setSpaces(data);
} catch (err) {
  setError(err instanceof Error ? err.message : 'Operation failed');
}
```

---

## 6. Error Handling & User Experience

### 6.1. Error Categories

**Network Errors**:
- Connection failures
- Timeout errors
- CORS issues (development)

**API Errors**:
- 4xx Client errors (bad requests, not found)
- 5xx Server errors (backend failures)
- Authentication errors (future)

**Application Errors**:
- Form validation errors
- State management errors
- Component lifecycle errors

### 6.2. User Feedback Mechanisms

**Loading States**:
```typescript
{loading && <div className="loading">Loading spaces...</div>}
```

**Error Messages**:
```typescript
{error && (
  <div className="alert alert-error">
    <strong>Error:</strong> {error}
  </div>
)}
```

**Success Feedback**:
- Immediate UI updates after successful operations
- Navigation to relevant pages after creation
- Visual confirmation of state changes

### 6.3. Graceful Degradation

**Empty States**:
- "No spaces found" when list is empty
- "Create your first space" call-to-action
- Helpful instructions for new users

**Partial Failures**:
- Display available data when some requests fail
- Allow retrying failed operations
- Maintain application functionality during partial outages

---

## 7. Development vs Production Configuration

### 7.1. Environment Differences

| Aspect | Development | Production |
|--------|-------------|------------|
| **Server** | localhost:3001 | AWS Amplify URL |
| **API Base** | `/api/proxy` | Direct AWS API Gateway |
| **CORS** | Next.js proxy handles | Backend must configure |
| **SSL** | HTTP (local) | HTTPS (required) |
| **Build** | Dev server | Static generation |

### 7.2. Configuration Management

**Environment Variables**:
```bash
# Development (.env.local)
NODE_ENV=development

# Production (Amplify Environment Variables)
NODE_ENV=production
NEXT_PUBLIC_MAIN_API_BASE=https://ozqiu4g1m7.execute-api.us-east-1.amazonaws.com/Prod
```

**API Base Resolution**:
```typescript
const API_BASE = process.env.NODE_ENV === 'production' 
  ? (process.env.NEXT_PUBLIC_MAIN_API_BASE || "https://ozqiu4g1m7.execute-api.us-east-1.amazonaws.com/Prod")
  : "/api/proxy";
```

### 7.3. Build Configuration

**Development**:
```bash
npm run dev  # Starts development server with hot reload
```

**Production**:
```bash
npm run build  # Creates optimized production build
npm start      # Serves production build locally (testing)
```

---

## 8. Logging & Monitoring Strategy

### 8.1. Client-Side Logging

**Development Logging**:
```typescript
console.log('🔍 Making request to:', targetUrl);
console.error('Error loading spaces:', err);
console.debug('State updated:', { spaces, selectedNode });
```

**Production Monitoring**:
- Browser error tracking (recommendation: Sentry)
- Performance monitoring (recommendation: AWS CloudWatch RUM)
- User interaction analytics

### 8.2. API Request Logging

**Request Tracking**:
```typescript
console.log('🔍 Making request to:', `${API_BASE}/${endpoint}`);
console.log('🔍 API_BASE:', API_BASE);
```

**Response Logging**:
```typescript
console.log('✅ API Response:', response.status);
console.error('❌ API Error:', error.message);
```

### 8.3. Error Correlation

**Frontend Error Context**:
- Current route/page
- User action that triggered error
- Application state at time of error
- API endpoint being called
- Browser/device information

---

## 9. Deployment Architecture

### 9.1. AWS Amplify Deployment

**Build Configuration**:
```yaml
version: 1
frontend:
  phases:
    preBuild:
      commands:
        - npm ci
    build:
      commands:
        - npm run build
  artifacts:
    baseDirectory: .next
    files:
      - '**/*'
  cache:
    paths:
      - node_modules/**/*
```

**Environment Setup**:
1. Connect Git repository to Amplify
2. Configure build settings
3. Set environment variables
4. Enable automatic deployments

### 9.2. Production Considerations

**Performance**:
- Next.js automatic code splitting
- Optimized image loading
- Static asset caching
- CDN distribution via Amplify

**Security**:
- HTTPS enforcement
- CORS configuration on backend
- Input validation and sanitization
- Environment variable protection

**Scalability**:
- CDN edge caching
- Automatic scaling via Amplify
- Backend API rate limiting
- Database connection pooling

---

## 10. Future Enhancements

### 10.1. Planned Features
- User authentication and authorization
- Real-time collaboration
- Advanced node visualization
- Export/import functionality
- Mobile app development

### 10.2. Technical Improvements
- Implement proper error boundaries
- Add comprehensive test suite
- Enhance accessibility (WCAG compliance)
- Implement Progressive Web App features
- Add offline capability

---

This documentation provides a comprehensive overview of the Mind Map Explorer frontend architecture, functionality, and operational considerations. It serves as both a technical reference and a guide for future development and maintenance activities.
