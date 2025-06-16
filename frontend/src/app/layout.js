import './globals.css'

export const metadata = {
  title: 'Mind Map Explorer',
  description: 'A simple mind mapping application',
}

export default function RootLayout({ children }) {
  return (
    <html lang="en" style={{ height: 'auto', width: 'auto', margin: 0, padding: 0, boxSizing: 'border-box', overflow: 'auto' }}>
      <body style={{
        background: '#f3f4f6',
        minHeight: '100vh',
        minWidth: 0,
        height: 'auto',
        width: 'auto',
        color: '#1a202c',
        fontFamily: 'Inter, Arial, sans-serif',
        margin: 0,
        padding: 0,
        boxSizing: 'border-box',
        overflow: 'auto',
        display: 'flex',
        flexDirection: 'column',
      }}>
        <header style={{ width: '100%', background: 'white', boxShadow: '0 2px 8px #0001', padding: '1rem 0', marginBottom: 0, flexShrink: 0 }}>
          <nav style={{ maxWidth: 900, margin: '0 auto', padding: '0 1rem', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <h1 style={{ fontSize: '2rem', fontWeight: 700, color: '#1a202c', textAlign: 'center', width: '100%' }}>Mind Map Explorer</h1>
          </nav>
        </header>
        <main style={{
          flex: 1,
          width: '100%',
          height: 'auto',
          maxWidth: '100vw',
          margin: 0,
          padding: 0,
          boxSizing: 'border-box',
          overflow: 'visible',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'flex-start',
        }}>
          {children}
        </main>
      </body>
    </html>
  )
}