'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { api, Space, TreeNode, NodeWithContent } from '../../../lib/api';

// Collapsible state for each node
function TreeNodeComponent({ node, selectedNodeId, onSelect, onAdd, onEdit, onDelete, level = 0, collapsedNodes, setCollapsedNodes }) {
  const isCollapsed = collapsedNodes[node.nodeId];
  const hasChildren = node.children && node.children.length > 0;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', position: 'relative', width: '100%' }}>
      <div style={{ display: 'flex', alignItems: 'center', position: 'relative' }}>
        {hasChildren && (
          <button
            onClick={e => { e.stopPropagation(); setCollapsedNodes((prev) => ({ ...prev, [node.nodeId]: !isCollapsed })); }}
            style={{ marginRight: 8, background: '#e0e7ef', color: '#2563eb', border: 'none', borderRadius: 4, padding: '2px 8px', cursor: 'pointer', fontWeight: 600 }}
            title={isCollapsed ? 'Expand' : 'Collapse'}
          >
            {isCollapsed ? '+' : '–'}
          </button>
        )}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            minWidth: 180,
            background: selectedNodeId === node.nodeId ? '#e0e7ef' : level === 0 ? '#2563eb' : '#fff',
            color: selectedNodeId === node.nodeId ? '#2563eb' : level === 0 ? '#fff' : '#1a202c',
            border: selectedNodeId === node.nodeId ? '2px solid #2563eb' : '1px solid #d1d5db',
            borderRadius: 8,
            padding: '10px 20px',
            fontWeight: selectedNodeId === node.nodeId ? 700 : 500,
            boxShadow: selectedNodeId === node.nodeId ? '0 2px 8px #2563eb22' : '0 1px 4px #0001',
            cursor: 'pointer',
            transition: 'background 0.2s, color 0.2s',
            marginBottom: 8,
            marginTop: level === 0 ? 0 : 16,
            position: 'relative',
            zIndex: 2,
          }}
          onClick={() => onSelect(node)}
        >
          <span style={{ flex: 1 }}>{node.title}</span>
          <button
            style={{ marginLeft: 8, background: '#e0e7ef', color: '#2563eb', border: 'none', borderRadius: 4, padding: '2px 8px', cursor: 'pointer', fontWeight: 600 }}
            onClick={e => { e.stopPropagation(); onAdd(node); }}
            title="Add Child"
          >+
          </button>
          <button
            style={{ marginLeft: 4, background: '#fef9c3', color: '#b45309', border: 'none', borderRadius: 4, padding: '2px 8px', cursor: 'pointer', fontWeight: 600 }}
            onClick={e => { e.stopPropagation(); onEdit(node); }}
            title="Edit Node"
          >✎
          </button>
          <button
            style={{ marginLeft: 4, background: '#fee2e2', color: '#b91c1c', border: 'none', borderRadius: 4, padding: '2px 8px', cursor: 'pointer', fontWeight: 600 }}
            onClick={e => { e.stopPropagation(); onDelete(node); }}
            title="Delete Node"
          >🗑
          </button>
        </div>
      </div>
      {/* Draw vertical line from parent to this node */}
      {level > 0 && (
        <div style={{
          position: 'absolute',
          top: -24,
          left: '50%',
          width: 2,
          height: 24,
          background: '#d1d5db',
          transform: 'translateX(-50%)',
          zIndex: 1,
        }} />
      )}
      {/* Draw horizontal lines to children */}
      {hasChildren && !isCollapsed && (
        <div style={{
          display: 'flex',
          flexDirection: 'row',
          justifyContent: 'center',
          alignItems: 'flex-start',
          width: '100%',
          gap: 24,
          marginTop: 8,
          flexWrap: 'wrap',
          position: 'relative',
        }}>
          {/* Horizontal line connecting all children */}
          <div style={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            height: 2,
            background: '#d1d5db',
            zIndex: 0,
            width: '100%',
            marginTop: 24,
          }} />
          {node.children.map((child, idx) => (
            <div key={child.nodeId} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', position: 'relative' }}>
              {/* Draw vertical line from horizontal to child */}
              <div style={{
                width: 2,
                height: 24,
                background: '#d1d5db',
                position: 'absolute',
                top: 0,
                left: '50%',
                transform: 'translateX(-50%)',
                zIndex: 1,
              }} />
              <TreeNodeComponent
                node={child}
                selectedNodeId={selectedNodeId}
                onSelect={onSelect}
                onAdd={onAdd}
                onEdit={onEdit}
                onDelete={onDelete}
                level={level + 1}
                collapsedNodes={collapsedNodes}
                setCollapsedNodes={setCollapsedNodes}
              />
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function Modal({ open, onClose, children }) {
  if (!open) return null;
  return (
    <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.4)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
      <div style={{ background: 'white', borderRadius: 12, padding: 32, minWidth: 320, boxShadow: '0 4px 24px #0002', position: 'relative' }}>
        <button onClick={onClose} style={{ position: 'absolute', top: 12, right: 16, background: 'none', border: 'none', fontSize: 20, color: '#6b7280', cursor: 'pointer' }}>×</button>
        {children}
      </div>
    </div>
  );
}

export default function SpaceViewer({ params }) {
  const [space, setSpace] = useState<Space | null>(null);
  const [selectedNode, setSelectedNode] = useState<TreeNode | null>(null);
  const [selectedNodeContent, setSelectedNodeContent] = useState<NodeWithContent | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [modal, setModal] = useState({ type: null, node: null });
  const [inputValue, setInputValue] = useState('');
  const [contentValue, setContentValue] = useState('');
  const [collapsedNodes, setCollapsedNodes] = useState({});
  const [showContentModal, setShowContentModal] = useState(false);

  // Handle async params
  useEffect(() => {
    const resolveParams = async () => {
      const resolvedParams = await params;
      loadSpace(resolvedParams.id);
    };
    resolveParams();
  }, [params]);

  const loadSpace = async (spaceId: string) => {
    setLoading(true);
    setError(null);
    try {
      const spaceData = await api.getSpaceTree(spaceId);
      setSpace(spaceData);
    } catch (err) {
      setError('Failed to load space');
    } finally {
      setLoading(false);
    }
  };

  const handleSelectNode = async (node: TreeNode) => {
    setSelectedNode(node);
    setSelectedNodeContent(null);
    setShowContentModal(true);
    try {
      const nodeWithContent = await api.getNode(space?.spaceId, node.nodeId);
      setSelectedNodeContent(nodeWithContent);
    } catch {
      setSelectedNodeContent(null);
    }
  };

  const handleAddNode = (parentNode) => {
    setModal({ type: 'add', node: parentNode });
    setInputValue('');
    setContentValue('');
  };
  const handleEditNode = async (node) => {
    setModal({ type: 'edit', node });
    setInputValue(node.title);
    // fetch content for editing
    try {
      const nodeWithContent = await api.getNode(space.spaceId, node.nodeId);
      setContentValue(nodeWithContent.content || '');
    } catch {
      setContentValue('');
    }
  };
  const handleDeleteNode = (node) => {
    setModal({ type: 'delete', node });
  };
  const handleModalClose = () => {
    setModal({ type: null, node: null });
    setInputValue('');
    setContentValue('');
  };

  const submitAddNode = async (e) => {
    e.preventDefault();
    if (!inputValue.trim()) return;
    try {
      await api.createNode(space.spaceId, inputValue.trim(), modal.node ? modal.node.nodeId : undefined);
      handleModalClose();
      window.location.reload(); // Reload after add
    } catch {}
  };
  const submitEditNode = async (e) => {
    e.preventDefault();
    if (!inputValue.trim()) return;
    try {
      await api.updateNode(space.spaceId, modal.node.nodeId, inputValue.trim(), contentValue);
      handleModalClose();
      window.location.reload(); // Reload after edit
    } catch {}
  };
  const submitDeleteNode = async (e) => {
    e.preventDefault();
    try {
      await api.deleteNode(space.spaceId, modal.node.nodeId);
      handleModalClose();
      window.location.reload(); // Reload after delete
    } catch {}
  };

  if (loading) {
    return (
      <div style={{ minHeight: '100vh', background: '#e5e7eb', display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: 'Inter, Arial, sans-serif' }}>
        <div style={{ textAlign: 'center', color: '#2563eb' }}>Loading Space...</div>
      </div>
    );
  }

  if (error || !space) {
    return (
      <div style={{ minHeight: '100vh', background: '#e5e7eb', display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: 'Inter, Arial, sans-serif' }}>
        <div style={{ textAlign: 'center', color: '#b91c1c', background: 'white', padding: 32, borderRadius: 12, boxShadow: '0 2px 8px #0001' }}>{error || 'Space not found.'}</div>
      </div>
    );
  }

  // Responsive container for the whole page
  return (
    <div style={{ background: '#e5e7eb', fontFamily: 'Inter, Arial, sans-serif', minHeight: '100vh', width: '100vw', margin: 0, padding: 0 }}>
      <div style={{ width: '100%', maxWidth: '100vw', margin: 0, display: 'flex', justifyContent: 'center', alignItems: 'flex-start', padding: 0 }}>
        {/* Mind Map Tree - now much larger and fills the page */}
        <div style={{ flex: 1, background: '#f3f4f6', borderRadius: 16, boxShadow: '0 2px 12px #0001', padding: 48, minHeight: '90vh', minWidth: 0, width: '100%', maxWidth: 1600, overflow: 'auto', margin: 0 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
            <h2 style={{ fontSize: '1.6rem', fontWeight: 700, color: '#2563eb', textAlign: 'center' }}>{space.name}</h2>
            <button
              style={{ background: '#2563eb', color: 'white', padding: '12px 28px', borderRadius: 8, fontWeight: 600, fontSize: 18, border: 'none', cursor: 'pointer', marginLeft: 16 }}
              onClick={() => handleAddNode(null)}
            >
              + Add Root Node
            </button>
          </div>
          {space.nodes && space.nodes.length > 0 ? (
            <div style={{ marginTop: 16 }}>
              {space.nodes.map(node => (
                <TreeNodeComponent
                  key={node.nodeId}
                  node={node}
                  selectedNodeId={selectedNode?.nodeId}
                  onSelect={handleSelectNode}
                  onAdd={handleAddNode}
                  onEdit={handleEditNode}
                  onDelete={handleDeleteNode}
                  collapsedNodes={collapsedNodes}
                  setCollapsedNodes={setCollapsedNodes}
                />
              ))}
            </div>
          ) : (
            <div style={{ color: '#6b7280', textAlign: 'center', marginTop: 48 }}>No nodes yet. Add your first node!</div>
          )}
        </div>
      </div>
      {/* Add/Edit/Delete Modals */}
      <Modal open={modal.type === 'add'} onClose={handleModalClose}>
        <h3 style={{ fontWeight: 700, fontSize: 18, marginBottom: 16, color: '#2563eb' }}>Add Node</h3>
        <form onSubmit={submitAddNode}>
          <input
            type="text"
            value={inputValue}
            onChange={e => setInputValue(e.target.value)}
            placeholder="Node title"
            style={{ width: '100%', border: '1px solid #d1d5db', borderRadius: 6, padding: '10px 12px', fontSize: 16, outline: 'none', marginBottom: 16 }}
            required
          />
          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 12 }}>
            <button type="button" onClick={handleModalClose} style={{ background: '#e5e7eb', color: '#1f2937', padding: '8px 20px', borderRadius: 8, fontWeight: 600, fontSize: 16, border: 'none', cursor: 'pointer' }}>Cancel</button>
            <button type="submit" style={{ background: '#2563eb', color: 'white', padding: '8px 20px', borderRadius: 8, fontWeight: 600, fontSize: 16, border: 'none', cursor: 'pointer' }}>Add</button>
          </div>
        </form>
      </Modal>
      <Modal open={modal.type === 'edit'} onClose={handleModalClose}>
        <h3 style={{ fontWeight: 700, fontSize: 18, marginBottom: 16, color: '#b45309' }}>Edit Node</h3>
        <form onSubmit={submitEditNode}>
          <input
            type="text"
            value={inputValue}
            onChange={e => setInputValue(e.target.value)}
            placeholder="Node title"
            style={{ width: '100%', border: '1px solid #d1d5db', borderRadius: 6, padding: '10px 12px', fontSize: 16, outline: 'none', marginBottom: 16 }}
            required
          />
          <textarea
            value={contentValue}
            onChange={e => setContentValue(e.target.value)}
            placeholder="Node content (optional)"
            rows={5}
            style={{ width: '100%', border: '1px solid #d1d5db', borderRadius: 6, padding: '10px 12px', fontSize: 16, outline: 'none', marginBottom: 16, resize: 'vertical' }}
          />
          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 12 }}>
            <button type="button" onClick={handleModalClose} style={{ background: '#e5e7eb', color: '#1f2937', padding: '8px 20px', borderRadius: 8, fontWeight: 600, fontSize: 16, border: 'none', cursor: 'pointer' }}>Cancel</button>
            <button type="submit" style={{ background: '#b45309', color: 'white', padding: '8px 20px', borderRadius: 8, fontWeight: 600, fontSize: 16, border: 'none', cursor: 'pointer' }}>Save</button>
          </div>
        </form>
      </Modal>
      <Modal open={modal.type === 'delete'} onClose={handleModalClose}>
        <h3 style={{ fontWeight: 700, fontSize: 18, marginBottom: 16, color: '#b91c1c' }}>Delete Node</h3>
        <p style={{ color: '#b91c1c', marginBottom: 24 }}>Are you sure you want to delete this node? This action cannot be undone.</p>
        <form onSubmit={submitDeleteNode}>
          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 12 }}>
            <button type="button" onClick={handleModalClose} style={{ background: '#e5e7eb', color: '#1f2937', padding: '8px 20px', borderRadius: 8, fontWeight: 600, fontSize: 16, border: 'none', cursor: 'pointer' }}>Cancel</button>
            <button type="submit" style={{ background: '#b91c1c', color: 'white', padding: '8px 20px', borderRadius: 8, fontWeight: 600, fontSize: 16, border: 'none', cursor: 'pointer' }}>Delete</button>
          </div>
        </form>
      </Modal>
      {/* Node Content Modal - responsive */}
      <Modal open={showContentModal && selectedNode && selectedNodeContent} onClose={() => setShowContentModal(false)}>
        <h3 style={{ fontWeight: 700, fontSize: 18, marginBottom: 16, color: '#2563eb', wordBreak: 'break-word' }}>{selectedNode?.title}</h3>
        <div style={{ color: '#6b7280', fontSize: 14, marginBottom: 8, wordBreak: 'break-all' }}>Node ID: {selectedNode?.nodeId}</div>
        {selectedNodeContent && (
          <div style={{
            marginTop: 16,
            background: '#f3f4f6',
            borderRadius: 8,
            padding: 16,
            color: '#1a202c',
            fontSize: 15,
            boxShadow: '0 1px 4px #0001',
            maxWidth: '70vw',
            maxHeight: '50vh',
            overflowY: 'auto',
            wordBreak: 'break-word',
          }}>
            {selectedNodeContent.contentHTML ? (
              <div dangerouslySetInnerHTML={{ __html: selectedNodeContent.contentHTML }} />
            ) : selectedNodeContent.content ? (
              <pre style={{ whiteSpace: 'pre-wrap', fontFamily: 'inherit', margin: 0 }}>{selectedNodeContent.content}</pre>
            ) : (
              <span style={{ color: '#b91c1c' }}>No content available for this node.</span>
            )}
          </div>
        )}
      </Modal>
    </div>
  );
}

// Helper function to count all nodes recursively (remains the same)
const countTotalNodes = (nodes: TreeNode[]): number => {
  let count = nodes.length;
  for (const node of nodes) {
    if (node.children) {
      count += countTotalNodes(node.children);
    }
  }
  return count;
};
