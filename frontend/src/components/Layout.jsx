import { Outlet, Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../AuthContext';

export default function Layout() {
  const { user, logout, isAdmin } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="min-h-screen flex flex-col">
      <header className="border-b border-slate-800 bg-slate-900/80 backdrop-blur">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex justify-between items-center h-14">
          <Link to={isAdmin ? '/admin' : '/'} className="text-lg font-semibold text-emerald-400">
            Payment Gateway
          </Link>
          <nav className="flex items-center gap-4">
            {isAdmin && (
              <Link to="/admin" className="text-slate-400 hover:text-white transition">
                Admin
              </Link>
            )}
            {!isAdmin && (
              <Link to="/" className="text-slate-400 hover:text-white transition">
                Dashboard
              </Link>
            )}
            <span className="text-slate-500 text-sm">{user?.email}</span>
            <button
              onClick={handleLogout}
              className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-sm transition"
            >
              Sair
            </button>
          </nav>
        </div>
      </header>
      <main className="flex-1 p-6">
        <Outlet />
      </main>
    </div>
  );
}
