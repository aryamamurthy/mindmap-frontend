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
      console.error('Error loading spaces:', err);
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
      console.error('Error creating space:', err);
      setError(err instanceof Error ? err.message : 'Failed to create space');
    } finally {
      setCreating(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen">
        <div className="header">
          <div className="container">
            <h1>Mind Map Explorer</h1>
          </div>
        </div>
        <div className="container">
          <div className="loading">Loading spaces...</div>
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
              <Link href="/" style={{ textDecoration: 'none', color: '#333' }}>
                <h1>Mind Map Explorer</h1>
              </Link>
              <p style={{ color: '#666', margin: 0 }}>Organize your thoughts with interactive mind maps</p>
            </div>
            <button 
              onClick={() => setCreateModalOpen(true)}
              className="btn btn-primary"
            >
              Create New Space
            </button>
          </div>
        </div>
      </div>

      <div className="container">
        {error && (
          <div className="error">
            {error}
            <button 
              onClick={loadSpaces} 
              className="btn btn-secondary"
              style={{ marginLeft: '10px' }}
            >
              Retry
            </button>
          </div>
        )}

        {spaces.length === 0 && !error ? (
          <div className="card text-center">
            <h2>No Spaces Found</h2>
            <p style={{ color: '#666', marginBottom: '20px' }}>
              Create your first space to start organizing your thoughts.
            </p>
            <button 
              onClick={() => setCreateModalOpen(true)}
              className="btn btn-primary"
            >
              Create Your First Space
            </button>
          </div>
        ) : (
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
              <h2>Your Spaces ({spaces.length})</h2>
              <button 
                onClick={loadSpaces}
                className="btn btn-secondary"
                disabled={loading}
              >
                Refresh
              </button>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '20px' }}>
              {spaces.map((space) => (
                <div key={space.spaceId} className="card">
                  <h3 style={{ marginBottom: '10px' }}>
                    <Link 
                      href={`/spaces/${space.spaceId}`}
                      style={{ textDecoration: 'none', color: '#007bff' }}
                    >
                      {space.name}
                    </Link>
                  </h3>
                  {space.description && (
                    <p style={{ color: '#666', marginBottom: '15px' }}>
                      {space.description}
                    </p>
                  )}
                  <div style={{ fontSize: '0.9em', color: '#999', marginBottom: '15px' }}>
                    <div>Created: {new Date(space.createdAt).toLocaleDateString()}</div>
                    {space.updatedAt && (
                      <div>Updated: {new Date(space.updatedAt).toLocaleDateString()}</div>
                    )}
                    {space.nodes && (
                      <div>Nodes: {space.nodes.length}</div>
                    )}
                  </div>
                  <Link 
                    href={`/spaces/${space.spaceId}`}
                    className="btn btn-primary"
                    style={{ textDecoration: 'none' }}
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
              <h2 style={{ marginBottom: '20px' }}>Create New Space</h2>
              <form onSubmit={handleCreateSpace}>
                <div style={{ marginBottom: '15px' }}>
                  <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
                    Space Name *
                  </label>
                  <input
                    type="text"
                    value={newSpaceName}
                    onChange={(e) => setNewSpaceName(e.target.value)}
                    placeholder="Enter space name..."
                    required
                    disabled={creating}
                  />
                </div>
                <div style={{ marginBottom: '20px' }}>
                  <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
                    Description (Optional)
                  </label>
                  <textarea
                    value={newSpaceDescription}
                    onChange={(e) => setNewSpaceDescription(e.target.value)}
                    placeholder="Enter space description..."
                    rows={3}
                    disabled={creating}
                  />
                </div>
                <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
                  <button
                    type="button"
                    onClick={() => {
                      setCreateModalOpen(false);
                      setNewSpaceName('');
                      setNewSpaceDescription('');
                      setError(null);
                    }}
                    className="btn btn-secondary"
                    disabled={creating}
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="btn btn-primary"
                    disabled={creating || !newSpaceName.trim()}
                  >
                    {creating ? 'Creating...' : 'Create Space'}
                  </button>
                </div>
              </form>
              {error && (
                <div className="error" style={{ marginTop: '15px' }}>
                  {error}
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
