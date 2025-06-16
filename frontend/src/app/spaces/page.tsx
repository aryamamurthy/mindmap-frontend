'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { api, Space } from '../../lib/api';

export default function SpacesListPage() {
  const [spaces, setSpaces] = useState<Space[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [newSpaceName, setNewSpaceName] = useState('');
  const [newSpaceDescription, setNewSpaceDescription] = useState('');
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    loadSpaces();
  }, []);

  const loadSpaces = async () => {
    try {
      setLoading(true);
      setError(null);
      const spacesData = await api.getSpaces();
      setSpaces(spacesData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load spaces');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateSpace = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newSpaceName.trim()) return;
    try {
      setCreating(true);
      setError(null);
      const newSpace = await api.createSpace(newSpaceName.trim(), newSpaceDescription.trim() || undefined);
      setSpaces([...spaces, newSpace]);
      setNewSpaceName('');
      setNewSpaceDescription('');
      setCreateModalOpen(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create space');
    } finally {
      setCreating(false);
    }
  };

  if (loading) {
    return (
      <div style={{ background: '#f3f4f6', minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: 'Inter, Arial, sans-serif' }}>
        <div style={{ textAlign: 'center' }}>
          <h1 style={{ fontSize: '2rem', fontWeight: 700, marginBottom: 16, color: '#1a202c' }}>Mind Map Explorer</h1>
          <div style={{ color: '#6b7280' }}>Loading spaces...</div>
        </div>
      </div>
    );
  }

  return (
    <div style={{ background: '#f3f4f6', fontFamily: 'Inter, Arial, sans-serif' }}>
      <div style={{ width: '100%', background: 'white', boxShadow: '0 2px 8px #0001', padding: '1.5rem 0', marginBottom: 32 }}>
        <div style={{ maxWidth: 900, margin: '0 auto', padding: '0 1rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div>
            <Link href="/" style={{ fontSize: '2rem', fontWeight: 700, color: '#1a202c', textDecoration: 'none' }}>
              Mind Map Explorer
            </Link>
            <p style={{ color: '#6b7280', fontSize: 14, marginTop: 4 }}>Organize your thoughts with interactive mind maps</p>
          </div>
          <button 
            onClick={() => setCreateModalOpen(true)}
            style={{ background: '#2563eb', color: 'white', padding: '10px 24px', borderRadius: 8, fontWeight: 600, fontSize: 16, boxShadow: '0 2px 8px #0001', border: 'none', cursor: 'pointer' }}
          >
            Create New Space
          </button>
        </div>
      </div>
      <div style={{ maxWidth: 900, margin: '0 auto', padding: '0 1rem' }}>
        {error && (
          <div style={{ background: '#fee2e2', color: '#b91c1c', padding: '12px 20px', borderRadius: 8, marginBottom: 24, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <span>{error}</span>
            <button 
              onClick={loadSpaces} 
              style={{ marginLeft: 16, background: '#fecaca', color: '#991b1b', padding: '6px 18px', borderRadius: 6, border: 'none', cursor: 'pointer', fontWeight: 600 }}
            >
              Retry
            </button>
          </div>
        )}
        {spaces.length === 0 && !error ? (
          <div style={{ background: 'white', borderRadius: 12, boxShadow: '0 2px 8px #0001', padding: 40, textAlign: 'center' }}>
            <h2 style={{ fontSize: '1.3rem', fontWeight: 600, marginBottom: 8, color: '#1a202c' }}>No Spaces Found</h2>
            <p style={{ color: '#6b7280', marginBottom: 24 }}>Create your first space to start organizing your thoughts.</p>
            <button 
              onClick={() => setCreateModalOpen(true)}
              style={{ background: '#2563eb', color: 'white', padding: '10px 24px', borderRadius: 8, fontWeight: 600, fontSize: 16, boxShadow: '0 2px 8px #0001', border: 'none', cursor: 'pointer' }}
            >
              Create Your First Space
            </button>
          </div>
        ) : (
          <div>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 24 }}>
              <h2 style={{ fontSize: '1.1rem', fontWeight: 600, color: '#1a202c' }}>Your Spaces ({spaces.length})</h2>
              <button 
                onClick={loadSpaces}
                style={{ background: '#e5e7eb', color: '#1f2937', padding: '6px 18px', borderRadius: 6, border: 'none', cursor: 'pointer', fontWeight: 600 }}
                disabled={loading}
              >
                Refresh
              </button>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 24, width: '100%' }}>
              {spaces.map((space) => (
                <div key={space.spaceId} style={{ background: 'white', borderRadius: 12, boxShadow: '0 2px 8px #0001', padding: 28, display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                  <div>
                    <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: 8, color: '#2563eb' }}>
                      <Link 
                        href={`/spaces/${space.spaceId}`}
                        style={{ textDecoration: 'none', color: '#2563eb' }}
                      >
                        {space.name}
                      </Link>
                    </h3>
                    {space.description && (
                      <p style={{ color: '#6b7280', marginBottom: 12 }}>{space.description}</p>
                    )}
                    <div style={{ fontSize: 13, color: '#9ca3af', marginBottom: 12 }}>
                      <div>Created: {new Date(space.createdAt).toLocaleDateString()}</div>
                      {space.updatedAt && (
                        <div>Updated: {new Date(space.updatedAt).toLocaleDateString()}</div>
                      )}
                      {space.nodes && (
                        <div>Nodes: {space.nodes.length}</div>
                      )}
                    </div>
                  </div>
                  <Link 
                    href={`/spaces/${space.spaceId}`}
                    style={{ marginTop: 16, background: '#2563eb', color: 'white', padding: '10px 24px', borderRadius: 8, fontWeight: 600, fontSize: 16, boxShadow: '0 2px 8px #0001', textAlign: 'center', textDecoration: 'none', display: 'inline-block' }}
                  >
                    Explore Space
                  </Link>
                </div>
              ))}
            </div>
          </div>
        )}
        {/* Create Space Modal */}
        {createModalOpen && (
          <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
            <div style={{ background: 'white', padding: 40, borderRadius: 12, width: '100%', maxWidth: 480, boxShadow: '0 4px 24px #0002' }}>
              <h2 style={{ fontSize: '1.3rem', fontWeight: 700, marginBottom: 24, color: '#1a202c' }}>Create New Space</h2>
              <form onSubmit={handleCreateSpace}>
                <div style={{ marginBottom: 16 }}>
                  <label style={{ display: 'block', marginBottom: 8, fontWeight: 600, color: '#374151' }}>Space Name *</label>
                  <input
                    type="text"
                    value={newSpaceName}
                    onChange={(e) => setNewSpaceName(e.target.value)}
                    placeholder="Enter space name..."
                    required
                    disabled={creating}
                    style={{ width: '100%', border: '1px solid #d1d5db', borderRadius: 6, padding: '10px 12px', fontSize: 16, outline: 'none', marginBottom: 0 }}
                  />
                </div>
                <div style={{ marginBottom: 24 }}>
                  <label style={{ display: 'block', marginBottom: 8, fontWeight: 600, color: '#374151' }}>Description (Optional)</label>
                  <textarea
                    value={newSpaceDescription}
                    onChange={(e) => setNewSpaceDescription(e.target.value)}
                    placeholder="Enter space description..."
                    rows={3}
                    disabled={creating}
                    style={{ width: '100%', border: '1px solid #d1d5db', borderRadius: 6, padding: '10px 12px', fontSize: 16, outline: 'none' }}
                  />
                </div>
                <div style={{ display: 'flex', gap: 12, justifyContent: 'flex-end' }}>
                  <button
                    type="button"
                    onClick={() => {
                      setCreateModalOpen(false);
                      setNewSpaceName('');
                      setNewSpaceDescription('');
                      setError(null);
                    }}
                    style={{ background: '#e5e7eb', color: '#1f2937', padding: '10px 24px', borderRadius: 8, fontWeight: 600, fontSize: 16, border: 'none', cursor: 'pointer' }}
                    disabled={creating}
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    style={{ background: '#2563eb', color: 'white', padding: '10px 24px', borderRadius: 8, fontWeight: 600, fontSize: 16, border: 'none', cursor: 'pointer' }}
                    disabled={creating || !newSpaceName.trim()}
                  >
                    {creating ? 'Creating...' : 'Create Space'}
                  </button>
                </div>
              </form>
              {error && (
                <div style={{ background: '#fee2e2', color: '#b91c1c', padding: '10px 16px', borderRadius: 6, marginTop: 16 }}>{error}</div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
