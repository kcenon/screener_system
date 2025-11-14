import { Outlet } from 'react-router-dom'
import { Navbar, Breadcrumb } from './components/navigation'
import { GlobalMarketBar } from './components/layout'

function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <GlobalMarketBar />
      <Breadcrumb />
      <main>
        <Outlet />
      </main>
    </div>
  )
}

export default App
