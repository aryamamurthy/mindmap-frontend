'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { api, Space, TreeNode, NodeWithContent } from '../../../lib/api';

interface SpaceViewerProps {
  params: Promise<{ id: string }>;
}

export default function SpaceViewer({ params }: SpaceViewerProps) {
  const [spaceId, setSpaceId] = useState<string>('');
  const [space, setSpace] = useState<Space | null>(null);
  const [selectedNode, setSelectedNode] = useState<TreeNode | null>(null);
  const [selectedNodeContent, setSelectedNodeContent] = useState<NodeWithContent | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [loadingContent, setLoadingContent] = useState(false);
  const [newNodeTitle, setNewNodeTitle] = useState('');
  const [showAddNode, setShowAddNode] = useState(false);
  const [addingNode, setAddingNode] = useState(false);

  // Handle async params
  useEffect(() => {
    const resolveParams = async () => {
      const resolvedParams = await params;
      setSpaceId(resolvedParams.id);
    };
    resolveParams();
  }, [params]);

  useEffect(() => {
    if (spaceId) {
      loadSpace();
    }
  }, [spaceId]);

  const loadSpace = async () => {
    if (!spaceId) return;
    
    try {
      setLoading(true);
      setError(null);
      const spaceData = await api.getSpaceTree(spaceId);
      setSpace(spaceData);
    } catch (err) {
      console.error('Error loading space:', err);
      setError(err instanceof Error ? err.message : 'Failed to load space');
    } finally {
      setLoading(false);
    }
  };

  const handleNodeClick = async (node: TreeNode) => {
    setSelectedNode(node);
    setLoadingContent(true);
    setSelectedNodeContent(null);
    
    try {
      const nodeWithContent = await api.getNode(spaceId, node.nodeId);
      setSelectedNodeContent(nodeWithContent);
    } catch (err) {
      console.error('Error loading node content:', err);
      setError(err instanceof Error ? err.message : 'Failed to load node content');
    } finally {
      setLoadingContent(false);
    }
  };

  const handleAddNode = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newNodeTitle.trim()) return;

    try {
      setAddingNode(true);
      setError(null);
      const parentNodeId = selectedNode?.nodeId;
      const newNode = await api.createNode(spaceId, newNodeTitle.trim(), parentNodeId);
      
      // Reload the space to get updated tree structure
      await loadSpace();
      
      // Select the new node
      const newTreeNode: TreeNode = {
        ...newNode,
        children: []
      };
      setSelectedNode(newTreeNode);
      setSelectedNodeContent(newNode);
      
      setNewNodeTitle('');
      setShowAddNode(false);
    } catch (err) {
      console.error('Error creating node:', err);
      setError(err instanceof Error ? err.message : 'Failed to create node');
    } finally {
      setAddingNode(false);
    }
  };

  const renderNode = (node: TreeNode, depth: number = 0) => {
    const isSelected = selectedNode?.nodeId === node.nodeId;
    
    return (
      <div key={node.nodeId} style={{ marginLeft: `${depth * 20}px` }}>
        <div
          className={`node-item ${isSelected ? 'selected' : ''}`}
          onClick={() => handleNodeClick(node)}
        >
          <div style={{ fontWeight: isSelected ? 'bold' : 'normal' }}>
            {node.title}
          </div>
          <div style={{ fontSize: '0.8em', color: '#666', marginTop: '5px' }}>
            Created: {new Date(node.createdAt).toLocaleDateString()}
            {node.updatedAt && ` • Updated: ${new Date(node.updatedAt).toLocaleDateString()}`}
          </div>
        </div>
        {node.children && node.children.map(child => renderNode(child, depth + 1))}
      </div>
    );
  };

  if (loading) {
    return (
      <div className="min-h-screen">
        <div className="header">
          <div className="container">
            <h1>Loading Space...</h1>
          </div>
        </div>
        <div className="container">
          <div className="loading">Loading space data...</div>
        </div>
      </div>
    );
  }

  if (error && !space) {
    return (
      <div className="min-h-screen">
        <div className="header">
          <div className="container">
            <h1>Error</h1>
          </div>
        </div>
        <div className="container">
          <div className="error">
            {error}
            <div style={{ marginTop: '10px' }}>
              <button onClick={loadSpace} className="btn btn-secondary">
                Retry
              </button>
              <Link href="/spaces" className="btn btn-primary" style={{ marginLeft: '10px', textDecoration: 'none' }}>
                Back to Spaces
              </Link>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!space) {
    return (
      <div className="min-h-screen">
        <div className="header">
          <div className="container">
            <h1>Space Not Found</h1>
          </div>
        </div>
        <div className="container">
          <div className="error">
            Space not found or you don't have access to it.
            <div style={{ marginTop: '10px' }}>
              <Link href="/spaces" className="btn btn-primary" style={{ textDecoration: 'none' }}>
                Back to Spaces
              </Link>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen">
      <div className="header">
        <div className="container">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <Link href="/spaces" style={{ textDecoration: 'none', color: '#007bff', fontSize: '0.9em' }}>
                ← Back to Spaces
              </Link>
              <h1 style={{ margin: '5px 0' }}>{space.name}</h1>
              {space.description && (
                <p style={{ color: '#666', margin: 0 }}>{space.description}</p>
              )}
            </div>
            <div>
              <button 
                onClick={() => setShowAddNode(true)}
                className="btn btn-primary"
                disabled={addingNode}
              >
                Add Node
              </button>
              <button 
                onClick={loadSpace}
                className="btn btn-secondary"
                style={{ marginLeft: '10px' }}
                disabled={loading}
              >
                Refresh
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="container">
        {error && (
          <div className="error">
            {error}
            <button 
              onClick={() => setError(null)} 
              style={{ marginLeft: '10px', background: 'none', border: 'none', color: '#721c24', cursor: 'pointer' }}
            >
              ×
            </button>
          </div>
        )}

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginTop: '20px' }}>
          {/* Tree Structure */}
          <div className="card">
            <h2>Mind Map Structure</h2>
            {!space.nodes || space.nodes.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '40px', color: '#666' }}>
                <div style={{ fontSize: '3em', marginBottom: '15px' }}>🌳</div>
                <h3>No nodes yet</h3>
                <p>Start building your mind map by adding the first node.</p>
                <button 
                  onClick={() => setShowAddNode(true)}
                  className="btn btn-primary"
                  style={{ marginTop: '15px' }}
                >
                  Add First Node
                </button>
              </div>
            ) : (
              <div className="tree-view">
                {space.nodes.map(node => renderNode(node))}
              </div>
            )}
          </div>

          {/* Node Content */}
          <div className="card">
            <h2>Node Details</h2>
            {!selectedNode ? (
              <div style={{ textAlign: 'center', padding: '40px', color: '#666' }}>
                <div style={{ fontSize: '3em', marginBottom: '15px' }}>📝</div>
                <h3>Select a node</h3>
                <p>Click on a node in the tree to view its details and content.</p>
              </div>
            ) : (
              <div>
                <h3>{selectedNode.title}</h3>
                <div style={{ fontSize: '0.9em', color: '#666', marginBottom: '20px' }}>
                  <div>Node ID: {selectedNode.nodeId}</div>
                  <div>Created: {new Date(selectedNode.createdAt).toLocaleDateString()}</div>
                  {selectedNode.updatedAt && (
                    <div>Updated: {new Date(selectedNode.updatedAt).toLocaleDateString()}</div>
                  )}
                  {selectedNode.parentNodeId && (
                    <div>Parent: {selectedNode.parentNodeId}</div>
                  )}
                </div>

                {loadingContent ? (
                  <div className="loading">Loading content...</div>
                ) : selectedNodeContent ? (
                  <div>
                    {selectedNodeContent.contentHTML ? (
                      <div className="node-content">
                        <h4>Generated Content:</h4>
                        <div 
                          dangerouslySetInnerHTML={{ __html: selectedNodeContent.contentHTML }}
                          style={{ marginTop: '10px' }}
                        />
                      </div>
                    ) : selectedNodeContent.content ? (
                      <div className="node-content">
                        <h4>Content:</h4>
                        <div style={{ marginTop: '10px', whiteSpace: 'pre-wrap' }}>
                          {selectedNodeContent.content}
                        </div>
                      </div>
                    ) : (
                      <div style={{ color: '#666', fontStyle: 'italic' }}>
                        No content available for this node.
                      </div>
                    )}

                    <div style={{ marginTop: '20px' }}>
                      <button 
                        onClick={() => setShowAddNode(true)}
                        className="btn btn-primary"
                      >
                        Add Child Node
                      </button>
                    </div>
                  </div>
                ) : (
                  <div className="error">
                    Failed to load node content.
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Add Node Modal */}
        {showAddNode && (
          <div style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0,0,0,0.5)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000
          }}>
            <div style={{
              backgroundColor: 'white',
              padding: '30px',
              borderRadius: '8px',
              width: '90%',
              maxWidth: '500px',
              boxShadow: '0 4px 12px rgba(0,0,0,0.15)'
            }}>
              <h2 style={{ marginBottom: '20px' }}>
                Add New Node
                {selectedNode && (
                  <div style={{ fontSize: '0.9em', color: '#666', fontWeight: 'normal' }}>
                    Parent: {selectedNode.title}
                  </div>
                )}
              </h2>
              <form onSubmit={handleAddNode}>
                <div style={{ marginBottom: '20px' }}>
                  <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
                    Node Title *
                  </label>
                  <input
                    type="text"
                    value={newNodeTitle}
                    onChange={(e) => setNewNodeTitle(e.target.value)}
                    placeholder="Enter node title..."
                    required
                    disabled={addingNode}
                    autoFocus
                  />
                </div>
                <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
                  <button
                    type="button"
                    onClick={() => {
                      setShowAddNode(false);
                      setNewNodeTitle('');
                      setError(null);
                    }}
                    className="btn btn-secondary"
                    disabled={addingNode}
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="btn btn-primary"
                    disabled={addingNode || !newNodeTitle.trim()}
                  >
                    {addingNode ? 'Creating...' : 'Create Node'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Space Info */}
        <div className="card" style={{ marginTop: '20px' }}>
          <h3>Space Information</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px', marginTop: '15px' }}>
            <div>
              <strong>Space ID:</strong><br />
              <span style={{ color: '#666', fontSize: '0.9em' }}>{space.spaceId}</span>
            </div>
            <div>
              <strong>Created:</strong><br />
              <span style={{ color: '#666', fontSize: '0.9em' }}>
                {new Date(space.createdAt).toLocaleDateString()}
              </span>
            </div>
            {space.updatedAt && (
              <div>
                <strong>Last Updated:</strong><br />
                <span style={{ color: '#666', fontSize: '0.9em' }}>
                  {new Date(space.updatedAt).toLocaleDateString()}
                </span>
              </div>
            )}
            <div>
              <strong>Total Nodes:</strong><br />
              <span style={{ color: '#666', fontSize: '0.9em' }}>
                {space.nodes ? space.nodes.length : 0}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
