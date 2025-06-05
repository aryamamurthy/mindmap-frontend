import React from 'react'
import Link from 'next/link';

export default function Home() {
  return (
    <div className="min-h-screen" style={{ background: 'linear-gradient(135deg, #f0f8ff 0%, #e6f3ff 100%)' }}>
      <div className="container" style={{ paddingTop: '4rem', paddingBottom: '4rem' }}>
        <div className="text-center">
          <h1 style={{ fontSize: '3rem', fontWeight: 'bold', marginBottom: '2rem', color: '#1a202c' }}>
            Mind Map Explorer
          </h1>
          <p style={{ fontSize: '1.25rem', color: '#4a5568', marginBottom: '2rem', maxWidth: '600px', margin: '0 auto 2rem' }}>
            Create, explore, and organize your thoughts with interactive mind maps. 
            Build hierarchical knowledge structures with AI-powered content generation.
          </p>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', alignItems: 'center', marginBottom: '2rem' }}>
            <Link
              href="/spaces"
              className="btn btn-primary"
              style={{ fontSize: '1.1rem', padding: '12px 32px', textDecoration: 'none' }}
            >
              Browse Spaces
            </Link>
            <Link
              href="/spaces/new"
              className="btn"
              style={{ 
                fontSize: '1.1rem', 
                padding: '12px 32px', 
                textDecoration: 'none',
                background: 'white',
                color: '#007bff',
                border: '2px solid #007bff'
              }}
            >
              Create New Space
            </Link>
          </div>
        </div>

        <div style={{ marginTop: '4rem', display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '2rem' }}>
          <div className="card">
            <div style={{ fontSize: '2rem', marginBottom: '1rem' }}>🗺️</div>
            <h3 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '0.5rem' }}>Interactive Mind Maps</h3>
            <p style={{ color: '#4a5568' }}>
              Create hierarchical mind maps with nodes and connections to organize your thoughts visually.
            </p>
          </div>
          
          <div className="card">
            <div style={{ fontSize: '2rem', marginBottom: '1rem' }}>🤖</div>
            <h3 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '0.5rem' }}>AI-Powered Content</h3>
            <p style={{ color: '#4a5568' }}>
              Generate detailed content for your nodes using AI to expand and enrich your mind maps.
            </p>
          </div>
          
          <div className="card">
            <div style={{ fontSize: '2rem', marginBottom: '1rem' }}>📚</div>
            <h3 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '0.5rem' }}>Organized Spaces</h3>
            <p style={{ color: '#4a5568' }}>
              Organize your mind maps in spaces for different projects, topics, or areas of interest.
            </p>
          </div>
        </div>

        <div style={{ marginTop: '4rem', textAlign: 'center' }}>
          <h2 style={{ fontSize: '2rem', fontWeight: 'bold', marginBottom: '1rem', color: '#1a202c' }}>
            Start Exploring
          </h2>
          <p style={{ color: '#4a5568', marginBottom: '2rem' }}>
            Ready to organize your thoughts? Create your first space or browse existing ones.
          </p>
          <Link
            href="/spaces"
            style={{ color: '#007bff', textDecoration: 'none', fontWeight: '600' }}
          >
            View All Spaces →
          </Link>
        </div>
      </div>
    </div>
  );
}
