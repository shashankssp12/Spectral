import {
  BrowserRouter as Router,
  Route,
  Routes
} from 'react-router-dom';


import Home from './pages/Home';
import Dashboard from './pages/Dashboard';
import Auth from './pages/Auth';
import SharedFile from './pages/Shared-File';

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/shared-file/:fileId" element={<SharedFile />} />
        <Route path="/auth" element={<Auth />} />
      </Routes>
    </Router>
  );
}