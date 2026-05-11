import { useAuth } from "../context/AuthContext";

export default function Navbar() {
  const { user, logout } = useAuth();

  return (
    <header className="border-b border-gray-800 bg-gray-900/80 backdrop-blur sticky top-0 z-40">
      <div className="max-w-5xl mx-auto px-4 h-16 flex items-center justify-between">
        <h1 className="text-2xl font-bold text-white">
          Task<span className="text-brand-500">Flow</span>
        </h1>

        <div className="flex items-center gap-4">
          <span className="text-gray-400 text-sm hidden sm:block">
            @{user?.username}
          </span>
          <button onClick={logout} className="btn-secondary text-sm px-3 py-1.5">
            Sign out
          </button>
        </div>
      </div>
    </header>
  );
}
