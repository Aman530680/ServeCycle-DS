import React from 'react'
import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom'
import { OverviewPage } from './pages/OverviewPage'
import { WastePage } from './pages/WastePage'
import { DemandPage } from './pages/DemandPage'
import { EventsPage } from './pages/EventsPage'
import { ModelPage } from './pages/ModelPage'
import { RecommendationsPage } from './pages/RecommendationsPage'
import './styles/tokens.css'
import './styles/layout.css'

const NAV_ITEMS = [
  { to: '/', label: 'Overview', end: true },
  { to: '/waste', label: 'Waste Analysis' },
  { to: '/demand', label: 'Demand' },
  { to: '/events', label: 'Promotions & Events' },
  { to: '/model', label: 'Model' },
  { to: '/recommendations', label: 'Recommendations' },
]

function Sidebar() {
  return (
    <nav className="sidebar" aria-label="Main navigation">
      <div className="sidebar__logo">ServeCycle</div>
      <ul className="sidebar__nav">
        {NAV_ITEMS.map(({ to, label, end }) => (
          <li key={to} className="sidebar__nav-item">
            <NavLink
              to={to}
              end={end}
              className={({ isActive }) => (isActive ? 'active' : '')}
            >
              {label}
            </NavLink>
          </li>
        ))}
      </ul>
    </nav>
  )
}

export function App() {
  return (
    <BrowserRouter>
      <div className="app-shell">
        <Sidebar />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<OverviewPage />} />
            <Route path="/waste" element={<WastePage />} />
            <Route path="/demand" element={<DemandPage />} />
            <Route path="/events" element={<EventsPage />} />
            <Route path="/model" element={<ModelPage />} />
            <Route path="/recommendations" element={<RecommendationsPage />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}
