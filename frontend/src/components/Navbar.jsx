import { Shield, Activity, Sparkles, LogIn, LogOut, User, Clock, Settings } from "lucide-react";

export default function Navbar({ currentPage, onNavigate, user, onLogout }) {
  const links = [
    { id: "home", label: "Home", icon: Activity },
    { id: "predict", label: "Get Recommendation", icon: Shield },
    { id: "bundles", label: "Bundles", icon: Shield },
  ];

  // Add history link for logged-in users
  if (user) {
    links.push({ id: "history", label: "My History", icon: Clock });
  }

  // Add admin link for admins
  if (user?.role === "admin") {
    links.push({ id: "admin", label: "Admin", icon: Settings });
  }

  return (
    <nav className="glass sticky top-0 z-50 border-b border-slate-700/50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <button
            onClick={() => onNavigate("home")}
            className="flex items-center gap-3 group cursor-pointer"
          >
            <div className="relative">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-violet-600 flex items-center justify-center shadow-lg shadow-blue-500/20 group-hover:shadow-blue-500/40 transition-shadow">
                <Sparkles className="w-5 h-5 text-white" />
              </div>
              <div className="absolute -top-1 -right-1 w-3 h-3 bg-emerald-400 rounded-full border-2 border-slate-900 animate-pulse" />
            </div>
            <div>
              <h1 className="text-lg font-bold text-white tracking-tight">
                Assurance<span className="text-blue-400">AI</span>
              </h1>
              <p className="text-[10px] text-slate-400 -mt-1 font-medium tracking-wider uppercase">
                Smart Insurance
              </p>
            </div>
          </button>

          {/* Navigation */}
          <div className="flex items-center gap-1">
            {links.map(({ id, label, icon: Icon }) => (
              <button
                key={id}
                onClick={() => onNavigate(id)}
                className={`
                  flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-all cursor-pointer
                  ${
                    currentPage === id
                      ? "bg-blue-500/20 text-blue-400 shadow-inner"
                      : "text-slate-400 hover:text-white hover:bg-slate-800/50"
                  }
                `}
              >
                <Icon className="w-4 h-4" />
                <span className="hidden md:inline">{label}</span>
              </button>
            ))}

            {/* Divider */}
            <div className="w-px h-6 bg-slate-700/50 mx-2" />

            {/* Auth buttons */}
            {user ? (
              <div className="flex items-center gap-2">
                <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-800/50">
                  <div className="w-6 h-6 rounded-full bg-gradient-to-br from-blue-500 to-violet-500 flex items-center justify-center">
                    <User className="w-3 h-3 text-white" />
                  </div>
                  <span className="text-xs text-slate-300 font-medium max-w-[100px] truncate">
                    {user.full_name}
                  </span>
                  {user.role === "admin" && (
                    <span className="px-1.5 py-0.5 rounded text-[10px] bg-violet-500/20 text-violet-400 font-bold">
                      ADMIN
                    </span>
                  )}
                </div>
                <button
                  onClick={onLogout}
                  className="flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm text-slate-400 hover:text-red-400 hover:bg-red-500/10 transition-all cursor-pointer"
                >
                  <LogOut className="w-4 h-4" />
                  <span className="hidden sm:inline">Logout</span>
                </button>
              </div>
            ) : (
              <button
                onClick={() => onNavigate("login")}
                className="flex items-center gap-2 px-4 py-2 rounded-lg bg-blue-500/20 text-blue-400 text-sm font-medium hover:bg-blue-500/30 transition-all cursor-pointer"
              >
                <LogIn className="w-4 h-4" />
                <span className="hidden sm:inline">Sign In</span>
              </button>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}
