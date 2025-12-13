import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { authService } from './services/api';
import Auth from './pages/Auth';
import Home from './pages/Home';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  return authService.isAuthenticated() ? <>{children}</> : <Navigate to="/auth" />;
}

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/auth" element={<Auth />} />
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <Home />
            </ProtectedRoute>
          }
        />
      </Routes>
    </Router>
  );
}

export default App;
