import './globals.css'

export const metadata = {
  title: 'Mind Map Explorer',
  description: 'A simple mind mapping application',
}

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <header className="header">
          <nav className="nav">
            <h1 className="title">Mind Map Explorer</h1>
          </nav>
        </header>
        <main className="main">
          {children}
        </main>
      </body>
    </html>
  )
}