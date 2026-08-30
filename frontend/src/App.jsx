import { NavLink, Route, Routes } from "react-router-dom";
import Home from "./pages/Home.jsx";
import ProductListing from "./pages/ProductListing.jsx";
import ProductDetail from "./pages/ProductDetail.jsx";
import Wishlist from "./pages/Wishlist.jsx";
import Bag from "./pages/Bag.jsx";
import DecisionStudio from "./pages/DecisionStudio.jsx";
import { ToastProvider } from "./state/ToastContext.jsx";

const navClass = ({ isActive }) => (isActive ? "nav-link active" : "nav-link");

export default function App() {
  return (
    <ToastProvider>
      <div className="app">
        <header className="topbar">
          <div className="topbar-inner">
            <NavLink to="/" className="brand">
              Myntra
            </NavLink>
            <nav className="nav" aria-label="Primary">
              <NavLink to="/" className={navClass} end>
                Home
              </NavLink>
              <NavLink to="/wishlist" className={navClass}>
                Wishlist
              </NavLink>
              <NavLink to="/bag" className={navClass}>
                Bag
              </NavLink>
            </nav>
          </div>
        </header>
        <main className="main">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/products" element={<ProductListing />} />
            <Route path="/product/:productId" element={<ProductDetail />} />
            <Route path="/wishlist" element={<Wishlist />} />
            <Route path="/bag" element={<Bag />} />
            <Route path="/decision-studio" element={<DecisionStudio />} />
          </Routes>
        </main>
      </div>
    </ToastProvider>
  );
}
