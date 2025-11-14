import { Outlet } from 'react-router-dom'
import { Navbar, Breadcrumb } from './components/navigation'

function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <Breadcrumb />
      <main>
        <Outlet />
      </main>
    </div>
  )
}

export default App
