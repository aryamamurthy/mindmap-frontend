import React from 'react'
import Link from 'next/link';

export default function Home() {
  return (
    <div style={{ minHeight: '100vh', background: '#f3f4f6', fontFamily: 'Inter, Arial, sans-serif' }}>
      <div style={{ maxWidth: 900, margin: '0 auto', padding: '4rem 1rem' }}>
        <div style={{ textAlign: 'center' }}>
          <h1 style={{ fontSize: '2.5rem', fontWeight: 700, marginBottom: '2rem', color: '#1a202c' }}>
            Mind Map Explorer
          </h1>
          <p style={{ fontSize: '1.15rem', color: '#4b5563', marginBottom: '2rem', maxWidth: 600, marginLeft: 'auto', marginRight: 'auto' }}>
            Create, explore, and organize your thoughts with interactive mind maps. 
            Build hierarchical knowledge structures with AI-powered content generation.
          </p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 16, alignItems: 'center', marginBottom: '2rem' }}>
            <Link
              href="/spaces"
              style={{ background: '#2563eb', color: 'white', padding: '14px 36px', borderRadius: 8, fontWeight: 600, fontSize: '1.1rem', textDecoration: 'none', boxShadow: '0 2px 8px #0001' }}
            >
              Browse Spaces
            </Link>
            <Link
              href="/spaces/new"
              style={{ background: 'white', color: '#2563eb', border: '2px solid #2563eb', padding: '14px 36px', borderRadius: 8, fontWeight: 600, fontSize: '1.1rem', textDecoration: 'none', boxShadow: '0 2px 8px #0001' }}
            >
              Create New Space
            </Link>
          </div>
        </div>
        <div style={{ marginTop: '4rem', display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: 32 }}>
          <div style={{ background: 'white', borderRadius: 12, boxShadow: '0 2px 8px #0001', padding: 32, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
            <div style={{ fontSize: '2.2rem', marginBottom: 16 }}>🗺️</div>
            <h3 style={{ fontSize: '1.15rem', fontWeight: 600, marginBottom: 8 }}>Interactive Mind Maps</h3>
            <p style={{ color: '#6b7280', textAlign: 'center' }}>
              Create hierarchical mind maps with nodes and connections to organize your thoughts visually.
            </p>
          </div>
          <div style={{ background: 'white', borderRadius: 12, boxShadow: '0 2px 8px #0001', padding: 32, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
            <div style={{ fontSize: '2.2rem', marginBottom: 16 }}>🤖</div>
            <h3 style={{ fontSize: '1.15rem', fontWeight: 600, marginBottom: 8 }}>AI-Powered Content</h3>
            <p style={{ color: '#6b7280', textAlign: 'center' }}>
              Generate detailed content for your nodes using AI to expand and enrich your mind maps.
            </p>
          </div>
          <div style={{ background: 'white', borderRadius: 12, boxShadow: '0 2px 8px #0001', padding: 32, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
            <div style={{ fontSize: '2.2rem', marginBottom: 16 }}>📚</div>
            <h3 style={{ fontSize: '1.15rem', fontWeight: 600, marginBottom: 8 }}>Organized Spaces</h3>
            <p style={{ color: '#6b7280', textAlign: 'center' }}>
              Organize your mind maps in spaces for different projects, topics, or areas of interest.
            </p>
          </div>
        </div>
        <div style={{ marginTop: '4rem', textAlign: 'center' }}>
          <h2 style={{ fontSize: '2rem', fontWeight: 700, marginBottom: 16, color: '#1a202c' }}>
            Start Exploring
          </h2>
          <p style={{ color: '#4b5563', marginBottom: 32 }}>
            Ready to organize your thoughts? Create your first space or browse existing ones.
          </p>
          <Link
            href="/spaces"
            style={{ color: '#2563eb', textDecoration: 'none', fontWeight: 600, fontSize: '1.1rem' }}
          >
            View All Spaces →
          </Link>
        </div>
      </div>
    </div>
  );
}
