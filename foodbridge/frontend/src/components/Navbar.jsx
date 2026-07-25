import { NavLink } from "react-router-dom";

const linkClass = ({ isActive }) =>
  `px-4 py-2 rounded-full text-sm font-medium transition ${
    isActive ? "bg-brand-600 text-white" : "text-brand-700 hover:bg-brand-100"
  }`;

export default function Navbar() {
  return (
    <nav className="bg-white shadow-sm sticky top-0 z-10">
      <div className="max-w-6xl mx-auto flex items-center justify-between px-6 py-4">
        <div className="flex items-center gap-2">
          <span className="text-2xl">🍲</span>
          <span className="font-bold text-brand-700 text-lg">FoodBridge India</span>
        </div>
        <div className="flex gap-2">
          <NavLink to="/" className={linkClass} end>Home</NavLink>
          <NavLink to="/donate" className={linkClass}>Donate Food</NavLink>
          <NavLink to="/ngos" className={linkClass}>NGOs</NavLink>
        </div>
      </div>
    </nav>
  );
}
